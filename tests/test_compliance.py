"""Request-contract coverage for the compliance namespace (customer case methods)."""
from pathlib import Path
import io
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
from signalhouse_sms.domains.compliance import Compliance  # noqa: E402
from signalhouse_sms.exceptions import SignalHouseValidationError  # noqa: E402


class CaptureSession:
    """Record each request and answer 200 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}", content=b"%PDF-1.7")


class ComplianceContracts(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()
        self.compliance = self.sdk.compliance

    def last(self):
        """Return (path, query, request kwargs) of the last captured request."""
        call = self.session.calls[-1]
        url = urlsplit(call["url"])
        return url.path, parse_qs(url.query), call

    def test_sdk_exposes_compliance_without_staff_methods(self):
        self.assertIsInstance(self.compliance, Compliance)
        self.assertFalse(hasattr(SignalHouseSDK(api_key="t", base_url="https://x", enable_admin=True).compliance, "admin"))

    def test_get_cases_sends_only_given_filters(self):
        self.compliance.get_cases()
        path, query, call = self.last()
        self.assertEqual((path, call["method"]), ("/compliance/cases", "GET"))
        self.assertEqual(call["url"], "https://example.invalid/compliance/cases")
        self.assertIsNone(call["json"])

        self.compliance.get_cases(
            group_id="G1", status="OPEN", stage="customer", object_type="CAMPAIGN", object_id="C1",
            subgroup_id="S1", suspended=True, from_="2026-11-01T00:00:00Z", to="2026-11-13T00:00:00Z",
            sort="fixBy", page=2, limit=50, token="session",
        )
        _, query, call = self.last()
        self.assertEqual(query, {
            "groupId": ["G1"], "status": ["OPEN"], "stage": ["customer"], "objectType": ["CAMPAIGN"],
            "objectId": ["C1"], "subgroupId": ["S1"], "suspended": ["true"],
            "from": ["2026-11-01T00:00:00Z"], "to": ["2026-11-13T00:00:00Z"],
            "sort": ["fixBy"], "page": ["2"], "limit": ["50"],
        })
        self.assertEqual(call["headers"]["Authorization"], "Bearer session")

        self.compliance.get_cases(suspended=False, status="CLOSED")
        _, query, _ = self.last()
        self.assertEqual(query, {"suspended": ["false"], "status": ["CLOSED"]})

    def test_get_case_reads_the_encoded_case(self):
        self.compliance.get_case("CASE-1/2")
        _, _, call = self.last()
        self.assertEqual(call["url"], "https://example.invalid/compliance/cases/CASE-1%2F2")
        self.assertEqual(call["method"], "GET")
        self.assertIsNone(call["json"])
        with self.assertRaisesRegex(SignalHouseValidationError, "caseId"):
            self.compliance.get_case("")

    def test_answer_requirement_puts_only_given_keys(self):
        self.compliance.answer_requirement("CASE-1", "CASE-1-1", answer="Removed the number", file_ids=["F1", "F2"], idempotency_key="k1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/compliance/cases/CASE-1/requirements/CASE-1-1", "PUT"))
        self.assertEqual(call["json"], {"answer": "Removed the number", "fileIds": ["F1", "F2"]})
        self.assertEqual(call["headers"]["Idempotency-Key"], "k1")

        self.compliance.answer_requirement("CASE-1", "CASE-1-1", answer="Done")
        self.assertEqual(self.last()[2]["json"], {"answer": "Done"})

        self.compliance.answer_requirement("CASE-1", "CASE-1-1", file_ids=["F1"])
        self.assertEqual(self.last()[2]["json"], {"fileIds": ["F1"]})

        self.compliance.answer_requirement("CASE 1", "CASE-1/1")
        _, _, call = self.last()
        self.assertEqual(call["url"], "https://example.invalid/compliance/cases/CASE%201/requirements/CASE-1%2F1")
        self.assertEqual(call["json"], {})

        with self.assertRaisesRegex(SignalHouseValidationError, "caseId"):
            self.compliance.answer_requirement("", "CASE-1-1", answer="x")
        with self.assertRaisesRegex(SignalHouseValidationError, "requirementId"):
            self.compliance.answer_requirement("CASE-1", None, answer="x")

    def test_upload_file_sends_a_multipart_content_type(self):
        """The session's JSON default must not label a multipart body."""
        sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        sent = []

        def send(prepared, **_):
            sent.append(prepared)
            return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}", content=b"{}")

        sdk._session.send = send
        sdk.compliance.upload_file("CASE-1", ("records.csv", io.BytesIO(b"a,b\n"), "text/csv"))
        self.assertTrue(sent[0].headers["Content-Type"].startswith("multipart/form-data; boundary="))

    def test_upload_file_posts_multipart_fields(self):
        file = ("records.csv", io.BytesIO(b"a,b\n"), "text/csv")
        self.compliance.upload_file("CASE-1", file, requirement_id="CASE-1-1")
        path, _, call = self.last()
        self.assertEqual((path, call["method"]), ("/compliance/files", "POST"))
        self.assertEqual(call["data"], {"caseId": "CASE-1", "requirementId": "CASE-1-1"})
        self.assertEqual(call["files"], [("file", file)])
        self.assertNotIn("json", call)
        self.assertIsNone(call["headers"]["Content-Type"])

        self.compliance.upload_file("CASE-1", file)
        self.assertEqual(self.last()[2]["data"], {"caseId": "CASE-1"})

        with self.assertRaisesRegex(SignalHouseValidationError, "caseId"):
            self.compliance.upload_file("", file)
        with self.assertRaisesRegex(SignalHouseValidationError, "file"):
            self.compliance.upload_file("CASE-1", None)

    def test_get_file_reads_the_encoded_file(self):
        self.assertEqual(self.compliance.get_file("CF1/2")["data"], b"%PDF-1.7")
        _, _, call = self.last()
        self.assertEqual(call["url"], "https://example.invalid/compliance/files/CF1%2F2")
        self.assertEqual(call["method"], "GET")
        self.assertIsNone(call["json"])
        with self.assertRaisesRegex(SignalHouseValidationError, "fileId"):
            self.compliance.get_file(None)


if __name__ == "__main__":
    unittest.main()
