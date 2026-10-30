"""Groups domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class GroupsAdmin:
    """Admin-only group operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_group_counts(
        self,
        *,
        group_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get resource counts grouped by group ID.

        Only signalhouse_admin can query all groups; every other allowed role
        is restricted to its JWT group scope.

        Args:
            group_id: Optional group ID filter. Serialized as ``groupId``.
            limit: Maximum rows to return.
            offset: Rows to skip; requires limit.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.
        """
        query_string = self._sdk._get_query_string({"groupId": group_id, "limit": limit, "offset": offset})
        return self._sdk._request(f"/group/counts{query_string}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key)

    def get_groups(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of all groups with optional pagination.

        Args:
            page: The page number for pagination.
            limit: The number of items per page.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({"page": page, "limit": limit})
        return self._sdk._request(
            f"/group{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_group(
        self,
        group_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new group with the specified group data.

        Args:
            group_data: The data for the new group, including required fields such as groupName.
                Optionally accepts psPartnerKey and ownerEmail to credit a referring partner.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_data is missing.
        """
        self._sdk._require({"groupData": group_data})
        return self._sdk._request(
            "/group",
            method="POST",
            body=group_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_group(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a group with the specified group ID.

        Args:
            group_id: The ID of the group to delete.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/group/{safe_group_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_compliance_status(
        self,
        group_id: str,
        compliance_status: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Set a group's KYC compliance_status.

        Only flips the field — it does not trigger any lockout side effects (halted sends,
        revoked API keys, etc.) for "rejected".

        Args:
            group_id: The ID of the group to update.
            compliance_status: One of "unverified", "pending", "verified", "rejected".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If group_id or compliance_status is missing.
        """
        self._sdk._require({"groupId": group_id, "complianceStatus": compliance_status})
        safe_group_id = quote(str(group_id), safe="")
        return self._sdk._request(
            f"/group/{safe_group_id}/compliance-status",
            method="PUT",
            body={"complianceStatus": compliance_status},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def link_external(
        self,
        link_token: str,
        external_system: str,
        external_id: str,
        *,
        existing_group_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Link an external tenant (GHL/Shopify) to a V2 group (server-to-server).

        Exchanges a single-use link token for a canonical group, adopting an empty portal
        group, repointing to an existing group, or flagging for manual review.

        Args:
            link_token: The single-use external-link token minted by the portal user.
            external_system: The external system ("ghl" or "shopify").
            external_id: The external tenant identifier.
            existing_group_id: An existing V2 group ID to repoint to, if any.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"status": ..., "canonicalGroupId": ..., ...}).

        Raises:
            SignalHouseValidationError: If link_token, external_system, or external_id is missing.
        """
        self._sdk._require({
            "linkToken": link_token,
            "externalSystem": external_system,
            "externalId": external_id,
        })
        body: dict[str, Any] = {
            "linkToken": link_token,
            "externalSystem": external_system,
            "externalId": external_id,
        }
        if existing_group_id is not None:
            body["existingGroupId"] = existing_group_id
        return self._sdk._request(
            "/group/link-external",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Groups:
    """Group management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: GroupsAdmin | None = None
        if sdk.enable_admin:
            self.admin = GroupsAdmin(sdk)

    def get_group(
        self,
        *,
        id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get details of a group by its ID.

        Args:
            id: The ID of the group to retrieve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({"id": id})
        return self._sdk._request(
            f"/group{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_group(
        self,
        id: str,
        group_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update a group with the specified group data.

        Args:
            id: The ID of the group to update.
            group_data: The data for the group, including required fields such as groupName.
                Optional CNP fields: cspId (str | None), defaultCnpSubgroupId (str | None).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If id or group_data is missing.
        """
        self._sdk._require({"id": id, "groupData": group_data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/group/{safe_id}",
            method="PUT",
            body=group_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_sso_configuration(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a group's Enterprise SSO configuration.

        Reports whether SSO is available, the redirect URL to register at the identity provider,
        the saved provider (never its client secret), and each claimed domain with the DNS TXT
        record that verifies it.

        Args:
            group_id: The group.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"groupId": ..., "available": ..., "callbackUrl": ..., "connection": ..., "domains": [...]}).

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id})
        return self._sdk._request(
            f"/group/sso{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def save_sso_connection(
        self,
        group_id: str,
        issuer: str,
        client_id: str,
        client_secret: str | None = None,
        enabled: bool | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create or update a group's OpenID Connect identity provider.

        Requires a fresh auth.confirm_two_factor_identity from the same session.

        Args:
            group_id: The group.
            issuer: The provider's https issuer URL.
            client_id: The client ID registered at the provider.
            client_secret: The client secret; required the first time, omit to keep the saved one.
            enabled: Whether sign-in through the provider is on (default True).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the SSO configuration).

        Raises:
            SignalHouseValidationError: If group_id, issuer or client_id is missing.
        """
        self._sdk._require({"groupId": group_id, "issuer": issuer, "clientId": client_id})
        body: dict[str, Any] = {"groupId": group_id, "issuer": issuer, "clientId": client_id}
        if client_secret is not None:
            body["clientSecret"] = client_secret
        if enabled is not None:
            body["enabled"] = enabled
        return self._sdk._request(
            "/group/sso",
            method="PUT",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_sso_connection(
        self,
        group_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove a group's identity provider and its domains.

        Unlinks every account that signed in through it. Requires a fresh
        auth.confirm_two_factor_identity from the same session.

        Args:
            group_id: The group.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the now-empty SSO configuration).

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id})
        return self._sdk._request(
            f"/group/sso{query_string}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def add_sso_domain(
        self,
        group_id: str,
        domain: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Claim an email domain for a group's SSO.

        The response includes the DNS TXT record that verifies it.

        Args:
            group_id: The group.
            domain: The domain, e.g. "acme.com".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the SSO configuration).

        Raises:
            SignalHouseValidationError: If group_id or domain is missing.
        """
        self._sdk._require({"groupId": group_id, "domain": domain})
        return self._sdk._request(
            "/group/sso/domains",
            method="POST",
            body={"groupId": group_id, "domain": domain},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def verify_sso_domain(
        self,
        group_id: str,
        domain: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Verify a claimed domain by its DNS TXT record.

        Args:
            group_id: The group.
            domain: The claimed domain.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the SSO configuration).

        Raises:
            SignalHouseValidationError: If group_id or domain is missing.
        """
        self._sdk._require({"groupId": group_id, "domain": domain})
        safe_domain = quote(str(domain), safe="")
        return self._sdk._request(
            f"/group/sso/domains/{safe_domain}/verify",
            method="POST",
            body={"groupId": group_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def remove_sso_domain(
        self,
        group_id: str,
        domain: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove a domain from a group's SSO.

        Args:
            group_id: The group.
            domain: The domain.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the SSO configuration).

        Raises:
            SignalHouseValidationError: If group_id or domain is missing.
        """
        self._sdk._require({"groupId": group_id, "domain": domain})
        safe_domain = quote(str(domain), safe="")
        query_string = self._sdk._get_query_string({"groupId": group_id})
        return self._sdk._request(
            f"/group/sso/domains/{safe_domain}{query_string}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
