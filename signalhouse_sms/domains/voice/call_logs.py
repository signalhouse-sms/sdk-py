"""Call Logs — the account-scoped voice call history.

Wraps the Voice service's ``/voice/api/v1/call-logs`` surface. Distinct from
``sdk.voice.calls``, which is the Twilio-compatible programmatic call-control
surface; this is the richer log read surface with cost, recording, and
voice-config attribution used by the portal Call Logs view. Accessed via
``sdk.voice.call_logs``.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class CallLogs:
    """Account-scoped voice call history. Accessed via ``sdk.voice.call_logs``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        direction: str | None = None,
        status: str | None = None,
        call_source: str | None = None,
        subgroup_id: str | None = None,
        sip_trunk_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        q: str | None = None,
        sentiment: str | None = None,
        voicemail: bool | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List call logs for the current account, paginated and filterable.
        ``GET /voice/api/v1/call-logs``.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Page size (max 1000). Defaults to 20.
            direction: Filter by direction (``INBOUND``, ``OUTBOUND``,
                ``INTERNAL``).
            status: Filter by status (``QUEUED``, ``RINGING``, ``IN_PROGRESS``,
                ``COMPLETED``, ``FAILED``, ``BUSY``, ``NO_ANSWER``,
                ``CANCELED``).
            call_source: Filter by how the call was handled (``SIP_TRUNK``,
                ``PROGRAMMABLE_VOICE``, ``AI_VOICE``, ``WEBRTC``, ``VOICEMAIL``,
                ``CONFERENCE``, ``PSTN``). Serialized as ``callSource``.
            subgroup_id: Filter by owning subgroup. Serialized as ``subgroupId``.
            sip_trunk_id: Filter by SIP trunk id. Serialized as ``sipTrunkId``.
            from_: Filter by caller number (contains). Trailing underscore avoids
                the Python ``from`` keyword; serialized over the wire as ``from``.
            to: Filter by called number (contains).
            q: Free-text search over callId / from / to.
            sentiment: Filter by sentiment (``positive``, ``negative``,
                ``neutral``).
            voicemail: When true, return only voicemails.
            date_from: ISO-8601 lower bound on start time. Serialized as
                ``dateFrom``.
            date_to: ISO-8601 upper bound on start time. Serialized as ``dateTo``.
            sort: Sort field (default ``startTime``).
            order: Sort order (``asc`` or ``desc``, default ``desc``).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict wrapping
            ``{ success, data: [...call logs], meta: { total, page, limit, totalPages } }``.
        """
        query_string = self._sdk._get_query_string({
            "page": page,
            "limit": limit,
            "direction": direction,
            "status": status,
            "callSource": call_source,
            "subgroupId": subgroup_id,
            "sipTrunkId": sip_trunk_id,
            "from": from_,
            "to": to,
            "q": q,
            "sentiment": sentiment,
            "voicemail": voicemail,
            "dateFrom": date_from,
            "dateTo": date_to,
            "sort": sort,
            "order": order,
        })
        return self._sdk._request(
            f"/voice/api/v1/call-logs{query_string}",
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
        """Get a single call log by its UUID or callId.
        ``GET /voice/api/v1/call-logs/:id``. Returns ``{ success, data: {...} }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-logs/{safe_id}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def get_recording(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a short-TTL presigned playback URL for a call's recording.

        Account-scoped — only the owning account can presign. 404 if the call
        has no recording. ``GET /voice/api/v1/call-logs/:id/recording``. Returns
        ``{ success, data: { callId, url, expiresIn } }``.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-logs/{safe_id}/recording", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def mark_voicemail_read(
        self,
        id: str,
        read: bool = True,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Mark a call's voicemail as read or unread.

        Account-scoped — only the owning account can update. ``PATCH
        /voice/api/v1/call-logs/:id/voicemail-read`` with body ``{ read }``.
        Returns the standardized response dict.

        Args:
            id: The call log UUID or callId.
            read: Whether the voicemail is read. Defaults to ``True``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-logs/{safe_id}/voicemail-read",
            method="PATCH",
            body={"read": read},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
