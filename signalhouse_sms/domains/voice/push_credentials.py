"""Push Credentials — the keys that wake your mobile app for incoming calls.

The Apple APNs auth key and Firebase service account the Voice service uses to
push your iOS or Android app before an inbound call rings it. One credential per
app; secrets are encrypted and never returned (responses show a ``fingerprint``).
Wraps the Voice service's ``/voice/api/v1/push-credentials`` surface.
Accessed via ``sdk.voice.push_credentials``.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class PushCredentials:
    """Mobile push credentials. Accessed via ``sdk.voice.push_credentials``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def list(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the account's push credentials (metadata only).
        ``GET /voice/api/v1/push-credentials``.

        Returns ``{ success, data: [{ id, provider, name, appId, keyId, teamId,
        bundleId, projectId, clientEmail, fingerprint, createdAt, updatedAt }] }``.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. A retried upload that already succeeded answers 409 because the credential exists, so treat that as success.
        """
        return self._sdk._request(
            "/voice/api/v1/push-credentials", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def get(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get one push credential (metadata only).
        ``GET /voice/api/v1/push-credentials/:id``.

        Args:
            id: The credential ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. A retried upload that already succeeded answers 409 because the credential exists, so treat that as success.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/push-credentials/{safe_id}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def create(
        self,
        credential_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Upload push credentials for one app. The key is checked on upload.
        ``POST /voice/api/v1/push-credentials``.

        Args:
            credential_data: Apple: ``{"provider": "apns", "name"?, "keyId",
                "teamId", "bundleId", "privateKey"}`` where ``privateKey`` is the
                contents of the .p8 file. Firebase: ``{"provider": "fcm",
                "name"?, "serviceAccount"}`` where ``serviceAccount`` is the key
                file as JSON text or a dict.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. A retried upload that already succeeded answers 409 because the credential exists, so treat that as success.
        """
        self._sdk._require({"credentialData": credential_data})
        return self._sdk._request(
            "/voice/api/v1/push-credentials",
            method="POST",
            body=credential_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update(
        self,
        id: str,
        credential_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Replace a credential's key or service account (and name). Same body as
        ``create``; the provider cannot change. Registered devices keep working.
        ``PUT /voice/api/v1/push-credentials/:id``.

        Args:
            id: The credential ID.
            credential_data: The replacement, shaped as for ``create``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. A retried upload that already succeeded answers 409 because the credential exists, so treat that as success.
        """
        self._sdk._require({"id": id, "credentialData": credential_data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/push-credentials/{safe_id}",
            method="PUT",
            body=credential_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a credential and every device registered for that app.
        ``DELETE /voice/api/v1/push-credentials/:id``. Returns ``{ success }``.

        Args:
            id: The credential ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header, but the Voice service ignores it: a retry is a new request. A retried upload that already succeeded answers 409 because the credential exists, so treat that as success.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/push-credentials/{safe_id}", method="DELETE", token=token, headers=headers, idempotency_key=idempotency_key,
        )
