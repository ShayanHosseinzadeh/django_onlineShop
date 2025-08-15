# comments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Comment
from notifications.services import notify

User = get_user_model()

# --- Helper: تشخیص target از روی فیلدهای موجود ---
def get_comment_target(c: Comment):
    # هر اسمی که در مدل خودت داری اضافه/حذف کن:
    candidate_fields = ("product", "post", "article", "blog", "order")
    for name in candidate_fields:
        obj = getattr(c, name, None)
        if obj is not None:
            return obj
    return None

def get_comment_url(c: Comment):
    # بر اساس وجود فیلدها URL مناسب بساز
    if getattr(c, "product_id", None):
        return reverse("product_detail", args=[c.product_id]) + f"#comment-{c.pk}"
    if getattr(c, "post_id", None):
        return reverse("post_detail", args=[c.post_id]) + f"#comment-{c.pk}"
    # fallback
    return reverse("home")

def get_target_owner(target):
    # مالک هدف را از یکی از فیلدهای رایج پیدا کن
    for attr in ("owner", "seller", "user", "created_by", "author"):
        val = getattr(target, attr, None)
        if val is not None:
            return val
    return None

@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance: Comment, created, **kwargs):
    if not created:
        return

    c = instance
    target = get_comment_target(c)
    url = get_comment_url(c)

    # اعلان برای مالک هدف (اگر مشخص شد و کامنت‌گذار خودش مالک نبود)
    owner = get_target_owner(target) if target else None
    if owner and owner != getattr(c, "user", None):
        notify(
            user=owner,
            verb="کامنت گذاشت",
            level="info",
            actor=getattr(c, "user", None),
            target=target,
            payload={
                "url": url,
                "description": (c.text[:80] + "…") if len(getattr(c, "text", "")) > 80 else getattr(c, "text", ""),
            },
            enable_batch=True,
        )

    # (اختیاری) به ادمین‌ها هم خبر بده
    admins = User.objects.filter(is_superuser=True, is_active=True)
    for admin in admins:
        notify(
            user=admin,
            verb="کامنت جدید ثبت شد",
            level="info",
            actor=getattr(c, "user", None),
            target=target or c,
            payload={"url": url},
            dedup_key=f"comment_created:{admin.pk}:{c.pk}",
        )