"""Core SignalHouse SDK client."""

from __future__ import annotations

import json
from typing import Any, BinaryIO
from urllib.parse import quote, urlencode

import requests

from .exceptions import SignalHouseValidationError
from .domains.agents import Agents
from .domains.auth import Auth
from .domains.billing import Billing
from .domains.brands import Brands
from .domains.campaigns import Campaigns
from .domains.groups import Groups
from .domains.landings import Landings
from .domains.messages import Messages
from .domains.notifications import Notifications
from .domains.numbers import Numbers
from .domains.registrations import Registrations
from .domains.onboarding import Onboarding
from .domains.shortlinks import Shortlinks
from .domains.subgroups import Subgroups
from .domains.subscriptions import Subscriptions
from .domains.templates import Templates
from .domains.tickets import Tickets
from .domains.users import Users
from .domains.voice import Voice
from .domains.webhooks import Webhooks


class SignalHouseSDK:
    """Initialize the SignalHouseSDK with the required configuration.

    Args:
        api_key: The API key for authenticating requests to the SignalHouse API.
        base_url: The base URL for the SignalHouse API (e.g., "https://v2.signalhouse.io").
        enable_admin: Whether to enable admin-only methods on supported domains.

    Raises:
        ValueError: If the API key or base URL is missing.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        enable_admin: bool = False,
    ) -> None:
        if not api_key:
            raise ValueError("API key is required to initialize SignalHouseSDK")
        if not base_url:
            raise ValueError("Base URL is required to initialize SignalHouseSDK")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.enable_admin = enable_admin

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

        # API Domains
        self.agents = Agents(self)
        self.auth = Auth(self)
        self.billing = Billing(self)
        self.brands = Brands(self)
        self.campaigns = Campaigns(self)
        self.groups = Groups(self)
        self.landings = Landings(self)
        self.messages = Messages(self)
        self.notifications = Notifications(self)
        self.numbers = Numbers(self)
        self.registrations = Registrations(self)
        self.onboarding = Onboarding(self)
        self.shortlinks = Shortlinks(self)
        self.subgroups = Subgroups(self)
        self.subscriptions = Subscriptions(self)
        self.templates = Templates(self)
        self.tickets = Tickets(self)
        self.users = Users(self)
        self.voice = Voice(self)
        self.webhooks = Webhooks(self)

    def _request(
        self,
        url: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        files: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the SignalHouse API.

        Args:
            url: The API endpoint path (e.g., "/auth").
            method: The HTTP method (GET, POST, PUT, DELETE).
            body: The request body as a dictionary.
            token: An optional bearer token to override the default API key.
            headers: Additional headers to include in the request.
            files: Files to upload (for multipart requests).
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            A standardized response dict with keys: success, data/error, status.
        """
        full_url = f"{self.base_url}{url}"

        req_headers: dict[str, str] = {}
        if token:
            req_headers["Authorization"] = f"Bearer {token}"
        if headers:
            req_headers.update(headers)
        if idempotency_key:
            req_headers["Idempotency-Key"] = idempotency_key

        try:
            if files is not None:
                # Multipart request — don't send Content-Type, let requests set it
                req_headers.pop("Content-Type", None)
                response = self._session.request(
                    method=method,
                    url=full_url,
                    data=body,
                    files=files,
                    headers=req_headers,
                )
            else:
                response = self._session.request(
                    method=method,
                    url=full_url,
                    json=body,
                    headers=req_headers,
                )

            if 200 <= response.status_code < 300:
                try:
                    data = response.json()
                except (ValueError, requests.exceptions.JSONDecodeError):
                    data = response.text
                return {"success": True, "data": data, "status": response.status_code}
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_data)
                except (ValueError, requests.exceptions.JSONDecodeError):
                    error_message = response.text or response.status_code
                return {"success": False, "error": error_message, "status": response.status_code}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status": None}

    def _multipart_request(
        self,
        url: str,
        method: str = "POST",
        form_data: dict[str, Any] | None = None,
        files: list[tuple[str, Any]] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Make a multipart/form-data request to the SignalHouse API.

        Args:
            url: The API endpoint path.
            method: The HTTP method.
            form_data: Form fields as a dictionary.
            files: Files to upload as a list of (field_name, file_or_tuple) pairs.
            token: An optional bearer token to override the default API key.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            A standardized response dict with keys: success, data/error, status.
        """
        full_url = f"{self.base_url}{url}"

        req_headers: dict[str, str] = {}
        if token:
            req_headers["Authorization"] = f"Bearer {token}"
        # Remove Content-Type so requests can set multipart boundary
        req_headers.pop("Content-Type", None)
        if headers:
            req_headers.update(headers)
        if idempotency_key:
            req_headers["Idempotency-Key"] = idempotency_key

        try:
            response = self._session.request(
                method=method,
                url=full_url,
                data=form_data,
                files=files or [],
                headers=req_headers,
            )

            if 200 <= response.status_code < 300:
                try:
                    data = response.json()
                except (ValueError, requests.exceptions.JSONDecodeError):
                    data = response.text
                return {"success": True, "data": data, "status": response.status_code}
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_data)
                except (ValueError, requests.exceptions.JSONDecodeError):
                    error_message = response.text or response.status_code
                return {"success": False, "error": error_message, "status": response.status_code}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status": None}

    @staticmethod
    def _get_query_string(params: dict[str, Any]) -> str:
        """Convert a dictionary to a query string, excluding None values and the 'options' key.

        Args:
            params: The dictionary of query parameters.

        Returns:
            The query string (e.g., "?key=value&key2=value2"), or empty string if no params.
        """
        filtered = {
            k: v for k, v in params.items()
            if v is not None and k != "options"
        }
        if not filtered:
            return ""
        return f"?{urlencode(filtered, doseq=True)}"

    @staticmethod
    def _require(fields: dict[str, Any]) -> None:
        """Validate that required fields are present and non-empty.

        Args:
            fields: A dictionary where keys are field names and values are the values to check.

        Raises:
            SignalHouseValidationError: If any required field is missing or empty.
        """
        for name, value in fields.items():
            if value is None or value == "":
                raise SignalHouseValidationError(f"Missing required parameter: {name}")
