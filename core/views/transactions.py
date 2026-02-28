import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from core.forms import TransactionForm, TransactionFilterForm
from core.services import transaction_service, account_service, category_service


def _save_receipt(user_id, file):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'receipts', str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    filename = file.name
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return os.path.join('receipts', str(user_id), filename)


@login_required
def transaction_list(request):
    user_id = request.user.id
    accounts = account_service.get_accounts(user_id)
    categories = category_service.get_categories(user_id)

    filter_form = TransactionFilterForm(request.GET or None, accounts=accounts, categories=categories)

    filters = {}
    if filter_form.is_valid():
        d = filter_form.cleaned_data
        if d.get('date_from'):
            filters['date_from'] = str(d['date_from'])
        if d.get('date_to'):
            filters['date_to'] = str(d['date_to'])
        if d.get('category_id'):
            filters['category_id'] = d['category_id']
        if d.get('account_id'):
            filters['account_id'] = d['account_id']
        if d.get('transaction_type'):
            filters['transaction_type'] = d['transaction_type']

    transactions = transaction_service.get_transactions(user_id, **filters)
    return render(request, 'transactions/list.html', {
        'transactions': transactions,
        'filter_form': filter_form,
    })


@login_required
def transaction_create(request):
    user_id = request.user.id
    accounts = account_service.get_accounts(user_id)
    categories = category_service.get_categories(user_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, accounts=accounts, categories=categories)
        if form.is_valid():
            d = form.cleaned_data
            receipt_path = None
            if d.get('receipt_image'):
                receipt_path = _save_receipt(user_id, d['receipt_image'])
            transaction_service.create_transaction(
                user_id=user_id,
                account_id=int(d['account_id']),
                category_id=int(d['category_id']) if d.get('category_id') else None,
                amount=float(d['amount']),
                transaction_type=d['transaction_type'],
                description=d.get('description', ''),
                date=str(d['date']),
                receipt_image=receipt_path,
            )
            messages.success(request, 'Transaction added.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(accounts=accounts, categories=categories)

    return render(request, 'transactions/form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def transaction_update(request, pk):
    user_id = request.user.id
    tx = transaction_service.get_transaction(pk, user_id)
    if not tx:
        messages.error(request, 'Transaction not found.')
        return redirect('transaction_list')

    accounts = account_service.get_accounts(user_id)
    categories = category_service.get_categories(user_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, accounts=accounts, categories=categories)
        if form.is_valid():
            d = form.cleaned_data
            receipt_path = None
            if d.get('receipt_image'):
                receipt_path = _save_receipt(user_id, d['receipt_image'])
            transaction_service.update_transaction(
                transaction_id=pk,
                user_id=user_id,
                account_id=int(d['account_id']),
                category_id=int(d['category_id']) if d.get('category_id') else None,
                amount=float(d['amount']),
                transaction_type=d['transaction_type'],
                description=d.get('description', ''),
                date=str(d['date']),
                receipt_image=receipt_path,
            )
            messages.success(request, 'Transaction updated.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(
            initial={
                'account_id': tx['account_id'],
                'category_id': tx['category_id'] or '',
                'amount': tx['amount'],
                'transaction_type': tx['transaction_type'],
                'description': tx['description'],
                'date': tx['date'],
            },
            accounts=accounts,
            categories=categories,
        )

    return render(request, 'transactions/form.html', {
        'form': form, 'title': 'Edit Transaction', 'transaction': tx
    })


@login_required
def transaction_delete(request, pk):
    user_id = request.user.id
    tx = transaction_service.get_transaction(pk, user_id)
    if not tx:
        messages.error(request, 'Transaction not found.')
        return redirect('transaction_list')

    if request.method == 'POST':
        transaction_service.delete_transaction(pk, user_id)
        messages.success(request, 'Transaction deleted.')
        return redirect('transaction_list')

    return render(request, 'transactions/confirm_delete.html', {'transaction': tx})


@login_required
def transaction_export(request):
    csv_data = transaction_service.export_csv(request.user.id)
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    return response
