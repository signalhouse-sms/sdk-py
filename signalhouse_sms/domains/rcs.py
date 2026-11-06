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
        brand_id: The brand, or None to leave it out.
        campaign_id: The campaign, None to send null (unlink), or _UNSET to leave it out.
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

    An agent links one brand and one campaign, of any registration type: the campaign's numbers are the SMS
    fallback, and the brand and campaign supply the company identity and consent text for the carrier launch. One
    brand or campaign can serve many agents. An agent is a registration (type RCS_AGENT, id RCSA...), so the
    registrations methods read and edit the same record. 404 while the environment's RCS switch is off; 400 while
    the group's rcsEnabled flag is off.
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
        """Create an agent draft on a brand, optionally with its campaign. The agent's subgroup is the brand's.

        Blank consent fields fill from the linked campaign.

        Args:
            brand_id: The brand: carrier brand ID, provisional UUID or _id.
            campaign_id: A campaign of that brand (campaign ID or _id); required before submit.
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
            brand_id: Agents linked to this brand (carrier brand ID, provisional UUID or _id).
            campaign_id: Agents linked to this campaign (campaign ID or _id).
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
            brand_id: Relink to another brand of the same subgroup.
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
        The request charges the agent's launch fees: a wallet that cannot cover them gets a 402, and the agent stays where it is. The agent's launchFees quotes what the next request charges.

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


class RcsMessages:
    """RCS messages, accessed via ``sdk.rcs.messages``.

    Sends go through an agent to POST /message/rcs. A message is a Message record (messageType RCS), so the messages
    methods read the same record. 404 while the environment's RCS switch is off; 403 while the group's rcsEnabled flag
    is off; 409 while the agent cannot send yet.
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def send(
        self,
        *,
        agent_id: str,
        recipients: list[dict[str, Any]],
        template_id: str | None = None,
        template_version: int | None = None,
        content: dict[str, Any] | None = None,
        content_format: str | None = None,
        traffic_type: str | None = None,
        ttl_seconds: int | None = None,
        expire_time: str | None = None,
        fallback: dict[str, Any] | None = None,
        status_callback_url: str | None = None,
        enable_shortlink: bool | None = None,
        is_test: bool | None = None,
        simulate: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send an RCS message to up to 100 recipients.

        A check that blocks one recipient writes a BLOCKED message for it and the rest still send.

        Args:
            agent_id: The agent that sends (RCSA...).
            recipients: Up to 100 recipients {phoneNumber, variables, clientMessageId, metadata}.
            template_id: A template to send; exactly one of template_id or content.
            template_version: A published version of template_id; needs template_id.
            content: Inline content; exactly one of template_id or content.
            content_format: content.v1 (default) or google.rcs.
            traffic_type: AUTHENTICATION, TRANSACTION, SERVICEREQUEST, ACKNOWLEDGEMENT or PROMOTION; required on a
                MULTI_USE agent when the template sets none.
            ttl_seconds: Seconds the RCS message may wait for delivery; at most one of ttl_seconds or expire_time.
            expire_time: ISO-8601 time the RCS message expires.
            fallback: {mode (auto, rcs_only, sms_only), channel (auto, sms, mms), from, content: {text, mediaUrls},
                validitySeconds}; from is a Ready number on the agent's linked Active campaign. If content is omitted
                the template's fallback, else a generated one, is used.
            status_callback_url: URL that receives this message's status events.
            enable_shortlink: Shorten the links in the message.
            is_test: Send as a test; approved testers only.
            simulate: not_capable, ttl_expired, delivered or read; approved testers only.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {requested, enqueued, failed, bulkId, messages} (201).
            A blocked row carries blockReason, reason and issues; an archived template answers 409 TEMPLATE_ARCHIVED.

        Raises:
            SignalHouseValidationError: If agent_id or recipients is missing.
        """
        self._sdk._require({"agentId": agent_id, "recipients": recipients})
        return self._post(
            "/message/rcs",
            {
                "agentId": agent_id,
                "recipients": recipients,
                "templateId": template_id,
                "templateVersion": template_version,
                "content": content,
                "contentFormat": content_format,
                "trafficType": traffic_type,
                "ttlSeconds": ttl_seconds,
                "expireTime": expire_time,
                "fallback": fallback,
                "statusCallbackUrl": status_callback_url,
                "enableShortlink": enable_shortlink,
                "isTest": is_test,
                "simulate": simulate,
            },
            token,
            headers,
            idempotency_key,
        )

    def validate(
        self,
        *,
        agent_id: str,
        recipients: list[dict[str, Any]],
        template_id: str | None = None,
        template_version: int | None = None,
        content: dict[str, Any] | None = None,
        content_format: str | None = None,
        traffic_type: str | None = None,
        ttl_seconds: int | None = None,
        expire_time: str | None = None,
        fallback: dict[str, Any] | None = None,
        status_callback_url: str | None = None,
        enable_shortlink: bool | None = None,
        is_test: bool | None = None,
        simulate: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Run a send's checks without writing anything or holding funds. Takes the same arguments as send.

        Args:
            agent_id: The agent that sends (RCSA...).
            recipients: Up to 100 recipients {phoneNumber, variables, clientMessageId, metadata}.
            template_id: A template to send; exactly one of template_id or content.
            template_version: A published version of template_id; needs template_id.
            content: Inline content; exactly one of template_id or content.
            content_format: content.v1 (default) or google.rcs.
            traffic_type: AUTHENTICATION, TRANSACTION, SERVICEREQUEST, ACKNOWLEDGEMENT or PROMOTION; required on a
                MULTI_USE agent when the template sets none.
            ttl_seconds: Seconds the RCS message may wait for delivery; at most one of ttl_seconds or expire_time.
            expire_time: ISO-8601 time the RCS message expires.
            fallback: {mode (auto, rcs_only, sms_only), channel (auto, sms, mms), from, content: {text, mediaUrls},
                validitySeconds}; from is a Ready number on the agent's linked Active campaign. If content is omitted
                the template's fallback, else a generated one, is used.
            status_callback_url: URL that receives this message's status events.
            enable_shortlink: Shorten the links in the message.
            is_test: Send as a test; approved testers only.
            simulate: not_capable, ttl_expired, delivered or read; approved testers only.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {valid, errors, warnings, billingClass, segments,
            estimatedCostMicros, unsupportedFiles, recipients}. valid is True only with no errors; each blocked
            recipient adds an error and carries blockReason, reason and issues.

        Raises:
            SignalHouseValidationError: If agent_id or recipients is missing.
        """
        self._sdk._require({"agentId": agent_id, "recipients": recipients})
        return self._post(
            "/message/rcs/validate",
            {
                "agentId": agent_id,
                "recipients": recipients,
                "templateId": template_id,
                "templateVersion": template_version,
                "content": content,
                "contentFormat": content_format,
                "trafficType": traffic_type,
                "ttlSeconds": ttl_seconds,
                "expireTime": expire_time,
                "fallback": fallback,
                "statusCallbackUrl": status_callback_url,
                "enableShortlink": enable_shortlink,
                "isTest": is_test,
                "simulate": simulate,
            },
            token,
            headers,
            idempotency_key,
        )

    def estimate(
        self,
        *,
        agent_id: str,
        recipients: list[dict[str, Any]] | None = None,
        recipient_count: int | None = None,
        template_id: str | None = None,
        template_version: int | None = None,
        content: dict[str, Any] | None = None,
        content_format: str | None = None,
        traffic_type: str | None = None,
        ttl_seconds: int | None = None,
        expire_time: str | None = None,
        fallback: dict[str, Any] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Price an RCS draft in microdollars; no charge or send. Sends POST /message/estimate with channel "rcs".

        Args:
            agent_id: The agent that would send (RCSA...).
            recipients: Named recipients {phoneNumber, variables, clientMessageId, metadata}; exactly one of
                recipients or recipient_count.
            recipient_count: A recipient count; carriers are unknown, so the default fees apply.
            template_id: A template to price; exactly one of template_id or content.
            template_version: A published version of template_id; needs template_id.
            content: Inline content; exactly one of template_id or content.
            content_format: content.v1 (default) or google.rcs.
            traffic_type: AUTHENTICATION, TRANSACTION, SERVICEREQUEST, ACKNOWLEDGEMENT or PROMOTION; required on a
                MULTI_USE agent when the template sets none.
            ttl_seconds: Seconds the RCS message may wait for delivery; at most one of ttl_seconds or expire_time.
            expire_time: ISO-8601 time the RCS message expires.
            fallback: {mode, channel, from, content: {text, mediaUrls}, validitySeconds}, as on send. from is optional
                for an estimate; with none, the fallback leg is priced on the channel of the agent's linked campaign.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {billingClass, segments, recipientCount, rcsLeg, fallbackLeg, totals,
            balance, issues, warnings}. issues lists what would block the send; warnings what an iPhone draws differently. rcsLeg.mediaSurcharge is the carrier's surcharge on media over 5 MB, already inside rcsLeg.cost; a message over 100 MB adds a MEDIA_TOO_LARGE issue.

        Raises:
            SignalHouseValidationError: If agent_id is missing.
        """
        self._sdk._require({"agentId": agent_id})
        return self._post(
            "/message/estimate",
            {
                "channel": "rcs",
                "agentId": agent_id,
                "recipients": recipients,
                "recipientCount": recipient_count,
                "templateId": template_id,
                "templateVersion": template_version,
                "content": content,
                "contentFormat": content_format,
                "trafficType": traffic_type,
                "ttlSeconds": ttl_seconds,
                "expireTime": expire_time,
                "fallback": fallback,
            },
            token,
            headers,
            idempotency_key,
        )

    def capabilities(
        self,
        agent_id: str,
        *,
        phone_numbers: list[str],
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Report which numbers can receive RCS from an agent.

        Args:
            agent_id: The agent (RCSA...).
            phone_numbers: Up to 500 numbers, 10-15 digits, with or without the +.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {results: [{phoneNumber, capability}]}, capability being ENABLED,
            UNREACHABLE or UNKNOWN.

        Raises:
            SignalHouseValidationError: If agent_id or phone_numbers is missing.
        """
        self._sdk._require({"agentId": agent_id, "phoneNumbers": phone_numbers})
        return self._post("/rcs/capabilities", {"agentId": agent_id, "phoneNumbers": phone_numbers}, token, headers, idempotency_key)

    def get(
        self,
        message_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get one message by its ID. The same route as messages.get_message.

        Args:
            message_id: The message ID.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the message; an unknown ID is a 404.

        Raises:
            SignalHouseValidationError: If message_id is missing.
        """
        self._sdk._require({"messageId": message_id})
        safe_message_id = quote(str(message_id), safe="")
        return self._sdk._request(
            f"/message/{safe_message_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        group_id: str,
        from_: str,
        to: str,
        agent_id: str | None = None,
        status: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        template_id: str | None = None,
        template_version: int | None = None,
        bulk_id: str | None = None,
        fallback_reason: str | None = None,
        billing_class: str | None = None,
        delivered_channel: str | None = None,
        is_test: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List RCS messages. Sends GET /message with messageType RCS.

        A fallback leg is an SMS or MMS message: read it with messages.get_message and the parent's fallbackMessageId.

        Args:
            group_id: The group whose messages to list.
            from_: ISO-8601 date or timestamp; sent as startDate. Trailing underscore avoids the Python keyword.
            to: ISO-8601 date or timestamp; sent as endDate.
            agent_id: Messages this agent sent; sent as registrationId.
            status: ENQUEUED, DEQUEUED, SENT, FAILED, DELIVERED, READ, EXPIRED, FALLBACK or BLOCKED.
            page: The page number.
            limit: Messages per page.
            template_id: Messages sent from this template.
            template_version: Messages sent from this template version.
            bulk_id: Messages of one send.
            fallback_reason: NOT_CAPABLE, CARRIER_NOT_LAUNCHED, TTL_EXPIRED, RCS_ERROR, PROVIDER_ERROR or SMS_ONLY.
            billing_class: RICH or RICH_MEDIA.
            delivered_channel: The channel that delivered the message: rcs, sms or mms.
            is_test: True for test messages only, False to leave them out.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id, from_ or to is missing.
        """
        self._sdk._require({"groupId": group_id, "from": from_, "to": to})
        query_string = self._sdk._get_query_string({
            "registrationId": agent_id,
            "startDate": from_,
            "endDate": to,
            "groupId": group_id,
            "status": status,
            "page": page,
            "limit": limit,
            "templateId": template_id,
            "templateVersion": template_version,
            "bulkId": bulk_id,
            "fallbackReason": fallback_reason,
            "billingClass": billing_class,
            "deliveredChannel": delivered_channel,
            "isTest": None if is_test is None else str(is_test).lower(),
            "messageType": "RCS",
        })
        return self._sdk._request(
            f"/message{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def _post(
        self,
        path: str,
        fields: dict[str, Any],
        token: str | None,
        headers: dict[str, str] | None,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        """POST a JSON body, leaving out the fields that are None.

        Args:
            path: The request path.
            fields: The body fields.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header.

        Returns:
            Standardized response dict.
        """
        return self._sdk._request(
            path,
            method="POST",
            body={key: value for key, value in fields.items() if value is not None},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Rcs:
    """RCS (Google RBM) resources, accessed via ``sdk.rcs``. Templates for RCS live under ``sdk.templates``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.agents = RcsAgents(sdk)
        self.messages = RcsMessages(sdk)
