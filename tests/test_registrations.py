"""Request-contract coverage for registrations and regional reporting filters."""
import importlib.util
import json
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
    enable_admin = True

    def __init__(self):
        self.calls = []

    def _require(self, values):
        if any(value is None or value == "" for value in values.values()):
            raise ValueError("Missing required field")

    def _request(self, path, **kwargs):
        self.calls.append((path, kwargs))
        return {"success": True}

    def _get_query_string(self, values):
        """Serialize optional filters for the captured request."""
        return "?" + urlencode({key: value for key, value in values.items() if value is not None}, doseq=True)


REPORT_METHODS = {
    "get_messages": "/message",
    "get_analytics": "/message/analytics",
    "get_analytics_detail": "/message/analytics/detail",
    "get_analytics_by_subgroup": "/message/analytics/by-subgroup",
    "get_analytics_by_error_code": "/message/analytics/by-error-code",
    "get_dnc_records": "/message/dnc",
    "get_dnc_analytics": "/message/dnc/analytics",
}


class RegistrationContracts(unittest.TestCase):
    def setUp(self):
        self.client = CaptureClient()

    def test_reporting_methods_serialize_region_and_json_scopes(self):
        """Every regional read repeats region values and JSON-encodes the scope branches."""
        domain = load_domain("messages").Messages(self.client)
        scopes = [{"region": "GB", "channels": ["virtualLongCode"], "phoneNumber": ["447400123456"]}]
        for method, expected_path in REPORT_METHODS.items():
            with self.subTest(method=method):
                getattr(domain, method)(group_id="G1", region=["US", "GB"], region_scopes=scopes, token="test-token")
                path, request = self.client.calls[-1]
                query = parse_qs(urlsplit(path).query)
                self.assertEqual(urlsplit(path).path, expected_path)
                self.assertEqual(query["region"], ["US", "GB"])
                self.assertEqual(json.loads(query["regionScopes"][0]), scopes)
                self.assertEqual(request["token"], "test-token")

    def test_empty_scopes_and_string_scopes_pass_through(self):
        """[] is sent as the JSON empty array and a pre-serialized string is not re-encoded."""
        domain = load_domain("messages").Messages(self.client)
        domain.get_messages(region_scopes=[])
        self.assertEqual(parse_qs(urlsplit(self.client.calls[-1][0]).query)["regionScopes"], ["[]"])
        domain.get_analytics(region_scopes='[{"region":"US","channels":["tenDLC"]}]')
        self.assertEqual(parse_qs(urlsplit(self.client.calls[-1][0]).query)["regionScopes"], ['[{"region":"US","channels":["tenDLC"]}]'])
        domain.get_dnc_records(group_id="G1")
        self.assertNotIn("region", parse_qs(urlsplit(self.client.calls[-1][0]).query))

    def test_filter_options_accept_region_only(self):
        domain = load_domain("messages").Messages(self.client)
        domain.get_analytics_filter_options(group_id="G1", region="GB")
        path, _ = self.client.calls[-1]
        self.assertEqual(urlsplit(path).path, "/message/analytics/filter-options")
        self.assertEqual(parse_qs(urlsplit(path).query), {"groupId": ["G1"], "region": ["GB"]})

    def test_analytics_methods_repeat_registration_id(self):
        """Every registration-aware read sends registrationId as repeated keys, like campaignId."""
        domain = load_domain("messages").Messages(self.client)
        paths = {
            "get_analytics": "/message/analytics",
            "get_analytics_detail": "/message/analytics/detail",
            "get_analytics_throughput": "/message/analytics/throughput",
            "get_dnc_analytics": "/message/dnc/analytics",
            "get_analytics_by_subgroup": "/message/analytics/by-subgroup",
            "get_analytics_by_error_code": "/message/analytics/by-error-code",
            "get_dnc_records": "/message/dnc",
            "get_messages": "/message",
        }
        for method, expected_path in paths.items():
            with self.subTest(method=method):
                getattr(domain, method)(group_id="G1", campaign_id="C1", registration_id=["REG1", "REG2"],
                                        start_date="2026-09-01", end_date="2026-09-02")
                path, _ = self.client.calls[-1]
                query = parse_qs(urlsplit(path).query)
                self.assertEqual(urlsplit(path).path, expected_path)
                self.assertEqual(query["registrationId"], ["REG1", "REG2"])
                self.assertEqual(query["campaignId"], ["C1"])
                getattr(domain, method)(group_id="G1", start_date="2026-09-01", end_date="2026-09-02")
                self.assertNotIn("registrationId", parse_qs(urlsplit(self.client.calls[-1][0]).query))

    def test_phone_numbers_forward_registration_id(self):
        load_domain("numbers").Numbers(self.client).get_phone_numbers(campaign_id="C1", registration_id="REG1")
        path, _ = self.client.calls[-1]
        self.assertEqual(urlsplit(path).path, "/number")
        self.assertEqual(parse_qs(urlsplit(path).query), {"campaignId": ["C1"], "registrationId": ["REG1"]})

    def test_catalog_and_quotes_contracts(self):
        domain = load_domain("registrations").Registrations(self.client)
        domain.get_catalog("GB", token="test-token")
        path, request = self.client.calls[-1]
        self.assertEqual(urlsplit(path).path, "/registration/catalog")
        self.assertEqual(parse_qs(urlsplit(path).query), {"region": ["GB"]})
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["token"], "test-token")

        domain.get_quotes(region="GB", type="VIRTUAL_LONG_CODE", quantity=2)
        path, request = self.client.calls[-1]
        self.assertEqual(urlsplit(path).path, "/registration/quotes")
        self.assertEqual(parse_qs(urlsplit(path).query), {"region": ["GB"], "type": ["VIRTUAL_LONG_CODE"], "quantity": ["2"]})
        self.assertEqual(request["method"], "GET")
        domain.get_quotes(region="UK", type="VIRTUAL_LONG_CODE", group_id="G1")
        self.assertEqual(parse_qs(urlsplit(self.client.calls[-1][0]).query), {
            "region": ["UK"], "type": ["VIRTUAL_LONG_CODE"], "quantity": ["1"], "groupId": ["G1"],
        })

    def test_list_read_and_submission_contracts(self):
        domain = load_domain("registrations").Registrations(self.client)
        domain.get_registrations(
            group_id="G1", subgroup_id="S1", region=["GB", "CA"], type="VIRTUAL_LONG_CODE", kind="sender",
            status=["PENDING_PROVIDER", "APPROVED"], parent_registration_id="REG0", phone_number="15551234567",
            sort_by="status", sort_order="asc", page=2, limit=10,
        )
        path, _ = self.client.calls[-1]
        self.assertEqual(urlsplit(path).path, "/registration")
        self.assertIn("region=GB&region=CA", path)
        self.assertIn("status=PENDING_PROVIDER&status=APPROVED", path)
        self.assertEqual(parse_qs(urlsplit(path).query), {
            "groupId": ["G1"], "subgroupId": ["S1"], "region": ["GB", "CA"], "type": ["VIRTUAL_LONG_CODE"], "kind": ["sender"],
            "status": ["PENDING_PROVIDER", "APPROVED"], "parentRegistrationId": ["REG0"], "phoneNumber": ["15551234567"],
            "sortBy": ["status"], "sortOrder": ["asc"], "page": ["2"], "limit": ["10"],
        })
        domain.get_registrations()
        self.assertEqual(self.client.calls[-1][0], "/registration?")

        domain.get_registration("REG 1")
        self.assertEqual(self.client.calls[-1][0], "/registration/REG%201")

        domain.cancel_registration("GB8T9GTD5AZY", token="session")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/registration/GB8T9GTD5AZY")
        self.assertEqual(request["method"], "DELETE")

        data = {
            "region": "GB", "type": "VIRTUAL_LONG_CODE", "subgroupId": "S1",
            "capabilities": ["SMS"],
            "data": {"quantity": 1, "useCases": ["Support"]},
        }
        domain.create_registration(data, token="test-token")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/registration")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["body"], data)
        for legacy in ("quoteVersion", "version", "country", "quantity"):
            self.assertNotIn(legacy, request["body"])

    def test_staff_review_corrections_numbers_reconcile_and_application(self):
        domain = load_domain("registrations").Registrations(self.client)
        domain.admin.review_registration("REG1", "APPROVE")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/registration/REG1/review")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["body"], {"action": "APPROVE"})
        domain.admin.review_registration("REG1", "REJECT", "Not a business use case")
        self.assertEqual(self.client.calls[-1][1]["body"], {"action": "REJECT", "reason": "Not a business use case"})

        domain.admin.correct_registration("REG1", "Provider asked", {"useCases": ["Support"]})
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/registration/REG1/corrections")
        self.assertEqual(request["body"], {"reason": "Provider asked", "data": {"useCases": ["Support"]}})

        domain.admin.add_number("REG1", "447400123456")
        self.assertEqual(self.client.calls[-1][0], "/registration/REG1/numbers")
        self.assertEqual(self.client.calls[-1][1]["body"], {"phoneNumber": "447400123456"})

        domain.admin.reconcile("REG1", "ORDER-123")
        self.assertEqual(self.client.calls[-1][0], "/registration/REG1/reconcile")
        self.assertEqual(self.client.calls[-1][1]["body"], {"externalId": "ORDER-123"})
        self.assertNotIn("providerReference", self.client.calls[-1][1]["body"])

        domain.admin.get_application("REG1")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/registration/REG1/application?format=json")
        self.assertEqual(request["method"], "GET")

    def test_missing_identifier_and_staff_gate(self):
        self.client.enable_admin = False
        domain = load_domain("registrations").Registrations(self.client)
        self.assertIsNone(domain.admin)
        with self.assertRaises(ValueError):
            domain.get_registration("")
        with self.assertRaises(ValueError):
            domain.cancel_registration("")
        with self.assertRaises(ValueError):
            domain.get_catalog("")
        with self.assertRaises(ValueError):
            domain.get_quotes(region="GB", type="")

    def test_uk_estimate_keeps_the_shared_payload(self):
        """A +44 sender uses the same estimate body as Canada; the server decides the region."""
        load_domain("messages").Messages(self.client).estimate_message("447400123456", ["447911123456"], "Hello")
        path, request = self.client.calls[0]
        self.assertEqual(path, "/message/estimate")
        self.assertEqual(request["body"], {
            "senderPhoneNumber": "447400123456", "recipientPhoneNumbers": ["447911123456"],
            "messageBody": "Hello", "messageType": "SMS",
        })

    def test_gb_alphanumeric_sender_submission_posts_data_unchanged(self):
        data = {
            "region": "GB", "type": "ALPHANUMERIC_SENDER_ID", "subgroupId": "S1",
            "capabilities": ["SMS"],
            "data": {
                "requestedSenderId": "ACME", "trafficOrigin": "LOCAL", "trafficType": "TRANSACTIONAL",
                "companyName": "Acme Ltd", "companyCountry": "United Kingdom", "companyWebsite": "https://acme.example",
                "industry": "Retail", "senderRelationship": "Trading name of Acme Ltd",
                "messageExample": "Your Acme order has shipped.",
            },
        }
        load_domain("registrations").Registrations(self.client).create_registration(data)
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/registration")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["body"], data)


