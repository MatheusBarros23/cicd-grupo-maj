"""Ponto de entrada do pacote, executado pelo container (`python -m app`)."""

from app.core import calculate_total, is_valid_email, normalize_name


def main():
    """Exercita as funções do pacote como smoke check da imagem."""
    print("app — Atividade 1 de CI/CD")
    print("calculate_total([40, 25, 35], 10, 10) =",
          calculate_total([40, 25, 35], discount_percent=10, tax_rate=10))
    print("normalize_name('  Maria Souza  ') =",
          normalize_name("  Maria Souza  "))
    print("is_valid_email('aluno@instituicao.com.br') =",
          is_valid_email("aluno@instituicao.com.br"))


if __name__ == "__main__":
    main()
