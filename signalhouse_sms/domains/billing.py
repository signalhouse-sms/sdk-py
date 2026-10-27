"""Billing domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Billing:
    """Billing operations including wallets, payment methods, funds, invoices, and fees."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_transaction_history(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        brand_id: str | None = None,
        campaign_id: str | None = None,
        entry_type: str | None = None,
        transaction_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get transaction history with optional filters.

        Args:
            group_id: The ID of the group to filter by.
            subgroup_id: The ID of the subgroup to filter by.
            brand_id: The brand ID to filter by.
            campaign_id: The campaign ID to filter by.
            entry_type: The type of entry to filter by.
            transaction_type: The type of transaction to filter by.
            start_date: ISO-8601 date or timestamp; normalized to start-of-UTC-day (inclusive).
            end_date: ISO-8601 date or timestamp; normalized to end-of-UTC-day (inclusive). Hourly resolution is not supported.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "entryType": entry_type,
            "transactionType": transaction_type,
            "startDate": start_date,
            "endDate": end_date,
        })
        return self._sdk._request(
            f"/billing/wallet/transactionHistory{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_payment_history(
        self,
        *,
        group_id: str,
        start_date: str,
        end_date: str,
        page: int | None = None,
        limit: int | None = None,
        timezone: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get payment history (wallet recharge transactions) with server-side pagination.

        Args:
            group_id: The ID of the group to filter by.
            start_date: Start date in YYYY-MM-DD format (inclusive).
            end_date: End date in YYYY-MM-DD format (inclusive).
            page: Page number (positive integer, default 1).
            limit: Results per page (positive integer, max 10000, default 10).
            timezone: IANA timezone (default: "UTC").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with data array and pagination metadata.
        """
        params: dict[str, Any] = {
            "groupId": group_id,
            "startDate": start_date,
            "endDate": end_date,
        }
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if timezone is not None:
            params["timezone"] = timezone
        query_string = self._sdk._get_query_string(params)
        return self._sdk._request(
            f"/billing/wallet/paymentHistory{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_wallet(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the wallet information for a specific group.

        Args:
            group_id: The ID of the group to get the wallet information for.
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
            f"/billing/wallet/{safe_group_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_wallet(
        self,
        group_id: str,
        *,
        auto_recharge_enabled: bool | None = None,
        auto_recharge_threshold: int | None = None,
        auto_recharge_to_amount: int | None = None,
        primary_payment_method_id: str | None = None,
        secondary_payment_method_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update the wallet settings for a specific group.

        Args:
            group_id: The ID of the group to update the wallet settings for.
            auto_recharge_enabled: Whether auto-recharge is enabled for the wallet.
            auto_recharge_threshold: The threshold amount for auto-recharge to trigger.
            auto_recharge_to_amount: The amount to recharge to when auto-recharge is triggered.
            primary_payment_method_id: The ID of the primary payment method for auto-recharge.
            secondary_payment_method_id: The ID of the secondary payment method if primary fails.
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
        body: dict[str, Any] = {}
        if auto_recharge_enabled is not None:
            body["autoRechargeEnabled"] = auto_recharge_enabled
        if auto_recharge_threshold is not None:
            body["autoRechargeThreshold"] = auto_recharge_threshold
        if auto_recharge_to_amount is not None:
            body["autoRechargeToAmount"] = auto_recharge_to_amount
        if primary_payment_method_id is not None:
            body["primaryPaymentMethodId"] = primary_payment_method_id
        if secondary_payment_method_id is not None:
            body["secondaryPaymentMethodId"] = secondary_payment_method_id
        return self._sdk._request(
            f"/billing/wallet/{safe_group_id}",
            method="PUT",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_payment_methods(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the payment methods for a specific group.

        Args:
            group_id: The ID of the group to get the payment methods for.
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
            f"/billing/wallet/paymentMethods/{safe_group_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def add_funds(
        self,
        group_id: str,
        amount: int,
        *,
        payment_method_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Add funds to a group's wallet.

        Args:
            group_id: The ID of the group to add funds to.
            amount: The amount to add in microdollars (e.g., $10 would be 10000000).
            payment_method_id: The ID of the payment method to use for adding funds.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or amount is missing.
        """
        self._sdk._require({"groupId": group_id, "amount": amount})
        safe_group_id = quote(str(group_id), safe="")
        body: dict[str, Any] = {"amount": amount}
        if payment_method_id is not None:
            body["paymentMethodId"] = payment_method_id
        return self._sdk._request(
            f"/billing/wallet/addfunds/{safe_group_id}",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def add_payment_method(
        self,
        group_id: str,
        payment_method_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Add a payment method to a group's wallet.

        Args:
            group_id: The ID of the group to add the payment method to.
            payment_method_id: The ID of the payment method to add.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or payment_method_id is missing.
        """
        self._sdk._require({"groupId": group_id, "paymentMethodId": payment_method_id})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/billing/wallet/paymentMethod/{safe_group_id}",
            method="POST",
            body={"paymentMethodId": payment_method_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def remove_payment_method(
        self,
        group_id: str,
        payment_method_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove a payment method from a group's wallet.

        Args:
            group_id: The ID of the group to remove the payment method from.
            payment_method_id: The ID of the payment method to remove.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or payment_method_id is missing.
        """
        self._sdk._require({"groupId": group_id, "paymentMethodId": payment_method_id})
        safe_group_id = quote(str(group_id), safe="")
        safe_payment_method_id = quote(str(payment_method_id), safe="")
        return self._sdk._request(
            f"/billing/wallet/paymentMethod/{safe_group_id}/{safe_payment_method_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_invoice_details(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get invoice details with optional filters.

        Args:
            group_id: The ID of the group to filter by.
            subgroup_id: The ID of the subgroup to filter by.
            start_date: ISO-8601 date or timestamp; normalized to start-of-UTC-day (inclusive).
            end_date: ISO-8601 date or timestamp; normalized to end-of-UTC-day (inclusive). Hourly resolution is not supported.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "startDate": start_date,
            "endDate": end_date,
        })
        return self._sdk._request(
            f"/billing/invoiceDetails{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_fees(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the fee schedule for a specific group.

        When the group is on a custom volume-tiered plan, the response also includes volumePricing: tiers,
        the current period's dates, count and minimum, ramp, and current rate (rates in microdollars per segment).

        Args:
            group_id: The ID of the group to get fees for.
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
            f"/billing/fees/{safe_group_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
