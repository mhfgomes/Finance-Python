from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from core.forms import BudgetForm
from core.services import budget_service, category_service


@login_required
def budget_list(request):
    user_id = request.user.id
    now = datetime.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))
    budgets = budget_service.get_budget_usage(user_id, month, year)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render(request, 'budgets/list.html', {
        'budgets': budgets,
        'month': month,
        'year': year,
        'month_name': datetime(year, month, 1).strftime('%B %Y'),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })


@login_required
def budget_create(request):
    user_id = request.user.id
    categories = category_service.get_categories_by_type(user_id, 'expense')

    if request.method == 'POST':
        form = BudgetForm(request.POST, categories=categories)
        if form.is_valid():
            d = form.cleaned_data
            try:
                budget_service.create_budget(
                    user_id, int(d['category_id']),
                    float(d['amount']), int(d['month']), int(d['year'])
                )
                messages.success(request, 'Budget created.')
                return redirect('budget_list')
            except Exception:
                messages.error(request, 'A budget for that category/month/year already exists.')
    else:
        form = BudgetForm(categories=categories)

    return render(request, 'budgets/form.html', {'form': form, 'title': 'Add Budget'})


@login_required
def budget_update(request, pk):
    user_id = request.user.id
    budget = budget_service.get_budget(pk, user_id)
    if not budget:
        messages.error(request, 'Budget not found.')
        return redirect('budget_list')

    categories = category_service.get_categories_by_type(user_id, 'expense')

    if request.method == 'POST':
        form = BudgetForm(request.POST, categories=categories)
        if form.is_valid():
            d = form.cleaned_data
            budget_service.update_budget(pk, user_id, float(d['amount']))
            messages.success(request, 'Budget updated.')
            return redirect('budget_list')
    else:
        form = BudgetForm(
            initial={
                'category_id': budget['category_id'],
                'amount': budget['amount'],
                'month': budget['month'],
                'year': budget['year'],
            },
            categories=categories,
        )

    return render(request, 'budgets/form.html', {'form': form, 'title': 'Edit Budget', 'budget': budget})


@login_required
def budget_delete(request, pk):
    user_id = request.user.id
    budget = budget_service.get_budget(pk, user_id)
    if not budget:
        messages.error(request, 'Budget not found.')
        return redirect('budget_list')

    if request.method == 'POST':
        budget_service.delete_budget(pk, user_id)
        messages.success(request, 'Budget deleted.')
        return redirect('budget_list')

    return render(request, 'budgets/confirm_delete.html', {'budget': budget})
