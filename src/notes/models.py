from colorfield.fields import ColorField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class Note(models.Model):
    worktable = models.ForeignKey(
        verbose_name=_('worktable'),
        to='Worktable',
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        verbose_name=_('category'), to='Category', on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=50,
    )
    text = models.TextField(
        verbose_name=_('text'),
        null=True,
        blank=True,
    )
    words = models.PositiveIntegerField(
        verbose_name=_('Quantity of words in text'),
        default=0,
    )
    unique_words = models.PositiveIntegerField(
        verbose_name=_('Quantity of unique words in text'),
        default=0,
    )
    is_archived = models.BooleanField(
        verbose_name=_('archived'),
        default=False,
    )
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        ordering = ['-created']

    def __str__(self):
        return self.title


class Category(models.Model):
    worktable = models.ForeignKey(
        verbose_name=_('worktable'),
        to='Worktable',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=50,
    )
    color = ColorField(
        verbose_name=_('color'),
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['title']

    def __str__(self):
        return self.title


class Worktable(models.Model):
    user = models.OneToOneField(
        verbose_name=_('user'),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session_key = models.CharField(
        verbose_name=_('session'),
        max_length=50,
        unique=True,
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
        if (self.user and self.session_key) or (not self.user and not self.session_key):
            raise ValidationError(self.error_messages['invalid_user_and_session'], 'invalid_user_and_session')

    def __str__(self):
        if self.user:
            return self.user.email
        elif self.session_key:
            return str(self.session_key)

    def get_all_categories(self):
        return self.category_set.all().order_by('title')

    def get_all_notes(self):
        return self.note_set.all()
