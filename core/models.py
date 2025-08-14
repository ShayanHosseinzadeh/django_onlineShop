# core/models.py
from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="فروشگاه آنلاین")
    logo = models.ImageField(upload_to="settings/", blank=True, null=True)
    favicon = models.ImageField(upload_to="settings/", blank=True, null=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=50, blank=True)
    support_address = models.CharField(max_length=500, blank=True)
    maintenance_enabled = models.BooleanField(default=False, verbose_name="حالت نگه‌داری")
    maintenance_message = models.TextField(
        blank=True,
        default="سایت موقتاً در حال بروزرسانی است. لطفاً دقایقی دیگر مراجعه کنید.",
        verbose_name="متن پیام حالت نگه‌داری",
    )

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
