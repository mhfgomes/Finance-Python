from django.urls import path
from core.views.dashboard import dashboard
from core.views.accounts import account_list, account_create, account_update, account_delete
from core.views.transactions import (
    transaction_list, transaction_create, transaction_update,
    transaction_delete, transaction_export
)
from core.views.categories import category_list, category_create, category_update, category_delete
from core.views.budgets import budget_list, budget_create, budget_update, budget_delete
from core.views import panel

urlpatterns = [
    path('', dashboard, name='dashboard'),

    # Accounts
    path('accounts/', account_list, name='account_list'),
    path('accounts/add/', account_create, name='account_create'),
    path('accounts/<int:pk>/edit/', account_update, name='account_update'),
    path('accounts/<int:pk>/delete/', account_delete, name='account_delete'),

    # Transactions
    path('transactions/', transaction_list, name='transaction_list'),
    path('transactions/add/', transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', transaction_delete, name='transaction_delete'),
    path('transactions/export/', transaction_export, name='transaction_export'),

    # Categories
    path('categories/', category_list, name='category_list'),
    path('categories/add/', category_create, name='category_create'),
    path('categories/<int:pk>/edit/', category_update, name='category_update'),
    path('categories/<int:pk>/delete/', category_delete, name='category_delete'),

    # Budgets
    path('budgets/', budget_list, name='budget_list'),
    path('budgets/add/', budget_create, name='budget_create'),
    path('budgets/<int:pk>/edit/', budget_update, name='budget_update'),
    path('budgets/<int:pk>/delete/', budget_delete, name='budget_delete'),

    # Staff panel
    path('panel/', panel.staff_panel, name='staff_panel'),
]
