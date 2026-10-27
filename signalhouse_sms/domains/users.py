"""Users domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class UsersAdmin:
    """Admin-only user operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_users(
        self,
        *,
        email: str | None = None,
        user_type: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of users with optional filters (admin).

        Args:
            email: Filter users by email (partial match).
            user_type: Filter users by type (user, service).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "email": email,
            "userType": user_type,
        })
        return self._sdk._request(
            f"/user{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_internal_user(
        self,
        data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new internal user (admin or service user).

        Args:
            data: The data for the new internal user, including groupId, name, and role.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If data is missing.
        """
        self._sdk._require({"data": data})
        return self._sdk._request(
            "/user/signalhouse",
            method="POST",
            body=data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Users:
    """User management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: UsersAdmin | None = None
        if sdk.enable_admin:
            self.admin = UsersAdmin(sdk)

    def get_users(
        self,
        *,
        id: str | None = None,
        group_id: str | None = None,
        user_type: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of users with optional filters.

        Args:
            id: Filter by user ID.
            group_id: Filter by group ID.
            user_type: Filter by user type (user, service).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "id": id,
            "groupId": group_id,
            "userType": user_type,
        })
        return self._sdk._request(
            f"/user{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_user(
        self,
        data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new user with the specified user data.

        Args:
            data: The data for the new user. Required fields include groupId, role,
                  password, and email.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If data is missing.
        """
        self._sdk._require({"data": data})
        return self._sdk._request(
            "/user",
            method="POST",
            body=data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_service_user(
        self,
        data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new service user for API keys and non-human users.

        Args:
            data: The data for the new service user. Required fields include groupId,
                  name, and role. Optional for customer API keys (role "api"):
                  allowedIps (list of IPv4/IPv6 addresses or CIDR ranges, max 100) and
                  allowedCountries (list of ISO 3166-1 alpha-2 codes such as "US", max 250).
                  The key is then only accepted from matching callers; when both are set,
                  both must match. allowedDestinationCountries (ISO 3166-1 alpha-2, max 250)
                  limits the countries the key can send messages to.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If data is missing.
        """
        self._sdk._require({"data": data})
        return self._sdk._request(
            "/user/serviceuser",
            method="POST",
            body=data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_user(
        self,
        id: str,
        data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing user's information.

        Args:
            id: The ID of the user to update.
            data: The data to update for the user. For a customer API key, allowedIps,
                  allowedCountries and allowedDestinationCountries replace its restrictions
                  ([] removes one). Changing
                  restrictions needs an interactive admin or developer session; an API key
                  cannot change its own.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id or data is missing.
        """
        self._sdk._require({"id": id, "data": data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/user/{safe_id}",
            method="PUT",
            body=data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_user(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a user by their ID (mark as inactive).

        Args:
            id: The ID of the user to delete.
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
            f"/user/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_notification_preferences(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get notification preferences for a user.

        Args:
            id: The ID of the user.
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
            f"/user/{safe_id}/notification-preferences",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_notification_preferences(
        self,
        id: str,
        notification_preferences: list[dict[str, Any]],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update notification preferences for a user.

        Args:
            id: The ID of the user.
            notification_preferences: Array of notification preference objects with
                                     keys: name (str), web (bool), email (bool).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id or notification_preferences is missing.
        """
        self._sdk._require({"id": id, "notificationPreferences": notification_preferences})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/user/{safe_id}/notification-preferences",
            method="PUT",
            body={"notificationPreferences": notification_preferences},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
