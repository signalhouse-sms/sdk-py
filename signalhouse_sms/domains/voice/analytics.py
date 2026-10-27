"""Voice Analytics — aggregated call metrics for the portal Voice Analytics view.

Wraps the Voice service's ``GET /voice/stats/voice-analytics``. Returns per-direction
summary tiles (both directions) plus byDate / byNumber / byCarrier status
breakdowns for charts. Distinct from ``sdk.voice.call_logs``, which is the raw
call history read surface. Accessed via ``sdk.voice.analytics``.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class Analytics:
    """Aggregated voice analytics. Accessed via ``sdk.voice.analytics``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        group_by: str | None = None,
        direction: str | None = None,
        call_source: str | None = None,
        subgroup_id: str | None = None,
        number: str | None = None,
        carrier: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated voice analytics for the current account.
        ``GET /voice/stats/voice-analytics``.

        Summary tiles honor every filter except ``direction`` and always cover
        both directions; the breakdowns honor all filters.

        Args:
            date_from: ISO-8601 lower bound on call start time. Serialized as
                ``dateFrom``.
            date_to: ISO-8601 upper bound on call start time. Serialized as
                ``dateTo``.
            group_by: Bucket size for the byDate breakdown (``day``, ``week``,
                ``month``; default ``day``). Serialized as ``groupBy``.
            direction: Restrict the breakdowns to one direction (``INBOUND``,
                ``OUTBOUND``). Summary tiles always cover both.
            call_source: Comma-separated ``CallLog.callSource`` list
                (``SIP_TRUNK``, ``PROGRAMMABLE_VOICE``, ``AI_VOICE``, ``WEBRTC``,
                ``VOICEMAIL``, ``CONFERENCE``, ``PSTN``). Serialized as
                ``callSource``.
            subgroup_id: Filter by owning subgroup. Serialized as ``subgroupId``.
            number: Substring match against either leg (from OR to).
            carrier: Filter by carrier.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict wrapping ``{ success, range: { dateFrom,
            dateTo, days }, outbound: <Summary>, inbound: <Summary>, byDate:
            [<Bucket>], byNumber: [<Bucket>], byCarrier: [<Bucket>], byChannel: [<Bucket>] }``
        (byChannel = per-callSource breakdown).
        """
        query_string = self._sdk._get_query_string({
            "dateFrom": date_from,
            "dateTo": date_to,
            "groupBy": group_by,
            "direction": direction,
            "callSource": call_source,
            "subgroupId": subgroup_id,
            "number": number,
            "carrier": carrier,
        })
        return self._sdk._request(
            f"/voice/stats/voice-analytics{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
