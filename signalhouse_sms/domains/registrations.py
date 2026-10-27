"""Registrations domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class RegistrationsAdmin:
    """Admin-only registration review and recovery operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def review_registration(
        self,
        registration_id: str,
        action: str,
        reason: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Approve or reject a registration awaiting Signal House review.

        Args:
            registration_id: The ID of the registration to review.
            action: "APPROVE" (submits the registration to the provider) or "REJECT".
            reason: Why the registration was rejected; required for "REJECT".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If registration_id or action is missing.
        """
        self._sdk._require({"registrationId": registration_id, "action": action})
        safe_registration_id = quote(str(registration_id), safe="")
        body: dict[str, Any] = {"action": action}
        if reason is not None:
            body["reason"] = reason
        return self._sdk._request(
            f"/registration/{safe_registration_id}/review",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def correct_registration(
        self,
        registration_id: str,
        reason: str,
        data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Save corrections for a registration the provider sent back for more information.

        Args:
            registration_id: The ID of the registration to correct.
            reason: Why the correction is being made.
            data: The type's correctable fields (for VIRTUAL_LONG_CODE: useCases and, for SMS + Voice, voice).
                Owner, quantity, capabilities and the provider order are fixed.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If registration_id, reason or data is missing.
        """
        self._sdk._require({"registrationId": registration_id, "reason": reason, "data": data})
        safe_registration_id = quote(str(registration_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_registration_id}/corrections",
            method="POST",
            body={"reason": reason, "data": data},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def add_number(
        self,
        registration_id: str,
        phone_number: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Allocate a provider-owned number to a registration through the staff recovery path.

        Args:
            registration_id: The ID of the registration.
            phone_number: The allocated number in E.164 digits (10-15 digits, optional leading +).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If registration_id or phone_number is missing.
        """
        self._sdk._require({"registrationId": registration_id, "phoneNumber": phone_number})
        safe_registration_id = quote(str(registration_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_registration_id}/numbers",
            method="POST",
            body={"phoneNumber": phone_number},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reconcile(
        self,
        registration_id: str,
        external_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Link a RECONCILIATION_REQUIRED registration to the provider order that was actually placed.

        Never place a second order to retry an ambiguous submission; reconcile the existing one.

        Args:
            registration_id: The ID of the registration to reconcile.
            external_id: The provider's identifier for the existing order.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If registration_id or external_id is missing.
        """
        self._sdk._require({"registrationId": registration_id, "externalId": external_id})
        safe_registration_id = quote(str(registration_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_registration_id}/reconcile",
            method="POST",
            body={"externalId": external_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_application(
        self,
        registration_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the completed carrier application as {filename, contentType, base64}; decode base64 to save the file.

        Args:
            registration_id: The ID of the registration whose application to download.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If registration_id is missing.
        """
        self._sdk._require({"registrationId": registration_id})
        safe_registration_id = quote(str(registration_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_registration_id}/application?format=json",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Registrations:
    """Sender registrations: the catalog, quotes, submission and status tracking for every jurisdiction."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: RegistrationsAdmin | None = None
        if sdk.enable_admin:
            self.admin = RegistrationsAdmin(sdk)

    def get_catalog(
        self,
        region: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the registration types a jurisdiction offers and whether each can be acquired right now.

        Args:
            region: The jurisdiction (US, GB, CA, AU; any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {region, jurisdiction, sendingRequiresRegistration, registeredThrough,
            provisioning, types: [{type, kind, channel, bundles, quantity: {min, max},
            requiresParent, available}]}.

        Raises:
            SignalHouseValidationError: If region is missing.
        """
        self._sdk._require({"region": region})
        query_string = self._sdk._get_query_string({"region": region})
        return self._sdk._request(
            f"/registration/catalog{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_quotes(
        self,
        *,
        region: str,
        type: str,
        quantity: int = 1,
        group_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get setup and monthly prices, in integer microdollars, for each capability bundle of a type.

        Args:
            region: The jurisdiction (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB).
            type: The registration type, e.g. "VIRTUAL_LONG_CODE", or "ALPHANUMERIC_SENDER_ID" for GB (one ["SMS"]
                bundle, 6000000 setup and 6000000 monthly by default).
            quantity: How many senders the order covers (1-100); defaults to 1.
            group_id: Staff only — quote on behalf of another group.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is a list of quotes, one per capability bundle:
            {capabilities, quantity, currency, setupAmount, monthlyAmount, totalSetupAmount,
            totalMonthlyAmount, etaDays}. setupAmount/monthlyAmount are per sender; the totals cover the quantity.

        Raises:
            SignalHouseValidationError: If region or type is missing.
        """
        self._sdk._require({"region": region, "type": type})
        query_string = self._sdk._get_query_string({
            "region": region,
            "type": type,
            "quantity": quantity,
            "groupId": group_id,
        })
        return self._sdk._request(
            f"/registration/quotes{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_registrations(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        region: str | list[str] | None = None,
        type: str | None = None,
        kind: str | None = None,
        status: str | list[str] | None = None,
        parent_registration_id: str | None = None,
        phone_number: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of registrations with optional filters and pagination.

        Args:
            group_id: Filter by group ID (staff may omit it for the review queue).
            subgroup_id: Filter by subgroup ID.
            region: Filter by one jurisdiction or a list.
            type: Filter by registration type.
            kind: Filter by kind — identity, program or sender.
            status: Filter by one registration status or a list — DRAFT, SIGNAL_HOUSE_REVIEW, SIGNAL_HOUSE_APPROVED, SIGNAL_HOUSE_REJECTED,
                SUBMITTING, PENDING_PROVIDER, NEEDS_INFORMATION, PAYMENT_REQUIRED, APPROVED, REJECTED, CANCELLED,
                PENDING_DELETE, DELETED, EXPIRED or RECONCILIATION_REQUIRED.
            parent_registration_id: Filter by the parent registration (e.g. a program's identity).
            phone_number: Filter to registrations holding this phone number.
            sort_by: Sort field — createdAt (default), subgroupId, registrationId, region or status.
            sort_order: Sort direction — asc or desc (default).
            page: The page number for pagination.
            limit: The number of items per page (max 100).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with data, totalCount, page, and limit.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "region": region,
            "type": type,
            "kind": kind,
            "status": status,
            "parentRegistrationId": parent_registration_id,
            "phoneNumber": phone_number,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/registration{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_registration(
        self,
        registration_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single registration with its type data, review outcome and status history.

        Args:
            registration_id: The ID of the registration to retrieve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If registration_id is missing.
        """
        self._sdk._require({"registrationId": registration_id})
        safe_registration_id = quote(str(registration_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_registration_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def cancel_registration(
        self,
        registration_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a registration.

        Allowed from SIGNAL_HOUSE_REVIEW, SIGNAL_HOUSE_APPROVED, PENDING_PROVIDER, NEEDS_INFORMATION,
        PAYMENT_REQUIRED and APPROVED (409 otherwise). Numbers already allocated stay on the account and stop sending.

        Args:
            registration_id: The ID of the registration to cancel.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the cancelled registration.

        Raises:
            SignalHouseValidationError: If registration_id is missing.
        """
        self._sdk._require({"registrationId": registration_id})
        safe_registration_id = quote(str(registration_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_registration_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_registration(
        self,
        registration_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Submit a registration for Signal House review.

        Args:
            registration_data: {"region", "type", "subgroupId", "capabilities"
                (one of the type's bundles), "data"}. The type selects the data shape; for VIRTUAL_LONG_CODE it is
                {"quantity" (1-100), "useCases" (1-10), "voice"? (required exactly when capabilities include VOICE)}.
                For GB ALPHANUMERIC_SENDER_ID (capabilities ["SMS"]) it is {"requestedSenderId" (3-11 letters/digits/
                space/dot/dash, at least one letter), "trafficOrigin" (LOCAL | INTERNATIONAL), "trafficType"
                (TRANSACTIONAL | PROMOTIONAL), "companyName", "companyCountry", "companyWebsite", "industry",
                "messageExample", "senderRelationship"? (required when requestedSenderId differs from companyName)};
                quantity is always 1 and data.phoneNumbers carries the granted sender (e.g. ["ACME"]) once APPROVED.
                Pass idempotency_key to make a retry safe.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (HTTP 201) containing the new registration.

        Raises:
            SignalHouseValidationError: If registration_data is missing.
        """
        self._sdk._require({"registrationData": registration_data})
        return self._sdk._request(
            "/registration",
            method="POST",
            body=registration_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
