"""SIP Trunks — peer-to-peer SIP connections to a customer PBX or carrier.

Routes are mounted under /voice/sip-trunks on the Voice service.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class SipTrunks:
    """SIP trunk management. Accessed via ``sdk.voice.sip_trunks``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def list(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List all SIP trunks for the current account. ``GET /voice/sip-trunks``."""
        return self._sdk._request(
            "/voice/sip-trunks", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def get(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a single SIP trunk by ID. ``GET /voice/sip-trunks/:id``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def create(
        self,
        trunk_data: dict[str, Any],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a SIP trunk. ``POST /voice/sip-trunks``.

        ``trunk_data`` keys: ``name``, ``region``, ``connectionType``
        (``"IP_AUTH"`` or ``"REGISTRATION"``), optional ``allowedIps``,
        ``transport``, ``maxSpendPerMinute``, ``destinationHosts``, ``sourceHosts``.
        Registration trunks return a one-time password on the response.
        """
        self._sdk._require({"trunkData": trunk_data})
        return self._sdk._request(
            "/voice/sip-trunks", method="POST", body=trunk_data, token=token, headers=headers, idempotency_key=idempotency_key,
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
        """Update a SIP trunk. ``PATCH /voice/sip-trunks/:id``."""
        self._sdk._require({"id": id, "updateData": update_data})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}", method="PATCH", body=update_data, token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def delete(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete a SIP trunk. ``DELETE /voice/sip-trunks/:id``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}", method="DELETE", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def toggle_active(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Toggle a trunk's active/inactive status. ``POST /voice/sip-trunks/:id/toggle-active``."""
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}/toggle-active", method="POST", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def regenerate_password(
        self,
        id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Regenerate the SIP password for a REGISTRATION-type trunk.

        Returns ``{ "password": "..." }``. The old password stops working immediately.
        ``POST /voice/sip-trunks/:id/regenerate-password``.
        """
        self._sdk._require({"id": id})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}/regenerate-password", method="POST", token=token, headers=headers, idempotency_key=idempotency_key,
        )

    def assign_numbers(
        self,
        id: str,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Assign phone numbers to a SIP trunk for outbound caller ID / inbound routing.

        Returns ``{ "assigned": [...], "skipped": [...] }``.
        ``POST /voice/sip-trunks/:id/assign-numbers``.
        """
        self._sdk._require({"id": id, "phoneNumbers": phone_numbers})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}/assign-numbers",
            method="POST",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def unassign_numbers(
        self,
        id: str,
        phone_numbers: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Unassign phone numbers from a SIP trunk.

        Returns ``{ "unassigned": [...] }``.
        ``POST /voice/sip-trunks/:id/unassign-numbers``.
        """
        self._sdk._require({"id": id, "phoneNumbers": phone_numbers})
        safe_id = quote(str(id), safe="")
        return self._sdk._request(
            f"/voice/sip-trunks/{safe_id}/unassign-numbers",
            method="POST",
            body={"phoneNumbers": phone_numbers},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_pops(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List available SIP POPs (Points of Presence). ``GET /voice/sip-trunks/pops``."""
        return self._sdk._request(
            "/voice/sip-trunks/pops", method="GET", token=token, headers=headers, idempotency_key=idempotency_key,
        )
