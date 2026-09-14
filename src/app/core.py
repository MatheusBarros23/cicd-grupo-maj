import re


def calculate_total(items, discount_percent=0, tax_rate=0):
    """Calcula o total de uma compra aplicando desconto e imposto."""
    subtotal = sum(float(item) for item in items)
    discount = subtotal * (float(discount_percent) / 100)
    taxed = (subtotal - discount) * (1 + float(tax_rate) / 100)
    return round(taxed, 2)


def normalize_name(name):
    """Normaliza um nome para uso em processamento posterior."""
    return str(name).strip().lower()


def is_valid_email(email):
    """Valida um endereço de e-mail simples."""
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(pattern, str(email)))
