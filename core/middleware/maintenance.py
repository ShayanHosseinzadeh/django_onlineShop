from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


class MaintenanceModeMiddleware:
    """
    اگر maintenance_enabled روشن باشد:
      - کاربران staff/superuser عبور می‌کنند
      - مسیرهای پنل، لاگین، static/media عبور می‌کنند
      - سایر کاربران صفحه 503 می‌بینند
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            from core.models import SiteSettings  # import داخل متد برای جلوگیری از چرخه
            ss = SiteSettings.get_solo()
        except Exception:
            ss = None

        # عبور در صورت غیرفعال‌بودن یا نبودن تنظیمات
        if not ss or not ss.maintenance_enabled:
            return self.get_response(request)

        # اجازه به ادمین‌ها
        user = getattr(request, "user", None)
        if user and (user.is_staff or user.is_superuser):
            return self.get_response(request)

        # اجازه به مسیرهای خاص
        path = request.path or ""
        allowed_prefixes = [
            getattr(settings, "STATIC_URL", "/static/"),
            getattr(settings, "MEDIA_URL", "/media/"),
            "/admin/",  # django admin (اگر داشته باشی)
            "/accounts/",  # لاگین/ثبت‌نام
            "/panel/",  # پنل سفارشی شما
        ]
        if any(path.startswith(p) for p in allowed_prefixes):
            return self.get_response(request)

        # پاسخ 503
        ctx = {
            "message": ss.maintenance_message or "",
            "site_name": ss.site_name or "سایت",
            "logo": ss.logo.url if ss.logo else None,
        }
        resp = render(request, "maintenance.html", ctx, status=503)
        resp["Retry-After"] = "1800"  # 30 دقیقه
        return resp
