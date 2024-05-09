import re
from collections import Counter
from typing import Type

from django.db.models import QuerySet, Model
from django.urls import reverse

from notes import models


def get_worktable(request):
    if request.user.is_authenticated:
        return request.user.worktable
    else:
        return models.Worktable.objects.get(session_key=request.session.session_key)


def serialize_filter_qs(qs: QuerySet) -> list[dict]:
    serialized_data = []
    for note in qs:
        note_data = serialize_model(
            note,
            ('id', 'title', 'is_archived'),
            ('update', 'retrieve', 'archive', 'delete'),
        )
        note_data['note']['created'] = note.created.strftime('%d.%m.%Y')
        if note.category:
            category_data = serialize_model(
                note.category,
                ('title', 'color'),
            )
            note_data.update(category_data)
        serialized_data.append(note_data)

    return serialized_data


def serialize_model(model_instance: Type[Model], fields, urls=()) -> dict:
    key_model = model_instance.__class__.__name__.lower()
    data = {
        key_model: {field: getattr(model_instance, field) for field in fields},
    }
    if urls:
        data['urls'] = {url: reverse(f'{url}_{key_model}', args=[model_instance.id]) for url in urls}

    return data


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
