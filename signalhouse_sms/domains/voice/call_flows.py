"""Call Flows — customer-built call trees a number or profile can run.

A call flow is a graph of steps (greeting, menu, forward, voicemail, hang up) that runs
when a number's route, or its Programmable Voice Profile, names it with
``routeAction: "CALL_FLOW"``. Each flow has one working draft you edit with
``save_draft``, and published versions: ``publish`` validates the draft and makes it the
version calls run, while the draft stays editable without affecting calls.

Routes are mounted under /voice/api/v1/call-flows on the Voice service.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class CallFlows:
    """Call flow management. Accessed via ``sdk.voice.call_flows``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        q: str | None = None,
        subgroup_id: str | None = None,
        include_deleted: bool | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the account's call flows, newest first by default.
        ``GET /voice/api/v1/call-flows``.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            limit: Page size (1-100). Defaults to 20.
            q: Match against the flow name.
            subgroup_id: Only flows in this subgroup. Serialized as ``subgroupId``.
            include_deleted: Include deleted flows. Serialized as ``includeDeleted``.
            sort_by: ``createdAt`` (default), ``updatedAt`` or ``name``. Serialized as ``sortBy``.
            sort_order: ``asc`` or ``desc`` (default). Serialized as ``sortOrder``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header.

        Returns:
            ``{ "data": [...], "meta": { "total", "page", "limit", "totalPages" } }``.
        """
        query_string = self._sdk._get_query_string({
            "page": page,
            "limit": limit,
            "q": q,
            "subgroupId": subgroup_id,
            # Lowercase on purpose: the shared helper would send Python's "True", and the
            # Voice service accepts only "true"/"false" for a boolean query parameter.
            "includeDeleted": None if include_deleted is None else ("true" if include_deleted else "false"),
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })
        return self._sdk._request(
            f"/voice/api/v1/call-flows{query_string}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def catalog(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the step types this service can run, with the outcomes each one offers.
        ``GET /voice/api/v1/call-flows/catalog``.
        Returns ``{ "data": { "nodeTypes": [{ "type", "ports", "configurable" }] } }``."""
        return self._sdk._request(
            "/voice/api/v1/call-flows/catalog", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def get(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a call flow with its working draft and the issues that stop it being published.
        ``GET /voice/api/v1/call-flows/:id``.
        Returns ``{ "data": { ...flow, "draft": { "versionId", "nodes", "edges", "issues" } } }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def create(
        self,
        flow_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a call flow, with its working draft and the Inbound Call step every flow
        starts from. ``POST /voice/api/v1/call-flows``.

        ``flow_data`` keys (camelCase, as the API expects): ``name`` (required, unique
        within the subgroup) and ``subgroupId`` (required). The subgroup is fixed once
        created; only numbers and Programmable Voice Profiles in it can run the flow.
        Returns ``{ "data": { ...flow, "draft": {...} } }``."""
        self._sdk._require({"flowData": flow_data})
        return self._sdk._request(
            "/voice/api/v1/call-flows", method="POST", body=flow_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def update(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Rename a call flow, or enable or disable it (partial update).
        ``PATCH /voice/api/v1/call-flows/:id``.

        ``update_data`` keys: ``name``, ``status`` (``ACTIVE`` or ``DISABLED``; a disabled
        flow does not run, and numbers routed to it fall through to their next routing
        layer). Returns ``{ "data": { ...flow, "draft": {...} } }``."""
        self._sdk._require({"id": id, "updateData": update_data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}", method="PATCH", body=update_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def delete(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a call flow. Reversible with ``restore``: while deleted, numbers and
        profiles routed to it fall through to their next routing layer.
        ``DELETE /voice/api/v1/call-flows/:id``. Returns ``{ "data": { ...flow } }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}", method="DELETE", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def restore(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Restore a deleted call flow. ``POST /voice/api/v1/call-flows/:id/restore``.

        Sends an empty JSON body: the client always declares JSON, and the Voice service
        rejects a JSON request with no body at all. Returns ``{ "data": { ...flow, "draft": {...} } }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}/restore", method="POST", body={}, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def duplicate(
        self,
        id: str,
        *,
        name: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Copy a call flow and its working draft into a new flow in the same subgroup. The
        copy is not published. ``POST /voice/api/v1/call-flows/:id/duplicate``.

        Args:
            id: The call flow to copy.
            name: Name for the copy. Defaults to ``"<name> (copy)"``.

        Returns ``{ "data": { ...flow, "draft": {...} } }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}/duplicate",
            method="POST",
            body={"name": name} if name else {},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def save_draft(
        self,
        id: str,
        draft: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Replace the working draft. ``PUT /voice/api/v1/call-flows/:id/draft``.

        ``draft`` is ``{ "nodes": [...], "edges": [...] }``. Each node is ``{ id, type,
        name, config, positionX, positionY }`` and each edge ``{ id, fromNodeId, toNodeId,
        port }``; ids are UUIDs you generate and are kept across saves. The whole draft is
        saved even when it is not finished, and the issues that would stop it being
        published come back in the response.
        Returns ``{ "data": { "nodes", "edges", "issues" } }``."""
        self._sdk._require({"id": id, "draft": draft})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}/draft", method="PUT", body=draft, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def publish(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Publish the working draft, making it the version calls run.
        ``POST /voice/api/v1/call-flows/:id/publish``. A draft that is not ready returns
        400 with ``error.issues`` listing each step that needs attention.

        Sends an empty JSON body: the client always declares JSON, and the Voice service
        rejects a JSON request with no body at all.
        Returns ``{ "data": { "id", "versionNumber", "status", "publishedAt" } }``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/api/v1/call-flows/{safe_id}/publish", method="POST", body={}, token=token, headers=headers, idempotency_key=idempotency_key,
        )
