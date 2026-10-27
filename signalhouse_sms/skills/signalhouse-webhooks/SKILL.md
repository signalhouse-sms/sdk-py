---
name: signalhouse-webhooks
description: >-
  Signal House webhooks: how delivery actually behaves, what a receiver can and cannot trust,
  and the retry window before an event is lost for good.
  TRIGGER when the user is setting up, debugging, or writing a receiver for Signal House
  webhooks; when webhook events appear to be missing, duplicated, or arriving late; when they
  ask how to verify a webhook is genuine; or when they are choosing an authType.
  SKIP for inbound message handling logic itself, for the SMS send path, and for questions about
  which events exist. That list is in the webhooks guide and changes independently of this.
---

# Signal House webhooks

## What a receiver can verify

**Deliveries to a webhook endpoint are signed.** Every endpoint created with `POST /webhook` gets a
signing secret, returned in plaintext **exactly once**, as `signingSecret` in that create response.
Every later read reports only `hasSigningSecret: true|false`. Store the secret at creation; nothing
can hand it back. If it is lost or exposed, rotate it: `POST /webhook/:id/rotate-secret` returns a new
secret once, and the old one keeps working for a grace window (`graceSeconds`, default 24h, max 7
days, `0` for none) so the receiver can switch over without dropping deliveries.

A signed delivery carries:

| Header | Value |
|---|---|
| `X-SignalHouse-Signature` | hex HMAC-SHA256, keyed with the signing secret, over `${timestamp}.${rawBody}`. During a rotation grace window it stays on the **previous** secret and switches when the window ends |
| `X-SignalHouse-Timestamp` | the `timestamp` in that string: Unix time in **milliseconds** |
| `X-SignalHouse-Signature-V1` | `t=<ms>,v1=<hex>[,v1=<hex>]`: one signature per currently valid secret, newest first. During a rotation grace window it carries both the new and the previous secret's signature; accept a match on any |
| `X-SignalHouse-Delivery-Id` | a UUID for this event to this endpoint, the same on every retry |

A correct verifier:

1. **Uses the raw request body**, byte for byte, before any JSON parsing. Re-serializing a parsed
   body changes whitespace and key order and the signature stops matching.
2. **Recomputes the HMAC and compares in constant time.** The signature is bare hex, no prefix.
3. **Rejects a stale timestamp.** The timestamp is inside the signed string, so a captured request
   cannot be replayed with a fresh one. Pick a window (five minutes is common) and remember the
   header is milliseconds, not seconds.
4. **Rejects an unsigned request to an endpoint that has a secret.** Otherwise a forger simply
   leaves the headers off.
5. **Prefers `X-SignalHouse-Signature-V1`**, so a secret rotation never breaks verification.

In Node, `verifyWebhookSignature` from `@signalhousellc/sdk/webhooks` does all of this and returns
`{ valid, reason }` without throwing. Other languages implement the five steps directly; the
Webhook Signing guide has a Python version.

What is still **not** verifiable:

