"""Webhooks domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Webhooks:
    """Webhook management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_webhooks(
        self,
        *,
        id: str | None = None,
        group_id: str | None = None,
        endpoint_type: str | None = None,
        phone_number: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of webhooks with optional filters.

        Each returned endpoint carries `hasSigningSecret` (bool) instead of the signing secret
        itself — see `create_webhook`.

        Args:
            id: Filter by webhook ID.
            group_id: Filter by associated group ID.
            endpoint_type: Filter by endpoint type (Global, Number).
            phone_number: Filter by associated phone number.
            page: The page number for pagination.
            limit: The number of items per page.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "id": id,
            "groupId": group_id,
            "endpointType": endpoint_type,
            "phoneNumber": phone_number,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/webhook{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_webhook(
        self,
        webhook_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new webhook with the specified data.

        The response includes a `signingSecret` (plaintext HMAC-SHA256 secret) used to sign every
        delivery to this endpoint via the `X-SignalHouse-Signature` header. It is returned exactly
        once, here — store it now, it is never exposed again by any read.

        `authType` is one of `NONE` (default), `BASIC`, `API_KEY`, `OAUTH2` or `HMAC`. `HMAC` sends
        no credentials (the receiver authenticates by the signature alone) and must be sent without
        `credentials` or `apiHeaderPrefix`.

        `eventSettings` holds per-event options keyed by event name: `NUMBER_HEALTH_BELOW_THRESHOLD`
        and `CAMPAIGN_HEALTH_BELOW_THRESHOLD` each take `{"threshold": <number>}`, the 7-day health
        score (1.5–10, in 0.5 steps) below which the event fires. A subscribed health event without
        a threshold is stored with the default, 6.

        Args:
            webhook_data: The data for the new webhook, including endpoint URL and event types.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict, including the plaintext `signingSecret` (this one time only).

        Raises:
            SignalHouseValidationError: If webhook_data is missing.
        """
        self._sdk._require({"webhookData": webhook_data})
        return self._sdk._request(
            "/webhook",
            method="POST",
            body=webhook_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_webhook(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing webhook with the specified data.

        `update_data` may include `name`, `url`, `subscribedEvents`, and `authType`,
        `apiHeaderPrefix` and `credentials` (`{"key", "secret"?}`) to change the endpoint's own
        credentials in place; credentials are required when switching to an auth type that needs them.
        Switching to `NONE` or `HMAC` clears the stored credentials; `HMAC` is rejected for an endpoint
        with no signing secret (call `rotate_webhook_secret` first).
        `eventSettings` changes per-event options by event name (`NUMBER_HEALTH_BELOW_THRESHOLD`,
        `CAMPAIGN_HEALTH_BELOW_THRESHOLD`, each `{"threshold": <number>}`, 1.5–10 in 0.5 steps);
        events you omit keep their stored settings.
        Like every read of a webhook, the response carries `hasSigningSecret` and `hasCredentials`
        (bools), never a secret or credential.

        Args:
            id: The ID of the webhook to update.
            update_data: The data for the webhook to be updated.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id or update_data is missing.
        """
        self._sdk._require({"id": id, "updateData": update_data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/webhook/{safe_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def rotate_webhook_secret(
        self,
        id: str,
        grace_seconds: int | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Rotate a webhook's signing secret, or give a webhook created before signing its first one.

        The response includes the new plaintext `signingSecret`, returned this one time only. The
        replaced secret keeps working for `grace_seconds` (default 86400, max 604800, 0 = stop now);
        during that window each delivery's `X-SignalHouse-Signature-V1` header carries a signature for
        both, and `previousSecretExpiresAt` in the response says when the old one stops.

        Args:
            id: The ID of the webhook.
            grace_seconds: How long the replaced secret stays valid.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id is missing.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/webhook/{safe_id}/rotate-secret",
            method="POST",
            body={} if grace_seconds is None else {"graceSeconds": grace_seconds},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_webhook(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a webhook by its ID (mark as inactive).

        Args:
            id: The ID of the webhook to delete.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id is missing.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/webhook/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
