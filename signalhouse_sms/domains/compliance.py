"""Compliance domain for the SignalHouse SDK."""

from __future__ import annotations

from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Compliance:
    """Compliance cases under /compliance.

    Signal House opens a case when a carrier suspends one of your objects, a
    carrier escalates a message, or Signal House needs something from you. You
    read your cases, answer their requirements and upload files; only Signal
    House opens, works and closes them.
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def get_cases(
        self,
        *,
        group_id: str | None = None,
        status: str | None = None,
        stage: str | None = None,
        object_type: str | None = None,
        object_id: str | None = None,
        subgroup_id: str | None = None,
        suspended: bool | None = None,
        from_: str | None = None,
        to: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """List the compliance cases you can see, newest first.

        ``counts.waitingOnYou`` is the open cases with requirements still to
        answer. Roles: api, admin, developer, billing, user.

        Args:
            group_id: A group you can view; defaults to your active group.
            status: OPEN, LIFT_REQUESTED or CLOSED.
            stage: new, customer, ready, lift_requested or closed.
            object_type: CAMPAIGN, BRAND, NUMBER, RCS_AGENT or SUBGROUP.
            object_id: The object's ID.
            subgroup_id: Only cases in this subgroup.
            suspended: True for cases with an open suspension or hold, False for the rest.
            from_: Opened on or after this ISO 8601 time (sent as ``from``).
            to: Opened on or before this ISO 8601 time.
            sort: createdAt (default), fixBy or severity.
            page: Page number, from 1.
            limit: Cases per page, 1-200.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is
            ``{data, total, page, limit, totalPages, counts: {open, waitingOnYou}}``.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "status": status,
            "stage": stage,
            "objectType": object_type,
            "objectId": object_id,
            "subgroupId": subgroup_id,
            "suspended": None if suspended is None else str(suspended).lower(),
            "from": from_,
            "to": to,
            "sort": sort,
            "page": page,
            "limit": limit,
        })
        return self._sdk._request(
            f"/compliance/cases{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_case(
        self,
        case_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get one compliance case: its stage, suspensions, tickets and requirements.

        Roles: api, admin, developer, billing, user.

        Args:
            case_id: The case ID (e.g. "CASE-12").
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is the case.

        Raises:
            SignalHouseValidationError: If case_id is missing.
        """
        self._sdk._require({"caseId": case_id})
        safe_case_id = quote(str(case_id), safe="")
        return self._sdk._request(
            f"/compliance/cases/{safe_case_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def answer_requirement(
        self,
        case_id: str,
        requirement_id: str,
        *,
        answer: str | None = None,
        file_ids: list[str] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Answer one requirement with a note, files, or both.

        A RECORDS requirement needs a file or a note. Roles: api, admin,
        developer, user.

        Args:
            case_id: The case ID (e.g. "CASE-12").
            requirement_id: The requirement ID (e.g. "CASE-12-1").
            answer: What you did, up to 2,000 characters.
            file_ids: Up to 10 fileIds from ``upload_file``, on this case.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is the case.

        Raises:
            SignalHouseValidationError: If case_id or requirement_id is missing.
        """
        self._sdk._require({"caseId": case_id, "requirementId": requirement_id})
        body: dict[str, Any] = {}
        if answer is not None:
            body["answer"] = answer
        if file_ids is not None:
            body["fileIds"] = file_ids
        safe_case_id = quote(str(case_id), safe="")
        safe_requirement_id = quote(str(requirement_id), safe="")
        return self._sdk._request(
            f"/compliance/cases/{safe_case_id}/requirements/{safe_requirement_id}",
            method="PUT",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def upload_file(
        self,
        case_id: str,
        file: BinaryIO | tuple,
        *,
        requirement_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Upload a file to a compliance case (CSV, XLSX, PDF, PNG, JPG or TXT, up to 10 MB).

        Pass the returned ``fileId`` in ``file_ids`` when you answer the
        requirement. Roles: api, admin, developer, user.

        Args:
            case_id: The case the file answers.
            file: The file to upload. Can be a file-like object or a tuple of
                  (filename, file_object, content_type). The API recognizes a
                  CSV or TXT by its filename, so pass the tuple for a file-like
                  object that has no name, such as ``io.BytesIO``.
            requirement_id: The requirement the file answers.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is ``{fileId, fileName, mimeType, size}``.

        Raises:
            SignalHouseValidationError: If case_id or file is missing.
        """
        self._sdk._require({"caseId": case_id, "file": file})
        form_data: dict[str, Any] = {"caseId": case_id}
        if requirement_id:
            form_data["requirementId"] = requirement_id
        files_list: list[tuple[str, Any]] = [("file", file)]
        return self._sdk._multipart_request(
            "/compliance/files",
            method="POST",
            form_data=form_data,
            files=files_list,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_file(
        self,
        file_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Download a compliance file.

        Roles: api, admin, developer, billing, user.

        Args:
            file_id: The ``fileId`` returned by ``upload_file``.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict; data is the file as ``bytes``.

        Raises:
            SignalHouseValidationError: If file_id is missing.
        """
        self._sdk._require({"fileId": file_id})
        safe_file_id = quote(str(file_id), safe="")
        return self._sdk._request(
            f"/compliance/files/{safe_file_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
            raw=True,
        )
