from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Set

from django.db import transaction

from usersystem.models import User

from .models import Notification


@dataclass
class NotificationPayload:
    title: str
    content: str
    body: str = ""
    related_type: str = ""
    related_id: str = ""


def _normalize_recipients(recipients: Iterable[Optional[User]]) -> list[User]:
    normalized: list[User] = []
    seen: Set[int] = set()
    for candidate in recipients:
        if candidate is None:
            continue
        if getattr(candidate, "status", User.STATUS_ACTIVE) != User.STATUS_ACTIVE:
            continue
        pk = getattr(candidate, "pk", None)
        if pk is None or pk in seen:
            continue
        seen.add(pk)
        normalized.append(candidate)
    return normalized


def send_notifications(
    recipients: Iterable[Optional[User]],
    *,
    title: str,
    content: str,
    body: str = "",
    related_type: str = "",
    related_id: Optional[str] = None,
) -> None:
    """
    Dispatch notifications to recipients. Uses transaction.on_commit to avoid
    notifying users when the surrounding operation fails.
    """
    users = _normalize_recipients(recipients)
    if not users:
        return

    payload = NotificationPayload(
        title=title.strip(),
        content=content.strip(),
        body=(body or "").strip(),
        related_type=(related_type or "").strip(),
        related_id=str(related_id or "").strip(),
    )

    def _create_entries():
        Notification.objects.bulk_create(
            [
                Notification(
                    recipient=user,
                    title=payload.title,
                    content=payload.content,
                    body=payload.body,
                    related_type=payload.related_type,
                    related_id=payload.related_id,
                )
                for user in users
            ]
        )

    transaction.on_commit(_create_entries)
