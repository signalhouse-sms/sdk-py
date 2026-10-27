"""Templates domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

from ..exceptions import SignalHouseValidationError

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class _Unset:
    """Marker for an argument the caller left out, distinct from an explicit None."""

    def __repr__(self) -> str:
        return "UNSET"


_UNSET: Any = _Unset()


def _create_payload(
    group_id: str,
    name: str,
    body: dict[str, Any],
    tag: str | None,
) -> dict[str, Any]:
    """Build a create request body, omitting unset optionals.

    Args:
        group_id: The group that owns the template.
        name: The template name.
        body: The raw template body.
        tag: Optional tag.

    Returns:
        The JSON request body.
    """
    payload: dict[str, Any] = {"groupId": group_id, "name": name, "body": body}
    if tag is not None:
        payload["tag"] = tag
    return payload


def _update_payload(
    group_id: str,
    name: str | None,
    tag: Any,
    body: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build an update request body; an explicit None tag clears it and _UNSET leaves it out.

    Args:
        group_id: The group that owns the template.
        name: A new template name, or None to keep it.
        tag: A new tag, None to clear it, or _UNSET to keep it.
        body: A full replacement body, or None to keep it.

    Returns:
        The JSON request body.
    """
    payload: dict[str, Any] = {"groupId": group_id}
    if name is not None:
        payload["name"] = name
    if tag is not _UNSET:
        payload["tag"] = tag
    if body is not None:
        payload["body"] = body
    return payload


def _validate_payload(group_id: str, body: dict[str, Any] | None, version: int | str | None) -> dict[str, Any]:
    """Build a validate request body from exactly one of body or version.

    Args:
        group_id: The group that owns the template.
        body: A candidate body.
        version: A stored version selector.

    Returns:
        The JSON request body.

    Raises:
        SignalHouseValidationError: If not exactly one of body or version is given.
    """
    if (body is None) == (version is None):
        raise SignalHouseValidationError("Pass exactly one of body or version")
    return {"groupId": group_id, "body": body} if body is not None else {"groupId": group_id, "version": version}


def _media_files(file: BinaryIO | bytes | tuple, file_name: str | None) -> list[tuple[str, Any]]:
    """Build the multipart file part, naming it file_name unless file is already a tuple.

    Args:
        file: A file-like object, bytes, or a (filename, file_object, content_type) tuple.
        file_name: The filename to send when file is not a tuple.

    Returns:
        The files list for a multipart request.
    """
    return [("file", file if isinstance(file, tuple) or file_name is None else (file_name, file))]


