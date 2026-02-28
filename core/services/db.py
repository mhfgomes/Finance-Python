def dictfetchall(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    cols = [c[0] for c in cursor.description]
    row = cursor.fetchone()
    return dict(zip(cols, row)) if row else None
