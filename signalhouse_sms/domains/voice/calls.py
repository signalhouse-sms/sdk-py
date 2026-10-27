"""Voice calls — REST API for placing outbound calls and inspecting call logs.

Wraps the Voice service's ``/voice/v1/calls`` surface. Accessed via ``sdk.voice.calls``.

Origination modes:

* **Single-leg** (no trunk/profile/identity): Twilio-style direct outbound —
  dial ``to`` from caller-ID ``from``. Customer's ``from`` must be an
  account-owned number.
* **SIP trunk** (``sip_trunk_id``): Route via a configured trunk; the trunk's
  auth/ACL governs caller-ID rules.
* **Two-leg-with-bridge** (``sip_profile_id`` OR ``to_identity``): Ring the
  SDK-registered endpoint first, then dial ``to`` and bridge. ``to_identity``
  resolves to the most recently-minted unexpired ephemeral identity for that
  name.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class Calls:
    """Voice call origination + call log queries. Accessed via ``sdk.voice.calls``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def create(
        self,
        call_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create an outbound call. ``POST /voice/v1/calls``.

        ``call_data`` keys: ``to`` (required, E.164 or SIP URI), ``from``
        (required, caller ID — must be account-owned when not using a trunk),
        optional ``sip_trunk_id``, ``sip_profile_id``, ``to_identity``,
        ``answer_url``, ``answer_method`` (``"GET"`` or ``"POST"``, default
        POST), ``status_callback``, ``status_callback_method``,
        ``recording_enabled``, ``transcription_enabled``, ``ivr_flow_id``,
        ``metadata``.

        ``sip_trunk_id``, ``sip_profile_id``, and ``to_identity`` are mutually
        exclusive routing modes. Returns
        ``{ call_id, status, direction, from, to, created_at }``.
        """
        self._sdk._require({"callData": call_data})
        return self._sdk._request(
            "/voice/v1/calls", method="POST", body=call_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        direction: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List call logs for the current account, paginated and filterable.
        ``GET /voice/v1/calls``.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Page size (1-100). Defaults to 20.
            status: Filter by call status (``QUEUED``, ``RINGING``,
                ``IN_PROGRESS``, ``COMPLETED``, ``FAILED``, ``BUSY``,
                ``NO_ANSWER``, ``CANCELED``).
            direction: Filter by call direction (``INBOUND`` or ``OUTBOUND``).
            from_: Filter by caller number. Trailing underscore avoids the
                Python ``from`` keyword; serialized over the wire as ``from``.
            to: Filter by destination number.
            date_from: ISO-8601 lower bound on ``start_time``.
            date_to: ISO-8601 upper bound on ``start_time``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict wrapping ``{ calls, total, page, limit }``.
        """
        query_string = self._sdk._get_query_string({
            "page": page,
            "limit": limit,
            "status": status,
            "direction": direction,
            "from": from_,
            "to": to,
            "date_from": date_from,
            "date_to": date_to,
        })
        return self._sdk._request(
            f"/voice/v1/calls{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single call log by ID. ``GET /voice/v1/calls/:id``.

        ``id`` is the call log UUID (the value returned as ``call_id`` from
        :py:meth:`create`).
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/v1/calls/{safe_id}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def hangup(
        self,
        id: str,
        *,
        reason: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Hang up an in-progress call. ``POST /voice/v1/calls/:id/hangup``.

        ``reason`` is one of ``"NORMAL"``, ``"BUSY"``, ``"NO_ANSWER"``,
        ``"REJECTED"`` and is recorded on the call log. Defaults to ``NORMAL``
        when omitted. Returns ``{ "success": bool, "message": str }``.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        body = {"reason": reason} if reason else {}
        return self._sdk._request(
            f"/voice/v1/calls/{safe_id}/hangup",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
