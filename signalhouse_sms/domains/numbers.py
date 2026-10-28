"""Numbers domain for the SignalHouse SDK."""

from __future__ import annotations

import json
from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class NumbersAdmin:
    """Admin-only number operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def change_porting_status(
        self,
        porting_id: str,
        status: str,
        description: str | None = None,
        on_hold_reason: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Change the status of a port-in request. Infobip exposes no porting-status API or
        webhook, so ON_HOLD and its reason are always staff-entered here.

        Args:
            porting_id: The ID of the port-in request.
            status: The new status to set (PENDING, IN_PROGRESS, ON_HOLD, REJECTED).
            description: Optional description for the status change.
            on_hold_reason: Required when status is ON_HOLD (DOCUMENTATION_MISMATCH,
                ACCOUNT_INFO_INCORRECT, CARRIER_REJECTED, PENDING_CUSTOMER_ACTION, OTHER).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If porting_id or status is missing.
        """
        self._sdk._require({"portingId": porting_id, "status": status})
        safe_porting_id = quote(str(porting_id), safe="")
        body: dict[str, Any] = {"status": status}
        if description is not None:
            body["description"] = description
        if on_hold_reason is not None:
            body["onHoldReason"] = on_hold_reason
        return self._sdk._request(
            f"/number/portin/{safe_porting_id}/status",
            method="PUT",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def approve_port_request(
        self,
        porting_id: str,
        *,
        sub_group_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Approve a port-in request.

        Args:
            porting_id: The ID of the port-in request to approve.
            sub_group_id: Subgroup to assign when the request has none yet. Ignored if the
                request already has a subgroup assigned -- an existing assignment is never overwritten.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If porting_id is missing.
        """
        self._sdk._require({"portingId": porting_id})
        safe_porting_id = quote(str(porting_id), safe="")
        body = {"subGroupId": sub_group_id} if sub_group_id is not None else None
        return self._sdk._request(
            f"/number/portin/{safe_porting_id}/approve",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_short_code_acquisition_requests(
        self, *, page: int | None = None, limit: int | None = None, status: str | None = None,
        search: str | None = None, token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List staff-only, campaign-bound Short Code acquisition requests."""
        query_string = self._sdk._get_query_string({"page": page, "limit": limit, "status": status, "search": search})
        return self._sdk._request(f"/number/short-code/requests{query_string}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key)


class Numbers:
    """Phone number management operations including purchase, assignment, transfer, and lookup."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: NumbersAdmin | None = None
        if sdk.enable_admin:
            self.admin = NumbersAdmin(sdk)

    def get_phone_numbers(
        self,
        *,
        phone_number: str | None = None,
        campaign_id: str | None = None,
        registration_id: str | None = None,
        brand_id: str | None = None,
        subgroup_id: str | None = None,
        group_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        current_toll_free_carrier: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of phone numbers with optional filters.

        Args:
            phone_number: Filter by phone number (partial match).
            campaign_id: Filter by campaign ID.
            registration_id: Filter to numbers provisioned under this registration.
            brand_id: Filter by brand ID.
            subgroup_id: Filter by subgroup ID.
            group_id: Filter by group ID.
            page: The page number for pagination (default: 1).
            limit: The number of items per page (default: 20).
            current_toll_free_carrier: With subgroup_id or group_id: when True, return only toll-free numbers that a new
                toll-free campaign in that group can use (those on the group's current toll-free carrier).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

            Every record carries a `sentiment` object -- trailing 7-day and 30-day inbound reply sentiment,
            refreshed periodically from analytics rather than computed per request: `{ sevenDay, thirtyDay,
            updatedAt }`, each window being `{ score, label, scoredCount, positive, neutral, negative }`. The
            object is always present and fully populated, so it can be read without a presence check.
            `score` is a volume-weighted average in -100..100 and is null when nothing was scored in the
            window, which is not the same as a score of 0 -- null means nobody replied, 0 means replies
            averaged neutral. `updatedAt` is null until the first rollup writes the record, and it tracks when
            the figures last CHANGED, not when the job last ran.

            Every record also carries a `health` object -- trailing 7-day and 30-day delivery/opt-out health from
            the same periodic refresh: `{ sevenDay, thirtyDay, updatedAt }`, each window being `{ score,
            deliveryRate, optOutRate, deliveryScore, optOutScore, messagesSent, messagesDelivered, messagesFailed,
            optOuts }`. `score` is 1.0..10.0 (the mean of the two bucket scores) and is null when nothing was sent
            in the window; the volumes say how much traffic sits behind it. A campaign's figure is scored from the
            campaign's own summed counters, never averaged from its numbers. For a live figure use GET /number/health
            or GET /campaign/health.
        """
        query_string = self._sdk._get_query_string({
            "phoneNumber": phone_number,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "brandId": brand_id,
            "subgroupId": subgroup_id,
            "groupId": group_id,
            "page": page,
            "limit": limit,
            # urlencode would send Python's "True"; the API expects "true"/"false".
            "currentTollFreeCarrier": None if current_toll_free_carrier is None else str(current_toll_free_carrier).lower(),
        })
        return self._sdk._request(
            f"/number{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_number_health(
        self,
        phone_number: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the health score, the same one the portal shows, (1–10) for an owned phone number.

        Returns 7-day and 30-day score breakdowns matching the portal Numbers table.

        Args:
            phone_number: Owned phone number to score (11 digits, no + prefix).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with ``phoneNumber``, ``groupId``,
            ``sevenDay``, and ``thirtyDay`` fields.

        Raises:
            SignalHouseValidationError: If phone_number is missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        query_string = self._sdk._get_query_string({"phoneNumber": phone_number})
        return self._sdk._request(
            f"/number/health{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_available_phone_numbers(
        self,
        *,
        sms_enabled: bool | None = None,
        mms_enabled: bool | None = None,
        voice_enabled: bool | None = None,
        country: str | None = None,
        state: str | None = None,
        city: str | None = None,
        npa: str | None = None,
        nxx: str | None = None,
        phone_number: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of available phone numbers for purchase with optional filters.

        Args:
            sms_enabled: Filter for SMS enabled numbers.
            mms_enabled: Filter for MMS enabled numbers.
            voice_enabled: Filter for voice enabled numbers.
            country: Filter by country code (e.g., "US").
            state: Filter by state code (e.g., "CA").
            city: City prefix; requires country US and state.
            npa: Filter by NPA (area code).
            nxx: Filter by NXX (central office code).
            phone_number: Filter by phone number.
            limit: The number of items per page.
            page: The page number for pagination.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "smsEnabled": sms_enabled,
            "mmsEnabled": mms_enabled,
            "voiceEnabled": voice_enabled,
            "country": country,
            "state": state,
            "city": city,
            "npa": npa,
            "nxx": nxx,
            "phoneNumber": phone_number,
            "limit": limit,
            "page": page,
        })
        return self._sdk._request(
            f"/number/available{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def purchase_phone_number(
        self,
        phone_numbers: list[str],
        subgroup_id: str,
        *,
        country: str = "US",
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Purchase phone numbers and assign them to a subgroup.

        Each requested number is queued and processed independently. Per-number success or
        failure is delivered via ``NUMBER_PURCHASE_SUCCESSFUL`` / ``NUMBER_PURCHASE_FAILED``
        webhooks — not in this response.

        Args:
            phone_numbers: The list of phone numbers to purchase.
            subgroup_id: The ID of the subgroup to assign the purchased numbers to.
            country: ISO-2 purchase country; US (default).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with a ``message`` field confirming the request was queued.

        Raises:
            SignalHouseValidationError: If phone_numbers or subgroup_id is missing.
        """
        self._sdk._require({"phoneNumbers": phone_numbers, "subgroupId": subgroup_id})
        return self._sdk._request(
            "/number",
            method="POST",
            body={"phoneNumbers": phone_numbers, "subgroupId": subgroup_id, "country": country},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def purchase_toll_free_numbers(
        self,
        quantity: int,
        subgroup_id: str,
        *,
        country: str = "US",
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Purchase one or more Toll-Free numbers via the asynchronous resource-request flow.

        Toll-Free numbers are ordered by quantity (not picked individually) and provisioned
        asynchronously; per-number completion is delivered via webhook/polling, not in this
        response. Poll the returned ``orderId`` with ``get_toll_free_order_status``.

        Args:
            quantity: The number of Toll-Free numbers to purchase (1-10).
            subgroup_id: The subgroup the purchased numbers are assigned to.
            country: ISO-2 purchase country; US (default). Sending requires an
                approved brand and campaign.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict resolving to ``{message, orderId}`` once the request is queued.

        Raises:
            SignalHouseValidationError: If quantity or subgroup_id is missing.
        """
        self._sdk._require({"quantity": quantity, "subgroupId": subgroup_id})
        return self._sdk._request(
            "/number/toll-free",
            method="POST",
            body={"quantity": quantity, "subgroupId": subgroup_id, "country": country},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def request_short_code_acquisition(
        self,
        subgroup_id: str,
        brand_id: str,
        campaign_id: str,
        request_type: str,
        *,
        lease_term_months: int | None = None,
        requested_vanity_code: str | None = None,
        actual_code: str | None = None,
        order_id: str | None = None,
        lease_end_date: str | None = None,
        lease_receipt_file: BinaryIO | tuple | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Request a campaign-bound Short Code acquisition or register a customer-owned Registry lease.

        RANDOM and VANITY requests are fulfilled by Signal House staff. EXTERNAL_LEASE creates a pending
        Short Code number immediately; it becomes READY only when its campaign becomes ACTIVE. A YYYY-MM-DD
        ``lease_end_date`` expires at 23:59:59 UTC.
        An EXTERNAL_LEASE request requires ``lease_receipt_file``, a PNG, JPEG, or PDF file-like object or
        ``(filename, file_object, content_type)`` tuple.
        """
        self._sdk._require({"subgroupId": subgroup_id, "brandId": brand_id, "campaignId": campaign_id, "requestType": request_type})
        acquisition_data = {
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "requestType": request_type,
            "leaseTermMonths": lease_term_months,
            "requestedVanityCode": requested_vanity_code,
            "actualCode": actual_code,
            "orderId": order_id,
            "leaseEndDate": lease_end_date,
        }
        files_list: list[tuple[str, Any]] = []
        if lease_receipt_file is not None:
            files_list.append(("leaseReceipt", lease_receipt_file))
        return self._sdk._multipart_request(
            "/number/short-code",
            method="POST",
            form_data={"acquisitionData": json.dumps(acquisition_data)},
            files=files_list,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_toll_free_order_status(
        self,
        order_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Read the outcome of a Toll-Free number purchase by its order ID.

        Reports per-number ready/provisioning/failed counts (plus failure reasons) and the
        provisioned numbers; ``numbers`` fills in as the order completes, so poll until the order
        reaches a terminal state.

        Args:
            order_id: The order id returned by ``purchase_toll_free_numbers``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict resolving to
            ``{orderId, counts: {ready, provisioning, failed}, failures: [{reason}], numbers: []}``.

        Raises:
            SignalHouseValidationError: If order_id is missing.
        """
        self._sdk._require({"orderId": order_id})
        safe_order_id = quote(str(order_id), safe="")
        return self._sdk._request(
            f"/number/toll-free/order/{safe_order_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_phone_number(
        self,
        phone_number: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing phone number's details (e.g., setting a friendly name).

        Args:
            phone_number: The phone number to update.
            update_data: The data to update for the phone number (e.g., friendlyName).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If phone_number or update_data is missing.
        """
        self._sdk._require({"phoneNumber": phone_number, "updateData": update_data})
        safe_phone_number = quote(str(phone_number), safe="")
        return self._sdk._request(
            f"/number/{safe_phone_number}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_caller_name(
        self,
        phone_number: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a phone number's outbound caller name (CNAM) - the name US carriers show for calls from it.

        Roles: api, admin, developer, billing, user.

        Args:
            phone_number: The phone number (E.164, leading + optional).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict resolving to
            ``{phoneNumber, cnam, autoApply, eligible, ineligibleReason}``.

        Raises:
            SignalHouseValidationError: If phone_number is missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        safe_phone_number = quote(str(phone_number), safe="")
        return self._sdk._request(
            f"/number/{safe_phone_number}/cnam",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def set_caller_name(
        self,
        phone_number: str,
        name: str,
        *,
        brand_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Set a phone number's outbound caller name (CNAM).

        The name may only remove characters from the registered name of the number's brand (its
        campaign's brand, else ``brand_id``, else the subgroup's default caller-ID brand), and must
        be 1-15 letters, digits, spaces, ``-`` or ``_``.

        Roles: api, admin, developer.

        Args:
            phone_number: The phone number (E.164, leading + optional).
            name: The caller name to show.
            brand_id: The verified brand the name comes from; only for numbers with no campaign.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict resolving to
            ``{phoneNumber, cnam, autoApply, eligible, ineligibleReason}``.

        Raises:
            SignalHouseValidationError: If phone_number or name is missing.
        """
        self._sdk._require({"phoneNumber": phone_number, "name": name})
        safe_phone_number = quote(str(phone_number), safe="")
        body: dict[str, Any] = {"name": name}
        if brand_id:
            body["brandId"] = brand_id
        return self._sdk._request(
            f"/number/{safe_phone_number}/cnam",
            method="PUT",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_caller_name(
        self,
        phone_number: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove a phone number's own caller name (CNAM).

        If its subgroup has caller name auto-apply on, the number goes back to the automatic name.

        Roles: api, admin, developer.

        Args:
            phone_number: The phone number (E.164, leading + optional).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict resolving to
            ``{phoneNumber, cnam, autoApply, eligible, ineligibleReason}``.

        Raises:
            SignalHouseValidationError: If phone_number is missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        safe_phone_number = quote(str(phone_number), safe="")
        return self._sdk._request(
            f"/number/{safe_phone_number}/cnam",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def port_in_phone_number(
        self,
        number_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Submit a port-in request for one or more phone numbers from another provider.

        Args:
            number_data: The port-in request data including owner info, address, phone numbers, and signature.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the created port-in request.

        Raises:
            SignalHouseValidationError: If number_data is missing.
        """
        self._sdk._require({"numberData": number_data})
        return self._sdk._request(
            "/number/portin",
            method="POST",
            body=number_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_port_requests(
        self,
        *,
        group_id: str | None = None,
        phone_number: str | None = None,
        status: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        exclude_documents: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get port-in requests with optional filters.

        Signal House staff can view all requests; regular users see only their group's requests.

        Args:
            group_id: Filter by group ID.
            phone_number: Filter by phone number.
            status: Filter by status (PENDING, IN_PROGRESS, ON_HOLD, REJECTED, SUCCESS).
            page: The page number for pagination (default: 1).
            limit: The number of items per page (default: 20).
            exclude_documents: When True, leave signatureUrl and billingUrl out of each request (the inline LOA signature and billing statement). Fetch one request by ID to read them.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with paginated port-in requests.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "phoneNumber": phone_number,
            "status": status,
            "page": page,
            "limit": limit,
            # urlencode would send Python's "True"; the API expects "true"/"false".
            "excludeDocuments": None if exclude_documents is None else str(exclude_documents).lower(),
        })
        return self._sdk._request(
            f"/number/portin{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_port_request_by_id(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single port-in request by its ID.

        Args:
            id: The ID of the port-in request to retrieve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the port-in request.

        Raises:
            SignalHouseValidationError: If id is missing.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/number/portin/{safe_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_porting_requests(
        self,
        porting_id: str | None = None,
        *,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get porting requests. If porting_id is provided, returns a single request; otherwise returns all.

        Args:
            porting_id: Optional ID of a specific port-in request. When provided, fetches that single request.
            page: The page number for pagination (only used when porting_id is not provided).
            limit: The number of items per page (only used when porting_id is not provided).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        if porting_id is not None:
            return self.get_port_request_by_id(id=porting_id, token=token, headers=headers, idempotency_key=idempotency_key)
        return self.get_port_requests(page=page, limit=limit, token=token, headers=headers, idempotency_key=idempotency_key)

    def assign_phone_number_to_campaign(
        self,
        campaign_id: str,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Assign phone numbers to a campaign. Numbers that are not found, already RELEASED, already
        assigned to a different campaign, on a mismatched DCA, or (for a 10DLC campaign without a number
        pool) beyond the remaining 49-number-per-campaign limit are not queued - each is reported back
        individually in skipped instead of failing the whole request. A Toll-Free campaign whose brand
        reports tollFree.maxNumbersPerCampaign as 1 holds one number: a request that would give it a
        second is refused with a 400 and nothing is queued.

        Args:
            campaign_id: The ID of the campaign to assign phone numbers to.
            phone_numbers: The list of phone numbers to assign.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict resolving to ``{message, queued, skipped}`` - ``queued`` numbers
            were sent for assignment; ``skipped`` numbers were rejected (not found, RELEASED, already
            assigned to a campaign, cross-DCA mismatch, or over the 49-number limit).

        Raises:
            SignalHouseValidationError: If campaign_id or phone_numbers is missing.
        """
        self._sdk._require({"campaignId": campaign_id, "phoneNumbers": phone_numbers})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/number/assign/{safe_campaign_id}",
            method="POST",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def unassign_phone_numbers_from_campaigns(
        self,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Unassign phone numbers from any campaign they are currently assigned to.

        Args:
            phone_numbers: The list of phone numbers to unassign.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If phone_numbers is missing.
        """
        self._sdk._require({"phoneNumbers": phone_numbers})
        return self._sdk._request(
            "/number/unassign",
            method="POST",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_phone_numbers(
        self,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete (release) phone numbers. This operation is irreversible.

        The phone numbers will no longer be active but will still be visible with status "RELEASED".

        Args:
            phone_numbers: The list of phone numbers to delete.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If phone_numbers is missing.
        """
        self._sdk._require({"phoneNumbers": phone_numbers})
        return self._sdk._request(
            "/number",
            method="DELETE",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def deactivate_phone_numbers(
        self,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Deactivate one or more phone numbers. Numbers must be in READY status.

        Deactivated numbers will not be able to send or receive messages but will
        remain assigned to their subgroup and campaign.

        Args:
            phone_numbers: The list of phone numbers to deactivate.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with an array of updated number objects.

        Raises:
            SignalHouseValidationError: If phone_numbers is missing.
        """
        self._sdk._require({"phoneNumbers": phone_numbers})
        return self._sdk._request(
            "/number/deactivate",
            method="POST",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reactivate_phone_numbers(
        self,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reactivate one or more previously deactivated phone numbers.

        Numbers must be in DEACTIVATED status. Reactivated numbers will return to
        PENDING or IN_PROGRESS status depending on their campaign assignment.

        Args:
            phone_numbers: The list of phone numbers to reactivate.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with an array of updated number objects.

        Raises:
            SignalHouseValidationError: If phone_numbers is missing.
        """
        self._sdk._require({"phoneNumbers": phone_numbers})
        return self._sdk._request(
            "/number/reactivate",
            method="POST",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def transfer_phone_numbers(
        self,
        phone_numbers: list[str],
        new_subgroup_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Transfer unassigned phone numbers from one subgroup to another.

        Args:
            phone_numbers: The list of phone numbers to transfer.
            new_subgroup_id: The ID of the new subgroup to transfer the numbers to.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        self._sdk._require({"phoneNumbers": phone_numbers, "newSubgroupId": new_subgroup_id})
        return self._sdk._request(
            "/number/transfer",
            method="POST",
            body={"phoneNumbers": phone_numbers, "newSubgroupId": new_subgroup_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def search_npa_nxx(
        self,
        *,
        country: str | None = None,
        state: str | None = None,
        city: str | None = None,
        npa: str | None = None,
        nxx: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Search NPA/NXX lookup data with optional filters.

        At least one search parameter is required.
        Country may scope NPA/NXX filters; state and city cannot be combined with them.

        Args:
            country: Filter by country code.
            state: Filter by state code (2 characters).
            city: Filter by city name (prefix match, case-insensitive; requires country and state).
            npa: Area code filter (1-3 digits; optional country, no state/city).
            nxx: Central office code filter (1-3 digits; optional country, no state/city).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "country": country,
            "state": state,
            "city": city,
            "npa": npa,
            "nxx": nxx,
        })
        return self._sdk._request(
            f"/number/lookup{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def lookup_locations(
        self,
        entries: list[dict[str, str]],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Batch lookup city/state for NPA/NXX pairs.

        Args:
            entries: NPA/NXX pairs to look up (max 50), each with 'npa' and 'nxx' keys.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with an array of {npa, nxx, city, state} objects.
        """
        return self._sdk._request(
            "/number/lookup/location",
            method="POST",
            body={"entries": entries},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def migrate_phone_number_to_v2(
        self,
        phone_number: str | None = None,
        campaign_id: str | None = None,
        group_id: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Migrate a phone number (or all numbers in a group) from v1 to v2.

        Args:
            phone_number: Phone number to migrate. If provided, group_id is ignored.
            campaign_id: Campaign ID to migrate all numbers for.
            group_id: Group ID to migrate all non-released numbers for.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with migration queue confirmation.
        """
        return self._sdk._request(
            "/number/migrate",
            method="POST",
            body={"phoneNumber": phone_number, "campaignId": campaign_id, "groupId": group_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
