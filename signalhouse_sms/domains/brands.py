"""Brands domain for the SignalHouse SDK.

Brand lookup id: carrier Brand ID (B… or TFNB…), record _id, or internal reference UUID.
Read/create responses return ``brandId: null`` for pending brands — poll ``GET /brand?id=<record _id>``.
"""

from __future__ import annotations

import json
from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Brands:
    """10DLC Brand registration operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_brands(
        self,
        *,
        id: str | None = None,
        subgroup_id: str | None = None,
        group_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        registration_type: str | None = None,
        current_toll_free_carrier: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of brands with optional filters.

        Args:
            id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            subgroup_id: The ID of the subgroup to filter by.
            group_id: The ID of the group to filter by.
            page: The page number for pagination.
            limit: The number of items per page.
            status: The status of the brand to filter by (PENDING_CREATION, PENDING_APPROVAL,
                    UNVERIFIED, VERIFIED, VETTED_VERIFIED, PENDING_DELETE, DELETED).
            registration_type: Optional registration-type filter ("TEN_DLC", "TOLL_FREE", or "SHORT_CODE").
            current_toll_free_carrier: With subgroup_id or group_id: when True, return only toll-free brands that a new
                    toll-free campaign in that group can use (those on the group's current toll-free carrier).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. Each brand may have ``brandId: null`` until a carrier
            Brand ID is assigned — use ``_id`` for polling. Each brand carries ``carrierSuspensions``
            (carrier brand suspension rules; active while ``liftedAt`` is null).
        """
        query_string = self._sdk._get_query_string({
            "id": id,
            "subgroupId": subgroup_id,
            "groupId": group_id,
            "page": page,
            "limit": limit,
            "status": status,
            "registrationType": registration_type,
            # urlencode would send Python's "True"; the API expects "true"/"false".
            "currentTollFreeCarrier": None if current_toll_free_carrier is None else str(current_toll_free_carrier).lower(),
        })
        return self._sdk._request(
            f"/brand{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_external_vetting(
        self,
        brand_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get external vetting information for a brand.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(
            f"/brand/externalvetting/{safe_brand_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_brand(
        self,
        brand_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new brand.

        Args:
            brand_data: The data for the brand to be created. Required fields include
                        subgroupId, entityType, displayName, companyName, ein, phone,
                        street, city, state, postalCode, country, email, vertical.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. ``brandId`` may be ``null`` until carrier assignment — use ``_id`` to poll.

        Raises:
            SignalHouseValidationError: If brand_data is missing.
        """
        self._sdk._require({"brandData": brand_data})
        return self._sdk._request(
            "/brand",
            method="POST",
            body=brand_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_toll_free_brand(
        self,
        brand_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Toll-Free (TFN) brand.

        registrationType is forced to TOLL_FREE server-side; TFN-specific fields live under
        ``brand_data["tollFree"]`` (businessRegistrationType, legalEntityType, taxId, countryCode,
        supportPhone, and optional taxIdIssuingCountry / businessDBA / businessWebsite).
        ``supportPhone`` must be E.164 with an optional leading ``+`` and no spaces, parentheses
        or hyphens (e.g. ``"17025550100"``).

        ``tollFree.businessVerificationId`` names the business verification the brand uses (starts with BV). A group
        whose toll-free brands need a business verification must send a VERIFIED one of the brand's group (in a group
        that verifies each subgroup's business separately, of the brand's subgroup); any other group gets 400 if it
        sends one. With it, the legal fields (companyName, street, city, state, postalCode, country, firstName,
        lastName and tollFree's businessRegistrationType, taxId, countryCode and taxIdIssuingCountry) are optional:
        the business verification's values replace any that are sent. It can't be changed after creation.

        Args:
            brand_data: The data for the toll-free brand to be created (see API docs for required
                        fields, including the ``tollFree`` sub-object).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. For Toll-Free, ``brandId`` is a ``TFNB``-prefixed id when
            assigned; otherwise ``null`` — use ``_id`` to poll.

        Raises:
            SignalHouseValidationError: If brand_data is missing.
        """
        self._sdk._require({"brandData": brand_data})
        return self._sdk._request(
            "/brand/toll-free",
            method="POST",
            body=brand_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_business_verifications(
        self,
        group_id: str,
        *,
        subgroup_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List a group's business verifications, newest first, and whether its toll-free brands need one.

        Some groups verify each subgroup's business separately: a platform whose subgroups are separate businesses, set
        up by Signal House. For those groups subgroup_id is required.

        Args:
            group_id: The ID of the group whose business verifications to list.
            subgroup_id: The subgroup whose business verifications to list, sent as the subgroupId query parameter
                only when given. Required for a group that verifies each subgroup's business separately (400 without
                it); for any other group, the group's business verifications cover every subgroup. It must be one of
                the group's subgroups (404 otherwise).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. ``data`` holds groupId, subgroupId (only when the business verifications
            belong to one subgroup), required (whether the group's new toll-free brands need a business
            verification) and businessVerifications, newest first. Each has businessVerificationId, groupId,
            subgroupId (only when set), status (SUBMITTING, IN_REVIEW, VERIFIED or NEEDS_CHANGES), details,
            submittedAt, reviewedAt and rejectionReason (why it needs changes, or None).

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        safe_group_id = quote(str(group_id), safe="")
        query_string = self._sdk._get_query_string({"subgroupId": subgroup_id}) if subgroup_id is not None else ""
        return self._sdk._request(
            f"/brand/business-verification/{safe_group_id}{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_business_verification(
        self,
        group_id: str,
        business_verification_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get one of a group's business verifications by its ID.

        Args:
            group_id: The ID of the group the business verification belongs to.
            business_verification_id: The ID of the business verification to get (starts with BV).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. ``data`` holds the business verification, as get_business_verifications
            lists it, plus required. 404 when it isn't one of the group's.

        Raises:
            SignalHouseValidationError: If group_id or business_verification_id is missing.
        """
        self._sdk._require({"groupId": group_id, "businessVerificationId": business_verification_id})
        safe_group_id = quote(str(group_id), safe="")
        safe_business_verification_id = quote(str(business_verification_id), safe="")
        return self._sdk._request(
            f"/brand/business-verification/{safe_group_id}/{safe_business_verification_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_business_verification(
        self,
        group_id: str,
        details: dict[str, Any],
        *,
        subgroup_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create and submit a new business verification.

        Review usually takes 1–2 business days. Once it is VERIFIED, a new toll-free brand uses it by sending its ID
        as ``tollFree.businessVerificationId`` (see create_toll_free_brand). Some groups verify each subgroup's
        business separately: a platform whose subgroups are separate businesses, set up by Signal House. For those
        groups subgroup_id is required, and only that subgroup's toll-free brands can use the business verification.

        Args:
            group_id: The ID of the group the business verification is for (the caller's active group).
            details: The business verification: businessName, businessType, industry, registrationType,
                     registrationNumber, website, street, optional street2, city, state, postalCode,
                     country ("US" or "CA") and a ``representative`` sub-object (firstName, lastName,
                     email, phone, jobTitle, jobLevel). See the API docs for each field's accepted values.
            subgroup_id: The subgroup whose business it verifies, sent as the subgroupId query parameter only when
                given. Required for a group that verifies each subgroup's business separately (400 without it); for
                any other group, the business verification covers every subgroup. It must be one of the group's
                subgroups (404 otherwise) and active (400 otherwise).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (status 202). ``data`` is the new business verification, as
            get_business_verifications lists it, with status SUBMITTING. 400 when the group's toll-free brands
            don't need a business verification.

        Raises:
            SignalHouseValidationError: If group_id or details is missing.
        """
        self._sdk._require({"groupId": group_id, "details": details})
        safe_group_id = quote(str(group_id), safe="")
        query_string = self._sdk._get_query_string({"subgroupId": subgroup_id}) if subgroup_id is not None else ""
        return self._sdk._request(
            f"/brand/business-verification/{safe_group_id}{query_string}",
            method="POST",
            body=details,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_business_verification(
        self,
        group_id: str,
        business_verification_id: str,
        details: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Correct and resubmit a business verification that needs changes.

        Allowed only while its status is NEEDS_CHANGES (400 otherwise). Review usually takes 1–2 business days; the
        toll-free brands that use it stay pending until it is verified.

        Args:
            group_id: The ID of the group the business verification belongs to (the caller's active group).
            business_verification_id: The ID of the business verification to update (starts with BV).
            details: The corrected business verification, with the same fields as create_business_verification.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (status 202). ``data`` is the business verification, as
            get_business_verifications lists it, with status SUBMITTING. 404 when it isn't one of the group's.

        Raises:
            SignalHouseValidationError: If group_id, business_verification_id or details is missing.
        """
        self._sdk._require({"groupId": group_id, "businessVerificationId": business_verification_id, "details": details})
        safe_group_id = quote(str(group_id), safe="")
        safe_business_verification_id = quote(str(business_verification_id), safe="")
        return self._sdk._request(
            f"/brand/business-verification/{safe_group_id}/{safe_business_verification_id}",
            method="PUT",
            body=details,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_toll_free_isv_account(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a group's toll-free ISV account: its own parent account at the toll-free provider. Staff-only.

        A group whose subgroups are separate businesses can have one; each subgroup then gets an account and
        business verifications of its own under it. Available to signalhouse_api, signalhouse_admin and
        signalhouse_user. The API key secret is never returned, and a group that doesn't exist or isn't active
        answers 404.

        Args:
            group_id: The ID of the group whose ISV account to get.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. ``data`` holds groupId, accountSid, apiKeySid, primaryProfileSid (the
            account's approved primary business profile), createdAt and updatedAt, or is None when the group has
            no ISV account.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/brand/toll-free-isv-account/{safe_group_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def set_toll_free_isv_account(
        self,
        group_id: str,
        account_sid: str,
        api_key_sid: str,
        api_key_secret: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Register a group's toll-free ISV account, its own parent account at the toll-free provider, or replace its API key.

        Available only to signalhouse_admin. The provider checks the account and key before they are stored and finds
        the account's approved primary business profile itself; a refusal answers 400 with the reason, and a group
        that doesn't exist or isn't active answers 404. Register it before the group has any toll-free records at
        that provider: after that, only the API key of the same account can be replaced.

        Args:
            group_id: The ID of the group to register the ISV account for.
            account_sid: The SID of the ISV's own top-level account (AC followed by 32 lowercase hexadecimal
                characters).
            api_key_sid: The SID of a Main API key created in that account, one that can create subaccounts (SK
                followed by 32 lowercase hexadecimal characters).
            api_key_secret: That API key's secret (1 to 128 characters), stored encrypted and never returned.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. ``data`` holds groupId, accountSid, apiKeySid, primaryProfileSid, createdAt
            and updatedAt, without the API key secret.

        Raises:
            SignalHouseValidationError: If group_id, account_sid, api_key_sid or api_key_secret is missing.
        """
        self._sdk._require({
            "groupId": group_id,
            "accountSid": account_sid,
            "apiKeySid": api_key_sid,
            "apiKeySecret": api_key_secret,
        })
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/brand/toll-free-isv-account/{safe_group_id}",
            method="PUT",
            body={"accountSid": account_sid, "apiKeySid": api_key_sid, "apiKeySecret": api_key_secret},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_short_code_brand(
        self,
        brand_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a local Short Code brand for manual Signal House review.

        The route forces the ``SHORT_CODE`` registration type. The payload requires standard contact
        and address fields plus ``shortCode`` with businessRegistrationType, legalEntityType, taxId,
        countryCode, and supportPhone. The synchronous response is a 201-created record in
        ``PENDING_APPROVAL`` with a stable ``SCB``-prefixed brandId.
        """
        self._sdk._require({"brandData": brand_data})
        return self._sdk._request("/brand/short-code", method="POST", body=brand_data, token=token, headers=headers, idempotency_key=idempotency_key)

    def approve_short_code_brand(
        self,
        brand_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Approve a pending Short Code brand. Available only to signalhouse_admin."""
        self._sdk._require({"brandId": brand_id})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(f"/brand/approve/{safe_brand_id}", method="POST", token=token, headers=headers, idempotency_key=idempotency_key)

    def reject_short_code_brand(
        self,
        brand_id: str,
        internal_rejection_reason: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reject a pending Short Code brand with its required customer-visible reason. signalhouse_admin only."""
        self._sdk._require({"brandId": brand_id, "internalRejectionReason": internal_rejection_reason})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(
            f"/brand/reject/{safe_brand_id}",
            method="POST",
            body={"internalRejectionReason": internal_rejection_reason},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def transfer_brand(
        self,
        subgroup_id: str,
        brand_ids: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Transfer one or more brands to a different subgroup.

        Args:
            subgroup_id: The ID of the subgroup to transfer the brands to.
            brand_ids: Brand lookup ids to transfer (carrier id, record _id, or internal reference).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If subgroup_id or brand_ids is missing.
        """
        self._sdk._require({"subgroupId": subgroup_id, "brandIds": brand_ids})
        safe_subgroup_id = quote(str(subgroup_id), safe="")
        return self._sdk._request(
            f"/brand/transfer/{safe_subgroup_id}",
            method="POST",
            body={"brandIds": brand_ids},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_external_vetting(
        self,
        brand_id: str,
        vetting_provider_id: str,
        vetting_class: str,
        additional_data: dict[str, Any] | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create external vetting for a brand.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            vetting_provider_id: The external vetting provider (AEGIS or WMC).
            vetting_class: The vetting class (STANDARD, ENHANCED, AUTHPLUS, or RCS; AEGIS accepts all
                four, WMC accepts STANDARD only).
            additional_data: Provider-specific additional data forwarded to TCR.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If brand_id, vetting_provider_id, or vetting_class is missing.
        """
        self._sdk._require({"brandId": brand_id, "vettingProviderId": vetting_provider_id, "vettingClass": vetting_class})
        safe_brand_id = quote(str(brand_id), safe="")
        body: dict[str, Any] = {"vettingProviderId": vetting_provider_id, "vettingClass": vetting_class}
        if additional_data is not None:
            body["additionalData"] = additional_data
        return self._sdk._request(
            f"/brand/externalvetting/{safe_brand_id}",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def import_external_vetting(
        self,
        brand_id: str,
        vetting_provider_id: str,
        vetting_id: str,
        vetting_token: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Import an existing external vetting record for a brand.

        Unlike create_external_vetting (which orders a new, billable vetting), this attaches a
        vetting the brand already completed directly with the provider, using the provider-issued
        vettingId and vettingToken. It is synchronous and not billable.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            vetting_provider_id: The external vetting provider (AEGIS, WMC, CV).
            vetting_id: The provider-issued vetting / transaction ID to import.
            vetting_token: The provider-issued vetting token (required by some providers, e.g. AEGIS).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If brand_id, vetting_provider_id, or vetting_id is missing.
        """
        self._sdk._require(
            {"brandId": brand_id, "vettingProviderId": vetting_provider_id, "vettingId": vetting_id}
        )
        safe_brand_id = quote(str(brand_id), safe="")
        body: dict[str, Any] = {"vettingProviderId": vetting_provider_id, "vettingId": vetting_id}
        if vetting_token is not None:
            body["vettingToken"] = vetting_token
        return self._sdk._request(
            f"/brand/externalvetting/import/{safe_brand_id}",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_brand(
        self,
        brand_id: str,
        brand_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update a brand's information.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            brand_data: The data for the brand to be updated. For a Toll-Free brand, pass the
                        editable Toll-Free fields under a ``tollFree`` sub-object (legalEntityType,
                        businessRegistrationType, taxId, countryCode, supportPhone,
                        taxIdIssuingCountry, businessDBA, businessWebsite); supportPhone must be
                        E.164 with an optional leading ``+`` and no spaces, parentheses or hyphens
                        (e.g. ``"17025550100"``); subgroupId is immutable.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(
            f"/brand/{safe_brand_id}",
            method="PUT",
            body=brand_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def revet_brand(
        self,
        brand_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Revet a brand that is in UNVERIFIED status due to an update after it was previously VERIFIED or VETTED_VERIFIED.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(
            f"/brand/revet/{safe_brand_id}",
            method="PUT",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_brand(
        self,
        brand_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a brand (mark it as DELETED). The brand will still be retrievable.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(
            f"/brand/{safe_brand_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_appeal_history(
        self,
        brand_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the appeal history for a brand.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing an array of BrandAppeal objects.

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        safe_brand_id = quote(str(brand_id), safe="")
        return self._sdk._request(
            f"/brand/appeal/{safe_brand_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def submit_appeal(
        self,
        brand_id: str,
        appeal_categories: list[str],
        explanation: str,
        file: BinaryIO | tuple,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Submit an appeal for a brand.

        Args:
            brand_id: Brand lookup id (carrier Brand ID, record _id, or internal reference).
            appeal_categories: A list of appeal category strings.
            explanation: The explanation for the appeal.
            file: The file to attach to the appeal. Can be a file-like object or
                  a tuple of (filename, file_object, content_type).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({
            "brandId": brand_id,
            "appealCategories": appeal_categories,
            "explanation": explanation,
            "file": file,
        })
        safe_brand_id = quote(str(brand_id), safe="")

        form_data: dict[str, Any] = {
            "appealCategories": json.dumps(appeal_categories),
            "explanation": explanation,
        }

        files_list: list[tuple[str, Any]] = []
        if isinstance(file, tuple):
            files_list.append(("file", file))
        else:
            files_list.append(("file", file))

        return self._sdk._multipart_request(
            f"/brand/appeal/{safe_brand_id}",
            method="POST",
            form_data=form_data,
            files=files_list,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
