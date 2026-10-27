# Why 10DLC registrations get rejected

Loaded on demand, and only needed once something has actually been rejected.

Every cause below is drawn from a **real Signal House support ticket** or verified against the
API, with the source noted. Nothing here is general industry knowledge.

> **Review status:** engineer-verified against support tickets and the API.

## How to read a rejection

`rejectionReason` is **free text, 10 to 256 characters** (verified: `campaign.validation.js`). It
is not an enum and cannot be reliably pattern-matched.

Registry errors arrive with a numeric code and a description, and the code is the reliable part.
**These are TCR's own error codes, not HTTP status codes**. They arrive *inside* the response
body of what is typically an HTTP 400, in the shape
`External service error: TCR - Request failed with status code 400 - [{ "code": 503, "description": "..." }]`.
A `503` here means "reference id already in use", not "service unavailable". Do not reason about
them as HTTP semantics.

## Registry error codes seen in production

### 509: "Brand does not qualify for submitted campaign use-case"

The brand is not eligible for the use case, on carrier-side vetting criteria. Two real cases:
a generic technology company rejected for `UCAAS_HIGH` (which expects a recognized UCaaS
provider), and a brand with `brandScore: 0` rejected for `DELIVERY_NOTIFICATION`.

**Not retryable.** Resubmitting the same campaign cannot fix it. The two real options are to
switch to a use case the brand qualifies for (`LOW_VOLUME` unblocks immediately), or to re-vet
the brand to earn a qualifying score.

Related: a brand with `brandScore: null` has not been scored by the registry yet. Campaigns
depending on a score will keep failing until scoring runs, and that is not something the
platform can force.

### 501: invalid sub-use-case

Two distinct real causes share this code.

**`Invalid sub-usecases: SOCIAL`.** `SOCIAL` is not a valid sub-use-case under any parent,
neither `LOW_VOLUME` nor `MIXED`. Valid sub-use-cases for `LOW_VOLUME` are
`ACCOUNT_NOTIFICATION`, `CUSTOMER_CARE`, `DELIVERY_NOTIFICATION`, `MARKETING`. Signal House's own
validation now rejects `SOCIAL` as a `subUsecases` value with an immediate 400, before the request
reaches TCR, so this 501 should no longer be reachable through the API. `SOCIAL` is still a valid
top-level `usecase`, just never a sub-use-case. If an older campaign carries this rejection,
resubmit with `SOCIAL` removed from `subUsecases`.

**Punctuation in a tag.** A tag of `maria-answers` was rejected for containing a hyphen. The
campaign content was fine. Fix the tag (`mariaanswers`), then the campaign has to be
re-approved internally before it re-registers.

### 503: "Reference ID already in use"

A duplicate `referenceId` on brand creation. The brand cannot be repaired: create a **new**
brand with the same details and **omit `referenceId` entirely**.

This is specific to a brand that landed in `TCR_REJECTED`. It is **not** the general rule: a
brand in `UNVERIFIED` can be fixed and re-submitted with an ordinary update (`PUT /brand/:brandId`
calls the registry and writes back its fresh status) or with `PUT /brand/revet/:brandId`. Only
`TCR_REJECTED` refuses both and forces recreation.

## Platform-side rejections (before the registry ever sees it)

**No numbers on the campaign.** Verified in `campaign.service.js`: registration throws
`No phone numbers assigned to campaign with ID <campaignId>`. At least one number must be
attached to the campaign. Confirmed by a real ticket where a campaign was rejected for exactly
this.

**Campaign not internally approved.** Campaigns wait on Signal House approval before they are
upstreamed to the provider. "Not approved in our system yet" is a distinct state from any
registry rejection.

## Content and use-case rejections

**Missing content attribute for the declared activity.** Real example: *"Campaign is for direct
lending or loan arrangement and is missing content attribute indicating direct lending."* The
campaign's declared attributes have to match what the traffic and landing page actually show.
A landing page saying "no direct lending" while the campaign reads as lending is a rejection.

## Adjacent gotchas

**Brand deletion is blocked by campaigns.** The actual error is
`Cannot delete brand <brandId> because it has active campaigns`, and the gate is broader than
"active" suggests: it blocks on any campaign not yet `EXPIRED`. Campaigns must be cleared first.
A brand can also show `EXPIRED` in Signal House while still `ACTIVE` at the registry, and the two
are not automatically in sync.

**Brand edits and fees, settled from the code.** Ordinary brand updates are **free**:
`brandUpdate` exists in the fee schedule but is never charged anywhere. Updating landing URLs is
its own path and charges nothing. The $4.50 people ask about is `brandRevet`, and it is only
charged by an explicit re-vet (`PUT /brand/revet/:brandId`), never as a side effect of an edit.
`brandCreate` is the same $4.50 and applies to creating a new brand, which is why a
registry-rejected brand that must be recreated does cost again.

What an edit *can* cost you is time, not money: changing verification-relevant data moves the
brand `VERIFIED → UNVERIFIED` and it re-verifies.

**A failed campaign holds its reserved funds.** Funds reserved at campaign creation are released
for `PENDING_REVIEW` / `REJECTED` / `TCR_REGISTER_FAILED` when the campaign is **deleted**, not
at the moment it fails. This is deliberate, because those states are appealable and re-registerable,
but it means a customer who abandons failed campaigns keeps funds tied up. Deleting the dead
campaign frees them.
