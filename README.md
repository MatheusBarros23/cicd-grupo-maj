# Atividade 1 - CI/CD com GitHub

![CI](https://github.com/MatheusBarros23/cicd-grupo-maj/actions/workflows/ci.yml/badge.svg)

Pipeline de integração contínua em GitHub Actions atuando como *quality gate*:
nenhum código entra na `main` sem passar por lint, testes e scans de segurança.

## Grupo

- Matheus Barros
- Andre Marques
- Jackson Silva

## Aplicação

A aplicação vem do `cicd-starter-kit`: uma todolist em Flask com persistência em
SQLite via SQLAlchemy e autenticação por sessão.

Rotas relevantes:

| Rota | O que faz |
|---|---|
| `/login`, `/logout` | Autenticação por sessão |
| `/` | Lista, com formulário de criação |
| `/add`, `/toggle/<id>`, `/delete/<id>` | CRUD das tarefas |
| `/healthz` | Health check — executa `SELECT 1` no banco; usado pelos probes do Kubernetes |
| `/pods` | Lista os pods do namespace consultando a API do Kubernetes via ServiceAccount |
| `/cleanup/status` | Histórico do CronJob de limpeza e controle de suspend/resume |
| `/cleanup` | Remove tarefas concluídas; exige o header `X-Cleanup-Token` |

As rotas `/pods` e `/cleanup/status` só funcionam dentro de um cluster — fora
dele degradam com mensagem de erro em vez de quebrar. Elas são o insumo da
Atividade 2.

Configuração por variável de ambiente: `DATABASE_URI`, `SESSION_KEY`,
`ADMIN_USER`, `ADMIN_PASSWORD`, `CLEANUP_TOKEN`, `CLEANUP_JOB_PREFIX`,
`APP_NAME`, `APP_COLOR`, `APP_PORT` e `IMAGE_TAGS`.

## Estrutura do projeto

- `app.py`: aplicação Flask;
- `test_app.py`: suíte pytest (13 testes);
- `requirements.txt`: dependências de runtime, pinadas;
- `requirements-dev.txt`: dependências de CI e desenvolvimento — inclui
  `-r requirements.txt`, então instalar este arquivo instala os dois;
- `pyproject.toml`: configuração do Ruff;
- `Dockerfile`: imagem da aplicação, servida por gunicorn;
- `.github/workflows/ci.yml`: pipeline de CI;
- `.github/workflows/_reusable-test.yml`: workflow reutilizável com os steps de teste;
- `.github/CODEOWNERS`: revisores automáticos por caminho;
- `k8s/`: manifests de deploy (Rolling e Blue/Green) — usados na Atividade 2;
- `docs/`: referência das pipelines de CI e CD e do setup da VM de laboratório.

## Pré-requisitos

- Python 3.11 ou superior (o Ruff está configurado com `target-version = "py311"`)
- Git
- Docker (opcional — apenas para construir a imagem localmente)

## Como rodar os checks localmente

Os comandos abaixo são **os mesmos que o CI executa**. Funcionam em Linux, macOS
e WSL.

```bash
git clone https://github.com/MatheusBarros23/cicd-grupo-maj.git
cd cicd-grupo-maj

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Os três gates:

```bash
ruff check .   # lint        (job "Lint (ruff)")
pytest -v      # testes      (job "Test")
pip-audit      # dependências (job "Dependency audit (pip-audit)")
```

## Como rodar a aplicação localmente

O `DATABASE_URI` padrão é `sqlite:////data/todos.db` — caminho absoluto que
existe dentro do container, mas não na sua máquina. Localmente, aponte o banco
para o diretório atual:

```bash
DATABASE_URI=sqlite:///todos.db python app.py
```

A app sobe em `http://localhost:5000`. As credenciais padrão são `admin` /
`admin`, sobrescrevíveis por `ADMIN_USER` e `ADMIN_PASSWORD`.

Via container, o `/data` já existe na imagem e o padrão funciona sem ajuste:

```bash
docker build -t app-k8s-todolist .
docker run --rm -p 5000:5000 app-k8s-todolist
```

## Pipeline de CI

O workflow em `.github/workflows/ci.yml` dispara em `pull_request` para a `main`,
em `push` na `main` e manualmente via `workflow_dispatch`. O padrão de permissão
é `contents: read`, e só o job que precisa de mais eleva o próprio privilégio.
Todas as actions são fixadas por SHA de commit, não por tag — tag é mutável, e
quem controlar a conta do mantenedor passaria a executar código no pipeline com
acesso aos secrets.

### Job `lint`

Roda `ruff check .` com as regras do `pyproject.toml` (`E`, `F`, `W`, `I`, `UP`,
`B`, com `E501` ignorado por causa dos templates HTML inline).

### Job `test`

Não tem steps próprios: chama o workflow reutilizável
`.github/workflows/_reusable-test.yml` via `uses:`, passando as versões do Python
como input. A matrix vive no chamador e a lógica de teste vive no reutilizável —
trocar as versões não toca nos steps, e mudar os steps não toca nas versões.

O reutilizável roda uma matrix de 3.11, 3.12 e 3.13 com `fail-fast: false`, e em
cada versão faz checkout, configura o Python, restaura o cache de `~/.cache/pip`
(chave por SO + versão do Python + hash dos requirements e do `pyproject.toml`),
instala as dependências e executa `pytest -v`.

### Job `security`

Executa `pip-audit` e falha se houver CVE com correção disponível. Rodamos sem
`-r`, sobre o ambiente já instalado: assim a auditoria alcança também as
dependências transitivas resolvidas, que não aparecem nos manifestos.

### Job `trivy`

Roda o Trivy em `scan-type: fs`, que analisa arquivos e manifestos sem precisar
buildar a imagem. Cobre mais que o `pip-audit`: além das bibliotecas Python,
alcança pacotes de sistema e outros ecossistemas do repo.

Está com `exit-code: '0'` **de propósito** — aqui o Trivy é camada de
visibilidade, não gate. O bloqueio de dependências é responsabilidade do
`pip-audit`, que falha o build. Assim evitamos deixar a `main` eternamente
vermelha por CVE de pacote de sistema fora do nosso controle, sem perder o
relatório. `ignore-unfixed: true` reforça isso e `severity: HIGH,CRITICAL`
mantém o resultado no que é acionável.

O resultado sai em SARIF e vai para **Security → Code scanning**, o que explica o
`security-events: write` nas `permissions` deste job — e só dele. O mesmo SARIF
sobe como artefato do run, garantindo acesso ao relatório de qualquer forma.

### Job `publish`

Depende de `lint`, `test`, `security` e `trivy`, e só executa em `push` na `main`
— nunca em pull request. Está associado ao environment `production`, que exige
aprovação humana antes de publicar.

Publica no GitHub Container Registry autenticando com o `GITHUB_TOKEN` do próprio
workflow. Foi uma decisão deliberada em vez de Docker Hub: dispensa criar e
guardar um access token, o que elimina a principal via de vazamento de credencial
no pipeline. O nome do owner é normalizado para minúsculas porque referências de
registry não aceitam maiúsculas.

A imagem é marcada com o SHA do commit, não com `latest`: tag imutável é o que
permite saber qual código está rodando e fazer rollback para um ponto exato. O
mesmo valor é injetado como `build-arg IMAGE_TAGS`, que a aplicação exibe no
rodapé — dá para confirmar visualmente qual build está no ar.

### Job `notify`

Roda com `if: always()`, justamente para avisar quando algo falhou, e envia o
resultado por webhook. O envio é pulado enquanto o secret `NOTIFY_WEBHOOK_URL`
não existir, para que a ausência de webhook não deixe o pipeline vermelho.

## Como demonstrar o shift-left

O objetivo é mostrar o gate **bloqueando um merge** e depois liberando-o.

### Falha de segurança (demonstração principal)

O `requirements.txt` fixa `requests==2.33.0`. Rebaixar essa versão introduz
vulnerabilidades conhecidas com correção disponível, que é exatamente o que o
`pip-audit` reprova:

```bash
git checkout -b demo/falha-seguranca
# em requirements.txt: requests==2.33.0  ->  requests==2.31.0
git commit -am "chore: rebaixa requests para demonstrar o gate"
git push origin demo/falha-seguranca
```

1. Abra o pull request;
2. o job `Dependency audit (pip-audit)` fica vermelho e lista os CVEs;
3. o merge é bloqueado pelo required status check;
4. **no mesmo PR**, volte para `requests==2.33.0`;
5. o check fica verde e o merge é liberado.

Custo da correção: 1x, no mesmo PR que introduziu o problema. Sem esse gate, a
versão vulnerável entraria na `main` e seria descoberta num scan tardio — ou num
incidente.

### Falha de teste (demonstração complementar)

```bash
git checkout -b demo/falha-teste
# em test_app.py, troque uma asserção por algo incorreto, ex.:
#   assert resp.status_code == 500   em test_healthz
```

O job `Test` fica vermelho e o log do `pytest` mostra exatamente qual asserção
falhou, em qual versão do Python.
