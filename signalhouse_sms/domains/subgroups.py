"""Subgroups domain for the SignalHouse SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Subgroups:
    """Subgroup management operations."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_subgroups(
        self,
        *,
        id: str | None = None,
        group_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of subgroups with optional filters.

        Args:
            id: Filter by subgroup ID.
            group_id: Filter by parent group ID.
            page: The page number for pagination.
            limit: The number of items per page.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.
        """
        query_string = self._sdk._get_query_string({
            "id": id,
            "groupId": group_id,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/subgroup{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_subgroup_counts(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get resource counts grouped by subgroup ID.

        Only signalhouse_admin can query all groups; every other allowed role
        is restricted to its JWT group scope.
        """
        query_string = self._sdk._get_query_string({"groupId": group_id, "subgroupId": subgroup_id, "limit": limit, "offset": offset})
        return self._sdk._request(f"/subgroup/counts{query_string}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key)

    def lookup_ghl_location(
        self,
        *,
        group_id: str | None = None,
        ghl_location_id: str | None = None,
        subgroup_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Resolve the mapping between a GoHighLevel location and a Signal House subgroup, in either
        direction. Provide exactly one of ghl_location_id or subgroup_id.

        Args:
            group_id: Restrict the lookup to an accessible group ID. Optional - customer roles
                default to their own accessible group(s) and are rejected if they name a group
                they don't belong to; a subgroup_id/ghl_location_id that belongs to a different
                group than the caller's returns a 404, identical to a nonexistent one.
            ghl_location_id: GHL location ID to resolve to its subgroup (mutually exclusive with subgroup_id).
            subgroup_id: Subgroup ID to resolve to its GHL location (mutually exclusive with ghl_location_id).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict: groupId, subgroupId, subgroupName, ghlLocationId, ghlLocationName.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "ghlLocationId": ghl_location_id,
            "subgroupId": subgroup_id,
        })
        return self._sdk._request(
            f"/subgroup/ghl-location-lookup{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def link_ghl_location(
        self,
        subgroup_id: str,
        ghl_location_id: str | None,
        *,
        ghl_location_name: str | None = None,
        claimed_at: str | datetime | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Link (or, with ghl_location_id=None, unlink) a GoHighLevel location to a subgroup.

        Requires signalhouse_api or signalhouse_admin role. At most one subgroup may hold a given
        ghl_location_id; linking it here steals it from any other subgroup that currently holds it.

        Args:
            subgroup_id: The subgroup to link.
            ghl_location_id: The GHL location ID to link, or None to unlink.
            ghl_location_name: Display name of the GHL location. Omit to leave the subgroup's
                currently stored name untouched (only when ghl_location_id is unchanged - otherwise
                cleared); always cleared when unlinking.
            claimed_at: When this link was locally claimed by the caller (a datetime or ISO 8601
                string). Required when linking (ghl_location_id is not None) - used to detect and
                reject a delayed/out-of-order push whose claim has since been superseded by a newer
                one recorded elsewhere. Ignored when unlinking.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict: the updated subgroup.

        Raises:
            SignalHouseValidationError: If subgroup_id is missing.
        """
        self._sdk._require({"subgroupId": subgroup_id})
        body: dict[str, Any] = {"subgroupId": subgroup_id, "ghlLocationId": ghl_location_id}
        if ghl_location_name is not None:
            body["ghlLocationName"] = ghl_location_name
        if claimed_at is not None:
            body["claimedAt"] = claimed_at.isoformat() if isinstance(claimed_at, datetime) else claimed_at
        return self._sdk._request(
            "/subgroup/ghl-location-link",
            method="PUT",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_subgroup(
        self,
        subgroup_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a new subgroup with the specified subgroup data.

        Args:
            subgroup_data: The data for the subgroup. Required fields include groupId and subgroupName.
                Optional carrier-ID fields include carrierIdFamily and carrierIdRegion. Setting
                those fields requires signalhouse_api, signalhouse_admin, signalhouse_user, api,
                admin, developer, or billing role.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If subgroup_data is missing.
        """
        self._sdk._require({"subgroupData": subgroup_data})
        return self._sdk._request(
            "/subgroup",
            method="POST",
            body=subgroup_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update_subgroup(
        self,
        id: str,
        update_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing subgroup with the specified data.

        Args:
            id: The ID of the subgroup to update.
            update_data: The data for the subgroup to be updated. Optional carrier-ID fields include
                carrierIdFamily and carrierIdRegion. Setting those fields requires signalhouse_api,
                signalhouse_admin, signalhouse_user, api, admin, developer, or billing role.
                Optional caller-name (CNAM) fields: cnamAutoApply (bool) turns auto-apply on or
                off, so eligible numbers get their brand's registered name on outbound calls;
                cnamBrandId (str or None) is the default caller-ID brand for numbers with no
                campaign (must be a verified brand in this subgroup; required when turning
                auto-apply on in a subgroup with more than one verified brand). Setting these
                requires signalhouse_api, signalhouse_admin, signalhouse_user, api, admin, or
                developer role.
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
            f"/subgroup/{safe_id}",
            method="PUT",
            body=update_data,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_subgroup(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a subgroup by its ID (mark as inactive).

        Args:
            id: The ID of the subgroup to delete.
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
            f"/subgroup/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
