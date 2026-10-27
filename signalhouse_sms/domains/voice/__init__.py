"""Voice domain — wraps the Voice service (mounted under /voice).

Groups all voice-service sub-resources under a single namespace, accessed via
``sdk.voice.*``:

* ``sdk.voice.sip_trunks``                 — SIP trunk (peer-to-peer connections to PBX/carrier).
* ``sdk.voice.sip_profiles``               — SIP profile / endpoint (single registerable UA).
* ``sdk.voice.programmable_voice_profiles`` — Programmable Voice Profile (route a set of numbers through Signal House).
* ``sdk.voice.number_routes``              — Per-number inbound route (overrides the profile and subgroup settings).
* ``sdk.voice.calls``                      — Outbound call origination + call log queries.
* ``sdk.voice.call_logs``                  — Account-scoped call history: list/get + presigned recording.
* ``sdk.voice.analytics``                  — Aggregated call metrics (summary tiles + byDate/byNumber/byCarrier breakdowns).
* ``sdk.voice.tokens``                     — Mint ephemeral SIP credentials for the browser voice SDK.
* ``sdk.voice.global_voice_settings``      — Account-wide voice defaults (accepted regions, max spend, E911).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .sip_trunks import SipTrunks
from .sip_profiles import SipProfiles
from .programmable_voice_profiles import ProgrammableVoiceProfiles
from .number_routes import NumberRoutes
from .calls import Calls
from .call_logs import CallLogs
from .analytics import Analytics
from .tokens import Tokens
from .global_voice_settings import GlobalVoiceSettings

if TYPE_CHECKING:
    from ...client import SignalHouseSDK


class Voice:
    """Voice domain namespace. Accessed via ``sdk.voice``."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.sip_trunks = SipTrunks(sdk)
        self.sip_profiles = SipProfiles(sdk)
        self.programmable_voice_profiles = ProgrammableVoiceProfiles(sdk)
        self.number_routes = NumberRoutes(sdk)
        self.calls = Calls(sdk)
        self.call_logs = CallLogs(sdk)
        self.analytics = Analytics(sdk)
        self.tokens = Tokens(sdk)
        self.global_voice_settings = GlobalVoiceSettings(sdk)


__all__ = ["Voice", "SipTrunks", "SipProfiles", "ProgrammableVoiceProfiles", "NumberRoutes","Calls", "CallLogs", "Analytics", "Tokens", "GlobalVoiceSettings"]
