from __future__ import annotations

from typing import Any, Mapping

from rest_framework import status
from rest_framework.response import Response


def _build_payload(
    status_code: int,
    message: str,
    data: Mapping[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": status_code, "message": message}
    if data is not None:
        payload["data"] = data
    return payload


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Mapping[str, Any] | list[Any] | None = None,
) -> Response:
    """
    Return an HTTP response that follows the Group 8 error payload format.
    """
    return Response(_build_payload(status_code, message, data), status=status_code)


def success_response(
    data: Mapping[str, Any] | list[Any] | None = None,
    message: str = "success",
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """
    Convenience helper for returning a success payload with an optional data block.
    """
    return Response(_build_payload(status_code, message, data), status=status_code)
