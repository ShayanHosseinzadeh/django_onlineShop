from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Order
from notifications.services import notify

User = get_user_model()

def _order_url(order):
    return reverse("panel_order_detail", args=[order.pk])

@receiver(post_save, sender=Order)
def on_order_created(sender, instance: Order, created, **kwargs):
    order = instance
    if created:
        # اعلان برای همه ادمین‌ها
        admin_qs = User.objects.filter(profile__role="admin", is_active=True)
        for admin in admin_qs:
            notify(
                user=admin,
                verb="ثبت سفارش جدید",
                level="success",
                actor=order.user,           # خریدار
                target=order,
                payload={
                    "url": _order_url(order),
                    "description": f"سفارش #{order.pk} ثبت شد",
                },
                # جلوگیری از دابل‌نوتیف برای همین سفارش/ادمین
                dedup_key=f"order_created:{admin.pk}:{order.pk}",
            )

        # اعلان برای خودِ خریدار (تأیید ثبت)
        notify(
            user=order.user,
            verb="سفارش شما ثبت شد",
            level="success",
            actor=order.user,
            target=order,
            payload={
                "url": reverse("panel_order_detail", args=[order.pk]),
                "description": f"سفارش #{order.pk} با موفقیت ثبت شد",
            },
            dedup_key=f"user_order_created:{order.user_id}:{order.pk}",
        )
    else:
        # تغییر وضعیت سفارش → اعلان برای خریدار
        if order.status in ["paid", "shipped", "delivered"]:
            notify(
                user=order.user,
                verb=f"وضعیت سفارش: {order.get_status_display()}",
                level="info",
                actor=None,
                target=order,
                payload={
                    "url": reverse("user_order_detail", args=[order.pk]),
                    "description": f"سفارش #{order.pk} {order.get_status_display()} شد",
                },
                # batching روشنه؛ برای تغییرات مکرر نزدیک به هم، در یک toast جمع می‌شود
                enable_batch=True,
            )