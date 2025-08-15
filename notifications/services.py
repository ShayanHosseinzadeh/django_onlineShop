# notifications/services.py
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Notification


def _conf_batch_window_seconds() -> int:
    """
    Read the batching window size (seconds) from settings.
    """
    return getattr(settings, "NOTIFS", {}).get("BATCH_WINDOW_SECONDS", 120)


def serialize_notification(n: Notification) -> Dict[str, Any]:
    """
    Convert a Notification object into a dict for WebSocket/API.
    """
    return {
        "id": n.id,
        "verb": n.verb,
        "level": n.level,
        "payload": n.payload or {},
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
        "target": {
            "ct": n.target_ct.model if n.target_ct else None,
            "id": n.target_id,
        },
        "actor": {
            "ct": n.actor_ct.model if n.actor_ct else None,
            "id": n.actor_id,
        },
    }


def _push_ws(user_id: int, event: str, n: Notification) -> None:
    """
    Send a realtime message to the user WebSocket group.
    """
    channel_layer = get_channel_layer()
    group = f"user_{user_id}"
    async_to_sync(channel_layer.group_send)(
        group,
        {
            "type": "notification.message",
            "event": event,  # "created" | "updated"
            "data": serialize_notification(n),
        },
    )


def notify(
    user,
    verb: str,
    *,
    level: str = "info",
    actor: Optional[object] = None,
    target: Optional[object] = None,
    payload: Optional[Dict[str, Any]] = None,
    dedup_key: str = "",
    enable_batch: bool = True,
) -> Notification:
    """
    Create or update a notification for a user.

    Behaviors:
    - If dedup_key is provided:
        * Try to create the notification.
        * If the UniqueConstraint fails, fetch the latest one with the same dedup_key
          and send "updated" event without changing its payload.
    - If no dedup_key and enable_batch=True:
        * Within the batching time window (BATCH_WINDOW_SECONDS), if there is an unread
          notification with the same (user, verb, target), increment payload['count'],
          update payload['actors'] list, and send "updated".
        * Otherwise, create a new notification and send "created".
    - If batching is disabled, always create a new notification (count=1).

    Note:
    - Actor display name comes from str(actor). You can replace it with get_full_name()
      or username if needed.
    """
    now = timezone.now()
    batch_window = _conf_batch_window_seconds()
    payload = dict(payload or {})

    # Prepare actor/target content type and IDs
    actor_ct = ContentType.objects.get_for_model(actor) if actor else None
    actor_id = str(actor.pk) if actor else None
    target_ct = ContentType.objects.get_for_model(target) if target else None
    target_id = str(target.pk) if target else None

    # --- Deduplication path ---
    if dedup_key:
        try:
            with transaction.atomic():
                n = Notification.objects.create(
                    user=user,
                    verb=verb,
                    level=level,
                    actor_ct=actor_ct,
                    actor_id=actor_id,
                    target_ct=target_ct,
                    target_id=target_id,
                    payload=payload,
                    delivered_at=now,
                    dedup_key=dedup_key or "",
                )
            _push_ws(user.pk, "created", n)
            return n
        except IntegrityError:
            # Found an existing notification with the same dedup_key
            n = (
                Notification.objects.filter(user=user, dedup_key=dedup_key)
                .order_by("-created_at")
                .first()
            )
            if n is None:
                # Fallback in rare race conditions: create again
                n = Notification.objects.create(
                    user=user,
                    verb=verb,
                    level=level,
                    actor_ct=actor_ct,
                    actor_id=actor_id,
                    target_ct=target_ct,
                    target_id=target_id,
                    payload=payload,
                    delivered_at=now,
                    dedup_key=dedup_key or "",
                )
                _push_ws(user.pk, "created", n)
                return n
            _push_ws(user.pk, "updated", n)
            return n

    # --- Batching path ---
    if enable_batch and batch_window > 0:
        since = now - timedelta(seconds=batch_window)
        with transaction.atomic():
            qs = (
                Notification.objects.select_for_update(skip_locked=True)
                .filter(
                    user=user,
                    verb=verb,
                    target_ct=target_ct,
                    target_id=target_id,
                    read_at__isnull=True,
                    created_at__gte=since,
                )
                .order_by("-created_at")
            )
            n = qs.first()
            if n:
                # Increment counter
                count = int(n.payload.get("count", 1)) + 1
                n.payload["count"] = count

                # Update actor list
                if actor:
                    actors = n.payload.get("actors", [])
                    if not isinstance(actors, list):
                        actors = []
                    label = str(actor)
                    if label not in actors:
                        actors.insert(0, label)  # newest first
                    # Limit to last 3 actors
                    n.payload["actors"] = actors[:3]

                n.delivered_at = now
                n.save(update_fields=["payload", "delivered_at"])
                _push_ws(user.pk, "updated", n)
                return n
            else:
                # Create new notification
                payload.setdefault("count", 1)
                if actor:
                    payload["actors"] = [str(actor)]
                n = Notification.objects.create(
                    user=user,
                    verb=verb,
                    level=level,
                    actor_ct=actor_ct,
                    actor_id=actor_id,
                    target_ct=target_ct,
                    target_id=target_id,
                    payload=payload,
                    delivered_at=now,
                )
                _push_ws(user.pk, "created", n)
                return n

    # --- No batching ---
    payload.setdefault("count", 1)
    if actor:
        payload["actors"] = [str(actor)]
    n = Notification.objects.create(
        user=user,
        verb=verb,
        level=level,
        actor_ct=actor_ct,
        actor_id=actor_id,
        target_ct=target_ct,
        target_id=target_id,
        payload=payload,
        delivered_at=now,
    )
    _push_ws(user.pk, "created", n)
    return n