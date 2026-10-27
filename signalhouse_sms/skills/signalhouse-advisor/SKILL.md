---
name: signalhouse-advisor
description: >-
  Planning a Signal House integration: the order the platform actually enforces, which work is
  asynchronous and how long it really takes, what the caller's role permits, and which Signal House
  skill answers which question.
  TRIGGER when the user asks how to build on Signal House, wants an integration plan or timeline,
  asks "what do I need to send my first message", is scoping or estimating work, or is deciding
  which endpoint or SDK namespace to reach for.
  SKIP once the plan is settled and the work is one specific area. Hand off to signalhouse-setup,
  signalhouse-10dlc, signalhouse-numbers, signalhouse-sms or signalhouse-webhooks and follow that.
---

# Planning a Signal House integration

## What cannot happen

**There is no path from zero to a sent message in one sitting.** Brand and campaign registration go
to external registries and carriers. Approval is measured in **days**, not minutes, and it can be
rejected. Any plan, estimate or demo script that ends "and then we send a test message" on day one
is wrong, and stating it optimistically wastes the customer's launch date rather than saving it.

**The order is enforced by the platform, not by convention.** Brand before campaign; numbers
attached at campaign creation; campaign `ACTIVE` before any send. A plan that discovers this at step
nine has to be rebuilt from step two.

**A plan is only executable if the token's role permits it.** Roles are checked server-side and
differ sharply: a customer `api` service user is bound to a single group, `developer` reaches
messaging, numbers, keys and webhooks, `billing` reaches billing only, and the `signalhouse_*` roles
are staff. Confirm what the authenticated caller actually is before planning work it cannot perform.
When the role is unknown, say so and plan against the least privilege rather than assuming `admin`.

**Nothing about cost may be stated from memory.** Fees are per group, configurable and writable.
`GET /billing/fees/:groupId` is the only correct answer to what something costs, and a number
written into a plan reads as authoritative long after it stops being true.

## The pipeline, in the order it must happen

1. **Credential and group.** A token, and the `groupId` it is scoped to. `signalhouse-setup`.
2. **Webhooks.** Before the first write, not after the first surprise. Most of what follows resolves
   out of band. `signalhouse-webhooks`.
3. **Funded wallet.** Registration and number purchase are charged. An unfunded account fails at the
   first billable step, which is usually the brand.
4. **Brand.** Submitted for verification. Days. Can be rejected, and some rejections require
   recreating the brand rather than editing it. `signalhouse-10dlc`.
5. **Numbers.** These can be bought while the brand is still verifying. Buying is not gated; sending is.
   `signalhouse-numbers`.
6. **Campaign.** Created **with its numbers attached**, then registered downstream. More days.
   `signalhouse-10dlc`.
7. **Send.** Only once the campaign is `ACTIVE` and the number is `READY`. `signalhouse-sms`.

Steps 4 and 5 overlap. Steps 4 and 6 do not.

## Asynchronous by design

Mutating operations across brand, campaign and number return **202** and complete out of band. The
HTTP response means accepted, not done. This shapes the whole integration:

- **Subscribe, do not poll.** The platform's own guidance says so, and a polling loop hits rate
  limits while still finding out late.
- **Every long-running step needs a persisted state machine on the caller's side.** An integration
  that holds "waiting for brand approval" in memory loses it on the next deploy.
- **Design for rejection, not just delay.** Brand and campaign both have terminal failure states. A
  flow with no path for "rejected, here is why" is unfinished.

## Which skill answers which question

| The question | Skill |
|---|---|
| How do I authenticate, what token, why a 401 | `signalhouse-setup` |
| How do I know when something finished | `signalhouse-webhooks` |
| Why is my campaign rejected or stuck, what does TCR need | `signalhouse-10dlc` |
| How do I find, buy, or release numbers, what do they cost | `signalhouse-numbers` |
| How do I send, why did a send fail, what does a message cost | `signalhouse-sms` |

If a question spans two of these, answer with the constraint first and the mechanics second. The
constraint is nearly always the part that changes the plan.

## Where to look it up

- **The full setup pipeline:** the Brands and Campaigns references
  (https://app2.signalhouse.io/docs/brands, https://app2.signalhouse.io/docs/campaigns).
- **A first working call:** https://app2.signalhouse.io/docs/getting-started.
- **Current fees and balance:** the billing endpoints, read live, per group.
