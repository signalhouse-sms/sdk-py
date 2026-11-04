"""RCS domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

from .templates import _UNSET

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


def _agent_payload(
    brand_id: str | None,
    campaign_id: Any,
    agent: dict[str, Any] | None,
    consent: dict[str, Any] | None,
    use_case: Any,
    billing_category: str | None,
    default_fallback: Any,
    excluded_carriers: list[str] | None,
    testers: list[str] | None,
    contact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an agent create or update body; None omits a field, except the nullable ones, where _UNSET omits it.

    Args:
        brand_id: The 10DLC brand, or None to leave it out.
        campaign_id: The 10DLC campaign, None to send null (unlink), or _UNSET to leave it out.
        agent: Profile fields, or None to leave them out.
        consent: Consent fields, or None to leave them out.
        use_case: The use case, None to send null, or _UNSET to leave it out.
        billing_category: The billing category, or None to leave it out.
        default_fallback: The fallback, None to send null, or _UNSET to leave it out.
        excluded_carriers: Excluded carriers, or None to leave them out.
        testers: Tester numbers, or None to leave them out.
        contact: The launch contact fields, or None to leave them out.

    Returns:
        The JSON request body.
    """
    optional = {
        "brandId": brand_id,
        "agent": agent,
        "consent": consent,
        "contact": contact,
        "billingCategory": billing_category,
        "excludedCarriers": excluded_carriers,
        "testers": testers,
    }
    nullable = {"campaignId": campaign_id, "useCase": use_case, "defaultFallback": default_fallback}
    payload = {key: value for key, value in optional.items() if value is not None}
    payload.update({key: value for key, value in nullable.items() if value is not _UNSET})
    return payload


def _asset_files(file: BinaryIO | bytes | tuple, file_name: str | None) -> list[tuple[str, Any]]:
    """Build the multipart file part, naming it file_name unless file is already a tuple.

    Args:
        file: A file-like object, bytes, or a (filename, file_object, content_type) tuple.
        file_name: The filename to send when file is not a tuple.

    Returns:
        The files list for a multipart request.
    """
    return [("file", file if isinstance(file, tuple) or file_name is None else (file_name, file))]


