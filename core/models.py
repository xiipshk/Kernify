"""
Core models and mixins for the project.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract model that provides created_at and updated_at fields.
    """
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class OrderedModel(models.Model):
    """
    Abstract model that provides an order field for ordering.
    """
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        abstract = True
        ordering = ['order']


class PublishedModel(models.Model):
    """
    Abstract model that provides publication status.
    """
    class PublishStatus(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        HIDDEN = 'hidden', _('Hidden')
        ARCHIVED = 'archived', _('Archived')

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
    )
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)

    class Meta:
        abstract = True

    def publish(self):
        """Publish the object."""
        self.status = self.PublishStatus.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at'])

    def hide(self):
        """Hide the object."""
        self.status = self.PublishStatus.HIDDEN
        self.save(update_fields=['status'])

    def archive(self):
        """Archive the object."""
        self.status = self.PublishStatus.ARCHIVED
        self.save(update_fields=['status'])

    @property
    def is_published(self):
        return self.status == self.PublishStatus.PUBLISHED

    @property
    def is_visible_to_students(self):
        return self.status == self.PublishStatus.PUBLISHED


class SoftDeleteModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(_('deleted'), default=False)
    deleted_at = models.DateTimeField(_('deleted at'), null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        """Permanently delete the object."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class ActiveManager(models.Manager):
    """Manager that returns only non-deleted objects."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class PublishedManager(models.Manager):
    """Manager that returns only published objects."""

    def get_queryset(self):
        return super().get_queryset().filter(status=PublishedModel.PublishStatus.PUBLISHED)


class TimeStampedSoftDeleteModel(TimeStampedModel, SoftDeleteModel):
    """Combines TimeStampedModel and SoftDeleteModel."""

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class OrderedTimeStampedModel(TimeStampedModel, OrderedModel):
    """Combines TimeStampedModel and OrderedModel."""

    class Meta:
        abstract = True
        ordering = ['order', '-created_at']


class PublishedTimeStampedModel(TimeStampedModel, PublishedModel):
    """Combines TimeStampedModel and PublishedModel."""

    objects = PublishedManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']