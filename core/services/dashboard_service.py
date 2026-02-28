from django.db import connection
from .db import dictfetchall, dictfetchone
from .budget_service import get_budget_usage
from . import currency_service
from datetime import datetime


def get_total_balance(user_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT balance, currency FROM fin_account WHERE user_id=%s",
            [user_id]
        )
        rows = cur.fetchall()
    rates = currency_service.get_rates()
    return sum(currency_service.convert_to_eur(bal, curr, rates) for bal, curr in rows)


def get_monthly_income_expense(user_id, month, year):
    month_str = f"{year}-{month:02d}"
    with connection.cursor() as cur:
        cur.execute(
            """SELECT t.transaction_type, t.amount, a.currency
               FROM fin_transaction t
               JOIN fin_account a ON t.account_id = a.id
               WHERE t.user_id=%s AND strftime('%%Y-%%m', t.date)=%s""",
            [user_id, month_str]
        )
        rows = cur.fetchall()
    rates = currency_service.get_rates()
    income = sum(currency_service.convert_to_eur(amt, curr, rates)
                 for ttype, amt, curr in rows if ttype == 'income')
    expense = sum(currency_service.convert_to_eur(amt, curr, rates)
                  for ttype, amt, curr in rows if ttype == 'expense')
    return {'income': income, 'expense': expense}


def get_recent_transactions(user_id, limit=10):
    with connection.cursor() as cur:
        cur.execute(
            """SELECT t.*, c.name AS category_name, c.color AS category_color,
                      a.name AS account_name, a.currency AS currency
               FROM fin_transaction t
               LEFT JOIN fin_category c ON t.category_id = c.id
               LEFT JOIN fin_account a ON t.account_id = a.id
               WHERE t.user_id=%s
               ORDER BY t.date DESC, t.id DESC
               LIMIT %s""",
            [user_id, limit]
        )
        txs = dictfetchall(cur)
    for tx in txs:
        tx['currency_symbol'] = currency_service.get_symbol(tx.get('currency', 'EUR'))
    return txs


def get_budget_alerts(user_id):
    """Return budgets where spending >= 80% of budget for current month."""
    now = datetime.now()
    budgets = get_budget_usage(user_id, now.month, now.year)
    return [b for b in budgets if b['percent'] >= 80]
