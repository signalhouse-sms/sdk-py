"""Auth domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Auth:
    """Authentication operations including login, password reset, and auth history."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def login(
        self,
        email: str,
        password: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Login with email and password.

        Args:
            email: The user's email address.
            password: The user's password.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        return self._sdk._request(
            "/auth",
            method="POST",
            body={"email": email, "password": password},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reset_password(
        self,
        user_id: str,
        new_password: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reset a user's password.

        Args:
            user_id: The id of the user.
            new_password: The new password to set for the user.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If user_id or new_password is missing.
        """
        self._sdk._require({"userId": user_id, "newPassword": new_password})
        safe_user_id = quote(str(user_id), safe="")
        return self._sdk._request(
            f"/auth/resetpassword/{safe_user_id}",
            method="PUT",
            body={"newPassword": new_password},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def forgot_password(
        self,
        email: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Request a password-reset link be emailed to the given address (public).

        Always resolves successfully regardless of whether an account exists for the
        email, so it cannot be used to enumerate registered emails.

        Args:
            email: The email address to send a reset link to.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"success": True}).

        Raises:
            SignalHouseValidationError: If email is missing.
        """
        self._sdk._require({"email": email})
        return self._sdk._request(
            "/auth/forgot-password",
            method="POST",
            body={"email": email},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reset_password_with_token(
        self,
        token_value: str,
        password: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reset a password using the single-use token from a reset email (public).

        Args:
            token_value: The single-use reset token from the email link.
            password: The new password to set (min 8 characters).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"success": True}).

        Raises:
            SignalHouseValidationError: If token_value or password is missing.
        """
        self._sdk._require({"token": token_value, "password": password})
        return self._sdk._request(
            "/auth/reset-password",
            method="POST",
            body={"token": token_value, "password": password},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_auth_history(
        self,
        *,
        group_id: str | None = None,
        user_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get token login history for a group or user.

        Args:
            group_id: Returns history for all users in the group (one of group_id/user_id required).
            user_id: Returns history for a specific user (one of group_id/user_id required).
            page: Page number (min 1, default 1).
            limit: Results per page (min 1, max 100, default 20).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If neither group_id nor user_id is provided.
        """
        self._sdk._require({"groupId or userId": group_id or user_id})
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "userId": user_id,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/auth/history{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def logout_all(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Log out all other users in the caller's active group.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing loggedOutCount.
        """
        return self._sdk._request(
            "/auth/logout-all",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_group_id(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the Group ID associated with the caller's JWT (their active group).

        Useful for discovering your own group_id, which is required on most other requests.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing {"groupId": ...}.
        """
        return self._sdk._request(
            "/auth/group-id",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def request_external_link_token(
        self,
        product: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Mint a single-use, short-lived external-link token for the authenticated caller.

        The token is handed to the GHL/Shopify backend so it can link the caller's existing
        V2 group to its tenant.

        Args:
            product: The external system to link to ("ghl" or "shopify").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"token": ...}).

        Raises:
            SignalHouseValidationError: If product is missing.
        """
        self._sdk._require({"product": product})
        return self._sdk._request(
            "/auth/external-link-token",
            method="POST",
            body={"product": product},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
