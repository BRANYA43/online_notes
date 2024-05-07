import django_filters as filters
from django.utils.translation import gettext as _
from django.db import models as dj_models

from notes import models


class NoteFilters(filters.FilterSet):
    class Status(dj_models.IntegerChoices):
        NONE = 0, '---'
        ACTIVE = 1, _('active')
        ARCHIVED = 2, _('archived')

    class IncreasingAndDecreasing(dj_models.IntegerChoices):
        NONE = 0, '---'
        INCREASING = 1, _('by increasing')
        DECREASING = 2, _('by decreasing')

    words = filters.ChoiceFilter(method='filter_by_words', choices=IncreasingAndDecreasing.choices)
    unique_words = filters.ChoiceFilter(method='filter_by_unique_words', choices=IncreasingAndDecreasing.choices)
    status = filters.ChoiceFilter(method='filter_by_status', choices=Status.choices)
    created = filters.DateFromToRangeFilter()

    class Meta:
        model = models.Note
        fields = ['category', 'created']

    def _get_value_as_int(self, value):
        try:
            value = int(value)
        except ValueError:
            value = 0
        return value

    def _filter_by_increasing_or_decreasing(self, queryset, name, value, field):
        value = self._get_value_as_int(value)

        if value == self.IncreasingAndDecreasing.INCREASING:
            result = queryset.order_by(field)
        elif value == self.IncreasingAndDecreasing.DECREASING:
            result = queryset.order_by(f'-{field}')
        else:
            result = queryset

        return result

    def filter_by_words(self, queryset, name, value):
        return self._filter_by_increasing_or_decreasing(queryset, name, value, 'words')

    def filter_by_unique_words(self, queryset, name, value):
        return self._filter_by_increasing_or_decreasing(queryset, name, value, 'unique_words')

    def filter_by_date(self, queryset, name, value):
        return self._filter_by_increasing_or_decreasing(queryset, name, value, 'created')

    def filter_by_status(self, queryset, name, value):
        value = self._get_value_as_int(value)

        if value == self.Status.ACTIVE:
            result = queryset.filter(is_archived=False)
        elif value == self.Status.ARCHIVED:
            result = queryset.filter(is_archived=True)
        else:
            result = queryset

        return result
