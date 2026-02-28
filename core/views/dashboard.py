from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from core.services.dashboard_service import (
    get_total_balance, get_monthly_income_expense,
    get_recent_transactions, get_budget_alerts
)


@login_required
def dashboard(request):
    now = datetime.now()
    user_id = request.user.id

    total_balance = get_total_balance(user_id)
    monthly = get_monthly_income_expense(user_id, now.month, now.year)
    recent = get_recent_transactions(user_id)
    alerts = get_budget_alerts(user_id)

    net = monthly['income'] - monthly['expense']

    return render(request, 'dashboard.html', {
        'total_balance': total_balance,
        'monthly_income': monthly['income'],
        'monthly_expense': monthly['expense'],
        'monthly_net': net,
        'recent_transactions': recent,
        'budget_alerts': alerts,
        'current_month': now.strftime('%B %Y'),
    })
