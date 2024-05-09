from django.apps import AppConfig


class NotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notes'

    def ready(self):
        from notes.signals import delete_worktable_after_deleting_session  # noqa
        from notes.signals import set_quantity_of_all_words  # noqa
