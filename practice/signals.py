"""Practice signals."""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction

from practice.models import PracticeTask, PracticeSession


@receiver(pre_save, sender=PracticeTask)
def sync_task_topic(sender, instance, **kwargs):
    """Sync denormalized topic field when task.topic changes."""
    if instance.pk:
        try:
            old = PracticeTask.objects.get(pk=instance.pk)
            if old.topic_id != instance.topic_id:
                # Topic changed - update all sessions for this task
                PracticeSession.objects.filter(task=instance).update(topic=instance.topic)
        except PracticeTask.DoesNotExist:
            pass


@receiver(post_save, sender=PracticeSession)
def update_task_topic(sender, instance, **kwargs):
    """Ensure session topic matches task topic."""
    if instance.task and instance.topic != instance.task.topic:
        PracticeSession.objects.filter(pk=instance.pk).update(topic=instance.task.topic)