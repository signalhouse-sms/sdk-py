"""Push Devices — register a mobile device so incoming calls wake it.

Called by your app with the user's **voice token** (from ``sdk.voice.tokens.create``,
minted with a ``subgroupId``) as ``token=``, not your API key. The device is tied
to that token's identity. Wraps the Voice service's ``/voice/api/v1/push-devices``
surface. Accessed via ``sdk.voice.push_devices``.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class PushDevices:
    """Mobile push devices. Accessed via ``sdk.voice.push_devices``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def register(
        self,
        device_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Register this device for push. Call it after each token mint and
        whenever the OS gives the app a new push token. A push token already
        registered to another user moves to this one.
        ``POST /voice/api/v1/push-devices``.

        Returns ``{ success, data: { id, identity, provider, environment, appId,
        registeredAt } }``.

        Args:
            device_data: ``{"provider": "apns" | "fcm", "deviceToken",
                "environment"?: "production" | "sandbox" (apns only),
                "appId"?}``. ``appId`` is only needed when the account has
                several apps for the provider.
            token: The user's voice token.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. Registering or unregistering the same device again is harmless.
        """
        self._sdk._require({"deviceData": device_data})
        return self._sdk._request(
            "/voice/api/v1/push-devices",
            method="POST",
            body=device_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def unregister(
        self,
        device_token: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Unregister this device, e.g. when the user signs out.
        ``DELETE /voice/api/v1/push-devices/:deviceToken``. Returns
        ``{ success, data: { removed } }``.

        Args:
            device_token: The device's push token.
            token: The user's voice token.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. Registering or unregistering the same device again is harmless.
        """
        self._sdk._require({"deviceToken": device_token})
        safe_token = quote(str(device_token), safe="")
        return self._sdk._request(
            f"/voice/api/v1/push-devices/{safe_token}", method="DELETE", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def list_deliveries(
        self,
        *,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """The pushes recently sent to the voice token's user, newest first
        (kept 7 days), for debugging. ``GET /voice/api/v1/push-devices/deliveries``.

        Returns ``{ success, data: [{ id, callUuid, provider, kind, status,
        error, createdAt }] }``.

        Args:
            limit: How many to return, 1 to 100 (default 20).
            token: The user's voice token.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. Registering or unregistering the same device again is harmless.
        """
        query = f"?limit={quote(str(limit), safe='')}" if limit is not None else ""
        return self._sdk._request(
            f"/voice/api/v1/push-devices/deliveries{query}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )
