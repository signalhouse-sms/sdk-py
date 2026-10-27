"""Request-contract coverage for Canadian purchases and message estimates."""
import importlib.util
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlencode, urlsplit


def load_domain(name):
    """Load a domain without constructing an authenticated network client."""
    path = Path(__file__).resolve().parents[1] / "signalhouse_sms" / "domains" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaptureClient:
    """Capture serialized requests without sending them."""
    _enable_admin = False
    enable_admin = False

    def __init__(self):
        self.calls = []

    def _require(self, values):
        pass

    def _request(self, path, **kwargs):
        self.calls.append((path, kwargs))
        return {"success": True}

    def _get_query_string(self, values):
        """Serialize optional filters for the captured request."""
        return "?" + urlencode({key: value for key, value in values.items() if value is not None})


class CanadaContracts(unittest.TestCase):
    def test_city_availability_preserves_country_and_request_options(self):
        """Canadian and US city searches retain geography and token overrides."""
        for country, state, city in (("CA", "QC", "Charny"), ("US", "TX", "Austin")):
            with self.subTest(country=country):
                client = CaptureClient()
                load_domain("numbers").Numbers(client).get_available_phone_numbers(
                    country=country, state=state, city=city, limit=10, token="test-token"
                )
                path, request = client.calls[0]
                query = parse_qs(urlsplit(path).query)
                self.assertEqual(urlsplit(path).path, "/number/available")
                self.assertEqual((query["country"], query["state"], query["city"]), ([country], [state], [city]))
                self.assertEqual(query["limit"], ["10"])
                self.assertEqual(request["token"], "test-token")

    def test_purchase_defaults_and_canada(self):
        """Both purchase endpoints serialize explicit CA and legacy US defaults."""
        for country in (None, "CA"):
            for method, first, path in (
                ("purchase_phone_number", ["14165550118"], "/number"),
                ("purchase_toll_free_numbers", 2, "/number/toll-free"),
            ):
                with self.subTest(country=country, method=method):
                    client = CaptureClient()
                    domain = load_domain("numbers").Numbers(client)
                    options = {"country": country} if country else {}
                    getattr(domain, method)(first, "S0000001", **options)
                    self.assertEqual(client.calls[0][0], path)
                    self.assertEqual(client.calls[0][1]["body"]["country"], country or "US")

    def test_mms_estimate(self):
        """MMS estimates preserve body, recipients, type and token override."""
        client = CaptureClient()
        load_domain("messages").Messages(client).estimate_message(
            "14165550118", ["16045550118"], "", message_type="MMS", token="test-token"
        )
        path, request = client.calls[0]
        self.assertEqual(path, "/message/estimate")
        self.assertEqual(request["token"], "test-token")
        self.assertEqual(request["body"], {
            "senderPhoneNumber": "14165550118", "recipientPhoneNumbers": ["16045550118"],
            "messageBody": "", "messageType": "MMS",
        })


if __name__ == "__main__":
    unittest.main()
