"""Campaigns domain for the SignalHouse SDK."""

from __future__ import annotations

import json
from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class CampaignsAdmin:
    """Admin-only campaign operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def approve_campaign(
        self,
        campaign_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Approve a campaign that is pending approval.

        Args:
            campaign_id: The ID of the campaign to approve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/approve/{safe_campaign_id}",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reject_campaign(
        self,
        campaign_id: str,
        *,
        rejection_reason: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reject a campaign that is pending approval.

        Args:
            campaign_id: The ID of the campaign to reject.
            rejection_reason: Optional rejection reason (10-256 characters).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        body = {"rejectionReason": rejection_reason} if rejection_reason else None
        return self._sdk._request(
            f"/campaign/reject/{safe_campaign_id}",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_short_code_campaign_status(
        self,
        campaign_id: str,
        *,
        status: str,
        rejection_reason: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Transition a Short Code campaign's review status.

        A customer-visible reason is required for both rejection states ("REJECTED" = Signal
        House Rejected, "DCA_REJECTED" = Rejected). Selecting "PENDING_DCA_APPROVAL" runs
        the guarded carrier-review transition; fulfillment remains a dedicated staff operation.

        Args:
            campaign_id: The ID of the campaign to transition.
            status: The target status: "PENDING_REVIEW", "REJECTED", "PENDING_DCA_APPROVAL",
                "DCA_REJECTED", or "ACTIVE". PENDING_DCA_APPROVAL
                requires a Signal House-approved brand, issued code, and captured opt-in proof.
            rejection_reason: Required and nonblank for "REJECTED"/"DCA_REJECTED" (max 1024 characters).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the updated campaign.

        Raises:
            SignalHouseValidationError: If campaign_id or status is missing.
        """
        self._sdk._require({"campaignId": campaign_id, "status": status})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/short-code/{safe_campaign_id}/status",
            method="PUT",
            body={"status": status, "rejectionReason": rejection_reason},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def fulfill_short_code_campaign(
        self, campaign_id: str, actual_code: str, *, lease_end_date: str, internal_notes: str | None = None,
        token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Record the issued code for a campaign-bound Signal House Short Code request. A YYYY-MM-DD lease date expires at 23:59:59 UTC."""
        self._sdk._require({"campaignId": campaign_id, "actualCode": actual_code, "leaseEndDate": lease_end_date})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(f"/campaign/short-code/{safe_campaign_id}/fulfill", method="POST", body={"actualCode": actual_code, "leaseEndDate": lease_end_date, "internalNotes": internal_notes}, token=token, headers=headers, idempotency_key=idempotency_key)

    def submit_short_code_campaign_to_carrier(
        self, campaign_id: str, *, token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Submit an internally approved and fully prepared Short Code campaign to carrier review."""
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(f"/campaign/short-code/{safe_campaign_id}/submit-to-carrier", method="POST", token=token, headers=headers, idempotency_key=idempotency_key)

    def complete_short_code_cancellation(
        self, campaign_id: str, request_id: str, *, note: str | None = None,
        token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Confirm Registry offboarding and complete a pending Short Code cancellation."""
        self._sdk._require({"campaignId": campaign_id, "requestId": request_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(f"/campaign/short-code/{safe_campaign_id}/cancellation/complete", method="POST", body={"requestId": request_id, "note": note}, token=token, headers=headers, idempotency_key=idempotency_key)

    def dismiss_short_code_cancellation(
        self, campaign_id: str, request_id: str, *, note: str | None = None,
        token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Dismiss a pending Short Code cancellation and restore its prior lifecycle state."""
        self._sdk._require({"campaignId": campaign_id, "requestId": request_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(f"/campaign/short-code/{safe_campaign_id}/cancellation/dismiss", method="POST", body={"requestId": request_id, "note": note}, token=token, headers=headers, idempotency_key=idempotency_key)

    def get_expired_short_code_leases(self, *, page: int | None = None, limit: int | None = None, token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
        """Read staff-only expired Short Code leases awaiting Registry offboarding."""
        query = self._sdk._get_query_string({"page": page, "limit": limit})
        return self._sdk._request(f"/campaign/short-code/expired-leases{query}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key)

    def release_expired_short_code_lease(self, campaign_id: str, *, note: str | None = None, token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
        """Confirm Registry offboarding and mark an expired Short Code released."""
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(f"/campaign/short-code/{safe_campaign_id}/expired-lease/release", method="POST", body={"note": note}, token=token, headers=headers, idempotency_key=idempotency_key)


class Campaigns:
    """10DLC Campaign management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: CampaignsAdmin | None = None
        if sdk.enable_admin:
            self.admin = CampaignsAdmin(sdk)

    def get_campaigns(
        self,
        *,
        id: str | None = None,
        brand_id: str | None = None,
        subgroup_id: str | None = None,
        group_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        registration_type: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of campaigns with optional filters.

        Args:
            id: The ID of the campaign to filter by.
            brand_id: The ID of the brand to filter by.
            subgroup_id: The ID of the subgroup to filter by.
            group_id: The ID of the group to filter by.
            page: The page number for pagination.
            limit: The number of items per page.
            status: The status of the campaign to filter by.
            registration_type: Optional registration-type filter ("TEN_DLC", "TOLL_FREE", or "SHORT_CODE").
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
            "id": id,
            "brandId": brand_id,
            "subgroupId": subgroup_id,
            "groupId": group_id,
            "page": page,
            "limit": limit,
            "status": status,
            "registrationType": registration_type,
        })
        return self._sdk._request(
            f"/campaign{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_campaign_health(
        self,
        *,
        campaign_id: str,
        include_numbers: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated campaign health (7-day and 30-day windows) for a campaign.

        Args:
            campaign_id: The campaign identifier.
            include_numbers: When true, include per-number health entries.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        self._sdk._require({"campaignId": campaign_id})
        query_string = self._sdk._get_query_string({
            "campaignId": campaign_id,
            "includeNumbers": include_numbers,
        })
        return self._sdk._request(
            f"/campaign/health{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_campaign_throughput_limits(
        self,
        *,
        campaign_id: str,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the carrier throughput ceilings a campaign is currently sending under.

        The AT&T per-minute limit (per campaign, held 10% under the published ceiling) and the
        T-Mobile daily cap (per brand), each with its current tier and the next rung on the
        ladder, plus today's T-Mobile usage. Resolved from the same brand status / brand score
        rules the send path enforces with.

        Args:
            campaign_id: The campaign identifier.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict: {campaignId, brandId, usecase, brand: {status, brandScore,
            entityType}, att: {tier, scope, unit, sms: {limit}, mms: {limit}, marginPercent,
            nextTier}, tmobile: {tier, scope, unit, dailyLimit, thresholds, nextTier,
            usedToday: {date, segments, resetsAt} | None}}. A None tier/limit means the carrier
            ladder does not apply (unverified brand, GOVERNMENT entity, PUBLIC_SAFETY_RESTRICTED
            usecase); a None nextTier means the top rung or a usecase-capped (LOW_VOLUME) campaign.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        query_string = self._sdk._get_query_string({"campaignId": campaign_id})
        return self._sdk._request(
            f"/campaign/throughput-limits{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_campaign(
        self,
        campaign_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new campaign.

        Args:
            campaign_data: The data for the campaign to be created. Required fields include
                          brandId, usecase, description, messageFlow, privacyPolicyLink,
                          termsAndConditionsLink, phoneNumbers. Optional ``sampleMediaIds``
                          (10DLC only): up to 5 ``mediaId`` strings from ``upload_sample_media``,
                          attached to the TCR campaign as sample MMS media for carrier review.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_data is missing.
        """
        self._sdk._require({"campaignData": campaign_data})
        return self._sdk._request(
            "/campaign",
            method="POST",
            body=campaign_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_toll_free_campaign(
        self,
        campaign_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Toll-Free (TFN) campaign and submit it for Signal House review.

        registrationType is forced to TOLL_FREE server-side; TFN-specific fields live under
        ``campaign_data["tollFree"]`` (useCase, messageVolume, programSummary, exampleMessage,
        customerCareEmail, optInImageURLs, optional optIns / multiNumberReason / useCases / channels / landingId).

        Args:
            campaign_data: The data for the toll-free campaign to be created (see API docs for
                           required fields, including the ``tollFree`` sub-object). ``phoneNumbers``
                           must list 1 up to the brand's ``tollFree.maxNumbersPerCampaign`` Toll-Free
                           numbers (at most 5), on the brand's toll-free carrier, or the campaign is
                           refused. They are locked to the campaign once assigned.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_data is missing.
        """
        self._sdk._require({"campaignData": campaign_data})
        return self._sdk._request(
            "/campaign/toll-free",
            method="POST",
            body=campaign_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_short_code_campaign(
        self,
        campaign_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Short Code campaign and submit it for Signal House review.

        Requires an approved (VERIFIED) Short Code brand. Upload the opt-in proof screenshot first with
        ``upload_opt_in_image`` and pass the returned URL as
        ``campaign_data["shortCode"]["screenshotUrl"]`` (required; external URLs are rejected).
        ``optInUrl`` (required) is the public HTTPS link to the live opt-in experience. Request or register the campaign's
        Short Code separately through ``numbers.request_short_code_acquisition`` after creation.

        Args:
            campaign_data: The Short Code campaign data. Top-level fields: brandId,
                privacyPolicyLink, termsAndConditionsLink, optinMessage, optoutMessage,
                helpMessage, sample1-3, tag, and a ``shortCode`` sub-object
                (useCases, optInMethods, optInMethodDescriptions, messageFrequency,
                pricingTier, adultContent, doubleOptInMessage, programSummary,
                optInConfirmationMessage, screenshotUrl, optInUrl).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the created campaign.

        Raises:
            SignalHouseValidationError: If campaign_data is missing.
        """
        self._sdk._require({"campaignData": campaign_data})
        return self._sdk._multipart_request(
            "/campaign/short-code",
            method="POST",
            form_data={"campaignData": json.dumps(campaign_data)},
            files=[],
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_short_code_campaign(
        self,
        campaign_id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update a Short Code campaign's editable fields.

        Only permitted while the campaign is in Signal House Review or Signal House Rejected
        status; the number source cannot be changed once submitted.

        Args:
            campaign_id: The ID of the campaign to update.
            update_data: The fields to update (top-level campaign fields plus an optional
                ``shortCode`` object of editable Short Code fields).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the updated campaign.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/short-code/{safe_campaign_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def cancel_short_code_campaign(
        self,
        campaign_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Short Code campaign.

        Customer cancellation of an issued Short Code returns ``PENDING_DELETE`` (Cancellation Pending)
        until Signal House confirms Registry offboarding. Unissued RANDOM/VANITY requests, plus
        staff-confirmed cancellations, return ``EXPIRED`` immediately.

        Args:
            campaign_id: The ID of the campaign to cancel.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the cancelled campaign.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/short-code/{safe_campaign_id}/cancel",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def read_campaign_artifact(
        self,
        artifact_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Download a private Short Code external lease receipt.

        Opt-in screenshots are public at the ``shortCode.screenshotUrl`` returned on the campaign.
        Authorized to the owning group's users or Signal House staff only.

        Args:
            artifact_id: The receipt identifier from
                ``numberSource.externalLease.receiptArtifactId`` on a Short Code campaign.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the raw file bytes.

        Raises:
            SignalHouseValidationError: If artifact_id is missing.
        """
        self._sdk._require({"artifactId": artifact_id})
        safe_artifact_id = quote(str(artifact_id), safe="")
        return self._sdk._request(
            f"/campaign/short-code/artifact/{safe_artifact_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upload_opt_in_image(
        self,
        file: BinaryIO | tuple,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Upload an opt-in proof image, returning a hosted URL for a Toll-Free campaign's optInImageURLs.

        Args:
            file: The image file to upload. Can be a file-like object or a tuple of
                  (filename, file_object, content_type).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the hosted image's ``id`` and ``url``.

        Raises:
            SignalHouseValidationError: If file is missing.
        """
        self._sdk._require({"file": file})
        files_list: list[tuple[str, Any]] = [("file", file)]
        return self._sdk._multipart_request(
            "/campaign/opt-in-image",
            method="POST",
            files=files_list,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upload_sample_media(
        self,
        file: BinaryIO | tuple,
        *,
        group_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Upload a sample media file (JPEG, PNG, GIF, MP4 or MP3, up to 5MB) for a 10DLC campaign.

        Reference the returned ``mediaId`` in ``sampleMediaIds`` on campaign create or update; it is
        attached to the TCR campaign for carrier review.

        Args:
            file: The media file to upload. Can be a file-like object or a tuple of
                  (filename, file_object, content_type).
            group_id: The group the file belongs to. Required with a staff (signalhouse_*) key, which
                      has no active group; otherwise optional and must be your own group.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the uploaded file's ``mediaId``, ``fileName``,
            ``mimeType`` and ``size``.

        Raises:
            SignalHouseValidationError: If file is missing.
        """
        self._sdk._require({"file": file})
        files_list: list[tuple[str, Any]] = [("file", file)]
        return self._sdk._multipart_request(
            "/campaign/sample-media",
            method="POST",
            form_data={"groupId": group_id} if group_id else None,
            files=files_list,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def read_sample_media(
        self,
        media_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Download a campaign sample media file your group owns.

        Args:
            media_id: The ``mediaId`` returned by ``upload_sample_media``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the raw file bytes.

        Raises:
            SignalHouseValidationError: If media_id is missing.
        """
        self._sdk._require({"mediaId": media_id})
        safe_media_id = quote(str(media_id), safe="")
        return self._sdk._request(
            f"/campaign/sample-media/{safe_media_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def capture_opt_in_image_from_landing(
        self,
        brand_id: str,
        *,
        landing_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Auto-capture an opt-in proof image from a brand's generated landing page.

        Hosts the captured image on-platform and returns a URL suitable for a Toll-Free campaign's
        optInImageURLs.

        Args:
            brand_id: The ID of the brand whose generated landing page should be captured.
            landing_id: The specific page to capture. Required for Toll-Free brands, which have one page per campaign — omitted, the request is refused rather than guessing. A 10DLC brand has a single page, so it may be omitted there.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing the hosted image's ``id`` and ``url``.

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        body: dict[str, Any] = {"brandId": brand_id}
        if landing_id is not None:
            body["landingId"] = landing_id
        return self._sdk._request(
            "/campaign/opt-in-image/from-landing",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_campaign(
        self,
        campaign_id: str,
        campaign_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing campaign.

        Args:
            campaign_id: The ID of the campaign to update.
            campaign_data: The data for the campaign to be updated. For a Toll-Free campaign, pass
                           the editable Toll-Free fields under a ``tollFree`` sub-object (useCase,
                           messageVolume, programSummary, exampleMessage, customerCareEmail,
                           optInImageURLs, optIns, multiNumberReason, useCases, channels, landingId); phoneNumbers cannot be
                           changed — Toll-Free numbers are locked to their campaign. For a 10DLC
                           campaign, an optional ``sampleMediaIds`` list (up to 5 ``mediaId`` strings
                           from ``upload_sample_media``) sets the sample MMS media for carrier review.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/{safe_campaign_id}",
            method="PUT",
            body=campaign_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_campaign(
        self,
        campaign_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete an existing campaign (mark it as EXPIRED). The campaign will still be retrievable.

        Args:
            campaign_id: The ID of the campaign to delete.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/{safe_campaign_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def appeal_dca_rejection(
        self,
        campaign_id: str,
        appeal_data: dict[str, Any] | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Appeal a DCA-rejected campaign.

        Args:
            campaign_id: The ID of the campaign to appeal.
            appeal_data: Optional request body (e.g., {"reason": "..."}).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/appealDcaRejection/{safe_campaign_id}",
            method="POST",
            body=appeal_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def nudge_dca_for_campaign(
        self,
        campaign_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Nudge a connectivity partner to prioritize review of a campaign.

        The campaign must be in PENDING_DCA_APPROVAL status.

        Args:
            campaign_id: The ID of the campaign to nudge.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If campaign_id is missing.
        """
        self._sdk._require({"campaignId": campaign_id})
        safe_campaign_id = quote(str(campaign_id), safe="")
        return self._sdk._request(
            f"/campaign/nudge/{safe_campaign_id}",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
