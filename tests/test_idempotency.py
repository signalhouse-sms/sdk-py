"""The idempotency_key option is accepted everywhere and reaches the wire as the Idempotency-Key header."""
import ast
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


class CaptureSession:
    """Record each request and answer 201 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=201, json=lambda: {}, text="{}")


class IdempotencyKeyTests(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()

    def test_request_sends_the_header(self):
        self.sdk._request("/registration", method="POST", body={}, idempotency_key="key-1")
        self.assertEqual(self.session.calls[0]["headers"]["Idempotency-Key"], "key-1")

    def test_multipart_request_sends_the_header(self):
        self.sdk._multipart_request("/brand/appeal/B1", form_data={}, idempotency_key="key-1")
        self.assertEqual(self.session.calls[0]["headers"]["Idempotency-Key"], "key-1")

    def test_no_header_without_the_option(self):
        self.sdk._request("/registration", method="POST", body={})
        self.assertNotIn("Idempotency-Key", self.session.calls[0]["headers"])

    def test_every_domain_method_accepts_and_forwards_the_option(self):
        problems = []
        for path in sorted((SDK_ROOT / "signalhouse_sms" / "domains").rglob("*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
                    if "headers" in names and "idempotency_key" not in names:
                        problems.append(f"{path.name}:{node.lineno} {node.name} lacks idempotency_key")
                if isinstance(node, ast.Call):
                    keywords = {keyword.arg: keyword.value for keyword in node.keywords}
                    forwards_headers = isinstance(keywords.get("headers"), ast.Name) and keywords["headers"].id == "headers"
                    forwarded = keywords.get("idempotency_key")
                    if forwards_headers and not (isinstance(forwarded, ast.Name) and forwarded.id == "idempotency_key"):
                        problems.append(f"{path.name}:{node.lineno} does not forward idempotency_key")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
