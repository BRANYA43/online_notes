from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class Worktable(models.Model):
    user = models.OneToOneField(
        verbose_name=_('user'),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session = models.OneToOneField(
        verbose_name=_('session'),
        to=Session,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    error_messages = {
        'invalid_user_and_session': _('Worktable must have only user or only session for creation.'),
    }

    class Meta:
        verbose_name = _('worktable')
        verbose_name_plural = _('worktables')
        ordering = ['user']

    def clean(self):
        if (self.user and self.session) or (not self.user and not self.session):
            raise ValidationError(self.error_messages['invalid_user_and_session'], 'invalid_user_and_session')

    def __str__(self):
        if self.user:
            return self.user.email
        elif self.session:
            return str(self.session.session_key)
