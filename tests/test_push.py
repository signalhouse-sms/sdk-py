"""sdk.voice.push_credentials and sdk.voice.push_devices send each request to the right path, method and body."""
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

CRED_ID = "5a3c2f8e-1b7d-4c9a-9e2f-0d4b6a8c1e33"


class CaptureSession:
    """Record each request and answer 200 with an empty JSON body."""

    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(status_code=200, json=lambda: {}, text="{}")


class PushTests(unittest.TestCase):
    def setUp(self):
        self.sdk = SignalHouseSDK(api_key="test", base_url="https://example.invalid")
        self.session = self.sdk._session = CaptureSession()

    def last(self):
        call = self.session.calls[-1]
        return call["method"], call["url"].replace("https://example.invalid", ""), call.get("json")

    def test_push_credentials_routes(self):
        creds = self.sdk.voice.push_credentials
        apns = {"provider": "apns", "keyId": "ABC123DEFG", "teamId": "TEAM123456", "bundleId": "com.example.app", "privateKey": "pem"}
        creds.list()
        self.assertEqual(self.last(), ("GET", "/voice/api/v1/push-credentials", None))
        creds.get(CRED_ID)
        self.assertEqual(self.last()[:2], ("GET", f"/voice/api/v1/push-credentials/{CRED_ID}"))
        creds.create(apns)
        self.assertEqual(self.last(), ("POST", "/voice/api/v1/push-credentials", apns))
        creds.update(CRED_ID, {"provider": "fcm", "serviceAccount": "{}"})
        self.assertEqual(self.last(), ("PUT", f"/voice/api/v1/push-credentials/{CRED_ID}", {"provider": "fcm", "serviceAccount": "{}"}))
        creds.delete(CRED_ID)
        self.assertEqual(self.last()[:2], ("DELETE", f"/voice/api/v1/push-credentials/{CRED_ID}"))

    def test_push_credentials_require_their_arguments(self):
        creds = self.sdk.voice.push_credentials
        with self.assertRaises(Exception):
            creds.get(None)
        with self.assertRaises(Exception):
            creds.create(None)

    def test_push_devices_use_the_voice_token_and_escape_the_device_token(self):
        devices = self.sdk.voice.push_devices
        devices.register({"provider": "fcm", "deviceToken": "fcm:tok/1"}, token="voice-jwt")
        self.assertEqual(self.last(), ("POST", "/voice/api/v1/push-devices", {"provider": "fcm", "deviceToken": "fcm:tok/1"}))
        self.assertEqual(self.session.calls[-1]["headers"]["Authorization"], "Bearer voice-jwt")
        devices.unregister("fcm:tok/1", token="voice-jwt")
        self.assertEqual(self.last()[:2], ("DELETE", "/voice/api/v1/push-devices/fcm%3Atok%2F1"))
        devices.list_deliveries(limit=5, token="voice-jwt")
        self.assertEqual(self.last()[:2], ("GET", "/voice/api/v1/push-devices/deliveries?limit=5"))
        devices.list_deliveries(token="voice-jwt")
        self.assertEqual(self.last()[:2], ("GET", "/voice/api/v1/push-devices/deliveries"))


if __name__ == "__main__":
    unittest.main()
