"""Request-contract coverage for the verify namespace (SIM Swap and Number Verify)."""
from pathlib import Path
import sys
import types
import unittest
from urllib.parse import urlsplit

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
from signalhouse_sms.domains.verify import Verify  # noqa: E402
from signalhouse_sms.exceptions import SignalHouseValidationError  # noqa: E402

PHONE = "+12025550123"


class CaptureSession:
    """Record each request and answer 200 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}")


class VerifyContracts(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()
        self.verify = self.sdk.verify

    def last(self):
        """Return (path, request kwargs) of the last captured request."""
        call = self.session.calls[-1]
        return urlsplit(call["url"]).path, call

    def test_sdk_exposes_verify(self):
        self.assertIsInstance(self.verify, Verify)

    def test_check_sim_swap_posts_only_given_fields(self):
        self.verify.check_sim_swap(PHONE, max_age=240, include_swap_date=True, idempotency_key="k1")
        path, call = self.last()
        self.assertEqual((path, call["method"]), ("/verify/sim-swap", "POST"))
        self.assertEqual(call["headers"]["Idempotency-Key"], "k1")
        self.assertEqual(call["json"], {"phoneNumber": PHONE, "maxAge": 240, "includeSwapDate": True})

        self.verify.check_sim_swap(PHONE, include_swap_date=False)
        self.assertEqual(self.last()[1]["json"], {"phoneNumber": PHONE, "includeSwapDate": False})

        self.verify.check_sim_swap(PHONE)
        self.assertEqual(self.last()[1]["json"], {"phoneNumber": PHONE})
        with self.assertRaisesRegex(SignalHouseValidationError, "phoneNumber"):
            self.verify.check_sim_swap("")

    def test_start_number_verification_posts_hint_and_redirect(self):
        self.verify.start_number_verification(PHONE, device_phone_number=PHONE, redirect_url="https://example.com/done")
        path, call = self.last()
        self.assertEqual((path, call["method"]), ("/verify/number", "POST"))
        self.assertEqual(call["json"], {"phoneNumber": PHONE, "devicePhoneNumber": PHONE, "redirectUrl": "https://example.com/done"})

        self.verify.start_number_verification(PHONE, token="session")
        path, call = self.last()
        self.assertEqual(call["json"], {"phoneNumber": PHONE})
        self.assertEqual(call["headers"]["Authorization"], "Bearer session")
        with self.assertRaisesRegex(SignalHouseValidationError, "phoneNumber"):
            self.verify.start_number_verification(None)

    def test_get_number_verification_reads_the_encoded_check(self):
        self.verify.get_number_verification("NVC1/2")
        _, call = self.last()
        self.assertEqual(call["url"], "https://example.invalid/verify/number/NVC1%2F2")
        self.assertEqual(call["method"], "GET")
        self.assertIsNone(call["json"])
        with self.assertRaisesRegex(SignalHouseValidationError, "checkId"):
            self.verify.get_number_verification("")


if __name__ == "__main__":
    unittest.main()