class ShortlinkOptOutContracts(unittest.TestCase):
    def setUp(self):
        self.client = CaptureClient()
        self.domain = load_domain("shortlinks").Shortlinks(self.client)

    def test_get_opt_out_encodes_the_code(self):
        self.domain.get_opt_out("ABC/1", token="session")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/shortlink/optout/ABC%2F1")
        self.assertEqual(request["method"], "GET")
        self.assertNotIn("body", request)
        self.assertEqual(request["token"], "session")

    def test_confirm_opt_out_posts_with_no_body(self):
        self.domain.confirm_opt_out("ABC/1")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/shortlink/optout/ABC%2F1")
        self.assertEqual(request["method"], "POST")
        self.assertNotIn("body", request)

    def test_opt_out_requires_a_code(self):
        with self.assertRaises(ValueError):
            self.domain.get_opt_out("")
        with self.assertRaises(ValueError):
            self.domain.confirm_opt_out("")


class TollFreeCarrierFilterContracts(unittest.TestCase):
    def setUp(self):
        self.client = CaptureClient()

    def test_list_methods_send_current_toll_free_carrier_lowercase(self):
        """The brand and number lists send "true"/"false", not Python's "True"/"False"."""
        lists = (
            (load_domain("brands").Brands(self.client), "get_brands", "/brand"),
            (load_domain("numbers").Numbers(self.client), "get_phone_numbers", "/number"),
        )
        for domain, method, expected_path in lists:
            for value, expected in ((True, "true"), (False, "false")):
                with self.subTest(method=method, value=value):
                    getattr(domain, method)(subgroup_id="S0000001", current_toll_free_carrier=value)
                    path, request = self.client.calls[-1]
                    self.assertEqual(urlsplit(path).path, expected_path)
                    self.assertEqual(request["method"], "GET")
                    self.assertEqual(parse_qs(urlsplit(path).query), {"subgroupId": ["S0000001"], "currentTollFreeCarrier": [expected]})

    def test_list_methods_omit_current_toll_free_carrier_by_default(self):
        """Callers that do not pass the flag get the unchanged request."""
        load_domain("brands").Brands(self.client).get_brands(group_id="G0000001")
        self.assertEqual(parse_qs(urlsplit(self.client.calls[-1][0]).query), {"groupId": ["G0000001"]})
        load_domain("numbers").Numbers(self.client).get_phone_numbers(group_id="G0000001")
        self.assertEqual(parse_qs(urlsplit(self.client.calls[-1][0]).query), {"groupId": ["G0000001"]})


