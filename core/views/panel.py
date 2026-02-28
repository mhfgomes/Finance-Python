from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from core.services.db import dictfetchall


@staff_member_required
def staff_panel(request):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT u.id, u.username, u.email, u.date_joined, u.last_login,
                   COUNT(t.id) AS transaction_count,
                   COALESCE(SUM(a.balance), 0) AS total_balance
            FROM auth_user u
            LEFT JOIN fin_transaction t ON t.user_id = u.id
            LEFT JOIN fin_account a ON a.user_id = u.id
            GROUP BY u.id
            ORDER BY u.date_joined DESC
        """)
        users = dictfetchall(cur)

    return render(request, 'panel/staff_panel.html', {'users': users})
