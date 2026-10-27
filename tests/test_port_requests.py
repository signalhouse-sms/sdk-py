"""Request-contract coverage for the port-in list's excludeDocuments flag."""
import unittest
from urllib.parse import parse_qs, urlsplit

from test_canada import CaptureClient, load_domain


class PortRequestContracts(unittest.TestCase):
    def test_exclude_documents_is_sent_lowercase(self):
        """The API reads "true"/"false", not Python's "True"/"False"."""
        for value, expected in ((True, "true"), (False, "false")):
            with self.subTest(value=value):
                client = CaptureClient()
                load_domain("numbers").Numbers(client).get_port_requests(group_id="G0000001", exclude_documents=value)
                path, _ = client.calls[0]
                self.assertEqual(urlsplit(path).path, "/number/portin")
                self.assertEqual(parse_qs(urlsplit(path).query)["excludeDocuments"], [expected])

    def test_exclude_documents_is_omitted_by_default(self):
        """Callers that do not pass the flag get the unchanged request."""
        client = CaptureClient()
        load_domain("numbers").Numbers(client).get_port_requests(group_id="G0000001")
        path, _ = client.calls[0]
        self.assertNotIn("excludeDocuments", parse_qs(urlsplit(path).query))


if __name__ == "__main__":
    unittest.main()
