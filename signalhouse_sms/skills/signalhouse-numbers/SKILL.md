---
name: signalhouse-numbers
description: >-
  Signal House phone numbers: the search, purchase and list flow, and what a purchase commits
  the account to financially.
  TRIGGER when the user is searching for, buying, listing or releasing Signal House numbers;
  when they are scripting or bulk-buying numbers; when a purchase fails; or when they ask what
  numbers cost or why their balance dropped.
  SKIP for toll-free verification and short-code provisioning, for porting numbers in, and for
  assigning an existing number to a campaign, which belongs to 10DLC registration.
---

# Signal House phone numbers

## What cannot happen

**Releasing a number is irreversible.** `DELETE /number` sets the number to `RELEASED`, and
**nothing transitions a number out of `RELEASED`**. It cannot be reactivated (reactivation
requires `DEACTIVATED`), cannot be assigned to a campaign, and cannot be re-deleted. The number
management guide says it plainly: released numbers cannot be recovered. Treat a release request
as destructive and confirm it explicitly, every time.

**A bulk local purchase has no ceiling.** `POST /number` accepts a `phoneNumbers` array with a
minimum of 1 and **no maximum**, unlike campaign assignment, which caps at 5000. Passing a whole
search page buys a whole search page. If a caller asks for "some numbers", establish the count
before purchasing, not after.

Toll-free is different: those purchases are capped at 10 per order and additionally gated by a
per-group toll-free flag. The unbounded risk above is specific to local numbers.

**A number is not sendable just because it was purchased.** It has to be attached to a campaign,
and that campaign has to be `ACTIVE`. See the `signalhouse-10dlc` skill.

## Order of operations

1. **Search** for available numbers, filtered to what is actually needed (state, area code,
   SMS/MMS capability). Searching and NPA/NXX lookup are **free**, with no billing call on those
   paths, so filter properly rather than buying to find out.
2. **Confirm the count and the cost** before purchasing. Read current fees from
   `GET /billing/fees/:groupId`. Do not assume a price or carry one over from a previous run.
3. **Purchase** the specific numbers chosen. `subgroupId` is required, and the subgroup must
   exist and be active.
4. **List** to confirm what the account now owns and is paying for.

Numbers can be purchased while a brand is still verifying. There is no brand or campaign gate on
the purchase path. What must wait is sending, not buying.

## Spend awareness

The rule to hold: **the account is billed for what it owns, not for what it uses.**

**Purchase is charged immediately**, per number, on both the local and toll-free paths.

**Renewal is recurring, but it is environment-gated.** There is a renewal scheduler that charges a
per-number renewal fee on a billing date. It only runs when `ENABLE_NUMBER_BILLING_RENEWALS` is
enabled, and that flag is **off by default** with the real value set per environment. So:

- Never tell a customer that numbers have no ongoing cost. The mechanism exists and is the
  intended behaviour.
- Never quote the renewal as definitely active either. If it matters to the answer, check the
  environment rather than asserting.
- The renewal fee is applied to toll-free numbers too, despite being named for local ones.

**Repeated renewal failures delete the number.** After a configured number of failed renewal
attempts the number is queued for deletion, and deletion is the irreversible release above. A
customer whose balance is empty does not simply go unbilled; they can lose the number.

Before any purchase, be able to state how many numbers are being bought and the current
per-number fee, read live. If either is unknown, ask rather than buy.

Never quote a price from memory or from this file. Fees are per-group and configurable,
and writable via `PUT /billing/fees/:groupId`, so a number here would be both stale and
authoritative-looking. `GET /billing/fees/:groupId` is the only correct answer to "what does this
cost".

## Where to look it up

- **Search filters, NPA/NXX lookup, friendly names, per-number inbound webhook URLs, and the
  release semantics:** the Numbers reference, https://app2.signalhouse.io/docs/numbers.
- **Current fees:** `GET /billing/fees/:groupId`.
- **Current balance before a bulk buy:** the wallet endpoints under `/billing/wallet`.
- **Whether a number can send:** its campaign's state, not the number's. See `signalhouse-10dlc`.
