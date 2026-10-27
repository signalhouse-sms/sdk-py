"""Request-contract coverage for the templates namespace."""
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
from signalhouse_sms.exceptions import SignalHouseValidationError  # noqa: E402

BODY = {
    "channel": "rcs",
    "contentFormat": "rcs.blocks.v1",
    "content": {"blocks": [{"id": "b1", "kind": "text", "text": "Hi {{first_name}}"}]},
    "variables": [{"key": "first_name", "type": "text", "required": True}],
    "defaults": {},
    "fallback": {},
}


class CaptureSession:
    """Record each request and answer 200 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}")


class TemplateContracts(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()

    def last(self):
        """Return (path, query, request kwargs) of the last captured request."""
        call = self.session.calls[-1]
        parts = urlsplit(call["url"])
        return parts.path, parse_qs(parts.query), call

    def test_generic_namespace_wire_contract(self):
        templates = self.sdk.templates

        templates.create(group_id="G1", name="Welcome", body=BODY, tag="Promo", idempotency_key="key-1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/template", "POST"))
        self.assertEqual(call["json"], {"groupId": "G1", "name": "Welcome", "body": BODY, "tag": "Promo"})
        self.assertEqual(call["headers"]["Idempotency-Key"], "key-1")
        templates.create(group_id="G1", name="Welcome", body=BODY)
        self.assertEqual(set(self.last()[2]["json"]), {"groupId", "name", "body"})

        templates.list(group_id="G1", state="PUBLISHED", channel="rcs", tag="Promo", search="wel",
                                sort_by="name", sort_order="asc", page=2, limit=50, token="session")
        path, query, call = self.last()
        self.assertEqual((path, call["method"]), ("/template", "GET"))
        self.assertEqual(query, {"groupId": ["G1"], "state": ["PUBLISHED"], "channel": ["rcs"], "tag": ["Promo"],
                                 "search": ["wel"], "sortBy": ["name"], "sortOrder": ["asc"], "page": ["2"], "limit": ["50"]})
        self.assertEqual(call["headers"]["Authorization"], "Bearer session")

        templates.get("TPL/1", group_id="G1", version="draft")
        path, query, call = self.last()
        self.assertTrue(call["url"].startswith("https://example.invalid/template/TPL%2F1?"))
        self.assertEqual((query, call["method"]), ({"groupId": ["G1"], "version": ["draft"]}, "GET"))

        templates.publish("TPL1", group_id="G1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/template/TPL1/publish", "POST"))
        self.assertEqual(call["json"], {"groupId": "G1"})

        templates.archive("TPL1", group_id="G1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/template/TPL1/archive", "POST"))
        self.assertEqual(call["json"], {"groupId": "G1"})

        templates.versions("TPL1", group_id="G1", page=1, limit=10)
        path, query, _ = self.last()
        self.assertEqual((path, query), ("/template/TPL1/versions", {"groupId": ["G1"], "page": ["1"], "limit": ["10"]}))

        templates.capabilities(group_id="G1", channel="rcs", provider="sinch")
        path, query, _ = self.last()
        self.assertEqual((path, query), ("/template/capabilities", {"groupId": ["G1"], "channel": ["rcs"], "provider": ["sinch"]}))

    def test_update_sends_only_group_id_and_given_fields_and_distinguishes_null_tag(self):
        templates = self.sdk.templates
        templates.update("TPL1", group_id="G1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/template/TPL1", "PUT"))
        self.assertEqual(call["json"], {"groupId": "G1"})

        templates.update("TPL1", group_id="G1", tag=None)
        self.assertEqual(self.last()[2]["json"], {"groupId": "G1", "tag": None})

        templates.update("TPL1", group_id="G1", name="New", tag="Promo", body=BODY)
        self.assertEqual(self.last()[2]["json"], {"groupId": "G1", "name": "New", "tag": "Promo", "body": BODY})

    def test_validate_takes_exactly_one_of_body_or_version(self):
        templates = self.sdk.templates
        templates.validate("TPL1", group_id="G1", body=BODY)
        path, _, call = self.last()
        self.assertEqual((path, call["method"], call["json"]), ("/template/TPL1/validate", "POST", {"groupId": "G1", "body": BODY}))
        templates.validate("TPL1", group_id="G1", version="published")
        self.assertEqual(self.last()[2]["json"], {"groupId": "G1", "version": "published"})
        for kwargs in ({}, {"body": BODY, "version": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(SignalHouseValidationError):
                templates.validate("TPL1", group_id="G1", **kwargs)

    def test_upload_media_is_multipart_with_file_and_group_id(self):
        image = io.BytesIO(b"\x89PNG")
        self.sdk.templates.upload_media(group_id="G1", file=image, file_name="logo.png", idempotency_key="key-2")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/template/media", "POST"))
        self.assertEqual(call["data"], {"groupId": "G1"})
        self.assertEqual(call["files"], [("file", ("logo.png", image))])
        self.assertNotIn("json", call)
        self.assertEqual(call["headers"]["Idempotency-Key"], "key-2")

    def test_required_parameters(self):
        templates = self.sdk.templates
        cases = [
            lambda: templates.list(group_id=""),
            lambda: templates.create(group_id="G1", name="", body=BODY),
            lambda: templates.create(group_id="G1", name="N", body=None),
            lambda: templates.get("", group_id="G1"),
            lambda: templates.update("", group_id="G1", name="New"),
            lambda: templates.update("TPL1", group_id=None, name="New"),
            lambda: templates.publish("TPL1", group_id=""),
            lambda: templates.archive("TPL1", group_id=None),
            lambda: templates.upload_media(group_id="G1", file=None),
        ]
        for index, call in enumerate(cases):
            with self.subTest(case=index), self.assertRaises(SignalHouseValidationError):
                call()
        self.assertEqual(self.session.calls, [])


if __name__ == "__main__":
    unittest.main()
