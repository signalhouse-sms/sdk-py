---
name: signalhouse-sms
description: >-
  Sending SMS and MMS on Signal House: what a successful-looking response does not prove, the
  parameter name that differs between the SDK and the raw API, how segments drive cost, and the
  carrier and opt-out gates that stop a send.
  TRIGGER when the user is sending or scripting SMS, MMS or group MMS; when a message came back
  successful but never arrived; when a send fails or is rejected; when they ask about delivery
  status, delivery receipts, message cost, segments, emoji, or STOP and opt-outs.
  SKIP for 10DLC brand and campaign registration, for buying numbers, and for webhook endpoint
  setup, which have their own skills. This one assumes a number that is already able to send.
---

# Sending on Signal House

## What cannot happen

**`success: true` does not prove the message went out.** When the Moderation API blocks content, the
send does **not** raise an API error. The recipients are written to the message log as **accepted but
`FAILED`** and returned like a normal send, so the caller sees a normal success envelope. Any code
that treats a 2xx as "delivered" reports a blocked campaign as a working one. Confirm outcomes from
message status or a delivery webhook, never from the send response alone.

**A number cannot send just because the account owns it.** It must be in `READY` status on an
`ACTIVE` campaign, under a brand that is `VERIFIED` or `VETTED_VERIFIED`. A brand-new number is not a
sendable number. See `signalhouse-10dlc`.

**The recipient field is named differently in the SDK and the API.** The raw API takes
`recipientPhoneNumber` (**singular**, still an array). The JS SDK takes `recipientPhoneNumbers`
(**plural**) and maps it internally. A direct HTTP caller who copies the SDK's plural name gets a
validation failure, and it reads as a mysterious 400 rather than a typo.

**Opt-out suppression is environment-gated, so a STOP is not automatically a block.**
`DNC_ENFORCEMENT_MODE` has three settings, `off`, `log` and `enforce`, and the default is **`log`**.
In `log` mode the platform queries suppressions and records what it *would* have blocked, then lets
every recipient through. So:

- Never tell a customer that STOP replies are being enforced without checking the environment.
- Never tell them suppression does not exist either. The list is real and is being recorded.
- STOP and HELP confirmations deliberately bypass suppression. They are addressed to someone who is
  on the list by design, so seeing one go out is not evidence that suppression is broken.

**Sending is billed per segment, not per message.** A single non-GSM character, such as an emoji or a
curly quote pasted from a document, flips the whole body to a different encoding and
multiplies the segment count, and the cost, silently. Message body length is a billing decision.

**Carrier throughput is capped above the API.** There is a T-Mobile daily segment cap tracked per
brand EIN and an AT&T per-minute segment limit. Hitting either fails messages with a recorded reason
rather than raising an exception at the call site. A burst where most messages went out and some did not
is what this looks like in practice.

## Order of operations

1. **Confirm the sender can send.** Check the number's status is `READY` rather than assuming.
2. **Know the segment count and current fee** before a bulk send. Fees are per group and read from
   `GET /billing/fees/:groupId`. Never quote a price from memory or from this file.
3. **Send.** `POST /message/sms` (JSON), `POST /message/mms` (multipart, max 5 attachments),
   `POST /message/groupMessage` (multipart, shared thread). The send is queued and returns **201**
   with an `insertedMessages` array holding one document per recipient.
4. **Read the outcome asynchronously.** `statusCallbackUrl` on the send, or `MESSAGE_DELIVERED` /
   `MESSAGE_FAILED` webhooks. Polling `GET /message` in a loop is the wrong shape and the rate-limit
   guidance says so explicitly.

Message status runs `ENQUEUED → DEQUEUED → SENT → DELIVERED`, with `FAILED` reachable from the
middle. `SENT` means handed to the carrier, not received by the handset. Only `DELIVERED` means
delivered, and not every carrier returns one.

## Querying messages

`GET /message` requires `groupId`, `startDate` and `endDate` **unless** you filter by `id`, which
routes to a single-record lookup and skips the date-range requirement. Omitting them without an `id`
is a 400, not an unbounded query. The API refuses rather than scanning.

## Where to look it up

- **Every send parameter, message statuses and delivery receipts:** the Messages reference,
  https://app2.signalhouse.io/docs/messages.
- **Current per-group fees:** `GET /billing/fees/:groupId`.
- **Failure codes and what is retryable:** https://app2.signalhouse.io/docs/error-handling.
- **Backoff and batching:** https://app2.signalhouse.io/docs/rate-limits.
- **Why a number cannot send yet:** `signalhouse-10dlc`.
