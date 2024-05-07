from unittest import TestCase

from notes import services


class CountAllWordsInTextTest(TestCase):
    def setUp(self) -> None:
        self.service_fn = services.count_words_in_text

        self.text = (
            'Why do I want to become a developer? Because I like to create something and check it how it '
            "work in the moment. It's interest how games or apps creation look like from the inside."
        )

    def test_service_counts_word_quantity_in_text_correctly(self):
        result = self.service_fn(self.text)

        self.assertEqual(result, 36)

    def test_service_counts_unique_word_quantity_in_text_correctly(self):
        result = self.service_fn(self.text, unique=True)

        self.assertEqual(result, 23)
