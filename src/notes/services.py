import re
from collections import Counter

from django.db.models import QuerySet
from django.urls import reverse


def serialize_filter_qs(qs: QuerySet) -> list[dict]:
    data = zip(qs.values('id', 'title', 'is_archived', 'created'), qs.values('category__title', 'category__color'))
    serialized_data = []
    for note, category in data:
        note['created'] = note['created'].strftime('%d.%m.%Y')

        category['title'] = category.pop('category__title')
        category['color'] = category.pop('category__color')

        urls = {
            'update': reverse('update_note', args=[note['id']]),
            'retrieve': reverse('retrieve_note', args=[note['id']]),
            'archive': reverse('archive_note', args=[note['id']]),
            'delete': reverse('delete_note', args=[note['id']]),
        }

        serialized_data.append(
            {
                'urls': urls,
                'note': note,
                'category': category if category['title'] else None,
            }
        )

    return serialized_data


def count_words_in_text(text: str, unique=False) -> int:
    """
    Count all words in text. If unique=True count unique words in text.
    """
    if not isinstance(text, str):
        raise ValueError('Type of "text" must be str.')

    clean_text = re.sub(r'[^\s\w]+', ' ', text)
    words = clean_text.lower().split()

    if unique:
        return sum(quantity for quantity in Counter(words).values() if quantity == 1)

    return len(words)
