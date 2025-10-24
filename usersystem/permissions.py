from __future__ import annotations

from typing import Iterable, Sequence

from rest_framework.permissions import BasePermission

from usersystem.models import User


_CACHE_ATTR = "_cached_active_user"


def _normalize_user(candidate) -> User | None:
    if isinstance(candidate, User):
        return candidate if candidate.status == User.STATUS_ACTIVE else None
    if getattr(candidate, "is_authenticated", False):
        if hasattr(candidate, "status") and candidate.status == User.STATUS_ACTIVE:
            return candidate
        username = getattr(candidate, "username", None)
        if username:
            try:
                return User.objects.get(username=username, status=User.STATUS_ACTIVE)
            except User.DoesNotExist:
                return None
    return None


def _resolve_from_authorization(header_value: str | None) -> User | None:
    if not header_value:
        return None
    parts = header_value.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    if not token:
        return None
    try:
        return User.objects.get(auth_token=token, status=User.STATUS_ACTIVE)
    except User.DoesNotExist:
        return None


def resolve_active_user(request) -> User | None:
    cached = getattr(request, _CACHE_ATTR, None)
    if cached is not None or hasattr(request, _CACHE_ATTR):
        return cached

    user = getattr(request, "user", None)
    resolved = _normalize_user(user)
    if resolved:
        setattr(request, _CACHE_ATTR, resolved)
        return resolved

    headers = getattr(request, "headers", {}) or {}
    auth_header = headers.get("Authorization") or getattr(
        request, "META", {}
    ).get("HTTP_AUTHORIZATION")
    resolved = _resolve_from_authorization(auth_header)
    if resolved:
        setattr(request, _CACHE_ATTR, resolved)
        return resolved

    setattr(request, _CACHE_ATTR, None)
    return None


def normalize_roles(value: Iterable[str] | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(sorted({item for item in value if item}))


class ActiveUserPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        return resolve_active_user(request) is not None


class RolePermission(BasePermission):
    def get_roles_from_view(self, view, request) -> Sequence[str]:
        if hasattr(view, 'get_required_roles'):
            return normalize_roles(view.get_required_roles(request))
        if hasattr(view, 'required_roles'):
            return normalize_roles(getattr(view, 'required_roles'))
        action_roles = getattr(view, 'role_permissions', None)
        action = getattr(view, 'action', None)
        if action_roles and action:
            if action in action_roles:
                return normalize_roles(action_roles[action])
            if 'default' in action_roles:
                return normalize_roles(action_roles['default'])
        return ()

    def has_permission(self, request, view) -> bool:
        user = resolve_active_user(request)
        if not user:
            return False
        roles = self.get_roles_from_view(view, request)
        if not roles:
            return True
        return user.role in roles
