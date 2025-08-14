# core/views.py
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import SiteSettings
from .forms import SiteSettingsForm


class AdminSiteSettingsView(UpdateView):
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = "adminpanel/admin/admin_site_settings.html"
    context_object_name = "site_settings"
    success_url = reverse_lazy("admin_settings")

    def get_object(self, queryset=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1, defaults={"site_name": "شایان شاپ"})
        return obj

    def form_valid(self, form):
        inst = form.save(commit=False)

        # اگر فایل جدید آپلود نشده و فلگ حذف زده شده، فایل قبلی را پاک کن
        if self.request.POST.get("remove_logo") == "1" and not self.request.FILES.get("logo"):
            if inst.logo:
                inst.logo.delete(save=False)
            inst.logo = None

        if self.request.POST.get("remove_favicon") == "1" and not self.request.FILES.get("favicon"):
            if inst.favicon:
                inst.favicon.delete(save=False)
            inst.favicon = None

        inst.save()
        messages.success(self.request, "تنظیمات با موفقیت ذخیره شد.")
        return super().form_valid(form)