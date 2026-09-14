from app.core import (
    calculate_total,
    is_valid_email,
    normalize_name,
)


def test_calculate_total_applies_discount_and_tax():
    total = calculate_total([40, 25, 35], discount_percent=10, tax_rate=10)
    assert total == 99.0


def test_calculate_total_handles_empty_cart():
    total = calculate_total([], discount_percent=5, tax_rate=8)
    assert total == 0.0


def test_normalize_name_trims_and_lowercases():
    assert normalize_name("  Maria Souza  ") == "maria souza"


def test_email_validation_accepts_valid_address():
    assert is_valid_email("aluno@instituicao.com.br") is True


def test_email_validation_rejects_invalid_address():
    assert is_valid_email("aluno@instituicao") is False
