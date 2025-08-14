# core/views.py
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
        # پشتیبانی از حذف لوگو/فاویکن اگر ورودی خالی شد
        obj = form.save(commit=False)
        if "logo" in form.changed_data and not form.cleaned_data.get("logo"):
            if obj.logo:
                obj.logo.delete(save=False)
            obj.logo = None
        if "favicon" in form.changed_data and not form.cleaned_data.get("favicon"):
            if obj.favicon:
                obj.favicon.delete(save=False)
            obj.favicon = None
        obj.save()
        messages.success(self.request, "تنظیمات با موفقیت ذخیره شد.")
        return super().form_valid(form)