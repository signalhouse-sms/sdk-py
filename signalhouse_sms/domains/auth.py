"""Auth domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class AuthAdmin:
    """Admin-only authentication operations (SignalHouse staff)."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def reset_user_two_factor(
        self,
        user_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Turn off two-factor authentication for a user who has lost every factor (lockout recovery).

        Clears their methods, backup codes and trusted devices. Audited.

        Args:
            user_id: The id of the user to reset.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"reset": True}).

        Raises:
            SignalHouseValidationError: If user_id is missing.
        """
        self._sdk._require({"userId": user_id})
        safe_user_id = quote(str(user_id), safe="")
        return self._sdk._request(
            f"/auth/2fa/users/{safe_user_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )


class Auth:
    """Authentication operations including login, password reset, and auth history."""

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk
        self.admin: AuthAdmin | None = None
        if sdk.enable_admin:
            self.admin = AuthAdmin(sdk)

    def login(
        self,
        email: str,
        password: str,
        device_token: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Login with email and password.

        Args:
            email: The user's email address.
            password: The user's password.
            device_token: A trusted-device token from an earlier verify_two_factor_challenge; skips 2FA while valid.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict: {"token": ...}, or {"mfaRequired": True, "challengeId": ..., ...}
            when the account has 2FA on, or {"token": ..., "twoFactorSetupRequired": True} (a setup-only
            session) when the user's group requires 2FA and they haven't turned it on.
        """
        body: dict[str, Any] = {"email": email, "password": password}
        if device_token is not None:
            body["deviceToken"] = device_token
        return self._sdk._request(
            "/auth",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reset_password(
        self,
        user_id: str,
        new_password: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reset a user's password.

        Args:
            user_id: The id of the user.
            new_password: The new password to set for the user.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If user_id or new_password is missing.
        """
        self._sdk._require({"userId": user_id, "newPassword": new_password})
        safe_user_id = quote(str(user_id), safe="")
        return self._sdk._request(
            f"/auth/resetpassword/{safe_user_id}",
            method="PUT",
            body={"newPassword": new_password},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def forgot_password(
        self,
        email: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Request a password-reset link be emailed to the given address (public).

        Always resolves successfully regardless of whether an account exists for the
        email, so it cannot be used to enumerate registered emails.

        Args:
            email: The email address to send a reset link to.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"success": True}).

        Raises:
            SignalHouseValidationError: If email is missing.
        """
        self._sdk._require({"email": email})
        return self._sdk._request(
            "/auth/forgot-password",
            method="POST",
            body={"email": email},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def reset_password_with_token(
        self,
        token_value: str,
        password: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reset a password using the single-use token from a reset email (public).

        Args:
            token_value: The single-use reset token from the email link.
            password: The new password to set (min 8 characters).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"success": True}).

        Raises:
            SignalHouseValidationError: If token_value or password is missing.
        """
        self._sdk._require({"token": token_value, "password": password})
        return self._sdk._request(
            "/auth/reset-password",
            method="POST",
            body={"token": token_value, "password": password},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_auth_history(
        self,
        *,
        group_id: str | None = None,
        user_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get token login history for a group or user.

        Args:
            group_id: Returns history for all users in the group (one of group_id/user_id required).
            user_id: Returns history for a specific user (one of group_id/user_id required).
            page: Page number (min 1, default 1).
            limit: Results per page (min 1, max 100, default 20).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If neither group_id nor user_id is provided.
        """
        self._sdk._require({"groupId or userId": group_id or user_id})
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "userId": user_id,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/auth/history{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def logout_all(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Log out all other users in the caller's active group.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing loggedOutCount.
        """
        return self._sdk._request(
            "/auth/logout-all",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_group_id(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the Group ID associated with the caller's JWT (their active group).

        Useful for discovering your own group_id, which is required on most other requests.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing {"groupId": ...}.
        """
        return self._sdk._request(
            "/auth/group-id",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def request_external_link_token(
        self,
        product: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Mint a single-use, short-lived external-link token for the authenticated caller.

        The token is handed to the GHL/Shopify backend so it can link the caller's existing
        V2 group to its tenant.

        Args:
            product: The external system to link to ("ghl" or "shopify").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"token": ...}).

        Raises:
            SignalHouseValidationError: If product is missing.
        """
        self._sdk._require({"product": product})
        return self._sdk._request(
            "/auth/external-link-token",
            method="POST",
            body={"product": product},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_oauth_providers(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the OAuth sign-in providers enabled on this API.

        Only providers with credentials configured are returned.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ([{"id": ..., "label": ...}]).
        """
        return self._sdk._request(
            "/auth/oauth/providers",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_oauth_authorization_url(
        self,
        provider: str,
        next: str | None = None,
        email: str | None = None,
        link_ticket: str | None = None,
        reauth_ticket: str | None = None,
    ) -> str:
        """Build the URL that starts an OAuth sign-in.

        Navigate a browser to it; it is a redirect, not an API call. The API returns the user to
        the portal's /auth/callback with a single-use ticket. With a link_ticket (from
        create_oauth_link) it links the provider to the signed-in account instead, and the API
        returns the user to /Settings/Security with a single-use `pendingLink` (pass it to
        confirm_oauth_link to finish linking) or `linkError`. With a reauth_ticket (from
        create_oauth_reauth) the signed-in user signs in again with a linked provider to confirm
        it's them, and the API returns them to /Settings/Security with a single-use `pendingReauth` (the session that started it redeems it with confirm_oauth_reauth) or
        `reauthError`.

        Args:
            provider: The provider id ("google", "microsoft", "apple" or "sso" for Enterprise SSO).
            next: A same-site path (e.g. "/oauth/consent?request=abc") to return the user to
                after sign-in. The API hands it back on the /auth/callback redirect as `next`;
                anything that isn't a rooted path on the portal is dropped.
            email: Required for "sso" sign-in: the user's work email, whose domain picks the
                organization's identity provider. Not needed with a reauth_ticket.
            link_ticket: Link the provider to the signed-in account that requested this ticket
                (from create_oauth_link). Serialized as ``linkTicket``.
            reauth_ticket: Sign in again with a linked provider to confirm it's the account that
                requested this ticket (from create_oauth_reauth). Serialized as ``reauthTicket``.

        Returns:
            The absolute authorization URL.

        Raises:
            SignalHouseValidationError: If provider is missing.
        """
        self._sdk._require({"provider": provider})
        safe_provider = quote(str(provider), safe="")
        params = [
            f"{key}={quote(str(value), safe='')}"
            for key, value in (("email", email), ("linkTicket", link_ticket), ("reauthTicket", reauth_ticket), ("next", next))
            if value
        ]
        query = f"?{'&'.join(params)}" if params else ""
        return f"{self._sdk.base_url}/auth/oauth/{safe_provider}{query}"

    def get_oauth_links(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the caller's sign-in methods.

        Reports whether the caller chose their own password (passwordKnown is False for an account
        created through a provider or Enterprise SSO), and every provider linked to the account.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"passwordKnown": ..., "links": [{"provider": ..., "email": ..., "linkedAt": ..., "lastLoginAt": ...}]}).
        """
        return self._sdk._request(
            "/auth/oauth/links",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_oauth_link(
        self,
        provider: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Start linking Google, Microsoft or Apple to the caller's account.

        Returns a single-use link ticket (valid 2 minutes): navigate the browser to
        get_oauth_authorization_url(provider, link_ticket=...). Requires a fresh
        confirm_two_factor_identity from the same session, which this spends.

        Args:
            provider: "google", "microsoft" or "apple".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"linkTicket": ..., "expiresInSeconds": ...}).

        Raises:
            SignalHouseValidationError: If provider is missing.
        """
        self._sdk._require({"provider": provider})
        safe_provider = quote(str(provider), safe="")
        return self._sdk._request(
            f"/auth/oauth/{safe_provider}/link",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def create_oauth_reauth(
        self,
        provider: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Start signing in again with a provider already linked to the caller's account.

        Confirms it's the caller without spending anything. Returns a single-use ticket (valid 2
        minutes): navigate the browser to get_oauth_authorization_url(provider, reauth_ticket=...).
        The provider asks for a fresh sign-in, and the API returns the browser to
        /Settings/Security with a single-use `pendingReauth` (the session that started it redeems it with confirm_oauth_reauth) or `reauthError` (reauth_wrong_account,
        reauth_unsupported, reauth_stale, invalid_state, sso_not_configured, access_denied or
        provider_error).

        Args:
            provider: "google", "microsoft", "apple" or "sso"; must be linked to the account.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"reauthTicket": ..., "reauthSecret": ..., "expiresInSeconds": ...}).
            Keep reauthSecret in the client that started the flow: it is returned only here, and
            confirm_oauth_reauth needs it.

        Raises:
            SignalHouseValidationError: If provider is missing.
        """
        self._sdk._require({"provider": provider})
        safe_provider = quote(str(provider), safe="")
        return self._sdk._request(
            f"/auth/oauth/{safe_provider}/reauth",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def confirm_oauth_reauth(
        self,
        pending_reauth: str,
        reauth_secret: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Finish signing in again with a linked provider.

        The round trip started with create_oauth_reauth returns the browser to
        /Settings/Security with a single-use `pendingReauth` (valid 5 minutes); this redeems it,
        but only for the same account and the same session that called create_oauth_reauth, so
        a re-sign-in completed in someone else's browser confirms nothing. Fails with 400 when it
        expired or was used, and 403 for another account or session.

        Args:
            pending_reauth: The `pendingReauth` query parameter from the redirect. Serialized as
                ``pendingReauth``.
            reauth_secret: The reauthSecret create_oauth_reauth returned. A wrong or missing
                secret is refused (403) and uses up the pending re-sign-in. Serialized as
                ``reauthSecret``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"identityConfirmed": ...}; True when 2FA is off, so it
            counts as a confirmed identity).

        Raises:
            SignalHouseValidationError: If pending_reauth or reauth_secret is missing.
        """
        self._sdk._require({"pendingReauth": pending_reauth, "reauthSecret": reauth_secret})
        return self._sdk._request(
            "/auth/oauth/reauth/confirm",
            method="POST",
            body={"pendingReauth": pending_reauth, "reauthSecret": reauth_secret},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def confirm_oauth_link(
        self,
        pending_link: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Finish linking a provider.

        The provider round trip started with create_oauth_link returns the browser to
        /Settings/Security with a single-use `pendingLink`; this links it, but only for the
        account the link was started for, so a link URL opened in someone else's browser can't
        attach their provider to your account.

        Args:
            pending_link: The `pendingLink` query parameter from the redirect. Serialized as
                ``pendingLink``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the caller's {"passwordKnown": ..., "links": [{"provider": ..., "email": ..., "linkedAt": ..., "lastLoginAt": ...}]}).

        Raises:
            SignalHouseValidationError: If pending_link is missing.
        """
        self._sdk._require({"pendingLink": pending_link})
        return self._sdk._request(
            "/auth/oauth/links/confirm",
            method="POST",
            body={"pendingLink": pending_link},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def delete_oauth_link(
        self,
        provider: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Unlink a provider from the caller's account.

        Refused (400) when it is the account's only way to sign in. Requires a fresh
        confirm_two_factor_identity from the same session.

        Args:
            provider: "google", "microsoft", "apple" or "sso".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the remaining {"passwordKnown": ..., "links": [...]}).

        Raises:
            SignalHouseValidationError: If provider is missing.
        """
        self._sdk._require({"provider": provider})
        safe_provider = quote(str(provider), safe="")
        return self._sdk._request(
            f"/auth/oauth/{safe_provider}/link",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def read_oauth_ticket(
        self,
        ticket: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Read what a single-use OAuth ticket resolves to, without consuming it.

        The kind is "session" (ready to exchange), "select" (pick one of several accounts) or
        "signup" (finish registration).

        Args:
            ticket: The ticket from the OAuth callback redirect.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"kind": ..., "provider": ..., "profile"?: ..., "accounts"?: ...}).

        Raises:
            SignalHouseValidationError: If ticket is missing.
        """
        self._sdk._require({"ticket": ticket})
        return self._sdk._request(
            "/auth/oauth/ticket",
            method="POST",
            body={"ticket": ticket},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def exchange_oauth_ticket(
        self,
        ticket: str,
        user_id: str | None = None,
        device_token: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Exchange a single-use "session" or "select" OAuth ticket for a JWT. Consumes the ticket.

        Args:
            ticket: The ticket from the OAuth callback redirect.
            user_id: Required for a "select" ticket: the chosen account from "accounts".
            device_token: A trusted-device token from an earlier verify_two_factor_challenge; skips 2FA while valid.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"token": ...}), or {"mfaRequired": True, ...} when the account has 2FA on.

        Raises:
            SignalHouseValidationError: If ticket is missing.
        """
        self._sdk._require({"ticket": ticket})
        body: dict[str, Any] = {"ticket": ticket}
        if user_id is not None:
            body["userId"] = user_id
        if device_token is not None:
            body["deviceToken"] = device_token
        return self._sdk._request(
            "/auth/oauth/exchange",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_two_factor_settings(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the caller's two-factor settings: methods (targets masked), default, backup-code counts, trusted devices.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the settings object).
        """
        return self._sdk._request(
            "/auth/2fa",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def confirm_two_factor_identity(
        self,
        password: str | None = None,
        code: str | None = None,
        method: str | None = None,
        using_backup_code: bool | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Confirm it's really the account owner before a sensitive change.

        Guards start_two_factor_enrollment, remove_two_factor_method, regenerate_backup_codes,
        disable_two_factor, create_oauth_link, delete_oauth_link, and groups.save_sso_connection /
        groups.delete_sso_connection. With 2FA on, pass a current code (or a backup code); with 2FA off,
        pass the account password, or, for an account without a password of its own (get_oauth_links
        returns passwordKnown False), the code from send_two_factor_identity_code("email") with
        method "email". A confirmation lasts 5 minutes, belongs to the session that made it, and unlocks
        exactly one change.

        Args:
            password: The account password. Required while 2FA is off.
            code: A code from an enrolled method, or a backup code. Required while 2FA is on.
            method: The method the code came from ("app", "sms" or "email"); defaults to the primary method.
            using_backup_code: True when code is a backup code.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"confirmed": True, "expiresInSeconds": ...}).
        """
        body: dict[str, Any] = {}
        for key, value in (
            ("password", password),
            ("code", code),
            ("method", method),
            ("usingBackupCode", using_backup_code),
        ):
            if value is not None:
                body[key] = value
        return self._sdk._request(
            "/auth/2fa/confirm-identity",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_two_factor_identity_code(
        self,
        method: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send a code by text or email to use with confirm_two_factor_identity (not needed for "app").

        Args:
            method: An enrolled "sms" or "email" method, or "email" for an account without a
                password of its own (get_oauth_links returns passwordKnown False).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"sent": ..., "target": ..., "expiresInSeconds"?: ...}).

        Raises:
            SignalHouseValidationError: If method is missing.
        """
        self._sdk._require({"method": method})
        return self._sdk._request(
            "/auth/2fa/confirm-identity/send",
            method="POST",
            body={"method": method},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def start_two_factor_enrollment(
        self,
        method: str,
        phone: str | None = None,
        address: str | None = None,
        device_name: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Start enrolling a two-factor method.

        For "app" the response carries the setup secret and otpauth URI; for "sms" and "email" a code is sent.
        Requires a fresh confirm_two_factor_identity from the same session (403 otherwise); each confirmation
        unlocks one change.

        Args:
            method: "app", "sms" or "email".
            phone: Required for "sms": the mobile number to send codes to.
            address: Required for "email": the address to send codes to.
            device_name: Optional label for an authenticator app.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"enrollmentId": ..., "secret"?: ..., "otpauthUri"?: ..., "sentTo"?: ...}).

        Raises:
            SignalHouseValidationError: If method is missing.
        """
        self._sdk._require({"method": method})
        body: dict[str, Any] = {"method": method}
        for key, value in (("phone", phone), ("address", address), ("deviceName", device_name)):
            if value is not None:
                body[key] = value
        return self._sdk._request(
            "/auth/2fa/enroll",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def confirm_two_factor_enrollment(
        self,
        enrollment_id: str,
        code: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Confirm a pending enrollment with its code. The first method turns 2FA on and returns backup codes.

        Args:
            enrollment_id: From start_two_factor_enrollment.
            code: The 6-digit code.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"settings": ..., "backupCodes": [...] | None}).

        Raises:
            SignalHouseValidationError: If enrollment_id or code is missing.
        """
        self._sdk._require({"enrollmentId": enrollment_id, "code": code})
        safe_id = quote(str(enrollment_id), safe="")
        return self._sdk._request(
            f"/auth/2fa/enroll/{safe_id}/verify",
            method="POST",
            body={"code": code},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def set_two_factor_primary_method(
        self,
        method: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Choose which enrolled method is offered first at sign-in.

        Args:
            method: An enrolled method: "app", "sms" or "email".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the settings object).

        Raises:
            SignalHouseValidationError: If method is missing.
        """
        self._sdk._require({"method": method})
        return self._sdk._request(
            "/auth/2fa/primary",
            method="PUT",
            body={"method": method},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def remove_two_factor_method(
        self,
        method: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Remove an enrolled two-factor method. Removing the last one turns 2FA off.

        Requires a fresh confirm_two_factor_identity from the same session (403 otherwise); each confirmation
        unlocks one change.

        Args:
            method: "app", "sms" or "email".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the settings object).

        Raises:
            SignalHouseValidationError: If method is missing.
        """
        self._sdk._require({"method": method})
        safe_method = quote(str(method), safe="")
        return self._sdk._request(
            f"/auth/2fa/methods/{safe_method}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def regenerate_backup_codes(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Replace all backup codes with a new set (shown only once); the previous codes stop working.

        Requires a fresh confirm_two_factor_identity from the same session (403 otherwise); each confirmation
        unlocks one change.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"codes": [...], "settings": ...}).
        """
        return self._sdk._request(
            "/auth/2fa/backup-codes",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def revoke_trusted_device(
        self,
        device_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Stop trusting a device, so its next sign-in asks for the second factor again.

        Args:
            device_id: The trusted device's id from get_two_factor_settings.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the settings object).

        Raises:
            SignalHouseValidationError: If device_id is missing.
        """
        self._sdk._require({"deviceId": device_id})
        safe_id = quote(str(device_id), safe="")
        return self._sdk._request(
            f"/auth/2fa/trusted-devices/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def disable_two_factor(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Turn two-factor authentication off: removes every method, backup code and trusted device.

        Requires a fresh confirm_two_factor_identity from the same session (403 otherwise); each confirmation
        unlocks one change.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict (the settings object).
        """
        return self._sdk._request(
            "/auth/2fa",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_two_factor_prompt(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Whether the "secure your account" enrollment prompt is due for the caller.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"due": ...}).
        """
        return self._sdk._request(
            "/auth/2fa/prompt",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def dismiss_two_factor_prompt(
        self,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Dismiss the enrollment prompt until the next sign-in; it stops for good after three dismissals.

        Args:
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"due": False}).
        """
        return self._sdk._request(
            "/auth/2fa/prompt/dismiss",
            method="POST",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_two_factor_challenge_code(
        self,
        challenge_id: str,
        method: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send a sign-in code by text or email for a pending two-factor challenge (not needed for "app").

        Args:
            challenge_id: From the mfaRequired login or exchange response.
            method: "sms" or "email".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"sent": ..., "target": ..., "expiresInSeconds": ...}).

        Raises:
            SignalHouseValidationError: If challenge_id or method is missing.
        """
        self._sdk._require({"challengeId": challenge_id, "method": method})
        safe_id = quote(str(challenge_id), safe="")
        return self._sdk._request(
            f"/auth/2fa/challenge/{safe_id}/send",
            method="POST",
            body={"method": method},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def verify_two_factor_challenge(
        self,
        challenge_id: str,
        code: str,
        method: str | None = None,
        using_backup_code: bool | None = None,
        remember_device: bool | None = None,
        device_name: str | None = None,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Verify a sign-in code (or backup code) for a pending challenge and receive the session JWT.

        Args:
            challenge_id: From the mfaRequired login or exchange response.
            code: The 6-digit code, or a backup code (xxxx-xxxx).
            method: The method the code came from ("app", "sms" or "email"); defaults to the primary method.
            using_backup_code: True when code is a backup code.
            remember_device: Trust this device for 30 days (the response then carries a deviceToken).
            device_name: Label for the trusted device.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"token": ..., "deviceToken"?: ...}).

        Raises:
            SignalHouseValidationError: If challenge_id or code is missing.
        """
        self._sdk._require({"challengeId": challenge_id, "code": code})
        safe_id = quote(str(challenge_id), safe="")
        body: dict[str, Any] = {"code": code}
        for key, value in (
            ("method", method),
            ("usingBackupCode", using_backup_code),
            ("rememberDevice", remember_device),
            ("deviceName", device_name),
        ):
            if value is not None:
                body[key] = value
        return self._sdk._request(
            f"/auth/2fa/challenge/{safe_id}/verify",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def cancel_two_factor_challenge(
        self,
        challenge_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a pending two-factor challenge.

        Args:
            challenge_id: From the mfaRequired login or exchange response.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict ({"cancelled": True}).

        Raises:
            SignalHouseValidationError: If challenge_id is missing.
        """
        self._sdk._require({"challengeId": challenge_id})
        safe_id = quote(str(challenge_id), safe="")
        return self._sdk._request(
            f"/auth/2fa/challenge/{safe_id}",
            method="DELETE",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