- **Endpoints created before signing shipped (2026-09-03) are sent unsigned** until they get a
  secret. They report `hasSigningSecret: false`. Call `POST /webhook/:id/rotate-secret` once (or use
  *Create signing secret* in the portal's webhook edit view) to issue their first secret; deliveries
  are signed from then on.
- **Per-number inbound URLs are never signed** (see below).

For anything unsigned, the old rules still apply: do not treat the request as authenticated, and
never take an irreversible or financial action on webhook content alone. Read the authoritative
state back from the API first. Do not put secrets in a webhook URL as a substitute for
verification; URLs end up in proxy logs and support screenshots.

The `authType` setting (`NONE`, `BASIC`, `API_KEY`, `OAUTH2`, `HMAC`) chooses what *else* Signal
House sends to the receiver. Signing does not depend on it: every endpoint with a secret is signed
whatever `authType` says. `BASIC`/`API_KEY`/`OAUTH2` add credentials as a second layer; `HMAC` sends
none and declares that the receiver authenticates by the signature alone.

## Retry behaviour, and when an event is gone

Delivery is a **direct HTTP POST with a 3-second timeout**, made up to **3 times in total**. The
waits between attempts back off exponentially with jitter: about 500 ms, then about 1 second
(each up to 25% longer). It is not queued, so there is no queue-level redelivery behind it. Each
attempt is signed afresh with a new timestamp and carries the **same** delivery id.

What gets retried:

- **Retried:** no response at all (network error, DNS failure, timeout), any **5xx**, and **429**.
- **Not retried:** every other **4xx**. A receiver that answers 400, 401, 403 or 404 gets the
  event once. So return a 4xx only for a request you will never accept (a bad signature, say), and
  a 5xx or 429 for anything transient.

Two numbers matter, and they are different things:

- **A receiver has 3 seconds to respond.** Exceed it and the attempt is a failure, even if the
  work eventually succeeds on your side.
- **The whole delivery window is about 11 seconds** worst case: three attempts that can each burn
  the full timeout, plus the two waits.

- A receiver that is down, restarting, or rate-limited for longer than that **loses the push for
  that event**. There is no dead-letter queue and no replay endpoint.
- A slow endpoint that exceeds 3 seconds and *then* completes its work has been recorded as a
  failure and will be sent the **same event again**. Dedupe on `X-SignalHouse-Delivery-Id`.

So a correct receiver:

1. **Responds inside 3 seconds, and does the work afterwards.** Acknowledge, enqueue, process out
   of band. Any processing done before responding is spending a budget you do not control, and
   blowing it converts a successful handler into a duplicate delivery.
2. **Is idempotent on `X-SignalHouse-Delivery-Id`**, which every delivery carries, signed or not,
   including per-number inbound URLs.
3. **Reconciles against `GET /notification`.** This is the important one. Every event that would
   trigger a group webhook also writes a **notification record, created before endpoints are even
   looked up and independent of whether delivery succeeds**. It carries the same `{timestamp,
   event, identifier, metaData}` shape and is filterable by group, status and event type.

   That makes it the durable record and the webhook merely the push. A receiver that must not
   miss anything polls it to catch up after any outage, which is the only reliable recovery,
   given there is no replay endpoint.

## Setting one up

Webhooks are created per group, and numbers can additionally carry their own inbound URL.
`authType` picks how Signal House authenticates to the endpoint, and `credentials` is
`{ key, secret }`, required whenever `authType` is not `NONE` or `HMAC` (and rejected with those two).

| authType | What is sent |
|---|---|
| `NONE` | nothing. The endpoint is open to anyone who knows the URL |
| `BASIC` | HTTP Basic; `key` is the username, `secret` is the password |
| `API_KEY` | `key` holds the key; `secret` optional |
| `OAUTH2` | `secret` is the access token sent as the Authorization value; `key` is required at create but unused in outgoing headers |
| `HMAC` | no credentials and no Authorization header; the receiver verifies the signature headers. Rejected for an endpoint with no signing secret until it has one |

Verify the signature on every endpoint that has one. `HMAC` (or `NONE`) is fine for a receiver
that verifies signatures; `BASIC` or `API_KEY` on top is cheap defense in depth.

**The table above does not cover per-number inbound URLs.** A number can carry
`primaryInboundWebhookUrl` and `secondaryInboundWebhookUrl`, and inbound messages are posted to
both. That path sends **no auth headers and no signature**, whatever is configured elsewhere: it has
no endpoint record to hold a secret, so it is always unauthenticated. It does carry
`X-SignalHouse-Delivery-Id`. Do not assume configuring a group webhook protects the per-number
ones; it does not. Treat those URLs as fully public and put nothing behind them that matters
without an independent check. If a number's inbound traffic needs verifying, route it through a
signed group endpoint instead.

## Where to look it up

- **The signing scheme, verification and rotation:** the Webhook Signing guide,
  https://app2.signalhouse.io/docs/webhook-signing.
- **Event types and payload shape:** the Webhooks reference,
  https://app2.signalhouse.io/docs/webhooks. The event list changes independently of this skill;
  read it there rather than reciting it here.
- **Whether an event actually happened:** `GET /notification`
  (https://app2.signalhouse.io/docs/notifications). The notification record is written
  independently of delivery, so it is the record and the webhook is the push.
- **Whether a delivery failed:** Signal House logs every failed delivery with the group, the
  endpoint, the event and the HTTP status your endpoint returned (or none, for a timeout), so
  support can answer "did you get a 401 from us". There is still no API for a customer to list
  failed deliveries or replay one, so do not design a process that depends on it.
