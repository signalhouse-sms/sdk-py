"""Notifications domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Notifications:
    """Notification management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_notifications(
        self,
        *,
        id: str | None = None,
        group_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        event_types: str | list[str] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get notifications by id or by group_id with optional filters.

        Args:
            id: Notification id (one of id/group_id required).
            group_id: Group id to fetch notifications for (one of id/group_id required).
            page: Page number (min 1, default 1).
            limit: Results per page (min 1, max 100, default 10).
            status: Filter by status: "READ" or "UNREAD".
            event_types: Event types to filter by (comma-separated string or list).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If neither id nor group_id is provided.
        """
        self._sdk._require({"id or groupId": id or group_id})
        query_string = self._sdk._get_query_string({
            "id": id,
            "groupId": group_id,
            "page": page,
            "limit": limit,
            "status": status,
            "eventTypes": event_types,
        })
        return self._sdk._request(
            f"/notification{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_notification_status(
        self,
        ids: str | list[str],
        status: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update the status of one or more notifications.

        Args:
            ids: Notification id or list of notification ids.
            status: New status: "READ" or "UNREAD".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If ids or status is missing.
        """
        self._sdk._require({"ids": ids, "status": status})
        return self._sdk._request(
            "/notification/status",
            method="PUT",
            body={"ids": ids, "status": status},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_notification(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a notification by id.

        Args:
            id: The notification id to delete.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id is missing.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/notification/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
