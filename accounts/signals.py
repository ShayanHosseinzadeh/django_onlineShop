from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model

from notifications.services import notify

User = get_user_model()

@receiver(post_save, sender=User)
def on_user_created(sender, instance: User, created, **kwargs):
    if not created:
        return

    # اعلان برای ادمین‌ها
    admins = User.objects.filter(profile__role="admin", is_active=True)
    for admin in admins:
        notify(
            user=admin,
            verb="کاربر جدید ثبت‌نام کرد",
            level="success",
            actor=instance,
            target=instance,
            payload={
                "url": reverse("admin_user_detail", args=[instance.pk]),
                "description": instance.get_username(),
            },
            dedup_key=f"user_signup:{admin.pk}:{instance.pk}",
        )

    notify(
        user=instance,
        verb="به فروشگاه خوش آمدید!",
        level="success",
        actor=None,
        target=instance,
        payload={
            "url": reverse("home"),
            "description": "حساب شما با موفقیت ساخته شد.",
        },
        dedup_key=f"user_welcome:{instance.pk}",
    )