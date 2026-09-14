# Atividade 1 - CI/CD com GitHub

Este projeto foi estruturado para demonstrar boas práticas de integração contínua e entrega contínua usando GitHub e GitHub Actions.

## Objetivo

Implementar uma base mínima e profissional de desenvolvimento com:

- controle de versão em GitHub;
- automação de qualidade com lint e testes;
- build do pacote Python;
- documentação de processo e evidências;
- pipeline de CI para validação automatizada em cada alteração.

## Estrutura do projeto

- `src/app/`: código-fonte do projeto;
- `tests/`: testes automatizados;
- `.github/workflows/ci.yml`: pipeline de CI;
- `pyproject.toml`: configuração do pacote e dependências de desenvolvimento.

## Pré-requisitos

- Python 3.11+
- Git
- GitHub

## Como executar localmente no WSL / Linux

1. Instale o UV se ainda não estiver disponível:

   curl -LsSf https://astral.sh/uv/install.sh | sh

2. Crie e sincronize o ambiente do projeto:

   cd /mnt/c/Users/mathe/OneDrive/Documents/devops\ -\ ci_cd
   uv venv
   uv sync --extra dev

3. Execute a validação local:

   source .venv/bin/activate
   uv run flake8 src tests
   uv run pytest
   uv build

> No Windows, o mesmo fluxo pode ser executado pela interface do WSL ou com `py -3` caso prefira. O projeto está preparado para usar UV como padrão de dependências.

## Pipeline de CI

O workflow em `.github/workflows/ci.yml` executa as seguintes etapas:

- checkout do repositório;
- configuração do Python;
- instalação das dependências com UV;
- análise estática com flake8;
- testes automatizados com pytest;
- build do pacote para geração de artefato;
- upload do artefato em GitHub Actions.

### Como simular uma falha de gate

Para demonstrar que o pipeline bloqueia falhas reais, execute uma alteração temporária em uma branch de teste, por exemplo:

1. Crie uma branch de demonstração: `git checkout -b demo/falha-gate`;
2. Altere um teste para quebrar a lógica, como `assert 1 == 2`;
3. Faça o push da branch e abra o pull request;
4. O pipeline falha em `pytest` ou `flake8`, bloqueando a entrega;
5. Corrija a alteração e reenvie para fechar a demonstração.

Esse processo mostra, de forma real, que o CI/CD está impedindo a promoção de código quebrado.

## Recomendação de uso no GitHub

1. Crie um repositório público ou privado no GitHub.
2. Envie este projeto para o repositório.
3. Ative o GitHub Actions.
4. Abra pull requests para validar o pipeline em branches de desenvolvimento.
5. Use tags semânticas para versionamento do produto quando houver release.
