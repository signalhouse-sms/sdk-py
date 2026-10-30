"""Messages domain for the SignalHouse SDK."""

from __future__ import annotations

import json
from typing import Any, BinaryIO, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..client import SignalHouseSDK


class Messages:
    """SMS/MMS messaging operations with multipart file upload support.

    Business-number filters and SMS/MMS senders accept digits-only 5-6 digit
    Short Codes or 10+ digit long numbers. Recipient numbers remain 10+ digits.
    """

    def __init__(self, sdk: SignalHouseSDK) -> None:
        self._sdk = sdk

    def estimate_message(self, sender_phone_number: str, recipient_phone_numbers: list[str], message_body: str, *, message_type: str = "SMS", token: str | None = None, headers: dict[str, str] | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
        """Estimate Canadian or UK retail cost in microdollars; no charge or send.

        A Ready Canadian sender takes SMS or MMS to Canadian or US recipients; a UK (+44) virtual long code
        takes SMS only to GB mobile recipients (10-15 digits). The response `region` is "CA" or "GB". Unavailable
        unless that region is enabled for the environment. The sender may also be a READY alphanumeric sender ID
        (e.g. "ACME"; UK recipients, SMS only); its estimate counts the "\\nOpt out: sihou.io/o/{code}" footer the
        server appends to every such message.
        """
        return self._sdk._request("/message/estimate", method="POST", body={"senderPhoneNumber": sender_phone_number, "recipientPhoneNumbers": recipient_phone_numbers, "messageBody": message_body, "messageType": message_type}, token=token, headers=headers, idempotency_key=idempotency_key)

    def get_messages(
        self,
        *,
        id: str | None = None,
        campaign_id: str | None = None,
        registration_id: str | list[str] | None = None,
        brand_id: str | None = None,
        subgroup_id: str | None = None,
        group_id: str | None = None,
        phone_number: str | None = None,
        sender_phone_number: str | None = None,
        recipient_phone_number: str | None = None,
        status: str | None = None,
        direction: str | None = None,
        message_type: str | list[str] | None = None,
        carrier: str | None = None,
        sentiment_label: str | list[str] | None = None,
        error_code: str | list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        sort_field: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of messages with optional filters and pagination.

        Args:
            registration_id: Filter to messages attributed to these registrations. Cannot be combined with campaign_id; each id must belong to the group. Single value or list.
            id: Filter messages by their unique ID.
            campaign_id: Filter messages by the ID of the associated campaign.
            brand_id: Filter messages by the ID of the associated brand.
            subgroup_id: Filter messages by the ID of the associated subgroup.
            group_id: Filter messages by the ID of the associated group.
            status: Filter by status (ENQUEUED, DEQUEUED, SENT, FAILED, DELIVERED).
            direction: Filter by direction (INBOUND, OUTBOUND).
            message_type: Filter by type (SMS, MMS).
            channel: Filter by channel — "tenDLC", "virtualLongCode", "tollFree", "shortCode", or "p2p" (single value or list).
                Filters on each message's stored channel; older messages without one count as tenDLC.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing.
            carrier: Filter by carrier used for sending.
            sentiment_label: Filter by sentiment bucket — "positive", "neutral", or "negative"
                (single value or list). Applied as the sentimentScore range the ±25 label threshold
                produces, so unscored messages match no bucket and outbound messages are excluded.
            error_code: Filter FAILED messages by Signal House error code (single value or list). "OUT" is the
                campaign opt-out, displayed as RECIPIENT_OPTED_OUT. Carrier codes are not filterable
                here; they live inside successOrFailureReason.
            sender_phone_number: Filter by sender phone number. A plain value is an exact match; a
                value containing % is a wildcard for a partial match (e.g. "%1234" matches numbers
                ending in 1234). 3-15 digits are required alongside any %.
            recipient_phone_number: Filter by recipient phone number. A plain value is an exact
                match; a value containing % is a wildcard for a partial match (e.g. "%1234" matches
                numbers ending in 1234). 3-15 digits are required alongside any %.
            start_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode.
            end_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode. In "exact" mode day buckets align to the UTC offset this bound carries, so a client that sends its own midnights gets its own calendar dates back.
            sort_field: The field to sort by (createdAt, segmentCount, status, sentimentScore).
            sort_order: The sort order (asc, desc).
            page: The page number for pagination.
            limit: The number of messages per page.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. Inbound messages also carry sentimentScore (-100..100, None
            when unscored), sentimentLabel ("positive"/"neutral"/"negative", None when sentimentScore
            is None) and sentimentScoredAt. Outbound messages are never scored.
        """
        query_string = self._sdk._get_query_string({
            "id": id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "brandId": brand_id,
            "subgroupId": subgroup_id,
            "groupId": group_id,
            "phoneNumber": phone_number,
            "senderPhoneNumber": sender_phone_number,
            "recipientPhoneNumber": recipient_phone_number,
            "status": status,
            "direction": direction,
            "messageType": message_type,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "carrier": carrier,
            "sentimentLabel": sentiment_label,
            "errorCode": error_code,
            "startDate": start_date,
            "endDate": end_date,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "page": page,
            "limit": limit,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_analytics(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        brand_id: str | None = None,
        campaign_id: str | None = None,
        registration_id: str | list[str] | None = None,
        phone_number: str | None = None,
        carrier: str | None = None,
        carrier_family: str | list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        message_type: str | list[str] | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated analytics for messages with optional filters.

        Args:
            group_id: Filter analytics by group ID.
            subgroup_id: Filter analytics by subgroup ID.
            brand_id: Filter analytics by brand ID.
            campaign_id: Filter analytics by campaign ID.
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). A phoneNumber filter takes precedence. Single value or list.
            phone_number: Filter analytics by phone number.
            carrier: Filter analytics by carrier.
            carrier_family: Filter analytics by the recipient's resolved carrier family (Default, ATT, TMobile, Verizon, USCellular, GoogleVoice, ClearSky, Interop, RogueMobile, P2P, Standard, IceWireless, Bell, Rogers, Telus, Videotron, SaskTel, Eastlink, Fibernetics);
                single value or list. Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400 -- omit the parameter unless it is wanted.
            start_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode.
            end_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode. In "exact" mode day buckets align to the UTC offset this bound carries, so a client that sends its own midnights gets its own calendar dates back.
            channel: Filter by channel — "tenDLC", "virtualLongCode", "tollFree", "shortCode", or "p2p" (single value or list).
                Filters on the stored channel; a tenDLC selection also includes older messages with
                no channel, and p2p is matched by carrier.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing. Same hourly-analytics gate as region.
            message_type: Message type(s) the SENTIMENT figures are scoped to: SMS, MMS or P2P. Omit for all scored types. Does NOT narrow the message counts, which are always returned split per type and have no filterable type dimension.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. Also includes inbound-message sentiment for the requested
            scope: sentimentScore (volume-weighted average of every scored inbound message in range,
            -100..100, None when nothing was scored), sentimentLabel ("positive"/"neutral"/"negative",
            None when sentimentScore is None), sentimentScoredCount, sentimentPositive,
            sentimentNeutral, sentimentNegative. sentimentScore is an average, so it must never be
            summed across responses — request one range instead.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "phoneNumber": phone_number,
            "carrier": carrier,
            "carrierFamily": carrier_family,
            "startDate": start_date,
            "endDate": end_date,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "messageType": message_type,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message/analytics{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_analytics_detail(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        brand_id: str | None = None,
        campaign_id: str | None = None,
        registration_id: str | list[str] | None = None,
        phone_number: str | None = None,
        carrier: str | None = None,
        carrier_family: str | list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        message_type: str | list[str] | None = None,
        granularity: str | None = None,
        breakdown: str | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get detailed analytics snapshot records for charting and aggregation.

        Args:
            group_id: Filter analytics by group ID.
            subgroup_id: Filter analytics by subgroup ID.
            brand_id: Filter analytics by brand ID.
            campaign_id: Filter analytics by campaign ID.
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). A phoneNumber filter takes precedence. Single value or list.
            phone_number: Filter analytics by phone number.
            carrier: Filter analytics by carrier.
            carrier_family: Filter analytics by the recipient's resolved carrier family (Default, ATT, TMobile, Verizon, USCellular, GoogleVoice, ClearSky, Interop, RogueMobile, P2P, Standard, IceWireless, Bell, Rogers, Telus, Videotron, SaskTel, Eastlink, Fibernetics);
                single value or list. Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400 -- omit the parameter unless it is wanted.
            start_date: ISO-8601 date or timestamp. It is bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode, then floored to the start of its hour at either granularity, because the hourly cube is keyed by hour and a mid-hour start would drop that hour's bucket.
            end_date: ISO-8601 date or timestamp. At day granularity it is bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode. In "exact" mode day buckets align to the UTC offset this bound carries, so a client that sends its own midnights gets its own calendar dates back; at hour granularity it is honoured as given.
            channel: Filter by channel — "tenDLC", "virtualLongCode", "tollFree", "shortCode", or "p2p" (single value or list).
                Filters on the stored channel; a tenDLC selection also includes older messages with
                no channel, and p2p is a real channel here.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing. Same hourly-analytics gate as region.
            message_type: Message type(s) the SENTIMENT figures are scoped to: SMS, MMS or P2P. Omit for all scored types. Does NOT narrow the message counts, which are always returned split per type and have no filterable type dimension.
            granularity: Time-bucket grain of the byDate rows: "day" or "hour". Omit for day (each row's
                _id is a "YYYY-MM-DD" date). "hour" buckets by hour (each row's _id is a
                "YYYY-MM-DD HH:MM:SS" UTC hour) and is capped to a 7-day span. Only accepted where the
                environment serves hourly analytics; elsewhere any value, including "day", is rejected
                with a 400 -- omit the parameter unless hour grain is wanted.
            breakdown: "carrier" or "carrierFamily". Adds a byBreakdown time × dimension series to the
                response ({dimension, rows}: each row is one byDate bucket (_id) for one carrier or
                carrier family (key), top 50 keys by volume, excluding P2P) and caps the span at 31 days.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400 -- omit the parameter unless it is wanted.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with array of analytics snapshot records. cardTotals and every
            byDate/byPhoneNumber/byCarrier row also carry that row's own inbound-message sentiment:
            sentimentScore (volume-weighted average, -100..100, None when nothing in that row's scope
            was scored), sentimentLabel, sentimentScoredCount, sentimentPositive, sentimentNeutral,
            sentimentNegative. The fields are always present; sentimentScore is an average and must
            never be summed across rows or responses.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "phoneNumber": phone_number,
            "carrier": carrier,
            "carrierFamily": carrier_family,
            "startDate": start_date,
            "endDate": end_date,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "messageType": message_type,
            "granularity": granularity,
            "breakdown": breakdown,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message/analytics/detail{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_analytics_throughput(
        self,
        *,
        group_id: str,
        brand_id: str | list[str] | None = None,
        campaign_id: str | list[str] | None = None,
        registration_id: str | list[str] | None = None,
        carrier_family: str | list[str] | None = None,
        start_date: str,
        end_date: str,
        granularity: str | None = None,
        ceiling: int | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get per-minute send throughput per time bucket and per carrier family.

        Peak segments per minute, sending minutes and minutes at a ceiling, measured from SENT
        transitions at campaign x carrier-family grain -- the grain carrier ceilings are enforced
        at -- so a peak here is the figure a ceiling is compared against. Only accepted where the
        environment serves hourly analytics; elsewhere the request is rejected with a 400.

        Args:
            group_id: The group to scope the read to.
            brand_id: Brand scope (single value or list).
            campaign_id: Campaign scope; wins over brand_id (single value or list).
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). Single value or list.
            carrier_family: Carrier-family filter (ATT, TMobile, Verizon, USCellular, ...); single value or list.
            start_date: ISO-8601 date or timestamp. bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode, then
                floored to the start of its hour at hour granularity and of its minute at day granularity
                (the cube is keyed by minute).
            end_date: ISO-8601 date or timestamp. At hour granularity honoured as given; at day
                granularity bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode. In "exact" mode day buckets align to the UTC offset this bound carries, so a client that sends its own midnights gets its own calendar dates back. The span is capped at 35 days.
            granularity: Bucket grain of the byDate and byBreakdown rows: "hour" (default; each row's
                _id is a "YYYY-MM-DD HH:MM:SS" UTC hour, span capped at 7 days) or "day".
            ceiling: Segments-per-minute ceiling. When given, every row also reports minutesAtCeiling
                (sending minutes at or above it); otherwise minutesAtCeiling is None.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with totals, byDate, byCarrierFamily and byBreakdown
            ({dimension: "carrierFamily", rows}). Every row carries segments, messages,
            peakSegmentsPerMinute, peakMessagesPerMinute, peakMinute (UTC "YYYY-MM-DD HH:MM:SS",
            None when no traffic), sendingMinutes, averageSegmentsPerSendingMinute and
            minutesAtCeiling.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "carrierFamily": carrier_family,
            "startDate": start_date,
            "endDate": end_date,
            "granularity": granularity,
            "ceiling": ceiling,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message/analytics/throughput{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_analytics_filter_options(
        self,
        *,
        group_id: str,
        region: str | list[str] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get filter dropdown options (subgroups, brands, campaigns, phone numbers, carriers) for the
        Analytics page, scoped to a single group. Only items with
        at least one message are returned.

        Args:
            group_id: The ID of the group whose filter options to load.
            region: Restrict the options to one region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or
                list. Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with subgroups, brands, campaigns, phoneNumbers, and carriers arrays.
            Each phone number carries type (TOLL_FREE, SHORT_CODE, ALPHANUMERIC, VIRTUAL_LONG_NUMBER, ...) and
            country (ISO-2), None when unknown: TOLL_FREE, SHORT_CODE and ALPHANUMERIC are channels by type; any
            other US number is 10DLC and a non-US one is a Virtual Long Code. carriers is a plain array of
            carrier name strings.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "region": region,
        })
        return self._sdk._request(
            f"/message/analytics/filter-options{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_analytics_by_subgroup(
        self,
        *,
        group_id: str,
        subgroup_id: str | list[str] | None = None,
        brand_id: str | list[str] | None = None,
        campaign_id: str | list[str] | None = None,
        registration_id: str | list[str] | None = None,
        phone_number: str | list[str] | None = None,
        carrier: str | list[str] | None = None,
        carrier_family: str | list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        message_type: str | list[str] | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a paginated breakdown of message metrics grouped by subgroup. Each row
        carries the full set of sms/mms/p2p metric columns plus ``smsOptOuts`` and
        ``mmsOptOuts`` (sourced from the DNC analytics MV — P2P has no opt-outs) so
        callers can apply channel toggles client-side.

        Args:
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). A phoneNumber filter takes precedence. Single value or list.
            carrier_family: Filter analytics by the recipient's resolved carrier family (Default, ATT, TMobile, Verizon, USCellular, GoogleVoice, ClearSky, Interop, RogueMobile, P2P, Standard, IceWireless, Bell, Rogers, Telus, Videotron, SaskTel, Eastlink, Fibernetics);
                single value or list. Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400 -- omit the parameter unless it is wanted.
            page: Page number (default 1).
            limit: Rows per page, max 50.
            channel: "both" (default, all activity) or "tenDLC" / "virtualLongCode" / "tollFree" / "shortCode" / "p2p" (single value
                or list). Scopes the ORDER BY + row inclusion by the stored channel column so a
                single-channel caller doesn't get pages dominated by other channels; toll-free is
                kept separate from 10DLC.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing. Same hourly-analytics gate as region.
            message_type: Message type(s) the SENTIMENT figures are scoped to: SMS, MMS or P2P
                (single value or list). Omit for all scored types. Does NOT narrow the message
                counts, which are always returned split per type and have no filterable type
                dimension.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".

        Returns:
            Standardized response dict with rows, totalCount, page, and limit. Each row carries that
            subgroup's inbound-message sentiment alongside its message counters: sentimentScore
            (volume-weighted average of every scored inbound message in that subgroup, -100..100,
            None when nothing was scored), sentimentLabel, sentimentScoredCount, sentimentPositive,
            sentimentNeutral, sentimentNegative, plus the same six per message type under
            smsSentiment*, mmsSentiment* and p2pSentiment* prefixes. The score is derived
            server-side and must never be re-averaged across rows — combine the counts, not the
            scores.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "phoneNumber": phone_number,
            "carrier": carrier,
            "carrierFamily": carrier_family,
            "startDate": start_date,
            "endDate": end_date,
            "page": page,
            "limit": limit,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "messageType": message_type,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message/analytics/by-subgroup{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_analytics_by_error_code(
        self,
        *,
        group_id: str,
        subgroup_id: str | list[str] | None = None,
        brand_id: str | list[str] | None = None,
        campaign_id: str | list[str] | None = None,
        registration_id: str | list[str] | None = None,
        phone_number: str | list[str] | None = None,
        carrier: str | list[str] | None = None,
        carrier_family: str | list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        date_bounds: str | None = None,
        error_code: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a paginated breakdown of failed messages grouped by error code. Each row
        contains per-channel (sms/mms/p2p) error counts plus an enriched description.

        Args:
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). A phoneNumber filter takes precedence. Single value or list.
            carrier_family: Filter analytics by the recipient's resolved carrier family (Default, ATT, TMobile, Verizon, USCellular, GoogleVoice, ClearSky, Interop, RogueMobile, P2P, Standard, IceWireless, Bell, Rogers, Telus, Videotron, SaskTel, Eastlink, Fibernetics);
                single value or list. Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400 -- omit the parameter unless it is wanted.
            page: Page number (default 1).
            limit: Rows per page, max 50.
            channel: "both" (default, every code) or "tenDLC" / "virtualLongCode" / "tollFree" / "shortCode" / "p2p" (single value
                or list). Scopes the ORDER BY + totalCount by the stored channel column; when one
                channel is selected, totalErrors reflects only that channel.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing. Same hourly-analytics gate as region.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            error_code: Narrow the breakdown to a single failure reason: a numeric Infobip carrier code
                (as a string, e.g. "607"), the Signal House campaign-opt-out code "OUT", or a no-code
                failure class (other, moderation, att_limit, p2p_stop, campaign_opt_out, dnc_blocked,
                bind_hold_expired). Omitted: every reason.

        Returns:
            Standardized response dict with rows, totalCount, totalErrors, page, and limit.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "phoneNumber": phone_number,
            "carrier": carrier,
            "carrierFamily": carrier_family,
            "startDate": start_date,
            "endDate": end_date,
            "page": page,
            "limit": limit,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "dateBounds": date_bounds,
            "errorCode": error_code,
        })
        return self._sdk._request(
            f"/message/analytics/by-error-code{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_dnc_analytics(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        brand_id: str | None = None,
        campaign_id: str | None = None,
        registration_id: str | list[str] | None = None,
        phone_number: str | None = None,
        carrier: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated DNC (Do Not Contact) opt-out analytics with optional filters.

        Returns totals, byDate, byPhoneNumber, bySenderNumber, byCampaign, bySubgroup, byType,
        byCarrier, byKeyword. bySenderNumber ({senderPhoneNumber, total, sms, mms}) attributes each
        opt-out to the first business number that received it, so it is unchanged by later campaign
        moves and START replies. byCampaign counts campaign-scoped opt-outs only, by the campaign at
        the time of the STOP; subgroup-scoped opt-outs (non-US recipients) are never attributed to a
        campaign and appear under bySubgroup instead. byType splits SMS/MMS.

        Args:
            group_id: Filter by group ID.
            subgroup_id: Filter by subgroup ID.
            brand_id: Filter by brand ID.
            campaign_id: Filter by campaign ID.
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). A phoneNumber filter takes precedence. Single value or list.
            phone_number: Filter by phone number.
            carrier: Filter by carrier.
            start_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode.
            end_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode. In "exact" mode day buckets align to the UTC offset this bound carries, so a client that sends its own midnights gets its own calendar dates back.
            channel: Filter by channel — "tenDLC", "virtualLongCode", "tollFree", or "shortCode" (single value or list). Opt-outs are
                A2P-only, so "p2p" applies no filter. A tenDLC selection also includes older opt-outs
                with no channel.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing. Same hourly-analytics gate as region.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with totals, byDate, byPhoneNumber, byCarrier, byKeyword.
            byKeyword breaks opt-outs down by the normalized keyword that revoked consent
            ({optOutKeyword, total, sms, mms}); opt-outs recorded before keyword capture shipped
            appear as a single ``optOutKeyword: None`` bucket ("not recorded"). The distinct keyword
            set is open-ended (campaigns register their own keywords beyond the mandatory floor) —
            render top-N plus Other, never a fixed list.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "phoneNumber": phone_number,
            "carrier": carrier,
            "startDate": start_date,
            "endDate": end_date,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message/dnc/analytics{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_dnc_records(
        self,
        *,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        brand_id: str | None = None,
        campaign_id: str | None = None,
        registration_id: str | list[str] | None = None,
        phone_number: str | None = None,
        carrier: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort_field: str | None = None,
        sort_order: str | None = None,
        channel: str | list[str] | None = None,
        region: str | list[str] | None = None,
        region_scopes: str | list[dict[str, Any]] | None = None,
        date_bounds: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get paginated Do Not Call records with optional filters.

        Args:
            registration_id: Filter to traffic attributed to these registrations (hourly analytics only; a 400 while hourly reads are off). A phoneNumber filter takes precedence. Single value or list.
            group_id: Filter by group ID.
            subgroup_id: Filter by subgroup ID.
            brand_id: Filter by brand ID.
            campaign_id: Filter by campaign ID.
            phone_number: Filter by phone number.
            carrier: Filter by carrier.
            start_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode.
            end_date: ISO-8601 date or timestamp; bound per dateBounds: a bare date is always that whole UTC day (inclusive); a timestamp is widened to its whole UTC day in "day" mode and bound as the instant it names, in whatever offset it was written, in "exact" mode. In "exact" mode day buckets align to the UTC offset this bound carries, so a client that sends its own midnights gets its own calendar dates back.
            page: Page number for pagination.
            limit: Number of records per page.
            sort_field: Field to sort by.
            sort_order: Sort direction (asc, desc).
            channel: Filter by channel — "tenDLC", "virtualLongCode", "tollFree", or "shortCode" (single value or list). Opt-outs are
                A2P-only, so "p2p" applies no filter. A tenDLC selection also includes older opt-outs
                with no channel.
            region: Filter by region — "US", "GB", or "CA" (any case of "UK"/"GB"/"GBR"/"United Kingdom" is accepted for GB); single value or list.
                Only accepted where the environment serves hourly analytics; elsewhere any value is rejected with a 400.
            region_scopes: OR-ed regional branches, each {"region", "channels", "brandId"?, "campaignId"?, "phoneNumber"?}
                (channels: tenDLC, virtualLongCode, tollFree, shortCode, p2p). A list is JSON-serialised for the query; a
                string is sent as-is. [] matches nothing. Same hourly-analytics gate as region.
            date_bounds: Which contract binds start_date/end_date. "day": each bound is widened to its
                whole UTC day. "exact": a timestamp is bound as the instant
                it names and a bare date is its whole UTC day. Omitted: "day".
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with paginated DNC records. Each record carries
            ``senderPhoneNumber`` — the first business number that received the opt-out (set once,
            never changed by a later STOP or a campaign move; the same value as ``phoneNumber``),
            ``campaignId`` (``None`` on subgroup-scoped records for non-US recipients),
            ``optOutKeyword`` — the normalized keyword that revoked consent (e.g. "stop",
            "opt out"; a repeat opt-out records the most recent word), ``None`` for opt-outs
            recorded before keyword capture shipped — and ``carrierFamily``, the resolved carrier
            family of the recipient number (Default, ATT, TMobile, Verizon, USCellular,
            GoogleVoice, ClearSky, Interop, RogueMobile, Standard, IceWireless, Bell, Rogers, Telus, Videotron, SaskTel, Eastlink, Fibernetics), copied from the inbound message that
            triggered the opt-out.
        """
        query_string = self._sdk._get_query_string({
            "groupId": group_id,
            "subgroupId": subgroup_id,
            "brandId": brand_id,
            "campaignId": campaign_id,
            "registrationId": registration_id,
            "phoneNumber": phone_number,
            "carrier": carrier,
            "startDate": start_date,
            "endDate": end_date,
            "page": page,
            "limit": limit,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "channel": channel,
            "region": region,
            "regionScopes": json.dumps(region_scopes) if isinstance(region_scopes, list) else region_scopes,
            "dateBounds": date_bounds,
        })
        return self._sdk._request(
            f"/message/dnc{query_string}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_sms(
        self,
        sender_phone_number: str,
        recipient_phone_numbers: str | list[str],
        message_body: str,
        *,
        status_callback_url: str | None = None,
        enable_shortlink: bool = False,
        filter_landlines_and_inactive_numbers: bool = False,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send an SMS message to one or more recipient phone numbers.

        Args:
            sender_phone_number: The digits-only 5-6 digit Short Code or 10+ digit
                long number to send the message from, or a READY alphanumeric sender
                ID (e.g. "ACME"; UK recipients and SMS only). Every message from an
                alphanumeric sender gets "\\nOpt out: sihou.io/o/{code}" appended by
                the server, counted in segments.
            recipient_phone_numbers: The 10+ digit phone number(s) to send the
                message to. A Short Code sender permits exactly one recipient,
                and it must be a +1 (US/Canada) number; a bare 10-digit number
                is treated as +1. The API rejects Short Code sends with multiple
                recipients or a non-+1 recipient.
            message_body: The body of the SMS message.
            status_callback_url: The URL to receive status callbacks.
            enable_shortlink: Whether to enable shortlink in the message.
            filter_landlines_and_inactive_numbers: Whether to filter out landline and inactive numbers before sending.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict. The payload reports the send outcome with three fields so
            callers need not inspect insertedMessages: requestedRecipientCount, enqueuedCount, and
            failedCount. enqueuedCount is the number of recipients accepted for delivery and is 0
            when the send was fully blocked (by the moderation filter or a campaign opt-out); the
            request still succeeds in that case, so treat enqueuedCount, not the HTTP status, as the
            signal that a message was accepted. Blocked recipients are returned in insertedMessages
            with status "FAILED"; recipients on the global Do Not Contact list are reported in
            dncBlockedNumbers with no message record. Each FAILED message carries errorCode, a stable
            machine-readable cause (campaign opt-out is "OUT"; None on success or on failures with no
            assigned code) that is also included on the FAILED status-callback payload.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({
            "senderPhoneNumber": sender_phone_number,
            "recipientPhoneNumbers": recipient_phone_numbers,
            "messageBody": message_body,
        })
        body: dict[str, Any] = {
            "senderPhoneNumber": sender_phone_number,
            "recipientPhoneNumber": recipient_phone_numbers,
            "messageBody": message_body,
            "enableShortlink": enable_shortlink,
        }
        if filter_landlines_and_inactive_numbers:
            body["filterLandlinesAndInactiveNumbers"] = True
        if status_callback_url is not None:
            body["statusCallbackUrl"] = status_callback_url
        return self._sdk._request(
            "/message/sms",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_p2p(
        self,
        recipient_phone_numbers: str | list[str],
        message_body: str,
        *,
        status_callback_url: str | None = None,
        group_id: str | None = None,
        subgroup_id: str | None = None,
        use_signal_house_shortlinks: bool | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send a P2P message via Rogue Mobile SMPP.

        Args:
            recipient_phone_numbers: The phone number(s) to send the message to.
            message_body: The body of the P2P message.
            status_callback_url: The URL to receive status callbacks.
            group_id: Explicit group to send from. Defaults to the group in your
                auth context.
            subgroup_id: Explicit subgroup to attribute the send (and its inbound
                reply) to. P2P has no dedicated sender number, so pass this to record
                the send against a specific subgroup; it also resolves the group.
                Defaults to the group's oldest subgroup.
            use_signal_house_shortlinks: When false, SignalHouse applies no
                link-shortening or text-spin and your pre-spun links/content are
                sent verbatim (bring-your-own spinner). Defaults to true.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({
            "recipientPhoneNumbers": recipient_phone_numbers,
            "messageBody": message_body,
        })
        body: dict[str, Any] = {
            "recipientPhoneNumber": recipient_phone_numbers,
            "messageBody": message_body,
        }
        if status_callback_url is not None:
            body["statusCallbackUrl"] = status_callback_url
        if group_id is not None:
            body["groupId"] = group_id
        if subgroup_id is not None:
            body["subgroupId"] = subgroup_id
        if use_signal_house_shortlinks is not None:
            body["useSignalHouseShortlinks"] = use_signal_house_shortlinks
        return self._sdk._request(
            "/message/p2p",
            method="POST",
            body=body,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_p2p_batch(
        self,
        batch_id: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Get the details of a P2P batch by its ID.

        Args:
            batch_id: The ID of the P2P batch to retrieve.
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If batch_id is missing.
        """
        self._sdk._require({"batchId": batch_id})
        safe_batch_id = quote(str(batch_id), safe="")
        return self._sdk._request(
            f"/message/p2p/batches/{safe_batch_id}",
            method="GET",
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def get_delivery_reports(
        self,
        message_ids: list[str],
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Fetch the latest upstream carrier delivery report for a set of messages by ID.

        Useful for reconciling messages stuck in a non-terminal state. Outbound SMS and MMS messages
        sent from numbers on supported carriers are looked up upstream (reports are retained about 48 hours); every other message, including P2P messages and messages sent from numbers
        on other carriers, is returned with its stored status and ``upstreamReportAvailable`` false. The
        request fails with a 500 when the sending numbers can't be read.

        Args:
            message_ids: The message IDs to fetch carrier delivery reports for (1-100).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict containing an array of carrier delivery reports.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({"messageIds": message_ids})
        return self._sdk._request(
            "/message/delivery-report",
            method="POST",
            body={"messageIds": message_ids},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_mms(
        self,
        sender_phone_number: str,
        recipient_phone_numbers: str | list[str],
        message_body: str,
        *,
        media_urls: list[str] | None = None,
        status_callback_url: str | None = None,
        enable_shortlink: bool = False,
        enable_compression: bool = True,
        filter_landlines_and_inactive_numbers: bool = False,
        images: list[BinaryIO | tuple] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send an MMS message to one or more recipients, with optional media attachments.

        The response reports the send outcome via requestedRecipientCount, enqueuedCount, and
        failedCount. enqueuedCount is the number of recipients accepted for delivery and is 0 when
        the send was fully blocked (moderation filter or campaign opt-out); the request still
        succeeds in that case, so treat enqueuedCount, not the HTTP status, as the signal that a
        message was accepted. Blocked recipients are returned in insertedMessages with status
        "FAILED"; global Do Not Contact recipients are reported in dncBlockedNumbers with no message
        record. Each FAILED message carries errorCode (campaign opt-out is "OUT"; None otherwise),
        also included on the FAILED status-callback payload.

        Args:
            sender_phone_number: The digits-only 5-6 digit Short Code or 10+ digit
                long number to send the message from.
            recipient_phone_numbers: The 10+ digit phone number(s) to send the
                message to. A Short Code sender permits exactly one recipient,
                and it must be a +1 (US/Canada) number; a bare 10-digit number
                is treated as +1. The API rejects Short Code sends with multiple
                recipients or a non-+1 recipient.
            message_body: The body of the MMS message.
            media_urls: The URLs of the media attachments.
            status_callback_url: The URL to receive status callbacks.
            enable_shortlink: Whether to enable shortlink in the message.
            enable_compression: Whether to enable image compression for attachments.
            filter_landlines_and_inactive_numbers: Whether to filter out landline and inactive numbers before sending.
            images: Image files to attach to the MMS message. Each can be a file-like object
                    or a tuple of (filename, file_object, content_type).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({
            "senderPhoneNumber": sender_phone_number,
            "recipientPhoneNumbers": recipient_phone_numbers,
        })

        form_data: dict[str, Any] = {
            "senderPhoneNumber": sender_phone_number,
            "messageBody": message_body,
            "enableShortlink": str(enable_shortlink).lower(),
            "enableCompression": str(enable_compression).lower(),
        }

        if filter_landlines_and_inactive_numbers:
            form_data["filterLandlinesAndInactiveNumbers"] = "true"

        if isinstance(recipient_phone_numbers, list):
            form_data["recipientPhoneNumber"] = json.dumps(recipient_phone_numbers)
        else:
            form_data["recipientPhoneNumber"] = recipient_phone_numbers

        if media_urls:
            form_data["mediaUrls"] = json.dumps(media_urls)

        if status_callback_url:
            form_data["statusCallbackUrl"] = status_callback_url

        files_list: list[tuple[str, Any]] = []
        if images:
            for image in images:
                if isinstance(image, tuple):
                    files_list.append(("images", image))
                else:
                    files_list.append(("images", image))

        return self._sdk._multipart_request(
            "/message/mms",
            method="POST",
            form_data=form_data,
            files=files_list if files_list else None,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def send_group_message(
        self,
        sender_phone_number: str,
        recipient_phone_numbers: str | list[str],
        message_body: str,
        *,
        media_urls: list[str] | None = None,
        status_callback_url: str | None = None,
        enable_shortlink: bool = False,
        enable_compression: bool = True,
        filter_landlines_and_inactive_numbers: bool = False,
        images: list[BinaryIO | tuple] | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Send a group MMS message to one or more recipients, with optional media attachments.

        The response reports the send outcome via requestedRecipientCount, enqueuedCount, and
        failedCount. enqueuedCount is the number of recipients accepted for delivery and is 0 when
        the send was fully blocked (moderation filter or campaign opt-out); the request still
        succeeds in that case, so treat enqueuedCount, not the HTTP status, as the signal that a
        message was accepted. Blocked recipients are returned in insertedMessages with status
        "FAILED"; global Do Not Contact recipients are reported in dncBlockedNumbers with no message
        record. Each FAILED message carries errorCode (campaign opt-out is "OUT"; None otherwise),
        also included on the FAILED status-callback payload.

        Args:
            sender_phone_number: The 10+ digit long number to send the group
                message from. Short Codes do not support group messaging.
            recipient_phone_numbers: The phone number(s) to send the message to.
            message_body: The body of the MMS message.
            media_urls: The URLs of the media attachments.
            status_callback_url: The URL to receive status callbacks.
            enable_shortlink: Whether to enable shortlink in the message.
            enable_compression: Whether to enable image compression for attachments.
            filter_landlines_and_inactive_numbers: Whether to filter out landline and inactive numbers before sending.
            images: Image files to attach to the MMS message. Each can be a file-like object
                    or a tuple of (filename, file_object, content_type).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({
            "senderPhoneNumber": sender_phone_number,
            "recipientPhoneNumbers": recipient_phone_numbers,
        })

        form_data: dict[str, Any] = {
            "senderPhoneNumber": sender_phone_number,
            "messageBody": message_body,
            "enableShortlink": str(enable_shortlink).lower(),
            "enableCompression": str(enable_compression).lower(),
        }

        if filter_landlines_and_inactive_numbers:
            form_data["filterLandlinesAndInactiveNumbers"] = "true"

        if isinstance(recipient_phone_numbers, list):
            form_data["recipientPhoneNumber"] = json.dumps(recipient_phone_numbers)
        else:
            form_data["recipientPhoneNumber"] = recipient_phone_numbers

        if media_urls:
            form_data["mediaUrls"] = json.dumps(media_urls)

        if status_callback_url:
            form_data["statusCallbackUrl"] = status_callback_url

        files_list: list[tuple[str, Any]] = []
        if images:
            for image in images:
                if isinstance(image, tuple):
                    files_list.append(("images", image))
                else:
                    files_list.append(("images", image))

        return self._sdk._multipart_request(
            "/message/groupMessage",
            method="POST",
            form_data=form_data,
            files=files_list if files_list else None,
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )

    def carrier_id_lookup(
        self,
        phone_number: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Look up the carrier for a phone number. Always fresh (not cached). Billed per request.

        Args:
            phone_number: The phone number to look up (10+ digits, no + prefix).
            token: Optional bearer token for authentication.
            headers: Additional headers to include in the request.
            idempotency_key: Sent as the Idempotency-Key header; a retry with the same key and request replays the first response.

        Returns:
            Standardized response dict with carrier information.

        Raises:
            SignalHouseValidationError: If required parameters are missing.
        """
        self._sdk._require({"phoneNumber": phone_number})
        return self._sdk._request(
            "/message/carrier-id",
            method="POST",
            body={"phoneNumber": phone_number},
            token=token,
            headers=headers,
            idempotency_key=idempotency_key,
        )
