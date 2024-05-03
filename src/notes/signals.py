from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete
from django.dispatch import receiver

from notes import models


@receiver(post_delete, sender=Session)
def delete_worktable_after_deleting_session(sender, instance, *args, **kwargs):
    try:
        worktable = models.Worktable.objects.get(session_key=instance.session_key)
        worktable.delete()
    except models.Worktable.DoesNotExist:
        pass
