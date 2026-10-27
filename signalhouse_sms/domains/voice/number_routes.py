"""Number Routes — one inbound route set directly on a single phone number.

A number's own route takes priority over its Programmable Voice Profile and
subgroup voice settings. Removing it makes the number fall back to its
Programmable Voice Profile, subgroup voice settings, or the default.

Routes are mounted under /voice/api/v1/numbers/:e164/route on the
Voice service.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class NumberRoutes:
    """Per-number inbound route management. Accessed via
    ``sdk.voice.number_routes``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get(
        self,
        e164: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a number's own route and the routing currently in effect for it.
        ``GET /voice/api/v1/numbers/:e164/route`` (``e164`` leading ``+`` optional).
        Roles: api, admin, developer, billing, user.
        Returns ``{ "e164": ..., "route": {...} | None, "effective": {...} }``."""
        self._sdk._require({"e164": e164})
        safe_e164 = quote(str(e164), safe="")
        return self._sdk._request(
            f"/voice/api/v1/numbers/{safe_e164}/route", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def set(
        self,
        e164: str,
        route_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Set (create or replace) a number's route. The whole route is replaced:
        fields the new ``routeAction`` doesn't use are cleared.
        ``PUT /voice/api/v1/numbers/:e164/route`` (``e164`` leading ``+`` optional).
        Roles: api, admin, developer.

        ``route_data`` keys (camelCase, as the API expects): ``routeAction``
        (required; one of ``FORWARD``, ``WEBRTC``, ``SIP_TRUNK``, ``SIP_PROFILE``,
        ``CALL_CONTROL``, ``AI``, ``VOICEMAIL``), ``forwardToE164`` (required for
        ``FORWARD``, or the ``WEBRTC`` no-answer destination when ``noAnswerAction``
        is ``FORWARD``), ``noAnswerAction`` (``WEBRTC`` only: ``VOICEMAIL``,
        ``FORWARD`` or ``KEEP_RINGING``; default ``VOICEMAIL``), ``noAnswerSeconds``
        (``WEBRTC`` only: 5-120, default 20), ``routeSipTrunkId`` (required for
        ``SIP_TRUNK``), ``routeSipProfileId`` (required for ``SIP_PROFILE``),
        ``webhookUrl`` (SHML program URL; required for ``CALL_CONTROL``),
        ``routeAgentProfileId`` (AI agent profile id, ``AGP…``; required for ``AI``),
        ``recordingEnabled`` (bool).
        Returns ``{ "e164": ..., "route": {...}, "effective": {...} }``."""
        self._sdk._require({"e164": e164, "routeData": route_data})
        safe_e164 = quote(str(e164), safe="")
        return self._sdk._request(
            f"/voice/api/v1/numbers/{safe_e164}/route", method="PUT", body=route_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def delete(
        self,
        e164: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove a number's own route. The number falls back to its Programmable
        Voice Profile, subgroup voice settings, or the default.
        ``DELETE /voice/api/v1/numbers/:e164/route`` (``e164`` leading ``+`` optional).
        Roles: api, admin, developer.
        Returns ``{ "e164": ..., "route": None, "effective": {...} }``."""
        self._sdk._require({"e164": e164})
        safe_e164 = quote(str(e164), safe="")
        return self._sdk._request(
            f"/voice/api/v1/numbers/{safe_e164}/route", method="DELETE", token=token, headers=headers, idempotency_key=idempotency_key,
        )