class BusinessVerificationContracts(unittest.TestCase):
    def setUp(self):
        self.client = CaptureClient()
        self.domain = load_domain("brands").Brands(self.client)

    def test_get_business_verifications_encodes_the_group(self):
        """The list is a GET on the group's encoded path with no body."""
        self.domain.get_business_verifications("G0000001/x", token="session")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/business-verification/G0000001%2Fx")
        self.assertEqual(request["method"], "GET")
        self.assertNotIn("body", request)
        self.assertEqual(request["token"], "session")

    def test_create_business_verification_posts_the_details(self):
        """The create sends the details unchanged as the POST body and forwards the idempotency key."""
        details = {
            "businessName": "Acme Inc", "businessType": "CORPORATION", "industry": "RETAIL",
            "registrationType": "EIN", "registrationNumber": "12-3456789", "website": "https://acme.example",
            "street": "1 Main St", "city": "Austin", "state": "TX", "postalCode": "78701", "country": "US",
            "representative": {
                "firstName": "Ada", "lastName": "Lee", "email": "ada@acme.example", "phone": "+15125550100",
                "jobTitle": "Owner", "jobLevel": "CEO",
            },
        }
        self.domain.create_business_verification("G0000001", details, idempotency_key="key-1")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/business-verification/G0000001")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["body"], details)
        self.assertEqual(request["idempotency_key"], "key-1")

    def test_get_business_verification_reads_one_by_its_id(self):
        """The read is a GET on the group's and the business verification's encoded path with no body."""
        self.domain.get_business_verification("G0000001/x", "BV1/2", token="session")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/business-verification/G0000001%2Fx/BV1%2F2")
        self.assertEqual(request["method"], "GET")
        self.assertNotIn("body", request)
        self.assertEqual(request["token"], "session")

    def test_update_business_verification_puts_the_details(self):
        """The update sends the details unchanged as the PUT body on the business verification's path."""
        details = {"businessName": "Acme Inc", "registrationType": "EIN", "registrationNumber": "12-3456789"}
        self.domain.update_business_verification("G0000001", "BV1/2", details, idempotency_key="key-1")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/business-verification/G0000001/BV1%2F2")
        self.assertEqual(request["method"], "PUT")
        self.assertEqual(request["body"], details)
        self.assertEqual(request["idempotency_key"], "key-1")

    def test_business_verification_requires_the_group_id_and_details(self):
        with self.assertRaises(ValueError):
            self.domain.get_business_verifications("")
        with self.assertRaises(ValueError):
            self.domain.create_business_verification("", {"businessName": "Acme Inc"})
        with self.assertRaises(ValueError):
            self.domain.create_business_verification("G0000001", None)
        with self.assertRaises(ValueError):
            self.domain.get_business_verification("", "BV1")
        with self.assertRaises(ValueError):
            self.domain.get_business_verification("G0000001", "")
        with self.assertRaises(ValueError):
            self.domain.update_business_verification("", "BV1", {"businessName": "Acme Inc"})
        with self.assertRaises(ValueError):
            self.domain.update_business_verification("G0000001", "", {"businessName": "Acme Inc"})
        with self.assertRaises(ValueError):
            self.domain.update_business_verification("G0000001", "BV1", None)
        self.assertEqual(self.client.calls, [])

    def test_submit_business_verification_is_gone(self):
        """create_business_verification and update_business_verification replace it."""
        self.assertFalse(hasattr(self.domain, "submit_business_verification"))


