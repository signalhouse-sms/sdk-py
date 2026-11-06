"""Request-contract coverage for the rcs.agents namespace and the registration draft methods."""
import io
from pathlib import Path
import sys
import types
import unittest
from urllib.parse import parse_qs, urlsplit

SDK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SDK_ROOT))

try:
    import requests  # noqa: F401
except ImportError:
    stub = types.ModuleType("requests")
    stub.Session = type("Session", (), {"__init__": lambda self: setattr(self, "headers", {})})
    stub.exceptions = types.SimpleNamespace(RequestException=OSError, JSONDecodeError=ValueError)
    sys.modules["requests"] = stub

from signalhouse_sms import SignalHouseSDK  # noqa: E402
from signalhouse_sms.domains.rcs import Rcs, RcsAgents, RcsMessages  # noqa: E402
from signalhouse_sms.exceptions import SignalHouseValidationError  # noqa: E402

AGENT = "RCSA7K2M1QZ8RP"


class CaptureSession:
    """Record each request and answer 200 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}")


class RcsMessageContracts(unittest.TestCase):
    RECIPIENTS = [{"phoneNumber": "+15125550199", "variables": {"name": "Ada"}}]

    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()
        self.messages = self.sdk.rcs.messages

    def last(self):
        """Return (path, query, request kwargs) of the last captured request."""
        call = self.session.calls[-1]
        parts = urlsplit(call["url"])
        return parts.path, parse_qs(parts.query), call

    def test_sdk_exposes_rcs_messages(self):
        self.assertIsInstance(self.messages, RcsMessages)

    def test_send_posts_given_fields_and_requires_agent_and_recipients(self):
        fallback = {"mode": "auto", "channel": "sms", "from": "15125550100", "content": {"text": "Hi"}, "validitySeconds": 600}
        self.messages.send(agent_id=AGENT, recipients=self.RECIPIENTS, content={"blocks": []}, content_format="content.v1",
                           traffic_type="TRANSACTION", ttl_seconds=900, fallback=fallback,
                           status_callback_url="https://example.com/cb", enable_shortlink=False, is_test=True,
                           simulate="delivered", idempotency_key="k1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/message/rcs", "POST"))
        self.assertEqual(call["headers"]["Idempotency-Key"], "k1")
        self.assertEqual(call["json"], {"agentId": AGENT, "recipients": self.RECIPIENTS, "content": {"blocks": []},
                                        "contentFormat": "content.v1", "trafficType": "TRANSACTION", "ttlSeconds": 900,
                                        "fallback": fallback, "statusCallbackUrl": "https://example.com/cb",
                                        "enableShortlink": False, "isTest": True, "simulate": "delivered"})
        self.messages.send(agent_id=AGENT, recipients=self.RECIPIENTS, template_id="T1", template_version=2,
                           expire_time="2026-11-05T00:00:00Z")
        self.assertEqual(self.last()[2]["json"], {"agentId": AGENT, "recipients": self.RECIPIENTS, "templateId": "T1",
                                                  "templateVersion": 2, "expireTime": "2026-11-05T00:00:00Z"})
        with self.assertRaisesRegex(SignalHouseValidationError, "agentId"):
            self.messages.send(agent_id="", recipients=self.RECIPIENTS)
        with self.assertRaisesRegex(SignalHouseValidationError, "recipients"):
            self.messages.send(agent_id=AGENT, recipients=None)

    def test_validate_posts_the_send_body(self):
        self.messages.validate(agent_id=AGENT, recipients=self.RECIPIENTS, template_id="T1", simulate="read")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/message/rcs/validate", "POST"))
        self.assertEqual(call["json"], {"agentId": AGENT, "recipients": self.RECIPIENTS, "templateId": "T1", "simulate": "read"})

    def test_estimate_adds_the_channel(self):
        self.messages.estimate(agent_id=AGENT, recipient_count=500, template_id="T1", template_version=2,
                               traffic_type="PROMOTION", fallback={"mode": "rcs_only"})
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/message/estimate", "POST"))
        self.assertEqual(call["json"], {"channel": "rcs", "agentId": AGENT, "recipientCount": 500, "templateId": "T1",
                                        "templateVersion": 2, "trafficType": "PROMOTION", "fallback": {"mode": "rcs_only"}})
        with self.assertRaisesRegex(SignalHouseValidationError, "agentId"):
            self.messages.estimate(agent_id="", recipient_count=500)

    def test_capabilities_posts_the_numbers(self):
        self.messages.capabilities(AGENT, phone_numbers=["+15125550199"])
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/rcs/capabilities", "POST"))
        self.assertEqual(call["json"], {"agentId": AGENT, "phoneNumbers": ["+15125550199"]})
        with self.assertRaisesRegex(SignalHouseValidationError, "phoneNumbers"):
            self.messages.capabilities(AGENT, phone_numbers=None)

    def test_get_and_get_message_address_the_message(self):
        self.messages.get("a/1")
        call = self.session.calls[-1]
        self.assertEqual((call["method"], call["url"]), ("GET", "https://example.invalid/message/a%2F1"))
        self.sdk.messages.get_message("a/1")
        call = self.session.calls[-1]
        self.assertEqual((call["method"], call["url"]), ("GET", "https://example.invalid/message/a%2F1"))
        with self.assertRaisesRegex(SignalHouseValidationError, "messageId"):
            self.messages.get("")
        with self.assertRaisesRegex(SignalHouseValidationError, "id"):
            self.sdk.messages.get_message("")

    def test_list_maps_filters_and_adds_the_type(self):
        self.messages.list(agent_id=AGENT, from_="2026-11-01", to="2026-11-02", group_id="G1", status="READ", page=2,
                           limit=50, template_id="T1", template_version=3, bulk_id="B1", fallback_reason="NOT_CAPABLE",
                           billing_class="RICH_MEDIA", delivered_channel="sms", is_test=False)
        path, query, call = self.last()
        self.assertEqual((path, call["method"]), ("/message", "GET"))
        self.assertEqual(query, {"registrationId": [AGENT], "startDate": ["2026-11-01"], "endDate": ["2026-11-02"],
                                 "groupId": ["G1"], "status": ["READ"], "page": ["2"], "limit": ["50"],
                                 "templateId": ["T1"], "templateVersion": ["3"], "bulkId": ["B1"],
                                 "fallbackReason": ["NOT_CAPABLE"], "billingClass": ["RICH_MEDIA"],
                                 "deliveredChannel": ["sms"], "isTest": ["false"], "messageType": ["RCS"]})
        with self.assertRaisesRegex(SignalHouseValidationError, "groupId"):
            self.messages.list(group_id=None, from_="2026-11-01", to="2026-11-02", agent_id=AGENT)
        with self.assertRaisesRegex(SignalHouseValidationError, "from"):
            self.messages.list(group_id="G1", from_="", to="2026-11-02")
        with self.assertRaisesRegex(SignalHouseValidationError, "to"):
            self.messages.list(group_id="G1", from_="2026-11-01", to=None)
        self.assertEqual(len(self.session.calls), 1)

    def test_get_messages_forwards_the_rcs_filters(self):
        self.sdk.messages.get_messages(group_id="G1", start_date="2026-11-01", end_date="2026-11-02", template_id="T1",
                                       template_version=3, bulk_id="B1", fallback_reason="TTL_EXPIRED",
                                       billing_class="RICH", delivered_channel="sms", is_test=False)
        path, query, call = self.last()
        self.assertEqual((path, call["method"]), ("/message", "GET"))
        self.assertEqual(query, {"groupId": ["G1"], "startDate": ["2026-11-01"], "endDate": ["2026-11-02"],
                                 "templateId": ["T1"], "templateVersion": ["3"], "bulkId": ["B1"],
                                 "fallbackReason": ["TTL_EXPIRED"], "billingClass": ["RICH"],
                                 "deliveredChannel": ["sms"], "isTest": ["false"]})


class RcsAgentContracts(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()
        self.agents = self.sdk.rcs.agents

    def last(self):
        """Return (path, query, request kwargs) of the last captured request."""
        call = self.session.calls[-1]
        parts = urlsplit(call["url"])
        return parts.path, parse_qs(parts.query), call

    def test_sdk_exposes_rcs_agents(self):
        self.assertIsInstance(self.sdk.rcs, Rcs)
        self.assertIsInstance(self.sdk.rcs.agents, RcsAgents)

    def test_create_posts_given_fields_and_requires_brand_id(self):
        self.agents.create(brand_id="BXYZ123", campaign_id="CABC123", agent={"name": "Acme"},
                           use_case="TRANSACTIONAL", idempotency_key="k1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/rcs/agent", "POST"))
        self.assertEqual(call["headers"]["Idempotency-Key"], "k1")
        self.assertEqual(call["json"], {"brandId": "BXYZ123", "campaignId": "CABC123",
                                        "agent": {"name": "Acme"}, "useCase": "TRANSACTIONAL"})
        self.agents.create(brand_id="BXYZ123")
        self.assertEqual(self.last()[2]["json"], {"brandId": "BXYZ123"})
        with self.assertRaisesRegex(SignalHouseValidationError, "brandId"):
            self.agents.create(brand_id=None, agent={"name": "Acme"})

    def test_list_forwards_link_and_status_filters(self):
        self.agents.list(brand_id="BXYZ123", campaign_id="CABC123", status="DRAFT", page=2, limit=50)
        path, query, call = self.last()
        self.assertEqual((path, call["method"]), ("/rcs/agent", "GET"))
        self.assertEqual(query, {"brandId": ["BXYZ123"], "campaignId": ["CABC123"], "status": ["DRAFT"],
                                 "page": ["2"], "limit": ["50"]})
        self.agents.list(status=["DRAFT", "REJECTED"])
        self.assertEqual(self.last()[1], {"status": ["DRAFT", "REJECTED"]})

    def test_resend_tester_invite(self):
        self.agents.resend_tester_invite(AGENT, phone_number="+15125550199")
        call = self.session.calls[-1]
        self.assertEqual((call["method"], call["url"]), ("POST", f"https://example.invalid/rcs/agent/{AGENT}/testers/%2B15125550199/resend"))
        with self.assertRaisesRegex(SignalHouseValidationError, "phoneNumber"):
            self.agents.resend_tester_invite(AGENT, phone_number="")

    def test_agent_paths_and_partial_update(self):
        self.agents.get(AGENT)
        self.agents.update(AGENT, campaign_id=None, agent={"description": "Alerts"}, contact={"firstName": "Ada"})
        self.agents.validate(AGENT)
        self.agents.submit(AGENT)
        self.agents.launch(AGENT)
        self.agents.archive(AGENT)
        self.assertEqual([(c["method"], urlsplit(c["url"]).path) for c in self.session.calls], [
            ("GET", f"/rcs/agent/{AGENT}"), ("PUT", f"/rcs/agent/{AGENT}"), ("POST", f"/rcs/agent/{AGENT}/validate"),
            ("POST", f"/rcs/agent/{AGENT}/submit"), ("POST", f"/registration/{AGENT}/launch"), ("POST", f"/rcs/agent/{AGENT}/archive"),
        ])
        self.assertEqual(self.session.calls[1]["json"], {"campaignId": None, "agent": {"description": "Alerts"}, "contact": {"firstName": "Ada"}})
        self.agents.get("A/1")
        self.assertEqual(self.session.calls[-1]["url"], "https://example.invalid/rcs/agent/A%2F1")
        with self.assertRaisesRegex(SignalHouseValidationError, "agentId"):
            self.agents.submit("")
        with self.assertRaisesRegex(SignalHouseValidationError, "agentId"):
            self.agents.launch("")

    def test_upload_asset_is_multipart_with_kind_and_file(self):
        image = io.BytesIO(b"\x89PNG")
        self.agents.upload_asset(AGENT, kind="logo", file=image, file_name="logo.png")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), (f"/rcs/agent/{AGENT}/asset", "POST"))
        self.assertEqual(call["data"], {"kind": "logo"})
        self.assertEqual(call["files"], [("file", ("logo.png", image))])
        self.assertNotIn("json", call)
        count = len(self.session.calls)
        for kwargs in ({"kind": "", "file": image}, {"kind": "hero", "file": None}):
            with self.subTest(kwargs=kwargs), self.assertRaises(SignalHouseValidationError):
                self.agents.upload_asset(AGENT, **kwargs)
        self.assertEqual(len(self.session.calls), count)

    def test_registrations_gain_draft_methods_and_link_filters(self):
        registrations = self.sdk.registrations
        registrations.update_registration(AGENT, {"useCase": "OTP"})
        registrations.validate_registration(AGENT)
        registrations.submit_registration(AGENT)
        registrations.launch_registration(AGENT)
        self.assertEqual([(c["method"], urlsplit(c["url"]).path) for c in self.session.calls], [
            ("PUT", f"/registration/{AGENT}"), ("POST", f"/registration/{AGENT}/validate"),
            ("POST", f"/registration/{AGENT}/submit"), ("POST", f"/registration/{AGENT}/launch"),
        ])
        self.assertEqual(self.session.calls[0]["json"], {"useCase": "OTP"})
        registrations.get_registrations(type="RCS_AGENT", brand_id="BXYZ123", campaign_id="CABC123")
        self.assertEqual(self.last()[1], {"type": ["RCS_AGENT"], "brandId": ["BXYZ123"], "campaignId": ["CABC123"]})
        with self.assertRaisesRegex(SignalHouseValidationError, "data"):
            registrations.update_registration(AGENT, None)


if __name__ == "__main__":
    unittest.main()
