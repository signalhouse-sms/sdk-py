"""Tickets domain for the SignalHouse SDK (staff-only customer tickets → Jira)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class TicketsAdmin:
    """Admin-only customer ticket operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_jira_metadata(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Load Jira form metadata (issue types, priorities, active sprint, field IDs). Staff-only.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with Jira form metadata.
        """
        return self._sdk._request(
            "/admin/ticket/jira/metadata",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def search_jira_epics(
        self,
        *,
        query: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Search open epics for the parent picker. Staff-only.

        Args:
            query: Optional epic summary/key filter.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with `{ epics: [...] }`.
        """
        query_string = self._sdk._get_query_string({"query": query})
        return self._sdk._request(
            f"/admin/ticket/jira/epics{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def search_jira_parent_issues(
        self,
        *,
        query: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Search open non-Epic, non-Subtask issues for the Subtask parent picker. Staff-only.

        Args:
            query: Optional issue summary/key filter.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with `{ issues: [...] }`.
        """
        query_string = self._sdk._get_query_string({"query": query})
        return self._sdk._request(
            f"/admin/ticket/jira/parent-issues{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def search_jira_assignees(
        self,
        *,
        query: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Search assignable Jira users for the assignee picker. Staff-only.

        Args:
            query: Partial name or email.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with `{ users: [...] }`.
        """
        query_string = self._sdk._get_query_string({"query": query})
        return self._sdk._request(
            f"/admin/ticket/jira/assignees{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def search_jira_labels(
        self,
        *,
        query: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Suggest Jira labels matching a query. Staff-only.

        Args:
            query: Partial label text.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with `{ labels: [...] }`.
        """
        query_string = self._sdk._get_query_string({"query": query})
        return self._sdk._request(
            f"/admin/ticket/jira/labels{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_jira_ticket(
        self,
        data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a Jira ticket from the admin customer ticket form. Staff-only.

        Args:
            data: Create payload. Required fields include groupId, issueTypeId,
                  priorityId, and summary.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with created ticket summary.

        Raises:
            SignalHouseValidationError: If data is missing.
        """
        self._sdk._require({"data": data})
        return self._sdk._request(
            "/admin/ticket/jira",
            method="POST",
            body=data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Tickets:
    """Tickets domain. Admin namespace only (staff-only customer tickets)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: TicketsAdmin | None = None
        if sdk.enable_admin:
            self.admin = TicketsAdmin(sdk)
