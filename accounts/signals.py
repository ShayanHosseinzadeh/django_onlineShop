# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from notifications.services import notify

User = get_user_model()

@receiver(post_save, sender=UserProfile)
def on_profile_created(sender, instance: UserProfile, created, **kwargs):
    if not created:
        return

    user = instance.user
    admins = User.objects.filter(profile__role="admin", is_active=True)
    for admin in admins:
        notify(
            user=admin,
            verb="کاربر جدید ثبت‌نام کرد",
            level="success",
            actor=user,
            target=user,
            payload={
                "url": reverse("edit_user_profile", args=[instance.pk]),
                "description": user.get_username(),
            },
            dedup_key=f"user_signup:{admin.pk}:{user.pk}",
        )