from __future__ import annotations

from typing import Optional

from django.http import HttpRequest

from usersystem.models import User
from usersystem.permissions import resolve_active_user


def resolve_business_user(request: HttpRequest) -> Optional[User]:
    return resolve_active_user(request)


def user_display_name(user: Optional[User], default: str = "System") -> str:
    if not user:
        return default
    for attr in ("name", "username"):
        value = getattr(user, attr, None)
        if value:
            return str(value)
    pk = getattr(user, "pk", None)
    return f"User {pk}" if pk is not None else default
