import django_filters as filters
from django.utils.translation import gettext as _
from django.db import models as dj_models

from notes import models


class NoteFilter(filters.FilterSet):
    class Status(dj_models.IntegerChoices):
        ACTIVE = 1, _('active')
        ARCHIVED = 2, _('archived')

    words = filters.RangeFilter()
    unique_words = filters.RangeFilter()
    status = filters.ChoiceFilter(method='filter_by_status', choices=Status.choices)
    created = filters.DateFromToRangeFilter()

    class Meta:
        model = models.Note
        fields = ['category', 'created', 'words', 'unique_words']

    def _get_value_as_int(self, value):
        try:
            value = int(value)
        except ValueError:
            value = 0
        return value

    def filter_by_status(self, queryset, name, value):
        value = self._get_value_as_int(value)

        if value == self.Status.ACTIVE:
            result = queryset.filter(is_archived=False)
        elif value == self.Status.ARCHIVED:
            result = queryset.filter(is_archived=True)
        else:
            result = queryset

        return result