class Templates:
    """Versioned message templates: drafts, publication, archiving, validation and template media.

    Writes apply directly (last write wins): a 409 means the template is archived
    (TEMPLATE_ARCHIVED), the name is taken (TEMPLATE_NAME_TAKEN), there is no draft
    to publish (NO_DRAFT) or the draft changed while it was being published (DRAFT_CHANGED;
    publish again).
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def create(
        self,
        *,
        group_id: str,
        name: str,
        body: dict[str, Any],
        tag: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a template whose first draft (version 1) holds the given body.

        Args:
            group_id: The group that owns the template.
            name: The template name (1-120 chars, unique per group and channel).
            body: The raw template body, e.g. an RcsTemplateBody {channel, contentFormat, content, variables, defaults, fallback}.
            tag: Optional tag (1-60 chars).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {head, version} (201).

        Raises:
            SignalHouseValidationError: If group_id, name or body is missing.
        """
        self._sdk._require({"groupId": group_id, "name": name, "body": body})
        return self._sdk._request(
            "/template",
            method="POST",
            body=_create_payload(group_id, name, body, tag),
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        group_id: str,
        state: str | None = None,
        channel: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List a group's templates with optional filters and pagination.

        Args:
            group_id: The group whose templates to list.
            state: Filter by DRAFT, PUBLISHED or ARCHIVED.
            channel: Filter by channel ("rcs").
            tag: Filter by tag.
            search: Free-text name search.
            sort_by: name, createdAt or updatedAt.
            sort_order: asc or desc.
            page: The page number (default 1).
            limit: Items per page (default 25, max 100).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {data: [TemplateSummary], total, page, limit}.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "state": state,
            "channel": channel,
            "tag": tag,
            "search": search,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/template{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get(
        self,
        template_id: str,
        *,
        group_id: str,
        version: int | str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a template's head and one of its versions.

        Args:
            template_id: The template ID.
            group_id: The group that owns the template.
            version: A version number, "draft" or "published"; omitted reads the published version, else the draft.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {head, version}.

        Raises:
            SignalHouseValidationError: If template_id or group_id is missing.
        """
        self._sdk._require({"templateId": template_id, "groupId": group_id})
        safe_template_id = quote(str(template_id), safe="")
        query_string = self._sdk._get_query_string({"groupId": group_id, "version": version})
        return self._sdk._request(
            f"/template/{safe_template_id}{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def update(
        self,
        template_id: str,
        *,
        group_id: str,
        name: str | None = None,
        tag: str | None = _UNSET,
        body: dict[str, Any] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Save the template's draft, creating one from the published version when none exists.

        Args:
            template_id: The template ID.
            group_id: The group that owns the template.
            name: A new template name; a name another template already uses answers 409 TEMPLATE_NAME_TAKEN.
            tag: A new tag; None clears it and leaving it out keeps it.
            body: A full replacement body.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {head, version}; an archived template answers 409 TEMPLATE_ARCHIVED.

        Raises:
            SignalHouseValidationError: If template_id or group_id is missing.
        """
        self._sdk._require({"templateId": template_id, "groupId": group_id})
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/template/{safe_template_id}",
            method="PUT",
            body=_update_payload(group_id, name, tag, body),
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def publish(
        self,
        template_id: str,
        *,
        group_id: str,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Publish the template's current draft.

        Args:
            template_id: The template ID.
            group_id: The group that owns the template.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {head, version}; an incomplete draft answers 400 TEMPLATE_INVALID,
            a template with no draft answers 409 NO_DRAFT, and a draft that changed while it was being published
            answers 409 DRAFT_CHANGED (publish again).

        Raises:
            SignalHouseValidationError: If template_id or group_id is missing.
        """
        self._sdk._require({"templateId": template_id, "groupId": group_id})
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/template/{safe_template_id}/publish",
            method="POST",
            body={"groupId": group_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def archive(
        self,
        template_id: str,
        *,
        group_id: str,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Archive a template.

        Args:
            template_id: The template ID.
            group_id: The group that owns the template.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the template head; an already archived template answers 409 TEMPLATE_ARCHIVED.

        Raises:
            SignalHouseValidationError: If template_id or group_id is missing.
        """
        self._sdk._require({"templateId": template_id, "groupId": group_id})
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/template/{safe_template_id}/archive",
            method="POST",
            body={"groupId": group_id},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def versions(
        self,
        template_id: str,
        *,
        group_id: str,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List a template's versions without their bodies.

        Args:
            template_id: The template ID.
            group_id: The group that owns the template.
            page: The page number.
            limit: Items per page.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {data: [VersionSummary], total, page, limit}.

        Raises:
            SignalHouseValidationError: If template_id or group_id is missing.
        """
        self._sdk._require({"templateId": template_id, "groupId": group_id})
        safe_template_id = quote(str(template_id), safe="")
        query_string = self._sdk._get_query_string({"groupId": group_id, "page": page, "limit": limit})
        return self._sdk._request(
            f"/template/{safe_template_id}/versions{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def validate(
        self,
        template_id: str,
        *,
        group_id: str,
        body: dict[str, Any] | None = None,
        version: int | str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Run publication validation against a candidate body or a stored version without saving anything.

        Args:
            template_id: The template ID.
            group_id: The group that owns the template.
            body: A candidate body to validate; pass exactly one of body or version.
            version: A stored version number, "draft" or "published"; pass exactly one of body or version.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {valid, contentHash, validatorVersion, errors, warnings}.

        Raises:
            SignalHouseValidationError: If template_id or group_id is missing, or not exactly one of body or version is given.
        """
        self._sdk._require({"templateId": template_id, "groupId": group_id})
        payload = _validate_payload(group_id, body, version)
        safe_template_id = quote(str(template_id), safe="")
        return self._sdk._request(
            f"/template/{safe_template_id}/validate",
            method="POST",
            body=payload,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def capabilities(
        self,
        *,
        group_id: str,
        channel: str | None = None,
        provider: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the template features, limits and media rules the server enforces, optionally for one provider.

        Args:
            group_id: The group asking.
            channel: The template channel ("rcs", the default).
            provider: infobip or sinch, to include that provider's limits and unsupported features.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is the capabilities document.

        Raises:
            SignalHouseValidationError: If group_id is missing.
        """
        self._sdk._require({"groupId": group_id})
        query_string = self._sdk._get_query_string({"groupId": group_id, "channel": channel, "provider": provider})
        return self._sdk._request(
            f"/template/capabilities{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upload_media(
        self,
        *,
        group_id: str,
        file: BinaryIO | bytes | tuple,
        file_name: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Upload one media file for use in template bodies and get its public URL.

        Args:
            group_id: The group that owns the media.
            file: A file-like object, bytes, or a (filename, file_object, content_type) tuple.
            file_name: The filename to send when file is not already a tuple.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict whose data is {mediaId, groupId, url, bytes, mimeType, kind, width, height, createdAt} (201).

        Raises:
            SignalHouseValidationError: If group_id or file is missing.
        """
        self._sdk._require({"groupId": group_id, "file": file})
        return self._sdk._multipart_request(
            "/template/media",
            method="POST",
            form_data={"groupId": group_id},
            files=_media_files(file, file_name),
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
