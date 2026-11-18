"""sdk.voice.call_flows sends each request to the right path, with the right method and body."""
from pathlib import Path
import sys
import types
import unittest

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

FLOW_ID = "0088947b-7821-4853-bfe6-744fce926de2"
BASE = "/voice/api/v1/call-flows"


class CaptureSession:
    """Record each request and answer 200 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}")


class CallFlowsTests(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()
        self.flows = self.sdk.voice.call_flows

    def last(self):
        call = self.session.calls[-1]
        return call["method"], call["url"].replace("https://example.invalid", ""), call.get("json")

    def test_list_sends_only_the_filters_that_are_set(self):
        self.flows.list()
        self.assertEqual(self.last()[1], BASE)
        self.flows.list(page=2, subgroup_id="S0000001", q=None)
        self.assertEqual(self.last()[1], f"{BASE}?page=2&subgroupId=S0000001")

    def test_list_sends_booleans_the_way_the_service_reads_them(self):
        # The Voice service accepts only lowercase "true"/"false"; Python's str(True) is "True".
        self.flows.list(include_deleted=True)
        self.assertEqual(self.last()[1], f"{BASE}?includeDeleted=true")
        self.flows.list(include_deleted=False)
        self.assertEqual(self.last()[1], f"{BASE}?includeDeleted=false")

    def test_catalog_and_get_read(self):
        self.flows.catalog()
        self.assertEqual(self.last()[:2], ("GET", f"{BASE}/catalog"))
        self.flows.get(FLOW_ID)
        self.assertEqual(self.last()[:2], ("GET", f"{BASE}/{FLOW_ID}"))

    def test_create_posts_and_update_patches(self):
        self.flows.create({"name": "Main line", "subgroupId": "S0000001"})
        self.assertEqual(self.last(), ("POST", BASE, {"name": "Main line", "subgroupId": "S0000001"}))
        self.flows.update(FLOW_ID, {"status": "DISABLED"})
        self.assertEqual(self.last(), ("PATCH", f"{BASE}/{FLOW_ID}", {"status": "DISABLED"}))

    def test_save_draft_puts_the_whole_draft(self):
        draft = {"nodes": [{"id": FLOW_ID, "type": "inbound", "name": "Inbound Call"}], "edges": []}
        self.flows.save_draft(FLOW_ID, draft)
        self.assertEqual(self.last(), ("PUT", f"{BASE}/{FLOW_ID}/draft", draft))

    def test_publish_and_restore_send_an_empty_json_body(self):
        self.flows.publish(FLOW_ID)
        self.assertEqual(self.last(), ("POST", f"{BASE}/{FLOW_ID}/publish", {}))
        self.flows.restore(FLOW_ID)
        self.assertEqual(self.last(), ("POST", f"{BASE}/{FLOW_ID}/restore", {}))

    def test_duplicate_names_the_copy_only_when_asked(self):
        self.flows.duplicate(FLOW_ID)
        self.assertEqual(self.last()[2], {})
        self.flows.duplicate(FLOW_ID, name="Weekend")
        self.assertEqual(self.last()[2], {"name": "Weekend"})

    def test_delete(self):
        self.flows.delete(FLOW_ID)
        self.assertEqual(self.last()[:2], ("DELETE", f"{BASE}/{FLOW_ID}"))

    def test_ids_are_url_encoded(self):
        self.flows.get("a/b")
        self.assertEqual(self.last()[1], f"{BASE}/a%2Fb")


if __name__ == "__main__":
    unittest.main()
