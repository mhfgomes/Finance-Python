from django.db import connection

CURRENCIES = {
    'EUR': {'symbol': '€',   'name': 'Euro'},
    'USD': {'symbol': '$',   'name': 'US Dollar'},
    'GBP': {'symbol': '£',   'name': 'British Pound'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},
    'JPY': {'symbol': '¥',   'name': 'Japanese Yen'},
    'CAD': {'symbol': 'CA$', 'name': 'Canadian Dollar'},
    'AUD': {'symbol': 'AU$', 'name': 'Australian Dollar'},
}

CURRENCY_CHOICES = [(k, f"{v['symbol']} — {v['name']}") for k, v in CURRENCIES.items()]


def get_symbol(currency_code):
    return CURRENCIES.get(currency_code, {}).get('symbol', currency_code)


def get_rates():
    """Return dict of {currency: rate_to_eur} from DB."""
    with connection.cursor() as cur:
        cur.execute("SELECT currency, rate_to_eur FROM fin_exchange_rate")
        return {row[0]: row[1] for row in cur.fetchall()}


def convert_to_eur(amount, currency_code, rates):
    """Convert amount in currency_code to EUR using the rates dict."""
    if currency_code == 'EUR':
        return amount
    rate = rates.get(currency_code, 1.0)
    return amount * rate
