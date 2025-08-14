from core.models import SiteSettings


def site_settings(request):
    return {"site_settings": SiteSettings.get_solo()}