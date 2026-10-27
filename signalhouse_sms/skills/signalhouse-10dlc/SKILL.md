---
name: signalhouse-10dlc
description: >-
  Signal House 10DLC brand and campaign registration: what has to exist before a message can
  send, what each registration step requires, and why registrations get rejected.
  TRIGGER when the user is registering, onboarding, or troubleshooting a 10DLC brand or
  campaign on Signal House; when a send is failing and the campaign may not be approved yet;
  when a brand or campaign was rejected and they are asking why or how to appeal; or when
  planning an onboarding flow that ends in sending SMS.
  SKIP for toll-free and short-code registration (different requirements), for message content
  or opt-out wording, and for questions about an already-ACTIVE campaign's throughput or
  pricing, which are live values the API owns.
---

# Signal House 10DLC registration

## What cannot happen

**A message cannot send until its campaign is `ACTIVE`.** This is enforced in the platform, not
by the caller. On the synchronous path the send is rejected with a `SendMessageError` reading
`Unable to send message: Campaign <campaignId> is not active`. On the queued path the messages
are marked `FAILED` with `Failed to send SMS message because the campaign is not active`, and
any reserved funds are released.

`ACTIVE` is the only state that permits a send. Every other campaign state, including pending, failed,
rejected and expired, blocks it. Do not infer approval from a campaign existing, from a
successful create call, or from a number being assigned.

**A group under compliance review cannot send**, regardless of campaign state. Queued messages
fail with `Failed to send SMS message because the group is under compliance review`.

These two are the *registration* gates, and they are the ones this skill is authoritative about.
They are **not** the complete list of reasons a send can fail. Number state, recipient opt-out
and DNC status, content filtering, throughput caps and balance all block sends independently of
registration. Do not treat an `ACTIVE` campaign plus a clean group as proof a send will succeed,
and do not present this section as an exhaustive troubleshooting list.

**A campaign cannot be registered before its brand exists.** Campaign registration references a
brand; there is no path that creates both together.

Consequences of getting this wrong are not recoverable by retrying: rejected registrations
carry a cost and a delay, and pre-approval send attempts are the most common reason an
onboarding flow appears broken when it is behaving correctly.

## Order of operations

The documented pipeline is:

```
Create Subgroup --> Register Brand --> Purchase Numbers --> Create Campaign --> Start Messaging
```

1. **Create a subgroup.** Brands belong to one, and `subgroupId` is a required brand field, so
   there is no brand without it.
2. **Register the brand** (`POST /brand`, `registrationType: "TEN_DLC"`).
3. **Purchase numbers while the brand verifies.** Nothing gates the purchase path on brand or
   campaign state, so this does not have to wait.
4. **Wait for the brand to reach `VERIFIED`.** Campaigns can only be created against a verified
   brand, so a campaign submitted earlier is wasted work. **A brand that fails verification is
   often recoverable. See "When a brand fails" below. Do not default to recreating it.**
5. **Create the campaign** (`POST /campaign`) against the verified brand, **with at least one
   phone number**. `phoneNumbers` is a required, non-empty field on create, and an empty array is
   rejected immediately with "At least one number is required". Numbers are part of the campaign,
   not a later step.
6. **Wait for the campaign to reach `ACTIVE`.** It is reviewed by Signal House and then
   submitted for carrier approval, and each stage can fail independently. Read current state
   with `GET /campaign`.
7. **Send.**

Steps 4 and 6 are asynchronous and are not instant. An onboarding flow that sends immediately
after step 5 is the failure this skill exists to prevent.

**Updating a verified brand can send it backwards.** An update that changes verification-relevant
data moves the brand `VERIFIED → UNVERIFIED` and it has to verify again. Do not treat an edit to
a live brand as cosmetic.

## Required fields

A 10DLC brand requires all of: `subgroupId`, `entityType`, `displayName`, `companyName`, `ein`,
`phone`, `street`, `city`, `state`, `postalCode`, `country`, `email`, `vertical`.

The two with constrained values, which is where callers get stuck:

| Field | Values |
|---|---|
| `entityType` | `PRIVATE_PROFIT`, `PUBLIC_PROFIT`, `NON_PROFIT`, `GOVERNMENT` |
| `vertical` | one of 23 industry values: `PROFESSIONAL`, `REAL_ESTATE`, `HEALTHCARE`, `FINANCIAL`, `TECHNOLOGY`, `RETAIL` and so on. Do not guess; read the list from the Brands reference. |