class RcsAgents:
    """RCS agents under /rcs/agent.

    An agent links one 10DLC brand and one 10DLC campaign: the campaign's numbers are the SMS fallback, and the
    brand and campaign supply the company identity and consent text for the carrier launch. One brand or campaign
    can serve many agents. An agent is a registration (type RCS_AGENT, id RCSA...), so the registrations methods
    read and edit the same record. 404 while the environment's RCS switch is off; 400 while the group's rcsEnabled
    flag is off.
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def create(
        self,
        *,
        brand_id: str,
        campaign_id: str | None = _UNSET,
        agent: dict[str, Any] | None = None,
        consent: dict[str, Any] | None = None,
        contact: dict[str, Any] | None = None,
        use_case: str | None = _UNSET,
        billing_category: str | None = None,
        default_fallback: dict[str, Any] | None = _UNSET,
        excluded_carriers: list[str] | None = None,
        testers: list[str] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create an agent draft on a 10DLC brand, optionally with its campaign. The agent's subgroup is the brand's.

        Blank consent fields fill from the linked campaign.

        Args:
            brand_id: The 10DLC brand: carrier brand ID, provisional UUID or _id.
            campaign_id: A 10DLC campaign of that brand (campaign ID or _id); required before submit.
            agent: The agent profile {name, description, color, logoUrl, heroUrl, phone, website, email,
                phoneLabel, websiteLabel, emailLabel (captions, max 40; submit defaults them to Call, Website and
                Email), privacyPolicyUrl, termsUrl}.
            consent: The launch text {optInDetails, optInUrl, optInResponse, optOutDetails, optOutResponse,
                helpResponse, campaignDescription, messageExamples, estimatedMonthlyVolume, launchVideoUrl}; every
                field is required before the launch request.
            contact: The launch contact {firstName, lastName, role, email, mobile}: the individual at the brand the
                carrier partner's reviewers may write to; required in full before the launch request.
            use_case: OTP, TRANSACTIONAL, PROMOTIONAL or MULTI_USE; required before submit.
            billing_category: NON_CONVERSATIONAL (default) or CONVERSATIONAL; submit refuses CONVERSATIONAL.
            default_fallback: {mode (auto, rcs_only, sms_only, none), channel (auto, sms, mms), from (a number on
                the linked campaign)}.
            excluded_carriers: [] or ["T_MOBILE"] (the carrier partner's carrier name).
            testers: Tester numbers (up to 200), invited once the agent exists at the carrier.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent (status DRAFT) (201).

        Raises:
            SignalHouseValidationError: If brand_id is missing.
        """
        self._sdk._require({"brandId": brand_id})
        return self._sdk._request(
            "/rcs/agent",
            method="POST",
            body=_agent_payload(brand_id, campaign_id, agent, consent, use_case, billing_category,
                                default_fallback, excluded_carriers, testers, contact),
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        status: str | list[str] | None = None,
        brand_id: str | None = None,
        campaign_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List agents, newest first.

        Args:
            group_id: Filter by group ID.
            subgroup_id: Filter by subgroup ID.
            status: DRAFT, PENDING_REVIEW, REJECTED, AGENT_CREATING or ARCHIVED, one or a list.
            brand_id: Agents linked to this 10DLC brand (carrier brand ID, provisional UUID or _id).
            campaign_id: Agents linked to this 10DLC campaign (campaign ID or _id).
            page: The page number (default 1).
            limit: Agents per page (default 25, max 100).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {data: [agents], total, page, limit}.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "status": status,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/rcs/agent{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get(
        self,
        agent_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get one agent with the live state of its brand and campaign links.

        Args:
            agent_id: The agent ID (e.g. RCSA7K2M1QZ8RP).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent.

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        return self._agent_call(agent_id, "", "GET", token, headers, idempotency_key)

    def update(
        self,
        agent_id: str,
        *,
        brand_id: str | None = None,
        campaign_id: str | None = _UNSET,
        agent: dict[str, Any] | None = None,
        consent: dict[str, Any] | None = None,
        contact: dict[str, Any] | None = None,
        use_case: str | None = _UNSET,
        billing_category: str | None = None,
        default_fallback: dict[str, Any] | None = _UNSET,
        excluded_carriers: list[str] | None = None,
        testers: list[str] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Edit an agent while it may change: a draft, a Signal House rejection, a request for changes, or an agent in
        testing (the change is pushed to the carrier partner). 409 in any other status; brand_id is locked once the agent
        exists at the partner and billing_category once a launch was requested.

        agent, consent and contact merge field by field; every other key replaces. Only the fields you pass are sent.

        Args:
            agent_id: The agent ID.
            brand_id: Relink to another 10DLC brand of the same subgroup.
            campaign_id: Link or relink the campaign; None unlinks it.
            agent: Profile fields to change.
            consent: Consent fields to change.
            contact: Contact fields to change.
            use_case: The use case; None clears it.
            billing_category: The billing category.
            default_fallback: The fallback; None clears it.
            excluded_carriers: [] or ["T_MOBILE"] (the carrier partner's carrier name).
            testers: Tester numbers.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent.

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        body = _agent_payload(brand_id, campaign_id, agent, consent, use_case, billing_category,
                              default_fallback, excluded_carriers, testers, contact)
        return self._agent_call(agent_id, "", "PUT", token, headers, idempotency_key, body=body)

    def validate(
        self,
        agent_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Check an agent against every submit requirement without writing.

        Args:
            agent_id: The agent ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {valid, errors: [{field, reason}], warnings: [{field, reason}]}.

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        return self._agent_call(agent_id, "/validate", "POST", token, headers, idempotency_key)

    def submit(
        self,
        agent_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Submit a draft: create the agent at the carrier partner, with no review first.

        It needs the full profile, a use case and NON_CONVERSATIONAL billing; otherwise a 400 whose details carry
        {code: "REGISTRATION_INCOMPLETE", errors, warnings}. The agent moves to AGENT_CREATING, then IN_TESTING once
        the partner reports it ready.

        Args:
            agent_id: The agent ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent (status AGENT_CREATING).

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        return self._agent_call(agent_id, "/submit", "POST", token, headers, idempotency_key)

    def launch(
        self,
        agent_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Request the agent's launch.

        The launch requirements are checked and the agent goes to Signal House review (status PENDING_REVIEW), whose
        approval files the launch with the carrier partner. Allowed from IN_TESTING, REJECTED and CARRIER_REJECTED
        (409 otherwise); a failed requirement is a 400 whose details carry {code: "REGISTRATION_INCOMPLETE", errors,
        warnings}. Sends POST /registration/{agent_id}/launch: the agent is a registration.

        Args:
            agent_id: The agent ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent (status PENDING_REVIEW).

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        self._sdk._require({"agentId": agent_id})
        safe_agent_id = quote(str(agent_id), safe="")
        return self._sdk._request(
            f"/registration/{safe_agent_id}/launch",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def archive(
        self,
        agent_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Archive an agent.

        Args:
            agent_id: The agent ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent (status ARCHIVED).

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        return self._agent_call(agent_id, "/archive", "POST", token, headers, idempotency_key)

    def resend_tester_invite(
        self,
        agent_id: str,
        *,
        phone_number: str,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Resend a tester's expired invitation, which starts a new 24 hours for the tester to accept it.

        The number must be a tester on the agent (404) and its invitation must be EXPIRED (409); up to 20 invitations
        go out a day (429).

        Args:
            agent_id: The agent ID.
            phone_number: The tester's US number, with or without the +.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent.

        Raises:
            SignalHouseValidationError: If agent_id or phone_number is missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        return self._agent_call(agent_id, f"/testers/{quote(phone_number, safe='')}/resend", "POST", token, headers, idempotency_key)

    def upload_asset(
        self,
        agent_id: str,
        *,
        kind: str,
        file: BinaryIO | bytes | tuple,
        file_name: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Host the agent's logo or hero image and set it on the draft.

        Logo: 224 x 224 px, 50 KB max. Hero: 1440 x 448 px, 200 KB max. PNG or JPEG; images of any other size are refused.

        Args:
            agent_id: The agent ID.
            kind: "logo" or "hero".
            file: A file-like object, bytes, or a (filename, file_object, content_type) tuple.
            file_name: The filename to send when file is not already a tuple.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the agent with the new URL.

        Raises:
            SignalHouseValidationError: If agent_id, kind or file is missing.
        """
        self._sdk._require({"agentId": agent_id, "kind": kind, "file": file})
        safe_agent_id = quote(str(agent_id), safe="")
        return self._sdk._multipart_request(
            f"/rcs/agent/{safe_agent_id}/asset",
            method="POST",
            form_data={"kind": kind},
            files=_asset_files(file, file_name),
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def _agent_call(
        self,
        agent_id: str,
        suffix: str,
        method: str,
        token: str | None,
        headers: dict[str, str] | None,
        idempotency_key: str | None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a JSON request to /rcs/agent/{agent_id}{suffix} after checking agent_id.

        Args:
            agent_id: The agent ID.
            suffix: The path after the agent ID ("" or e.g. "/submit").
            method: The HTTP method.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header.
            body: The JSON body, if any.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        self._sdk._require({"agentId": agent_id})
        safe_agent_id = quote(str(agent_id), safe="")
        return self._sdk._request(
            f"/rcs/agent/{safe_agent_id}{suffix}",
            method=method,
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Rcs:
    """RCS (Google RBM) resources, accessed via ``sdk.rcs``. Templates for RCS live under ``sdk.templates``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.agents = RcsAgents(sdk)
