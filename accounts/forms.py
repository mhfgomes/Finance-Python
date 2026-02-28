from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

_INPUT = (
    'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm '
    'text-gray-900 placeholder:text-gray-400 shadow-sm '
    'transition-colors duration-200 '
    'focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20'
)


class StyledAuthForm(AuthenticationForm):
    """AuthenticationForm with Tailwind-styled widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': _INPUT}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
