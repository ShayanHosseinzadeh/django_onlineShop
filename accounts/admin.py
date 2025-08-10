from django.contrib import admin
from .forms import CustomCreationForm,CustomChangeform
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeform
    model = CustomUser
    list_display = ['username','email']



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'city', 'created_at')  # فیلدهای قابل نمایش در لیست ادمین
    search_fields = ('user__username', 'phone_number', 'city')  # فیلدهایی که می‌توان بر اساس آن‌ها جستجو کرد
    list_filter = ('city', 'created_at')  # فیلدهای فیلتر در سمت راست ادمین
    readonly_fields = ('created_at', 'updated_at')  # فیلدهایی که فقط خواندنی باشند
    ordering = ('-created_at',)  # ترتیب نمایش در ادمین
