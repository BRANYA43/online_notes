from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from notes import models, services


@receiver(pre_save, sender=models.Note)
def set_quantity_of_all_words(sender, instance, *args, **kwargs):
    if instance.text:
        text = instance.text
        instance.words = services.count_words_in_text(text)
        instance.unique_words = services.count_words_in_text(text, unique=True)


@receiver(post_delete, sender=Session)
def delete_worktable_after_deleting_session(sender, instance, *args, **kwargs):
    try:
        worktable = models.Worktable.objects.get(session_key=instance.session_key)
        worktable.delete()
    except models.Worktable.DoesNotExist:
        pass