class SubgroupBusinessVerificationContracts(unittest.TestCase):
    def setUp(self):
        self.client = CaptureClient()
        self.domain = load_domain("brands").Brands(self.client)

    def test_get_business_verifications_sends_the_subgroup_as_a_query(self):
        """A given subgroup goes, encoded, into the subgroupId query parameter of the list."""
        self.domain.get_business_verifications("G0000001", subgroup_id="S0000001/x", token="session")
        path, request = self.client.calls[-1]
        self.assertEqual(urlsplit(path).path, "/brand/business-verification/G0000001")
        self.assertEqual(urlsplit(path).query, "subgroupId=S0000001%2Fx")
        self.assertEqual(request["method"], "GET")
        self.assertNotIn("body", request)
        self.assertEqual(request["token"], "session")

    def test_create_business_verification_sends_the_subgroup_as_a_query(self):
        """A given subgroup goes into the query, never the body, and the idempotency key is forwarded."""
        details = {"businessName": "Acme Inc", "country": "US"}
        self.domain.create_business_verification("G0000001", details, subgroup_id="S0000001", idempotency_key="key-1")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/business-verification/G0000001?subgroupId=S0000001")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["body"], {"businessName": "Acme Inc", "country": "US"})
        self.assertEqual(request["idempotency_key"], "key-1")

    def test_business_verification_urls_are_unchanged_without_a_subgroup(self):
        """Without a subgroup neither method adds a query string."""
        self.domain.get_business_verifications("G0000001")
        self.domain.create_business_verification("G0000001", {"businessName": "Acme Inc"})
        self.assertEqual([path for path, _ in self.client.calls], ["/brand/business-verification/G0000001"] * 2)


