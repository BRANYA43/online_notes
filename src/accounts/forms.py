from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        required=True,
    )
    password = forms.CharField(
        label=_('Password'),
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    error_messages = {
        'invalid_login': _('Please enter a correct email and password. Note: both fields may be case-sensitive.'),
    }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.cache_user = None

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.cache_user = authenticate(self.request, email=email, password=password)
            if self.cache_user is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    'invalid_login',
                )

        return self.cleaned_data


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Password'),
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    confirming_password = forms.CharField(
        label=_('Password confirmation'),
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    error_messages = {
        'password_mismatch': _("The passwords didn't match."),
    }

    class Meta:
        model = User
        fields = ('email',)

    def clean_confirming_password(self):
        password = self.cleaned_data.get('password')
        confirming_password = self.cleaned_data.get('confirming_password')

        if password and confirming_password and password != confirming_password:
            raise ValidationError(self.error_messages['password_mismatch'], 'password_mismatch')
        return confirming_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
