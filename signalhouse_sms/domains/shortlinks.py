"""Shortlinks domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Shortlinks:
    """URL shortlink operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_shortlink_redirect(
        self,
        shortlink_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the redirect URL for a shortlink by its ID.

        Args:
            shortlink_id: The ID of the shortlink.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If shortlink_id is missing.
        """
        self._sdk._require({"shortlinkId": shortlink_id})
        safe_shortlink_id = quote(str(shortlink_id), safe="")
        return self._sdk._request(
            f"/shortlink/redirect/{safe_shortlink_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_opt_out(
        self,
        code: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the recipient opt-out details behind an alphanumeric-sender opt-out link.

        Args:
            code: The opt-out code from the sihou.io/o/{code} link.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is
            ``{code, senderName, maskedRecipient, optedOut}``.

        Raises:
            SignalHouseValidationError: If code is missing.
        """
        self._sdk._require({"code": code})
        safe_code = quote(str(code), safe="")
        return self._sdk._request(
            f"/shortlink/optout/{safe_code}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def confirm_opt_out(
        self,
        code: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Confirm the recipient opt-out behind an alphanumeric-sender opt-out link; idempotent.

        Args:
            code: The opt-out code from the sihou.io/o/{code} link.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is
            ``{code, senderName, maskedRecipient, optedOut: True}``.

        Raises:
            SignalHouseValidationError: If code is missing.
        """
        self._sdk._require({"code": code})
        safe_code = quote(str(code), safe="")
        return self._sdk._request(
            f"/shortlink/optout/{safe_code}",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_shortlink(
        self,
        *,
        shortlink_id: str | None = None,
        message_id: str | None = None,
        phone_number: str | None = None,
        campaign_id: str | None = None,
        brand_id: str | None = None,
        subgroup_id: str | None = None,
        group_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get details of a shortlink with optional filters.

        Args:
            shortlink_id: The ID of the shortlink.
            message_id: Filter by associated message ID.
            phone_number: Filter by associated phone number.
            campaign_id: Filter by associated campaign ID.
            brand_id: Filter by associated brand ID.
            subgroup_id: Filter by associated subgroup ID.
            group_id: Filter by associated group ID.
            page: The page number for pagination.
            limit: The number of items per page.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "shortlinkId": shortlink_id,
            "messageId": message_id,
            "phoneNumber": phone_number,
            "campaignId": campaign_id,
            "brandId": brand_id,
            "subgroupId": subgroup_id,
            "groupId": group_id,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/shortlink{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