class TollFreeIsvAccountContracts(unittest.TestCase):
    ACCOUNT_SID = "AC" + "0" * 32
    API_KEY_SID = "SK" + "1" * 32

    def setUp(self):
        self.client = CaptureClient()
        self.domain = load_domain("brands").Brands(self.client)

    def test_get_toll_free_isv_account_encodes_the_group(self):
        """The staff read is a GET on the group's encoded path with no body."""
        self.domain.get_toll_free_isv_account("G0000001/x", token="session")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/toll-free-isv-account/G0000001%2Fx")
        self.assertEqual(request["method"], "GET")
        self.assertNotIn("body", request)
        self.assertEqual(request["token"], "session")

    def test_set_toll_free_isv_account_puts_the_account_and_key(self):
        """The staff write sends the account and its API key as the PUT body and forwards the idempotency key."""
        self.domain.set_toll_free_isv_account("G0000001", self.ACCOUNT_SID, self.API_KEY_SID, "key-secret", idempotency_key="key-1")
        path, request = self.client.calls[-1]
        self.assertEqual(path, "/brand/toll-free-isv-account/G0000001")
        self.assertEqual(request["method"], "PUT")
        self.assertEqual(request["body"], {"accountSid": self.ACCOUNT_SID, "apiKeySid": self.API_KEY_SID, "apiKeySecret": "key-secret"})
        self.assertEqual(request["idempotency_key"], "key-1")

    def test_toll_free_isv_account_requires_the_group_account_and_key(self):
        """Each method refuses a missing argument before sending anything."""
        with self.assertRaises(ValueError):
            self.domain.get_toll_free_isv_account("")
        for missing in range(4):
            args = ["G0000001", self.ACCOUNT_SID, self.API_KEY_SID, "key-secret"]
            args[missing] = ""
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                self.domain.set_toll_free_isv_account(*args)
        self.assertEqual(self.client.calls, [])


if __name__ == "__main__":
    unittest.main()
