# core/views.py
from django.shortcuts import redirect
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from adminpanel.views import AdminRequiredMixin
from .models import SiteSettings
from .forms import SiteSettingsForm


class AdminSiteSettingsView(AdminRequiredMixin, UpdateView):
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = "adminpanel/admin/admin_site_settings.html"
    success_url = reverse_lazy("admin_settings")

    def get_object(self, queryset=None):
        return SiteSettings.get_solo()

    def form_valid(self, form):
        obj = form.save(commit=False)

        # اگر فایل جدیدی آپلود شده باشد، همان را نگه می‌داریم و هیچ حذفـی انجام نمی‌دهیم.
        has_new_logo = "logo" in self.request.FILES
        has_new_favicon = "favicon" in self.request.FILES

        # پشتیبانی از هر دو روش فلگ: استاندارد (-clear) و فلگ‌های قبلی (remove_*)
        want_clear_logo = (
            self.request.POST.get("logo-clear") == "on" or
            self.request.POST.get("remove_logo") == "1"
        )
        want_clear_favicon = (
            self.request.POST.get("favicon-clear") == "on" or
            self.request.POST.get("remove_favicon") == "1"
        )

        # حذف لوگو
        if want_clear_logo and not has_new_logo:
            if obj.logo:
                obj.logo.delete(save=False)
            obj.logo = None

        # حذف فاوآیکن
        if want_clear_favicon and not has_new_favicon:
            if obj.favicon:
                obj.favicon.delete(save=False)
            obj.favicon = None

        obj.save()
        # form.save_m2m() اگر M2M نداریم، لازم نیست

        messages.success(self.request, "تنظیمات با موفقیت ذخیره شد.")
        return redirect(self.success_url)