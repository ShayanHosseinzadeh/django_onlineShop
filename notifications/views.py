from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Notification
from .services import serialize_notification, notify


@login_required
@require_http_methods(["GET"])
def list_notifications(request):
    qs = Notification.objects.filter(user=request.user)
    if request.GET.get("unread") in {"1", "true", "True"}:
        qs = qs.filter(read_at__isnull=True)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(int(request.GET.get("page", 1)))
    return JsonResponse({
        "results": [serialize_notification(n) for n in page_obj.object_list],
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "page": page_obj.number,
    })


@login_required
@require_http_methods(["POST"])
def mark_read(request, pk):
    try:
        n = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return HttpResponseForbidden()
    if not n.read_at:
        n.read_at = timezone.now()
        n.save(update_fields=["read_at"])
    return JsonResponse({"ok": True, "id": n.id})


@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read_at__isnull=True).update(read_at=timezone.now())
    return JsonResponse({"ok": True})




@login_required
def make_test_notification(request):
    n = notify(
        user=request.user,
        verb="Test notification arrived 🎉",
        level="info",
    )
    return JsonResponse({"ok": True, "id": n.id})