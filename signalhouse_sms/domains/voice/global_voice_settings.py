"""Global Voice Settings — account-wide voice defaults.

Account-level voice configuration (accepted regions, max spend per minute,
E911). SIP trunks and Programmable Voice Profiles override these defaults.
Wraps the Voice service's ``/voice/api/v1/global-voice-settings`` surface.
Accessed via ``sdk.voice.global_voice_settings``.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class GlobalVoiceSettings:
    """Account-wide voice defaults. Accessed via ``sdk.voice.global_voice_settings``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the current account's global voice settings.
        ``GET /voice/api/v1/global-voice-settings``.

        Returns ``{ success, data: { accountId, acceptedRegions,
        maxSpendPerMinute, e911Enabled, ... } | None }``. ``data`` is ``None``
        when the account has never configured them (defaults apply).

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.
        """
        return self._sdk._request(
            "/voice/api/v1/global-voice-settings", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def update(
        self,
        settings_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Upsert the account's global voice settings.
        ``PUT /voice/api/v1/global-voice-settings``.

        Partial — only the fields you provide are written; omitted fields are
        preserved. Returns ``{ success, data: { ...settings } }``.

        Args:
            settings_data: Fields to set (camelCase, as the backend expects):
                ``acceptedRegions`` (list[str]) — accepted regions as country
                calling codes; empty list = all allowed. ``maxSpendPerMinute``
                (number | None) — baseline max spend per minute in dollars;
                ``None`` = no limit. ``e911Enabled`` (bool) — whether numbers
                may dial 911.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.
        """
        self._sdk._require({"settingsData": settings_data})
        return self._sdk._request(
            "/voice/api/v1/global-voice-settings",
            method="PUT",
            body=settings_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
