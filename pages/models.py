from django.db import models


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('support', 'پشتیبانی فنی'),
        ('sales', 'فروش و خرید'),
        ('complaint', 'شکایت'),
        ('suggestion', 'پیشنهاد'),
        ('other', 'سایر'),
    ]

    name = models.CharField(max_length=255, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="شماره تلفن")
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    privacy_accepted = models.BooleanField(verbose_name="موافقت با قوانین و مقررات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    def __str__(self):
        return f"{self.name} - {self.subject}"
