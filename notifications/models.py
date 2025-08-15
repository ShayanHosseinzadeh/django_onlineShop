from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from config import settings


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO = "info", "Info"
        SUCCESS = "success", "Success"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    verb = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO)

    # --- اختیاری: جلوگیری از نوتیف تکراری
    dedup_key = models.CharField(max_length=128, blank=True, db_index=True)

    # actor/target (همان قبلی)
    actor_ct = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    actor_id = models.CharField(max_length=64, null=True, blank=True)
    actor = GenericForeignKey("actor_ct", "actor_id")

    target_ct = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    target_id = models.CharField(max_length=64, null=True, blank=True)
    target = GenericForeignKey("target_ct", "target_id")

    payload = models.JSONField(default=dict, blank=True)

    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "read_at"]),
        ]
        ordering = ["-created_at"]
        constraints = [
            # یکتا فقط وقتی که dedup_key خالی نیست
            models.UniqueConstraint(
                fields=["user", "dedup_key"],
                condition=~Q(dedup_key=""),
                name="uniq_user_dedup_nonempty",
            ),
        ]

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])

    @property
    def is_read(self):
        return self.read_at is not None