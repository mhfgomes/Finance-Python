import logging
from datetime import datetime, timezone

import requests
from django.db import connection

logger = logging.getLogger(__name__)

FRANKFURTER_URL = 'https://api.frankfurter.app/latest?base=EUR'


def fetch_and_update_rates():
    """
    Fetch the latest EUR-based exchange rates from the Frankfurter API
    and update fin_exchange_rate in the database.

    Frankfurter returns how many units of each currency equal 1 EUR,
    so we invert to get rate_to_eur (EUR per 1 unit of currency).
    """
    try:
        response = requests.get(FRANKFURTER_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error('Failed to fetch exchange rates: %s', e)
        return

    rates_from_eur = data.get('rates', {})
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    with connection.cursor() as cur:
        # EUR itself
        cur.execute(
            "INSERT OR IGNORE INTO fin_exchange_rate (currency, rate_to_eur, updated_at) VALUES ('EUR', 1.0, %s)",
            [now],
        )
        cur.execute(
            "UPDATE fin_exchange_rate SET rate_to_eur=1.0, updated_at=%s WHERE currency='EUR'",
            [now],
        )

        for currency, rate_from_eur in rates_from_eur.items():
            rate_to_eur = 1.0 / rate_from_eur
            cur.execute(
                "INSERT OR IGNORE INTO fin_exchange_rate (currency, rate_to_eur, updated_at) VALUES (%s, %s, %s)",
                [currency, rate_to_eur, now],
            )
            cur.execute(
                "UPDATE fin_exchange_rate SET rate_to_eur=%s, updated_at=%s WHERE currency=%s",
                [rate_to_eur, now, currency],
            )

    logger.info('Exchange rates updated at %s (%d currencies)', now, len(rates_from_eur) + 1)
