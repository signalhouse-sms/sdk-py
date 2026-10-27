"""Subscriptions domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class SubscriptionsAdmin:
    """Admin-only subscription operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_templates(
        self,
        *,
        template_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get subscription templates with optional filtering by template ID.

        Args:
            template_id: The ID of a specific template to retrieve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({"templateId": template_id})
        return self._sdk._request(
            f"/subscription/template{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_template(
        self,
        template_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new subscription template.

        Args:
            template_data: The data for the new template, including templateName and monthlyFee.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If template_data is missing.
        """
        self._sdk._require({"templateData": template_data})
        return self._sdk._request(
            "/subscription/template",
            method="POST",
            body=template_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_template(
        self,
        template_id: str,
        template_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing subscription template.

        Args:
            template_id: The ID of the subscription template to update.
            template_data: The data for the template, including templateName and monthlyFee.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If template_id or template_data is missing.
        """
        self._sdk._require({"templateId": template_id, "templateData": template_data})
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/subscription/template/{safe_template_id}",
            method="PUT",
            body=template_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_template(
        self,
        template_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete an existing subscription template.

        Args:
            template_id: The ID of the subscription template to delete.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If template_id is missing.
        """
        self._sdk._require({"templateId": template_id})
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/subscription/template/{safe_template_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_custom_subscription(
        self,
        group_id: str,
        subscription_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a custom subscription for a group.

        Args:
            group_id: The ID of the group to create the custom subscription for.
            subscription_data: The data for the custom subscription.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or subscription_data is missing.
        """
        self._sdk._require({"groupId": group_id, "subscriptionData": subscription_data})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/subscription/user/custom/{safe_group_id}",
            method="POST",
            body=subscription_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_custom_subscription(
        self,
        group_id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update volume tiers, ramp, and monthly minimum on an active custom subscription.

        Args:
            group_id: The ID of the group whose custom subscription to update.
            update_data: Fields to change (name, description, monthlyFee, volumeTiers,
                monthlyMinimumSmsSegments, rampDays).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or update_data is missing.
        """
        self._sdk._require({"groupId": group_id, "updateData": update_data})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/subscription/user/custom/{safe_group_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Subscriptions:
    """Subscription management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: SubscriptionsAdmin | None = None
        if sdk.enable_admin:
            self.admin = SubscriptionsAdmin(sdk)

    def get_subscriptions(
        self,
        *,
        group_id: str | None = None,
        only_active: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of subscription history for a group.

        Args:
            group_id: The ID of the group to get subscription history for.
            only_active: Whether to only include active subscriptions.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "onlyActive": only_active,
        })
        return self._sdk._request(
            f"/subscription/user{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def subscribe(
        self,
        group_id: str,
        template_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Subscribe a group to a template.

        Args:
            group_id: The ID of the group to subscribe.
            template_id: The ID of the template to subscribe the group to.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or template_id is missing.
        """
        self._sdk._require({"groupId": group_id, "templateId": template_id})
        safe_group_id = quote(str(group_id), safe="")
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/subscription/user/subscribe/{safe_group_id}/{safe_template_id}",
            method="POST",
            body={},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def unsubscribe(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Unsubscribe a group from a template.

        Args:
            group_id: The ID of the group to unsubscribe.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/subscription/user/cancel/{safe_group_id}",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
