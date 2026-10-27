"""WebRTC voice tokens — mint ephemeral SIP identities for the browser/mobile
voice SDK.

Wraps the Voice service's ``/voice/tokens`` endpoint. Accessed via
``sdk.voice.tokens``.

Customer flow:

1. Backend calls ``sdk.voice.tokens.create({"identity": "alice", "ttl": 1800})``
   and returns the resulting ``token`` to the customer's browser/app.
2. Browser SDK registers using the embedded ``sip_credentials``.
3. Outbound calls from the SDK go through OpenSIPS -> Asterisk -> carrier; the
   server-side ``sdk.voice.calls.create({"to_identity": "alice", ...})`` flow
   can also ring this identity for click-to-call patterns.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class Tokens:
    """Voice token minting. Accessed via ``sdk.voice.tokens``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def create(
        self,
        token_data: dict[str, Any] | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Mint an ephemeral voice token + SIP credentials.
        ``POST /voice/tokens``.

        ``token_data`` keys (all optional): ``identity`` (customer-facing
        logical name; persisted as ``requested_identity`` so server-initiated
        ``calls.create(to_identity=...)`` can resolve it later; defaults to
        ``"anonymous"``), ``ttl`` (seconds, clamped to the server's max;
        defaults to ``VOICE_TOKEN_DEFAULT_TTL_SEC``), ``grants`` (capability
        grants — ``{"voice": {"incoming": {"allow": bool}, "outgoing":
        {"allowedNumbers": [...]}}}``).

        Returns ``{ token, identity, expires_at, sip_credentials: { username,
        password, domain, wss_url } }``. The plaintext SIP password is sent
        ONCE inside ``sip_credentials`` and is never recoverable.
        """
        return self._sdk._request(
            "/voice/tokens",
            method="POST",
            body=token_data or {},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
