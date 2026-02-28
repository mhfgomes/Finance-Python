import csv
import io
from django.db import connection
from .db import dictfetchall, dictfetchone
from .account_service import adjust_balance
from . import currency_service
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _enrich(transactions):
    for tx in transactions:
        tx['currency_symbol'] = currency_service.get_symbol(tx.get('currency', 'EUR'))
    return transactions


def get_transactions(user_id, date_from=None, date_to=None, category_id=None,
                     account_id=None, transaction_type=None):
    sql = """
        SELECT t.*, c.name AS category_name, c.color AS category_color,
               a.name AS account_name, a.currency AS currency
        FROM fin_transaction t
        LEFT JOIN fin_category c ON t.category_id = c.id
        LEFT JOIN fin_account a ON t.account_id = a.id
        WHERE t.user_id=%s
    """
    params = [user_id]

    if date_from:
        sql += " AND t.date >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND t.date <= %s"
        params.append(date_to)
    if category_id:
        sql += " AND t.category_id = %s"
        params.append(category_id)
    if account_id:
        sql += " AND t.account_id = %s"
        params.append(account_id)
    if transaction_type:
        sql += " AND t.transaction_type = %s"
        params.append(transaction_type)

    sql += " ORDER BY t.date DESC, t.id DESC"

    with connection.cursor() as cur:
        cur.execute(sql, params)
        return _enrich(dictfetchall(cur))


def get_transaction(transaction_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            """SELECT t.*, a.currency AS currency
               FROM fin_transaction t
               JOIN fin_account a ON t.account_id = a.id
               WHERE t.id=%s AND t.user_id=%s""",
            [transaction_id, user_id]
        )
        tx = dictfetchone(cur)
    if tx:
        tx['currency_symbol'] = currency_service.get_symbol(tx.get('currency', 'EUR'))
    return tx


def create_transaction(user_id, account_id, category_id, amount, transaction_type,
                       description, date, receipt_image=None):
    now = _now()
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO fin_transaction
               (user_id, account_id, category_id, amount, transaction_type,
                description, date, receipt_image, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [user_id, account_id, category_id or None, amount, transaction_type,
             description, date, receipt_image, now]
        )
        tx_id = cur.lastrowid

    # Update account balance
    delta = amount if transaction_type == 'income' else -amount
    adjust_balance(account_id, delta)
    return tx_id


def update_transaction(transaction_id, user_id, account_id, category_id, amount,
                       transaction_type, description, date, receipt_image=None):
    # Reverse the old transaction's effect on balance
    old = get_transaction(transaction_id, user_id)
    if not old:
        return
    old_delta = old['amount'] if old['transaction_type'] == 'income' else -old['amount']
    adjust_balance(old['account_id'], -old_delta)

    with connection.cursor() as cur:
        if receipt_image is not None:
            cur.execute(
                """UPDATE fin_transaction
                   SET account_id=%s, category_id=%s, amount=%s, transaction_type=%s,
                       description=%s, date=%s, receipt_image=%s
                   WHERE id=%s AND user_id=%s""",
                [account_id, category_id or None, amount, transaction_type,
                 description, date, receipt_image, transaction_id, user_id]
            )
        else:
            cur.execute(
                """UPDATE fin_transaction
                   SET account_id=%s, category_id=%s, amount=%s, transaction_type=%s,
                       description=%s, date=%s
                   WHERE id=%s AND user_id=%s""",
                [account_id, category_id or None, amount, transaction_type,
                 description, date, transaction_id, user_id]
            )

    # Apply new effect on balance
    new_delta = amount if transaction_type == 'income' else -amount
    adjust_balance(account_id, new_delta)


def delete_transaction(transaction_id, user_id):
    tx = get_transaction(transaction_id, user_id)
    if not tx:
        return
    # Reverse the balance effect
    delta = tx['amount'] if tx['transaction_type'] == 'income' else -tx['amount']
    adjust_balance(tx['account_id'], -delta)

    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM fin_transaction WHERE id=%s AND user_id=%s",
            [transaction_id, user_id]
        )


def export_csv(user_id):
    transactions = get_transactions(user_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Amount', 'Currency', 'Category', 'Account', 'Description'])
    for tx in transactions:
        writer.writerow([
            tx['date'],
            tx['transaction_type'],
            tx['amount'],
            tx.get('currency', 'EUR'),
            tx.get('category_name', ''),
            tx.get('account_name', ''),
            tx.get('description', ''),
        ])
    return output.getvalue()
