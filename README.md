# Atividade 1 - CI/CD com GitHub

![CI](https://github.com/MatheusBarros23/cicd-grupo-maj/actions/workflows/ci.yml/badge.svg)

Este projeto demonstra boas práticas de integração contínua usando GitHub Actions,
com o pipeline atuando como *quality gate*: nenhum código entra na `main` sem
passar pelos checks automatizados.

## Objetivo

Implementar uma base mínima e profissional de desenvolvimento com:

- controle de versão em GitHub;
- automação de qualidade com testes e auditoria de dependências;
- publicação de imagem de container;
- documentação de processo e evidências;
- pipeline de CI para validação automatizada em cada alteração.

## Estrutura do projeto

- `src/app/`: código-fonte do projeto;
- `tests/`: testes automatizados;
- `.github/workflows/ci.yml`: pipeline de CI;
- `.github/workflows/_reusable-test.yml`: workflow reutilizável com os steps de teste;
- `.github/CODEOWNERS`: revisores automáticos por caminho;
- `pyproject.toml`: configuração do pacote e dependências de desenvolvimento;
- `.flake8`: configuração do linter;
- `Dockerfile`: imagem da aplicação, publicada no GHCR a cada push na `main`.

## Pré-requisitos

- Python 3.11 ou superior (definido em `requires-python` no `pyproject.toml`)
- Git
- Docker (opcional — apenas para construir a imagem localmente)

## Como rodar os checks localmente

Os comandos abaixo são **os mesmos que o CI executa**. Funcionam em Linux, macOS
e WSL. Clone o repositório em qualquer diretório de sua preferência:

```bash
git clone https://github.com/MatheusBarros23/cicd-grupo-maj.git
cd cicd-grupo-maj
```

Crie o ambiente e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

Execute os gates:

```bash
pytest -v    # testes (mesmo comando do job test)
pip-audit    # auditoria de dependências do ambiente (mesmo comando do job security)
```

Verificação de estilo (o mesmo comando que o job `lint` executa):

```bash
flake8 src tests
```

### Alternativa com UV

O repositório também versiona um `uv.lock`. Quem preferir usar o
[UV](https://astral.sh/uv) pode rodar:

```bash
uv venv
uv sync --extra dev
uv run pytest -v
uv run flake8 src tests
```

> O CI **não** usa UV — ele instala com `pip` a partir dos arquivos
> `requirements*.txt`. O `uv.lock` existe apenas como conveniência local.

## Pipeline de CI

O workflow em `.github/workflows/ci.yml` dispara em `pull_request` para a `main`,
em `push` na `main` e manualmente via `workflow_dispatch`. O padrão de permissão
é `contents: read`, e só o job que precisa de mais eleva o próprio privilégio.

### Job `lint`

Roda `flake8 src tests` com a configuração do `.flake8`.

### Job `test`

Não tem steps próprios: chama o workflow reutilizável
`.github/workflows/_reusable-test.yml` via `uses:`, passando as versões do Python
como input. A matrix vive no chamador e a lógica de teste vive no reutilizável —
trocar as versões não toca nos steps, e mudar os steps não toca nas versões.

O reutilizável roda uma matrix de 3.11, 3.12 e 3.13 com `fail-fast: false`, e em
cada versão faz checkout, configura o Python, restaura o cache de `~/.cache/pip`
(chave por SO + versão do Python + hash de `requirements*.txt` e
`pyproject.toml`), instala as dependências e executa `pytest -v`.

### Job `security`

Executa `pip-audit` sobre o ambiente instalado e falha se houver CVE. Auditamos o
ambiente em vez de passar `-r requirements.txt` porque aquele arquivo contém
`-e .`, e requisitos editáveis não são analisáveis a partir do manifesto —
auditar o ambiente cobre o pacote, as dependências de dev e todas as transitivas.

### Job `publish`

Depende de `lint`, `test` e `security`, e só executa em `push` na `main` — nunca
em pull request. Está associado ao environment `production`, o que exige
aprovação humana antes de publicar. Faz login no GitHub Container Registry com o
`GITHUB_TOKEN` do próprio workflow — sem PAT e sem credencial commitada — e
publica a imagem com duas tags: o SHA do commit (que é o que permite rollback) e
`latest`. O nome do owner é normalizado para minúsculas porque referências de
registry não aceitam maiúsculas.

### Job `notify`

Roda com `if: always()`, justamente para avisar quando algo falhou, e envia o
resultado por webhook. O envio é pulado enquanto o secret `NOTIFY_WEBHOOK_URL`
não existir, para que a ausência de webhook não deixe o pipeline vermelho.


## Como demonstrar o shift-left

O objetivo é mostrar o gate **bloqueando um merge** e depois liberando-o.

### Falha de segurança (demonstração principal)

1. Crie uma branch: `git checkout -b demo/falha-seguranca`;
2. Fixe uma versão vulnerável de uma dependência nos requirements;
3. Faça push e abra o pull request;
4. O `pip-audit` reprova, o check fica vermelho e o merge é bloqueado;
5. No mesmo PR, atualize para a versão corrigida;
6. O check volta a verde e o merge é liberado.

### Falha de teste (demonstração complementar)

1. Crie uma branch: `git checkout -b demo/falha-teste`;
2. Altere uma asserção em `tests/test_core.py` para algo incorreto;
3. Faça push e abra o pull request;
4. O `pytest` falha e o log mostra exatamente qual asserção quebrou;
5. Reverta a alteração para fechar a demonstração.
