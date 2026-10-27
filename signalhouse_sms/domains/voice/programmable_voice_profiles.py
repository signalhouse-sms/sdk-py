"""Programmable Voice Profiles — route a set of numbers through Signal House.

A Programmable Voice Profile groups a set of the account's numbers (across one
or more subgroups) under a single inbound call-handling decision routed through
Signal House's own voice servers — the same idea as a SIP trunk, but without a
customer SBC. A number can belong to at most one profile and is mutually
exclusive with SIP trunks.

Routes are mounted under /voice/api/v1/programmable-voice-profiles on the
Voice service.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class ProgrammableVoiceProfiles:
    """Programmable Voice Profile management. Accessed via
    ``sdk.voice.programmable_voice_profiles``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def list(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List all Programmable Voice Profiles for the current account.
        ``GET /voice/api/v1/programmable-voice-profiles``. Returns ``{ "profiles": [...] }``."""
        return self._sdk._request(
            "/voice/api/v1/programmable-voice-profiles", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def get(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single Programmable Voice Profile by ID.
        ``GET /voice/api/v1/programmable-voice-profiles/:id``. Returns ``{ "profile": {...} }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/programmable-voice-profiles/{safe_id}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def create(
        self,
        profile_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a Programmable Voice Profile. ``POST /voice/api/v1/programmable-voice-profiles``.

        ``profile_data`` keys (camelCase, as the API expects): ``name`` (required),
        ``subgroupIds`` (required, list of subgroup IDs, at least one), optional
        ``region``, ``routeAction`` (one of ``FORWARD``, ``WEBRTC``, ``SIP_TRUNK``,
        ``SIP_PROFILE``, ``CALL_CONTROL``; default ``FORWARD``) — deliver the call to
        a PSTN number (``FORWARD``), ring the profile's subgroup registered softphones
        (``WEBRTC``), send to a SIP trunk (``SIP_TRUNK``), ring a registered SIP
        endpoint (``SIP_PROFILE``), or hand the call to an inbound voice webhook /
        SHML program (``CALL_CONTROL``). Also: ``forwardToE164`` (required when
        ``routeAction`` is ``FORWARD``), ``routeSipTrunkId`` (required when
        ``routeAction`` is ``SIP_TRUNK``), ``routeSipProfileId`` (required when
        ``routeAction`` is ``SIP_PROFILE``), ``webhookUrl`` (inbound voice webhook /
        SHML program URL; required when ``routeAction`` is ``CALL_CONTROL``),
        ``forwardAfterSeconds``, ``recordingEnabled``, ``enabled``.
        Returns ``{ "profile": {...} }``.
        """
        self._sdk._require({"profileData": profile_data})
        return self._sdk._request(
            "/voice/api/v1/programmable-voice-profiles", method="POST", body=profile_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def update(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing Programmable Voice Profile (partial).
        ``PATCH /voice/api/v1/programmable-voice-profiles/:id``.

        ``update_data`` accepts any subset of the create keys (camelCase, as the
        API expects): ``name``, ``subgroupIds``, ``region``, ``routeAction`` (one
        of ``FORWARD``, ``WEBRTC``, ``SIP_TRUNK``, ``SIP_PROFILE``, ``CALL_CONTROL``),
        ``forwardToE164`` (required when ``routeAction`` is ``FORWARD``),
        ``routeSipTrunkId`` (required when ``routeAction`` is ``SIP_TRUNK``),
        ``routeSipProfileId`` (required when ``routeAction`` is ``SIP_PROFILE``),
        ``webhookUrl`` (inbound voice webhook / SHML program URL; required when
        ``routeAction`` is ``CALL_CONTROL``; pass ``None`` to clear),
        ``forwardAfterSeconds``, ``recordingEnabled``, ``enabled``.
        Returns ``{ "profile": {...} }``."""
        self._sdk._require({"id": id, "updateData": update_data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/programmable-voice-profiles/{safe_id}", method="PATCH", body=update_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def toggle_active(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Toggle a profile active/inactive.
        ``POST /voice/api/v1/programmable-voice-profiles/:id/toggle-active``. Returns ``{ "profile": {...} }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/programmable-voice-profiles/{safe_id}/toggle-active", method="POST", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def delete(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a Programmable Voice Profile. Its number assignments cascade away,
        so those numbers fall back to subgroup/global routing.
        ``DELETE /voice/api/v1/programmable-voice-profiles/:id``. Returns ``{ "message": "..." }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/programmable-voice-profiles/{safe_id}", method="DELETE", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def assign_number(
        self,
        id: str,
        e164: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Assign a phone number (by E.164) to this profile. Rejected if the number
        is already configured on a SIP trunk/endpoint or another profile — it must
        be de-configured there first (mutual exclusivity).
        ``POST /voice/api/v1/programmable-voice-profiles/:id/assign-number``. Returns ``{ "profile": {...} }``."""
        self._sdk._require({"id": id, "e164": e164})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/programmable-voice-profiles/{safe_id}/assign-number",
            method="POST",
            body={"e164": e164},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def unassign_number(
        self,
        id: str,
        e164: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Unassign a phone number (by E.164) from this profile.
        ``POST /voice/api/v1/programmable-voice-profiles/:id/unassign-number``. Returns ``{ "profile": {...} }``."""
        self._sdk._require({"id": id, "e164": e164})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/programmable-voice-profiles/{safe_id}/unassign-number",
            method="POST",
            body={"e164": e164},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
