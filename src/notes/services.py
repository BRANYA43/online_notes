import re
from collections import Counter


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
