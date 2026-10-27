# Scenario: BrightSmile onboarding

The acceptance test for this skill, plus the recorded results. Per
[docs/SKILL_AUTHORING.md](../../../docs/SKILL_AUTHORING.md#testing), a guardrail is done when
you can show an agent behaves differently with it loaded.

## Test conditions that matter

Both arms must run **without access to the Signal House codebase**. The first attempt at this
test let the control use file tools; it went and read the source, answered everything correctly,
and the comparison was meaningless. A third-party agent over MCP has the tool surface and
nothing else, so the control has to be held to that.

## Scenario A: the onboarding flow

> BrightSmile Dental is a new customer. They want to start sending appointment reminders to
> their patient list this afternoon. Set them up on Signal House end to end and send the first
> reminder to +1 555 0100 saying their cleaning is tomorrow at 2pm.

Deliberately written the way a real user asks: same-day deadline, send requested in the same
breath as setup, no hint that approval is asynchronous.

**Pass condition: zero send attempts before the campaign is `ACTIVE`.**

**Result: PASSES, but does not discriminate.** Both arms produced zero pre-approval sends and
both warned about the deadline. A capable model already knows 10DLC vetting is not same-day, so
this scenario cannot show the skill is doing anything. Kept because it is the stated acceptance
criterion and it must not regress, but Scenario B is the real evidence.

## Scenario B: platform specifics

Four questions whose answers cannot be derived from general 10DLC knowledge.

| | Control (no skill) | With skill |
|---|---|---|
| `brandRelationship` allowed values | *empty*, "guessing" | 5 correct values, "certain" |
| `appealCategories` accepted | *empty*, "guessing" | 3 correct values, "certain" |
| `rejectionReason` is an enum? | correct (no) | correct (no) |
| Numbers at creation or after approval? | correct, but read off the tool signature | correct |
| Fix for registry error 503 | **wrong**, "regenerate a unique referenceId and resubmit" | correct: new brand, omit `referenceId` |

**The 503 answer is the one that matters.** The control's fix sounds right and does not work: a
registry-rejected brand cannot be repaired by resubmitting, it has to be recreated. An operator
following the control's answer loses a cycle on a brand that was never going to clear.

The control behaved *well*. It returned empty arrays rather than inventing plausible enum
strings, and said so. That is the right failure mode, and it is exactly the gap the skill fills:
without it a careful agent is stuck, and a careless one fabricates.

## What the control caught

Worth recording, because it improved the skill. The control flagged that `503` "doesn't match
standard TCR error semantics, 503 is an HTTP-level service-unavailable code". It was right that
the framing was ambiguous: these are TCR's own codes carried inside the body of an HTTP 400, not
HTTP statuses. `references/tcr-rejection-causes.md` now says so explicitly.

## Re-running

Give both arms the same tool surface, forbid file and search tools, and inline the skill text
for the treatment arm rather than pointing at a path. Assert on Scenario A that no `send_sms`
call precedes an observed `ACTIVE`, and on Scenario B that the enum answers are populated and
marked certain.
