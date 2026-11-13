"""Verify domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Verify:
    """Carrier phone-number checks under /verify: SIM Swap and Number Verify.

    Every check the carrier answers is billed to the group's wallet (402 on
    insufficient funds); a check the carrier cannot run for the number is a 422
    and is not charged.
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def check_sim_swap(
        self,
        phone_number: str,
        *,
        max_age: int | None = None,
        include_swap_date: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Check whether a number's SIM card changed recently, as reported by its carrier.

        Billed once when the check answers; 422 when the check is not
        available for the number (not charged). Roles: api, admin, developer.

        Args:
            phone_number: The number to check, in international format (e.g. "+12025550123").
            max_age: Lookback window in hours, 1-2400; the carrier's default when omitted.
            include_swap_date: Also return the latest SIM change date (no extra charge; default False).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is
            ``{checkId, phoneNumber, swapped, maxAge, latestSimChange?, cost}``.

        Raises:
            SignalHouseValidationError: If phone_number is missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        body: dict[str, Any] = {"phoneNumber": phone_number}
        if max_age is not None:
            body["maxAge"] = max_age
        if include_swap_date is not None:
            body["includeSwapDate"] = include_swap_date
        return self._sdk._request(
            "/verify/sim-swap",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def start_number_verification(
        self,
        phone_number: str,
        *,
        device_phone_number: str | None = None,
        redirect_url: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Start a Number Verify check.

        The end user's phone must open the returned ``authorizationUrl`` on
        mobile data (Wi-Fi off) within 10 minutes; read the result with
        ``get_number_verification``. Billed only when the check is answered
        (VERIFIED or NOT_VERIFIED). Roles: api, admin, developer.

        Args:
            phone_number: The number to verify, in international format (e.g. "+12025550123").
            device_phone_number: The phone's own number, sent to the carrier as a login hint.
            redirect_url: An https URL the end user's browser is sent to after the check, with ``?checkId=...``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is
            ``{checkId, phoneNumber, status: "PENDING", authorizationUrl, expiresAt}``.

        Raises:
            SignalHouseValidationError: If phone_number is missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        body: dict[str, Any] = {"phoneNumber": phone_number}
        if device_phone_number is not None:
            body["devicePhoneNumber"] = device_phone_number
        if redirect_url is not None:
            body["redirectUrl"] = redirect_url
        return self._sdk._request(
            "/verify/number",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_number_verification(
        self,
        check_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a Number Verify check's status and result.

        A PENDING check past its ``expiresAt`` reads as EXPIRED. Roles: api,
        admin, developer, billing, user.

        Args:
            check_id: The check ID (e.g. "NVC...").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is ``{checkId, phoneNumber, status,
            devicePhoneNumberVerified, failureReason, createdAt, expiresAt,
            completedAt, cost}``.

        Raises:
            SignalHouseValidationError: If check_id is missing.
        """
        self._sdk._require({"checkId": check_id})
        safe_check_id = quote(str(check_id), safe="")
        return self._sdk._request(
            f"/verify/number/{safe_check_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
