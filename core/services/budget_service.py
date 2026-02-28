from django.db import connection
from .db import dictfetchall, dictfetchone
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def get_budgets(user_id, month=None, year=None):
    sql = """
        SELECT b.*, c.name AS category_name, c.color AS category_color
        FROM fin_budget b
        JOIN fin_category c ON b.category_id = c.id
        WHERE b.user_id=%s
    """
    params = [user_id]
    if month:
        sql += " AND b.month=%s"
        params.append(month)
    if year:
        sql += " AND b.year=%s"
        params.append(year)
    sql += " ORDER BY c.name"
    with connection.cursor() as cur:
        cur.execute(sql, params)
        return dictfetchall(cur)


def get_budget(budget_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fin_budget WHERE id=%s AND user_id=%s",
            [budget_id, user_id]
        )
        return dictfetchone(cur)


def create_budget(user_id, category_id, amount, month, year):
    now = _now()
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO fin_budget (user_id, category_id, amount, month, year, created_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            [user_id, category_id, amount, month, year, now]
        )
        return cur.lastrowid


def update_budget(budget_id, user_id, amount):
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE fin_budget SET amount=%s WHERE id=%s AND user_id=%s",
            [amount, budget_id, user_id]
        )


def delete_budget(budget_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM fin_budget WHERE id=%s AND user_id=%s",
            [budget_id, user_id]
        )


def get_budget_usage(user_id, month, year):
    """Return budgets with actual spending for the given month/year."""
    sql = """
        SELECT b.id, b.amount, b.month, b.year,
               c.name AS category_name, c.color AS category_color,
               COALESCE(SUM(CASE WHEN t.transaction_type='expense' THEN t.amount ELSE 0 END), 0) AS spent
        FROM fin_budget b
        JOIN fin_category c ON b.category_id = c.id
        LEFT JOIN fin_transaction t
            ON t.category_id = b.category_id
            AND t.user_id = b.user_id
            AND strftime('%%m', t.date) = printf('%%02d', b.month)
            AND strftime('%%Y', t.date) = CAST(b.year AS TEXT)
        WHERE b.user_id=%s AND b.month=%s AND b.year=%s
        GROUP BY b.id
        ORDER BY c.name
    """
    with connection.cursor() as cur:
        cur.execute(sql, [user_id, month, year])
        rows = dictfetchall(cur)

    for row in rows:
        row['percent'] = round((row['spent'] / row['amount']) * 100, 1) if row['amount'] else 0
    return rows
