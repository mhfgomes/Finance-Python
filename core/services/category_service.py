from django.db import connection
from .db import dictfetchall, dictfetchone
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def get_categories(user_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fin_category WHERE user_id=%s ORDER BY name",
            [user_id]
        )
        return dictfetchall(cur)


def get_categories_by_type(user_id, category_type):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fin_category WHERE user_id=%s AND category_type=%s ORDER BY name",
            [user_id, category_type]
        )
        return dictfetchall(cur)


def get_category(category_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fin_category WHERE id=%s AND user_id=%s",
            [category_id, user_id]
        )
        return dictfetchone(cur)


def create_category(user_id, name, category_type, color):
    now = _now()
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO fin_category (user_id, name, category_type, color, created_at) VALUES (%s, %s, %s, %s, %s)",
            [user_id, name, category_type, color, now]
        )
        return cur.lastrowid


def update_category(category_id, user_id, name, category_type, color):
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE fin_category SET name=%s, category_type=%s, color=%s WHERE id=%s AND user_id=%s",
            [name, category_type, color, category_id, user_id]
        )


def delete_category(category_id, user_id):
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM fin_category WHERE id=%s AND user_id=%s",
            [category_id, user_id]
        )
