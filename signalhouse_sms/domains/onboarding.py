"""Onboarding domain for the SignalHouse SDK (staff-only)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class OnboardingAdmin:
    """Admin-only onboarding operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_onboardings(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get all onboarding records (one per group). Staff-only.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with a list of onboarding records.
        """
        return self._sdk._request(
            "/group/onboarding",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_onboarding(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single onboarding record by group ID. Staff-only.

        Args:
            group_id: The ID of the group whose onboarding record to retrieve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/group/onboarding/{safe_group_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def set_toll_free_provider(
        self,
        group_id: str,
        toll_free_provider: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Set where a group's new toll-free brands and numbers go (``infobip`` or ``twilio``). Staff-only.

        Existing brands, numbers and campaigns stay where they are.

        Args:
            group_id: The ID of the group whose toll-free provider to set.
            toll_free_provider: The toll-free provider for the group's new toll-free brands and numbers ("infobip" or "twilio").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the updated onboarding record.

        Raises:
            SignalHouseValidationError: If group_id or toll_free_provider is missing.
        """
        self._sdk._require({"groupId": group_id, "tollFreeProvider": toll_free_provider})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/group/onboarding/{safe_group_id}/toll-free-provider",
            method="PUT",
            body={"tollFreeProvider": toll_free_provider},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def add_pricing_comment(
        self,
        group_id: str,
        comment: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Add an internal comment/note to a group's admin Pricing editor. Staff-only.

        Args:
            group_id: The ID of the group to comment on.
            comment: The comment/note text.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the updated onboarding record.

        Raises:
            SignalHouseValidationError: If group_id or comment is missing.
        """
        self._sdk._require({"groupId": group_id, "comment": comment})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/group/onboarding/{safe_group_id}/pricing-comments",
            method="POST",
            body={"comment": comment},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def add_credit_comment(
        self,
        group_id: str,
        comment: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Add an internal comment/note to a group's admin Credits page. Staff-only.

        Args:
            group_id: The ID of the group to comment on.
            comment: The comment/note text.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the updated onboarding record.

        Raises:
            SignalHouseValidationError: If group_id or comment is missing.
        """
        self._sdk._require({"groupId": group_id, "comment": comment})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/group/onboarding/{safe_group_id}/credit-comments",
            method="POST",
            body={"comment": comment},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Onboarding:
    """Onboarding domain. Admin namespace only (staff-only data)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: OnboardingAdmin | None = None
        if sdk.enable_admin:
            self.admin = OnboardingAdmin(sdk)
