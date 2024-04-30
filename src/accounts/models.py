from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext as _

from accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
    )
    last_login = models.DateTimeField(
        verbose_name=_('last login'),
        auto_now=True,
    )
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True,
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created']

    def __str__(self):
        return str(self.email)