**`brandRelationship` is not a field you set.** The service overwrites it before validation runs,
and every 10DLC brand ends up `MEDIUM_ACCOUNT` regardless of what was sent. Whatever a caller
passes is discarded silently. Do not ask a customer to choose one, and do not report it back as
something they selected.

`PUBLIC_PROFIT` additionally requires `stockSymbol`, `stockExchange`, `website` and
`businessContactEmail`.

`ein` and `companyName` are checked against an external record, not just validated for shape.
`displayName` is the public-facing name and `companyName` is the legal one. Using a trading name
in `companyName` is the single most common cause of a failed verification.

## When a brand fails

**Read the status before deciding what to do. The two failure states recover differently, and
guessing costs the customer money.**

| Status | What happened | Recovery |
|---|---|---|
| `UNVERIFIED` | verification failed after the brand registered, **the common case** | **Two options, both keep the brand.** Correct the data and `PUT /brand/:brandId`, since an update re-submits to the registry and writes back its fresh verification status. Or `PUT /brand/revet/:brandId` to re-submit as-is. |
| `VERIFIED` / `VETTED_VERIFIED` | already good | Updates are allowed, and a change to verification-relevant data can send it back to `UNVERIFIED`. |
| `TCR_REJECTED` | the initial registration was rejected outright | Update and re-vet are both refused. Recreation is the path, and it costs a fresh brand-creation fee. |

**Do not reach for recreation first.** Most failed brands are `UNVERIFIED`, and an update is a
genuine resubmission. Fixing a typo'd EIN and updating re-submits to the registry without paying
again. Recreating an `UNVERIFIED` brand throws away a recoverable one and charges for the
privilege.

Two traps in the failure path:

- **Re-vet only accepts `UNVERIFIED`.** Anything else is refused with
  `Cannot revet brand <brandId> because its status is <status>`.
- **An update on a status outside the allowed set fails silently.** It does not throw. It fires a
  brand-update-failed webhook and returns. A caller that only checks for an exception will believe
  the update worked. Read the status back.

## When it gets rejected

A rejected registration carries a free-text `rejectionReason` (10 to 256 characters) written by
whoever rejected it. Read it before acting. It is specific, and it is not drawn from a fixed
list, so do not pattern-match it against an enum.

**Campaigns have their own appeal, separate from the brand's.** A campaign rejected at the
carrier stage is appealed via `POST /campaign/appealDcaRejection/:id` with a free-text reason,
no category enum. The three-category appeal below applies to *brands* only; do not try to use it
on a campaign.

Brand **verification** failures can be appealed with evidence. The appeal takes one or more
categories, and these three are the whole set:

- `VERIFY_TAX_ID`: the EIN and legal name do not match the authoritative record
- `VERIFY_NON_PROFIT`: non-profit status is claimed but not confirmed
- `VERIFY_GOVERNMENT`: government status is claimed but not confirmed

An appeal requires a written explanation and usually supporting documentation. Which of these
three applies is determined by the rejection, not chosen freely.

Registry rejections arrive with a numeric code, and the code is the reliable part,
`509` brand not eligible for the use case (not retryable), `501` invalid sub-use-case or
punctuation in a tag, `503` duplicate reference id. Each has a specific fix, and for two of them
the fix is "recreate", not "retry". See
[references/tcr-rejection-causes.md](references/tcr-rejection-causes.md), which is drawn from
real support tickets and loaded on demand because it is only needed once something has actually
been rejected.

## Where to look it up

Never state a current status, price, or throughput figure from memory. Read it:

- **Campaign state:** `GET /campaign`. This is the only trustworthy answer to "can this send
  yet". The set of possible states is owned by the platform and changes; the only one you can
  reason about without reading it is `ACTIVE`.
- **Brand state and appeal history:** `GET /brand`, `GET /brand/appeal/:brandId`.
- **Whether a specific send will be allowed:** attempt it and read the error, or check campaign
  state first. There is no separate preflight endpoint.

- **The full field lists, verticals, use cases, status meanings and worked examples:** the Brands
  and Campaigns references (https://app2.signalhouse.io/docs/brands,
  https://app2.signalhouse.io/docs/campaigns) and the published help-centre articles *10DLC Messaging Overview*, *10DLC Campaign Website
  Review* and *10DLC Campaign Approvals*. This skill is a condensed guardrail, not a substitute
  for them. Where it and the references disagree, the references win and this file is the bug.

The platform enforces every constraint on this page. This skill exists so an agent stops
*before* a rejected registration or a failed send, not so it can predict the outcome.
