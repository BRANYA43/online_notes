from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

User = get_user_model()


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
