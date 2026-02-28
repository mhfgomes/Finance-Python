from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import AccountForm
from core.services import account_service


@login_required
def account_list(request):
    accounts = account_service.get_accounts(request.user.id)
    return render(request, 'accounts/list.html', {'accounts': accounts})


@login_required
def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            account_service.create_account(
                request.user.id, d['name'], d['account_type'],
                float(d['balance']), d['description'], d['currency']
            )
            messages.success(request, 'Account created.')
            return redirect('account_list')
    else:
        form = AccountForm()
    return render(request, 'accounts/form.html', {'form': form, 'title': 'Add Account'})


@login_required
def account_update(request, pk):
    account = account_service.get_account(pk, request.user.id)
    if not account:
        messages.error(request, 'Account not found.')
        return redirect('account_list')

    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            account_service.update_account(
                pk, request.user.id, d['name'], d['account_type'], d['description'], d['currency']
            )
            messages.success(request, 'Account updated.')
            return redirect('account_list')
    else:
        form = AccountForm(initial={
            'name': account['name'],
            'account_type': account['account_type'],
            'currency': account.get('currency', 'EUR'),
            'balance': account['balance'],
            'description': account['description'],
        })
    return render(request, 'accounts/form.html', {'form': form, 'title': 'Edit Account', 'account': account})


@login_required
def account_delete(request, pk):
    account = account_service.get_account(pk, request.user.id)
    if not account:
        messages.error(request, 'Account not found.')
        return redirect('account_list')

    if request.method == 'POST':
        try:
            account_service.delete_account(pk, request.user.id)
            messages.success(request, 'Account deleted.')
        except Exception:
            messages.error(request, 'Cannot delete account with existing transactions.')
        return redirect('account_list')

    return render(request, 'accounts/confirm_delete.html', {'account': account})
