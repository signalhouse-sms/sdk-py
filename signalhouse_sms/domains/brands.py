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
            (carrier brand suspension rules; active while ``liftedAt`` is null). Each toll-free brand
            carries ``tollFree.reviewsBusinessOnSubmit`` (whether it's reviewed when it's submitted and
            keeps its business details from then on); when that is True, it also carries the five
            business fields it was submitted with (tollFree's businessStructure, industry, contactEmail,
            contactJobTitle and contactJobLevel) and ``tollFree.rejectionReason`` (why it was rejected,
            or None).
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

        Some groups' toll-free brands are reviewed when they're submitted; get_toll_free_requirements says
        whether a group's are. Such a brand also needs five ``tollFree`` fields: businessStructure
        (CO_OPERATIVE, CORPORATION, LIMITED_LIABILITY_CORPORATION, NON_PROFIT_CORPORATION or PARTNERSHIP),
        industry (AGRICULTURE, AUTOMOTIVE, BANKING, CONSTRUCTION, CONSUMER, EDUCATION, ELECTRONICS,
        ENGINEERING, ENERGY, FAST_MOVING_CONSUMER_GOODS, FINANCIAL, FINTECH, FOOD_AND_BEVERAGE, GOVERNMENT,
        HEALTHCARE, HOSPITALITY, INSURANCE, JEWELRY, LEGAL, MANUFACTURING, MEDIA, NOT_FOR_PROFIT, OIL_AND_GAS,
        ONLINE, PROFESSIONAL_SERVICES, RAW_MATERIALS, REAL_ESTATE, RELIGION, RETAIL, TECHNOLOGY,
        TELECOMMUNICATIONS, TRANSPORTATION or TRAVEL), contactEmail (a valid email, at most 100
        characters), contactJobTitle (at most 100 characters) and contactJobLevel (DIRECTOR, GM, VP, CEO,
        CFO, GENERAL_COUNSEL or OTHER). Its ``tollFree.countryCode`` must be ``"US"`` or ``"CA"`` and its
        ``state`` a 2-letter state or province code. Any other group's toll-free brands are refused the
        five fields (400).

        Such a brand stays DCA_PENDING until its business details pass the review, which usually takes 1–2
        business days, then becomes DCA_ACTIVE; if they don't pass, it becomes DCA_REJECTED with
        ``tollFree.rejectionReason`` saying why. To fix a rejected brand, create it again with the
        corrections; the rejected one can then be deleted. Its business details (companyName, street, city,
        state, postalCode, country, firstName, lastName, tollFree's businessRegistrationType, taxId,
        countryCode and taxIdIssuingCountry, and the five) can't be changed after it's submitted.

        Args:
            brand_data: The data for the toll-free brand to be created (see API docs for required
                        fields, including the ``tollFree`` sub-object).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. For Toll-Free, ``brandId`` is a ``TFNB``-prefixed id when
            assigned; otherwise ``null`` — use ``_id`` to poll. The brand's ``tollFree`` carries
            ``reviewsBusinessOnSubmit`` (whether it's reviewed when it's submitted) and, when that is
            True, the five business fields and ``rejectionReason`` (None until it's rejected).

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

    def get_toll_free_requirements(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get whether a group's new toll-free brands are reviewed when they're submitted, which decides what they need.

        Args:
            group_id: The ID of the group whose toll-free brand requirements to get.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. ``data`` holds groupId and reviewsBusinessOnSubmit. When
            reviewsBusinessOnSubmit is True, a new toll-free brand in the group needs tollFree's
            businessStructure, industry, contactEmail, contactJobTitle and contactJobLevel, a
            ``tollFree.countryCode`` of ``"US"`` or ``"CA"`` and a 2-letter ``state``; it stays DCA_PENDING
            until it's reviewed, and its business details can't be changed after it's submitted (see
            create_toll_free_brand). When False, the group's toll-free brands are refused those five fields.
            403 when the caller can't view the group.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/brand/toll-free-requirements/{safe_group_id}",
            method="GET",
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
