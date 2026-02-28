from django import forms
from datetime import date
from core.services.currency_service import CURRENCY_CHOICES


INPUT_CLASS = (
    'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm '
    'text-gray-900 placeholder:text-gray-400 shadow-sm '
    'transition-colors duration-200 '
    'focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20'
)
SELECT_CLASS = (
    'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm '
    'text-gray-900 shadow-sm cursor-pointer '
    'transition-colors duration-200 '
    'focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20'
)
TEXTAREA_CLASS = (
    'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm '
    'text-gray-900 placeholder:text-gray-400 shadow-sm resize-none '
    'transition-colors duration-200 '
    'focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20'
)
FILE_INPUT_CLASS = (
    'w-full text-sm text-gray-500 cursor-pointer '
    'file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 '
    'file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 file:cursor-pointer '
    'file:transition-colors file:duration-200 hover:file:bg-indigo-100'
)

ACCOUNT_TYPE_CHOICES = [
    ('bank', 'Bank Account'),
    ('cash', 'Cash'),
    ('credit_card', 'Credit Card'),
]

CATEGORY_TYPE_CHOICES = [
    ('income', 'Income'),
    ('expense', 'Expense'),
]

TRANSACTION_TYPE_CHOICES = [
    ('income', 'Income'),
    ('expense', 'Expense'),
]

MONTH_CHOICES = [(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)]


class AccountForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial='EUR',
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    balance = forms.DecimalField(
        max_digits=12, decimal_places=2, initial=0,
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3})
    )


class CategoryForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    category_type = forms.ChoiceField(
        choices=CATEGORY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    color = forms.CharField(
        max_length=7,
        initial='#6366f1',
        widget=forms.TextInput(attrs={'type': 'color', 'class': 'h-10 w-16 rounded-lg cursor-pointer border border-gray-200 shadow-sm p-0.5'})
    )


class TransactionForm(forms.Form):
    account_id = forms.ChoiceField(widget=forms.Select(attrs={'class': SELECT_CLASS}))
    category_id = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0.01,
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'})
    )
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS}),
        initial=date.today
    )
    receipt_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': FILE_INPUT_CLASS})
    )

    def __init__(self, *args, accounts=None, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        if accounts:
            self.fields['account_id'].choices = [(a['id'], a['name']) for a in accounts]
        else:
            self.fields['account_id'].choices = []
        if categories:
            self.fields['category_id'].choices = [('', '— None —')] + [
                (c['id'], f"{c['name']} ({c['category_type']})") for c in categories
            ]
        else:
            self.fields['category_id'].choices = [('', '— None —')]


class BudgetForm(forms.Form):
    category_id = forms.ChoiceField(widget=forms.Select(attrs={'class': SELECT_CLASS}))
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0.01,
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'})
    )
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    year = forms.IntegerField(
        min_value=2000, max_value=2100, initial=date.today().year,
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS})
    )

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        if categories:
            self.fields['category_id'].choices = [(c['id'], c['name']) for c in categories]
        else:
            self.fields['category_id'].choices = []


class TransactionFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS})
    )
    category_id = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    account_id = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('income', 'Income'), ('expense', 'Expense')],
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )

    def __init__(self, *args, accounts=None, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        acct_choices = [('', 'All Accounts')]
        if accounts:
            acct_choices += [(a['id'], a['name']) for a in accounts]
        self.fields['account_id'].choices = acct_choices

        cat_choices = [('', 'All Categories')]
        if categories:
            cat_choices += [(c['id'], c['name']) for c in categories]
        self.fields['category_id'].choices = cat_choices
