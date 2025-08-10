from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')

    phone_regex = RegexValidator(
        regex=r'^(?:\+98|0)?9\d{9}$',
        message="شماره تلفن باید به صورت شماره موبایل ایرانی معتبر وارد شود. مثلاً 09123456789 یا +989123456789."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=14,
        blank=True,
        null=True,
        verbose_name='شماره تماس'
    )

    address = models.TextField(blank=True, null=True, verbose_name='آدرس')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='شهر')
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='کد پستی')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='تصویر پروفایل')
    birth_date = models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد پروفایل')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین به‌روزرسانی')

    def __str__(self):
        return f"{self.user.username} - پروفایل کاربر"