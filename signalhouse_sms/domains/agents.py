"""AI Agents domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Agents:
    """AI Agent profile management operations (customer-facing /agent domain).

    Agent profiles hold the configuration for an AI agent: its name, prompts,
    guardrails, voice, and LLM backend. Profiles are scoped to a group (and
    optionally a subgroup); that scope is immutable after creation.
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_agent_voices(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the voices an agent can be configured to speak with.

        The catalog is platform-wide, not per-account, so this takes no scope.
        `voiceId` is the value to set on a spoken channel's setting.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is a list of voices, each
            {voiceId, name, description, previewUrl, gender, accent, age, useCase, language}.
        """
        return self._sdk._request("/agent/voices", method="GET", token=token, headers=headers, idempotency_key=idempotency_key)

    def get_agent_profiles(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the agent profiles under a group.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            group_id: The group whose profiles to list (required).
            subgroup_id: Narrow to the agents this subgroup can use — its own, plus the group-level agents shared with every subgroup.
            page: The page number for pagination.
            limit: The number of items per page.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/agent/profiles{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_profile(
        self,
        agent_profile_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single agent profile by ID.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_profile_id: The ID of the agent profile to fetch.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_profile_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id})
        safe_id = quote(str(agent_profile_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_agent_profile(
        self,
        profile_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new agent profile.

        Allowed roles: api, admin, developer.

        Args:
            profile_data: The data for the agent profile to create. Required fields:
                groupId (str, starts with 'G') and name (str). Optional fields:
                subgroupId (str, starts with 'S', null = group-level agent),
                status ("active" | "inactive", defaults to "active"), systemPrompt,
                greeting, guardrails, and sendAuthority ("review" | "autopilot",
                defaults to "review"; deployments may override it per subgroup).
                publishStatus and publishedAt are read-only and change only through
                publish_agent_profile and unpublish_agent_profile. Model, voice and
                sampling settings are per-channel and live on the channel setting,
                not here.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If profile_data is missing.
        """
        self._sdk._require({"profileData": profile_data})
        return self._sdk._request(
            "/agent/profiles",
            method="POST",
            body=profile_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_agent_profile(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing agent profile.

        Allowed roles: api, admin, developer.

        Args:
            id: The ID of the agent profile to update.
            update_data: The fields to update. All create fields are accepted except
                groupId and subgroupId — the agent's scope is immutable. Updatable
                fields: name, status ("active" | "inactive"), systemPrompt, greeting,
                guardrails, and sendAuthority ("review" | "autopilot"). publishStatus
                and publishedAt are read-only and change only through
                publish_agent_profile and unpublish_agent_profile. Model, voice and
                sampling settings are per-channel and live on the channel setting,
                not here.
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
            f"/agent/profiles/{safe_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_agent_profile(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Permanently delete an agent profile by its ID.

        Permanently deletes the agent, its channel settings, and any tools and knowledge scoped to it, plus their provider-side counterparts. Tools and knowledge shared across the account are untouched. Conversation records survive — a transcript outlives the agent that produced it.

        Allowed roles: api, admin, developer.

        Args:
            id: The ID of the agent profile to delete.
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
            f"/agent/profiles/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_agent_message(
        self,
        *,
        agent_profile_id: str,
        channel: str,
        message: str,
        conversation_id: str | None = None,
        contact_identifier: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send a message to an agent and get its reply (webchat / SMS).

        Omit conversation_id to start a new conversation, or pass one to continue an
        existing one. Runs the agent's LLM tool loop server-side and returns the
        assistant's reply along with any tools it invoked.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_profile_id: The agent to talk to (required).
            channel: The channel: "webchat", "sms", or "voice" (required).
            message: The user's message (required).
            conversation_id: Continue this conversation; omit to start a new one.
            contact_identifier: The far-end identifier (webchat visitor id, sender number).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with conversationId, conversationSessionId,
            reply, toolInvocations, and ok.

        Raises:
            SignalHouseValidationError: If agent_profile_id, channel, or message is missing.
        """
        self._sdk._require({
            "agentProfileId": agent_profile_id,
            "channel": channel,
            "message": message,
        })
        body: dict[str, Any] = {
            "agentProfileId": agent_profile_id,
            "channel": channel,
            "message": message,
        }
        if conversation_id is not None:
            body["conversationId"] = conversation_id
        if contact_identifier is not None:
            body["contactIdentifier"] = contact_identifier
        return self._sdk._request(
            "/agent/messages",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def start_conversation(
        self,
        *,
        agent_profile_id: str,
        channel: str,
        contact_identifier: str | None = None,
        call_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Start a conversation without sending a message.

        The counterpart to send_agent_message for callers that run the model
        themselves — a voice runtime, or your own LLM. Those record what was said;
        send_agent_message decides it. Both write the same conversation records.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_profile_id: The agent this conversation belongs to (required).
            channel: The channel: "webchat", "sms", or "voice" (required).
            contact_identifier: The far-end identifier (visitor id, caller number).
            call_id: Telephony call id, for the voice channel.
            metadata: Arbitrary metadata stored with the conversation.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            The created conversation, including conversationId and conversationSessionId.

        Raises:
            SignalHouseValidationError: If agent_profile_id or channel is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id, "channel": channel})
        body: dict[str, Any] = {"agentProfileId": agent_profile_id, "channel": channel}
        if contact_identifier is not None:
            body["contactIdentifier"] = contact_identifier
        if call_id is not None:
            body["callId"] = call_id
        if metadata is not None:
            body["metadata"] = metadata
        return self._sdk._request("/agent/conversations", method="POST", body=body, token=token, headers=headers, idempotency_key=idempotency_key)

    def get_conversation(
        self,
        *,
        conversation_id: str,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Read one conversation with a page of its messages, in order.

        Paged rather than whole: a transcript has no natural ceiling. Omitting
        limit gives 100 messages, not all of them.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            conversation_id: The conversation to read (required).
            page: Page number; defaults to 1.
            limit: Messages per page; defaults to 100, capped at 500.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            A one-element list with the conversation and its messages.

        Raises:
            SignalHouseValidationError: If conversation_id is missing.
        """
        self._sdk._require({"conversationId": conversation_id})
        safe_id = quote(str(conversation_id), safe="")
        query_string = self._sdk._get_query_string({"page": page, "limit": limit})
        return self._sdk._request(f"/agent/conversations/{safe_id}{query_string}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key)

    def append_conversation_message(
        self,
        *,
        conversation_id: str,
        role: str,
        content: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        tool_results: list[dict[str, Any]] | None = None,
        ttfb_ms: int | None = None,
        latency_ms: int | None = None,
        barge_in_occurred: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Append one message to a conversation.

        Records a turn rather than generating one, so role is explicit — an assistant
        turn your own runtime produced is the normal case here. content is optional so
        a tool-only turn needs no prose.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            conversation_id: The conversation to append to (required).
            role: "user", "assistant", "system", or "tool" (required).
            content: What was said.
            tool_calls: Tools invoked on this turn.
            tool_results: Their results.
            ttfb_ms: Time to first byte/audio, in milliseconds.
            latency_ms: Total turn latency, in milliseconds.
            barge_in_occurred: Whether the far end talked over this turn.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            The persisted message.

        Raises:
            SignalHouseValidationError: If conversation_id or role is missing.
        """
        self._sdk._require({"conversationId": conversation_id, "role": role})
        safe_id = quote(str(conversation_id), safe="")
        body: dict[str, Any] = {"role": role}
        if content is not None:
            body["content"] = content
        if tool_calls is not None:
            body["toolCalls"] = tool_calls
        if tool_results is not None:
            body["toolResults"] = tool_results
        if ttfb_ms is not None:
            body["ttfbMs"] = ttfb_ms
        if latency_ms is not None:
            body["latencyMs"] = latency_ms
        if barge_in_occurred is not None:
            body["bargeInOccurred"] = barge_in_occurred
        return self._sdk._request(f"/agent/conversations/{safe_id}/messages", method="POST", body=body, token=token, headers=headers, idempotency_key=idempotency_key)

    def end_conversation(
        self,
        *,
        conversation_id: str,
        status: str | None = None,
        metadata: dict[str, Any] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """End a conversation, closing its open session.

        status records HOW it ended and cannot be recovered afterwards, so pass the one
        that actually happened. Ending an already-ended conversation is a no-op, so a
        retry after a dropped connection cannot overwrite it.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            conversation_id: The conversation to end (required).
            status: "completed", "escalated", or "abandoned" (defaults to "completed").
            metadata: Metadata merged onto the conversation.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            The ended conversation.

        Raises:
            SignalHouseValidationError: If conversation_id is missing.
        """
        self._sdk._require({"conversationId": conversation_id})
        safe_id = quote(str(conversation_id), safe="")
        body: dict[str, Any] = {}
        if status is not None:
            body["status"] = status
        if metadata is not None:
            body["metadata"] = metadata
        return self._sdk._request(f"/agent/conversations/{safe_id}", method="PUT", body=body, token=token, headers=headers, idempotency_key=idempotency_key)

    def get_agent_channel_settings(
        self,
        agent_profile_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List an agent's per-channel settings.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_profile_id: The agent whose channel settings to list.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_profile_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id})
        safe_id = quote(str(agent_profile_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/channels",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_channel_setting(
        self,
        agent_profile_id: str,
        channel: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single per-channel setting for an agent.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_profile_id: The agent the setting belongs to.
            channel: The channel — "webchat", "sms", or "voice".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_profile_id or channel is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id, "channel": channel})
        safe_id = quote(str(agent_profile_id), safe="")
        safe_channel = quote(str(channel), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/channels/{safe_channel}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upsert_agent_channel_setting(
        self,
        agent_profile_id: str,
        channel: str,
        setting_data: dict[str, Any] | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create or update (upsert) an agent's per-channel setting.

        One row per (agent, channel); the channel comes from the path.

        Allowed roles: api, admin, developer.

        Args:
            agent_profile_id: The agent the setting belongs to.
            channel: The channel — "webchat", "sms", or "voice".
            setting_data: Fields to set: allowedTools (list[str]), enabled (bool),
                channelPrompt (str), greeting (str | None), llmProvider ("bedrock" |
                "openai" | "anthropic" | "groq", defaults to "bedrock"), llmModel
                (str | None), temperature (0-2), and voiceId (str | None). Model
                settings are per-channel because each channel is served by a
                different runtime.

                Spoken channels also accept: speed (0.7-1.2), stability (0-1),
                similarityBoost (0-1), speechModel (str — how the agent is voiced,
                chosen independently of llmModel), turnEagerness ("patient" |
                "normal" | "eager"), turnTimeoutSeconds and initialWaitSeconds
                (1-300, or -1 for no timeout), silenceEndCallSeconds (10-7200),
                maxCallDurationSeconds (60-7200), allowGreetingInterruption (bool),
                keyterms (list[str] the transcriber is biased toward), and
                backgroundSound ({"preset": str, "volume": 0.01-1} | None), and
                workflow (the conversation workflow graph: "nodes" and "edges" keyed
                dicts, plus optional "subgraphs" and "prevent_subagent_loops"; node
                bodies are defined by the voice runtime and passed through as-is).
                workflow is accepted on the voice channel only — sending one on
                webchat or sms is a 400; None clears it.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_profile_id or channel is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id, "channel": channel})
        safe_id = quote(str(agent_profile_id), safe="")
        safe_channel = quote(str(channel), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/channels/{safe_channel}",
            method="PUT",
            body=setting_data or {},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_agent_channel_setting(
        self,
        agent_profile_id: str,
        channel: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete an agent's per-channel setting.

        Allowed roles: api, admin, developer.

        Args:
            agent_profile_id: The agent the setting belongs to.
            channel: The channel — "webchat", "sms", or "voice".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_profile_id or channel is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id, "channel": channel})
        safe_id = quote(str(agent_profile_id), safe="")
        safe_channel = quote(str(channel), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/channels/{safe_channel}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_deployments(
        self,
        agent_profile_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List a group-level agent's deployments to subgroups.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_profile_id: The agent whose deployments to list.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. Each deployment carries agentDeploymentId,
            groupId, subgroupId, agentProfileId, sendAuthorityOverride,
            sendAuthorityChangedBy, sendAuthorityChangedAt, enabled, createdAt,
            and updatedAt.

        Raises:
            SignalHouseValidationError: If agent_profile_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id})
        safe_id = quote(str(agent_profile_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/deployments",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upsert_agent_deployment(
        self,
        agent_profile_id: str,
        subgroup_id: str,
        deployment_data: dict[str, Any] | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Deploy a group-level agent to a subgroup, or change that deployment (upsert).

        One row per (agent, subgroup); the subgroup comes from the path.

        Allowed roles: api, admin, developer.

        Args:
            agent_profile_id: The agent to deploy.
            subgroup_id: The subgroup to deploy to (starts with 'S').
            deployment_data: Fields to set: sendAuthorityOverride ("review" |
                "autopilot" | None; None clears the override so the deployment
                inherits the profile default) and enabled (bool, defaults to True).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the created or updated deployment.

        Raises:
            SignalHouseValidationError: If agent_profile_id or subgroup_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id, "subgroupId": subgroup_id})
        safe_id = quote(str(agent_profile_id), safe="")
        safe_subgroup_id = quote(str(subgroup_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/deployments/{safe_subgroup_id}",
            method="PUT",
            body=deployment_data or {},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_agent_deployment(
        self,
        agent_profile_id: str,
        subgroup_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove an agent's deployment from a subgroup.

        Allowed roles: api, admin, developer.

        Args:
            agent_profile_id: The deployed agent.
            subgroup_id: The subgroup to remove the deployment from.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the removed deployment.

        Raises:
            SignalHouseValidationError: If agent_profile_id or subgroup_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id, "subgroupId": subgroup_id})
        safe_id = quote(str(agent_profile_id), safe="")
        safe_subgroup_id = quote(str(subgroup_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/deployments/{safe_subgroup_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_endpoints(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        agent_profile_id: str | None = None,
        channel: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the endpoint bindings (which agent answers which number) in a group.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            group_id: The group whose bindings to list (required).
            subgroup_id: Narrow to one subgroup's bindings.
            agent_profile_id: Narrow to one agent's bindings.
            channel: Narrow to one channel ("sms").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is a list of bindings, ordered by
            number. Each binding carries agentEndpointId, groupId, subgroupId,
            channel, endpointType, endpointValue, agentProfileId, answerMode,
            overrides, enabled, createdAt, and updatedAt.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "agentProfileId": agent_profile_id,
            "channel": channel,
        })
        return self._sdk._request(
            f"/agent/endpoints{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upsert_agent_endpoint(
        self,
        channel: str,
        endpoint_value: str,
        endpoint_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Assign an agent to answer a number (upsert keyed by channel + number).

        Assigning again replaces the previous agent, so a number has one agent
        per channel. Only SMS numbers can be bound.

        Allowed roles: api, admin, developer.

        Args:
            channel: The channel to bind; must be "sms".
            endpoint_value: The phone number: 10 to 15 digits, country code
                included, no "+".
            endpoint_data: agentProfileId (required; the agent must be active, in
                the number's group, and either belong to the number's subgroup or
                be a group-level agent with an enabled deployment there) and
                answerMode (optional; "all_inbound", the default).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the created or updated binding.

        Raises:
            SignalHouseValidationError: If channel, endpoint_value, or endpoint_data's agentProfileId is missing.
        """
        self._sdk._require({
            "channel": channel,
            "endpointValue": endpoint_value,
            "agentProfileId": (endpoint_data or {}).get("agentProfileId"),
        })
        safe_channel = quote(str(channel), safe="")
        safe_endpoint_value = quote(str(endpoint_value), safe="")
        return self._sdk._request(
            f"/agent/endpoints/{safe_channel}/{safe_endpoint_value}",
            method="PUT",
            body=endpoint_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_agent_endpoint(
        self,
        channel: str,
        endpoint_value: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove the agent assigned to a number.

        Allowed roles: api, admin, developer.

        Args:
            channel: The bound channel; must be "sms".
            endpoint_value: The phone number: digits only, country code included, no "+".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the removed binding.

        Raises:
            SignalHouseValidationError: If channel or endpoint_value is missing.
        """
        self._sdk._require({"channel": channel, "endpointValue": endpoint_value})
        safe_channel = quote(str(channel), safe="")
        safe_endpoint_value = quote(str(endpoint_value), safe="")
        return self._sdk._request(
            f"/agent/endpoints/{safe_channel}/{safe_endpoint_value}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_reply_drafts(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        agent_profile_id: str | None = None,
        status: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List held agent replies (the Pending Replies queue) in a group, newest first.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            group_id: The group whose drafts to list (required).
            subgroup_id: Narrow to one subgroup.
            agent_profile_id: Narrow to one agent.
            status: Narrow to one status: "pending", "sending", "sent",
                "rejected" or "failed".
            page: The page number for pagination.
            limit: Items per page (default 25, max 500).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is a list of drafts, newest
            first. Each draft carries agentReplyDraftId, groupId, subgroupId,
            agentProfileId, conversationId, channel, endpointValue,
            contactPhoneNumber, inboundText, draftText, sentText, reason,
            status, decidedBy, decidedAt, sentMessageId, deliveredBy
            ("signalhouse" or "external"; None until decided), failureReason
            ("delivery_unconfirmed" or None), claimId (the current claim's
            id; None until claimed), createdAt, and updatedAt.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "agentProfileId": agent_profile_id,
            "status": status,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/agent/drafts{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def approve_agent_reply_draft(
        self,
        agent_reply_draft_id: str,
        *,
        text: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Approve a held agent reply and send it from the agent's number.

        The reply goes through the normal SMS send path, so opt-out and billing
        apply; the draft comes back "failed" when the send path accepted
        nothing. A draft that is no longer pending returns 409.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_reply_draft_id: The draft to approve.
            text: Replacement text when a person edited the reply (1 to 10000
                characters). Omit to send the agent's draft as written.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the draft, now "sent" (or "failed").

        Raises:
            SignalHouseValidationError: If agent_reply_draft_id is missing.
        """
        self._sdk._require({"agentReplyDraftId": agent_reply_draft_id})
        safe_id = quote(str(agent_reply_draft_id), safe="")
        body: dict[str, Any] = {} if text is None else {"text": text}
        return self._sdk._request(
            f"/agent/drafts/{safe_id}/approve",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reject_agent_reply_draft(
        self,
        agent_reply_draft_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reject a held agent reply so it is never sent.

        A draft that is no longer pending returns 409.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_reply_draft_id: The draft to reject.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the rejected draft.

        Raises:
            SignalHouseValidationError: If agent_reply_draft_id is missing.
        """
        self._sdk._require({"agentReplyDraftId": agent_reply_draft_id})
        safe_id = quote(str(agent_reply_draft_id), safe="")
        return self._sdk._request(
            f"/agent/drafts/{safe_id}/reject",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def claim_agent_reply_draft(
        self,
        agent_reply_draft_id: str,
        *,
        text: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Claim a held agent reply for delivery through your own channel.

        Nothing is sent: the draft becomes "sending" with deliveredBy
        "external", sentText and a new claimId set, and you then report the
        outcome with complete_agent_reply_draft or release_agent_reply_draft,
        passing that claimId back. The claim
        means two approvals can never both deliver. A draft that is no longer
        pending returns 409; one whose number has left its subgroup returns
        400 and is closed as failed.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_reply_draft_id: The draft to claim.
            text: Replacement text when a person edited the reply (1 to 10000
                characters). Omit to claim the agent's draft as written.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the claimed draft, including its
            claimId.

        Raises:
            SignalHouseValidationError: If agent_reply_draft_id is missing.
        """
        self._sdk._require({"agentReplyDraftId": agent_reply_draft_id})
        safe_id = quote(str(agent_reply_draft_id), safe="")
        body: dict[str, Any] = {} if text is None else {"text": text}
        return self._sdk._request(
            f"/agent/drafts/{safe_id}/claim",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def complete_agent_reply_draft(
        self,
        agent_reply_draft_id: str,
        claim_id: str,
        *,
        external_message_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Mark a claimed agent reply sent once your channel accepted it.

        Only the claim named by claim_id can be completed; anything else
        returns 409. It is also accepted after an unfinished claim was closed
        as "failed" with failureReason "delivery_unconfirmed", which it turns
        into "sent".

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_reply_draft_id: The claimed draft.
            claim_id: The claim being completed, as returned by
                claim_agent_reply_draft.
            external_message_id: Your channel's id for the sent message (up to
                256 characters), stored as sentMessageId.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the draft, now "sent".

        Raises:
            SignalHouseValidationError: If agent_reply_draft_id or claim_id is
                missing.
        """
        self._sdk._require({"agentReplyDraftId": agent_reply_draft_id, "claimId": claim_id})
        safe_id = quote(str(agent_reply_draft_id), safe="")
        body: dict[str, Any] = {"claimId": claim_id}
        if external_message_id is not None:
            body["externalMessageId"] = external_message_id
        return self._sdk._request(
            f"/agent/drafts/{safe_id}/complete",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def release_agent_reply_draft(
        self,
        agent_reply_draft_id: str,
        claim_id: str,
        *,
        permanent: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Give back a claim whose reply certainly did not go out.

        The draft returns to "pending", or with permanent is closed as
        "failed". If you cannot tell whether it went out, do not release it;
        a claim left unfinished for 30 minutes is closed as failed with
        failureReason "delivery_unconfirmed". Only the claim named by
        claim_id can be released; anything else returns 409.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_reply_draft_id: The claimed draft.
            claim_id: The claim being released, as returned by
                claim_agent_reply_draft.
            permanent: True closes the draft as failed instead of returning it
                to pending.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the draft, "pending" again or "failed".

        Raises:
            SignalHouseValidationError: If agent_reply_draft_id or claim_id is
                missing.
        """
        self._sdk._require({"agentReplyDraftId": agent_reply_draft_id, "claimId": claim_id})
        safe_id = quote(str(agent_reply_draft_id), safe="")
        body: dict[str, Any] = {"claimId": claim_id}
        if permanent is not None:
            body["permanent"] = permanent
        return self._sdk._request(
            f"/agent/drafts/{safe_id}/release",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def publish_agent_profile(
        self,
        agent_profile_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Publish an agent profile.

        Sets publishStatus to "published" and stamps publishedAt. The server
        rejects the call with 400 when the agent has no enabled deployment, and
        with 409 when the agent is inactive.

        Allowed roles: api, admin, developer.

        Args:
            agent_profile_id: The agent profile to publish.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the published agent profile.

        Raises:
            SignalHouseValidationError: If agent_profile_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id})
        safe_id = quote(str(agent_profile_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/publish",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def unpublish_agent_profile(
        self,
        agent_profile_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Return an agent profile to draft (publishStatus "draft").

        Allowed roles: api, admin, developer.

        Args:
            agent_profile_id: The agent profile to unpublish.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with the unpublished agent profile.

        Raises:
            SignalHouseValidationError: If agent_profile_id is missing.
        """
        self._sdk._require({"agentProfileId": agent_profile_id})
        safe_id = quote(str(agent_profile_id), safe="")
        return self._sdk._request(
            f"/agent/profiles/{safe_id}/unpublish",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_tenant_ai_settings(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Read the tenant AI settings for a scope (group, or a subgroup within it).

        Returns the scope's own row only — no group-level fallback.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            group_id: The group (required).
            subgroup_id: The subgroup; omit for the group-level settings.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id, "subgroupId": subgroup_id})
        return self._sdk._request(
            f"/agent/tenant-settings{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upsert_tenant_ai_settings(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        settings_data: dict[str, Any] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create or update (upsert) the tenant AI settings for a scope.

        The scope is identified by the query params; the body carries the fields.

        Allowed roles: api, admin, developer.

        Args:
            group_id: The group (required).
            subgroup_id: The subgroup; omit for the group-level settings.
            settings_data: Fields to set: brandName (str), tone (str), timezone (IANA str),
                businessHours (list of {day, closed, open, close}), afterHoursMessage (str).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id, "subgroupId": subgroup_id})
        return self._sdk._request(
            f"/agent/tenant-settings{query_string}",
            method="PUT",
            body=settings_data or {},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_tenant_ai_settings(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete the tenant AI settings for a scope.

        Allowed roles: api, admin, developer.

        Args:
            group_id: The group (required).
            subgroup_id: The subgroup; omit for the group-level settings.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id, "subgroupId": subgroup_id})
        return self._sdk._request(
            f"/agent/tenant-settings{query_string}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_knowledge_items(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        agent_profile_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the knowledge-base items an agent can answer from (RAG).

        Scoped to a group, optionally narrowed to a subgroup and/or a single agent.
        Paginated: results are bounded (server default 25 per page, max 100).

        Allowed roles: api, admin, developer, billing, user.

        Args:
            group_id: The group whose knowledge to list (required).
            subgroup_id: Narrow to a subgroup.
            agent_profile_id: Narrow to one agent.
            page: Page number (1-based) for pagination.
            limit: Items per page (max 100; server default 25).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id, "subgroupId": subgroup_id, "agentProfileId": agent_profile_id, "page": page, "limit": limit})
        return self._sdk._request(
            f"/agent/knowledge{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_knowledge_item(
        self,
        knowledge_item_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single knowledge item by ID.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            knowledge_item_id: The ID of the knowledge item to fetch.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If knowledge_item_id is missing.
        """
        self._sdk._require({"knowledgeItemId": knowledge_item_id})
        safe_id = quote(str(knowledge_item_id), safe="")
        return self._sdk._request(
            f"/agent/knowledge/{safe_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_knowledge_item(
        self,
        item_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a knowledge item. The raw text is stored; Atlas Vector Search owns the embedding.

        Allowed roles: api, admin, developer.

        Args:
            item_data: The knowledge fields. Required: groupId (starts with 'G'), text.
                Optional: subgroupId (starts with 'S', nullable), agentProfileId (nullable =
                shared across the tenant's agents), title, source ("manual" | "url" |
                "document" | "import"), enabled (bool), metadata (dict | None).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If item_data is missing.
        """
        self._sdk._require({"itemData": item_data})
        return self._sdk._request(
            "/agent/knowledge",
            method="POST",
            body=item_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_knowledge_item(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update a knowledge item. The scope (group/subgroup/agent) is immutable.

        Allowed roles: api, admin, developer.

        Args:
            id: The ID of the knowledge item to update.
            update_data: The fields to update: title, text, source, enabled, metadata.
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
            f"/agent/knowledge/{safe_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_knowledge_item(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a knowledge item by its ID.

        Allowed roles: api, admin, developer.

        Args:
            id: The ID of the knowledge item to delete.
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
            f"/agent/knowledge/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_tools(
        self,
        *,
        group_id: str,
        subgroup_id: str | None = None,
        agent_profile_id: str | None = None,
        type: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the tools defined under a group (webhook, configured builtin, mcp).

        webhookAuth secrets are redacted in the response. Paginated (default 25, max 100).

        Allowed roles: api, admin, developer, billing, user.

        Args:
            group_id: The group whose tools to list (required).
            subgroup_id: Narrow to a subgroup.
            agent_profile_id: Narrow to one agent.
            type: Narrow to a tool type — "builtin", "webhook", or "mcp".
            page: Page number (1-based) for pagination.
            limit: Items per page (max 100; server default 25).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id, "subgroupId": subgroup_id, "agentProfileId": agent_profile_id, "type": type, "page": page, "limit": limit})
        return self._sdk._request(
            f"/agent/tools{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_agent_tool(
        self,
        agent_tool_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single agent tool by ID. webhookAuth secrets are redacted.

        Allowed roles: api, admin, developer, billing, user.

        Args:
            agent_tool_id: The ID of the tool to fetch.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If agent_tool_id is missing.
        """
        self._sdk._require({"agentToolId": agent_tool_id})
        safe_id = quote(str(agent_tool_id), safe="")
        return self._sdk._request(
            f"/agent/tools/{safe_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_agent_tool(
        self,
        tool_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create an agent tool. A webhook tool's webhookUrl must be an https URL that does not
        target a private/internal address. webhookAuth is stored and never echoed back.

        Allowed roles: api, admin, developer.

        Args:
            tool_data: The tool fields. Required: groupId (starts with 'G'), name, description.
                Type-specific: type ("builtin" | "webhook" | "mcp"); webhook -> webhookUrl,
                builtin -> builtinKey, mcp -> mcpServerUrl. Optional: subgroupId, agentProfileId
                (nullable), parametersSchema, config, channels, enabled, and webhookAuth — which
                MUST be {"headers"?: {name: value}, "signingSecret"?: str} (any other shape, e.g.
                {"header", "value"}, is rejected with a 400). headers are sent verbatim on every
                call (reserved/framing and x-signalhouse-* names are rejected); signingSecret makes
                us send X-SignalHouse-Signature: sha256=HMAC-SHA256(f"{X-SignalHouse-Timestamp}.{rawBody}")
                so you can verify the call and reject replays. Stored, never returned.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If tool_data is missing.
        """
        self._sdk._require({"toolData": tool_data})
        return self._sdk._request(
            "/agent/tools",
            method="POST",
            body=tool_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_agent_tool(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an agent tool. The scope is immutable; a supplied webhookUrl is SSRF-checked.

        Allowed roles: api, admin, developer.

        Args:
            id: The ID of the tool to update.
            update_data: The fields to update: name, description, type, builtinKey,
                parametersSchema, config, webhookUrl, webhookAuth, mcpServerUrl, channels, enabled.
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
            f"/agent/tools/{safe_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_agent_tool(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete an agent tool by its ID.

        Allowed roles: api, admin, developer.

        Args:
            id: The ID of the tool to delete.
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
            f"/agent/tools/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
