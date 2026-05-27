import uuid

from django.db import models

from apps.common.managers import ActiveManager, DeletedManager


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    auto_id = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        blank=True,
        null=True,
    )

    creator = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    updater = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_deleted = models.BooleanField(
        default=False,
    )

    # Managers
    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeletedManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=["is_deleted"])

    def save(self, *args, **kwargs):
        if not self.auto_id:
            last_auto_id = (
                self.__class__.objects.aggregate(
                    models.Max("auto_id")
                )["auto_id__max"]
            )

            self.auto_id = 1 if last_auto_id is None else last_auto_id + 1

        super().save(*args, **kwargs)
