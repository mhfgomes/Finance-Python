from django.db import connection
from .db import dictfetchall, dictfetchone
from . import currency_service
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _enrich(accounts):
    for a in accounts:
        a['currency_symbol'] = currency_service.get_symbol(a.get('currency', 'EUR'))
    return accounts


def get_accounts(user_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fin_account WHERE user_id=%s ORDER BY name",
            [user_id]
        )
        return _enrich(dictfetchall(cur))


def get_account(account_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fin_account WHERE id=%s AND user_id=%s",
            [account_id, user_id]
        )
        account = dictfetchone(cur)
    if account:
        account['currency_symbol'] = currency_service.get_symbol(account.get('currency', 'EUR'))
    return account


def create_account(user_id, name, account_type, balance, description, currency='EUR'):
    now = _now()
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO fin_account (user_id, name, account_type, balance, description, currency, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            [user_id, name, account_type, balance, description, currency, now, now]
        )
        return cur.lastrowid


def update_account(account_id, user_id, name, account_type, description, currency='EUR'):
    now = _now()
    with connection.cursor() as cur:
        cur.execute(
            """UPDATE fin_account
               SET name=%s, account_type=%s, description=%s, currency=%s, updated_at=%s
               WHERE id=%s AND user_id=%s""",
            [name, account_type, description, currency, now, account_id, user_id]
        )


def delete_account(account_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM fin_account WHERE id=%s AND user_id=%s",
            [account_id, user_id]
        )


def adjust_balance(account_id, delta):
    """Add delta (positive or negative) to account balance."""
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE fin_account SET balance = balance + %s, updated_at = %s WHERE id=%s",
            [delta, _now(), account_id]
        )
