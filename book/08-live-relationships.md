---
title: Live relationships
part: The document world
figure: fig-06-state.svg
summary: Five visible states for a live object, and the rule that failure never invents a value.
---

# Live relationships

![Five live-relationship states.](../figures/fig-06-state.svg)

An object that reads from a source — a currency rate, a dataframe cell, a note
entity, a diagram element — has a relationship with that source. The
relationship can be current, refreshing, stale, broken or denied. Each state
has a distinct appearance and a distinct promise.

The five labels are a projection. They are computed from independent facts:
whether the runtime's capability broker currently authorises the read, whether
a provider can resolve the object, whether an authorised cached value exists,
which source revision that value was validated against, and whether a refresh
request is in flight. No single fact is allowed to stand in for another. In
particular, resolution and authorisation are independent: an object can be
unresolved and still denied, or resolved and still denied.

## The five states

| State      | Meaning                                                        | Appearance            |
| ---------- | -------------------------------------------------------------- | --------------------- |
| Current    | An accepted value matches the source at its known revision.    | Pine text or chip.    |
| Refreshing | A refresh is in flight; an accepted value may still be shown.  | Teal chip, no alarm.  |
| Stale      | The source is known to have advanced past the accepted value.  | Amber ink chip.       |
| Broken     | The source cannot be reached, or no accepted value exists yet. | Oxide chip.           |
| Denied     | Current authority does not permit the read.                    | Oxide chip, no value. |

The states are exhaustive for the first batch. An application must not invent a
sixth state, and must not use colour alone to distinguish them. Every chip
carries a word.

**Precedence.** When several facts hold at once, the visible state is chosen in
this order: Denied, Broken, Refreshing, Stale, Current. Denial is not a variety
of failure and never renders as Broken. A refresh in flight does not mask a
denial that arrived after the request started.

## Authority and availability are events in their own right

Authority and availability change on their own schedule. They are not refresh
requests, and they do not wait for one.

- A grant is revoked or expires. Every affected relationship moves to
  **Denied** immediately, from every state, including **Current**,
  **Refreshing** and **Broken**.
- A provider crashes, is uninstalled or loses its transport. Every affected
  relationship that is not **Denied** moves to **Broken** immediately.
- A source reports a newer revision. Every affected relationship that is
  **Current** moves to **Stale**; a relationship already **Stale** stays
  **Stale**.

The runtime's capability broker owns the authority decision. A host-resource
decision enters through the broker's adapter; it does not bypass the broker.
Redaction is applied before the next presentation, export or diagnostic
projection of the protected value. A late reply from an older request cannot
reverse a later denial and cannot publish a value that authority no longer
permits.

The reverse direction is deliberately not automatic. A new grant, a restarted
provider or a recovered transport makes recovery possible but does not by
itself assert **Current**. Recovery requires a refresh whose result is
validated against current authority and the accepted source revisions, as
described under [Refresh](#refresh).

## Transitions

A state change names its event and its owner. The first batch permits only the
following transitions.

| From                    | Event                                                       | To          | Owner             |
| ----------------------- | ----------------------------------------------------------- | ----------- | ----------------- |
| Any state               | The grant is revoked or expires                             | Denied      | Capability broker |
| Any state except Denied | The provider or transport is lost                           | Broken      | Runtime           |
| Current                 | The source reports a newer revision                         | Stale       | Provider          |
| Current, Stale, Broken  | A refresh request starts                                    | Refreshing  | Application       |
| Denied                  | A new grant is issued and a refresh request starts          | Refreshing  | User or host      |
| Refreshing              | An accepted result validates against authority and revision | Current     | Application       |
| Refreshing              | The source is unreachable or the request times out          | Broken      | Application       |
| Refreshing              | The read is refused or authority is withdrawn               | Denied      | Capability broker |
| Refreshing              | The request is cancelled                                    | Prior state | Application       |
| Refreshing              | A reply from an older request generation arrives            | No change   | Application       |

A refresh enters **Refreshing** logically when the request starts, even when it
completes within 200 milliseconds, too quickly to paint the chip. A
relationship does not move from **Current** to **Broken** by inventing a
refresh first: the availability event moves it directly. A **Broken**
relationship does not become **Stale**, because without a source there is no
newer revision to report.

## The logical refresh lifecycle

The visible chip is the last step of a lifecycle that exists even when nothing
paints.

1. **Request.** The application allocates a monotonically increasing request
   generation and records the identity, the accepted source-revision vector and
   the authority decision at invocation. No accepted value is discarded.
2. **In flight.** The relationship is **Refreshing**. If an authorised cached
   value exists, it remains visible and selectable. If none exists, the object
   shows a non-disclosing loading placeholder, not an empty value and not a
   zero.
3. **Completion.** A result is accepted only when its generation is the current
   generation, its authority is still valid and it was produced from revisions
   at least as new as the accepted vector. Acceptance replaces the vector and
   moves the relationship to **Current**.
4. **Rejection.** A transport failure or timeout moves the relationship to
   **Broken** and records the reason. A refusal or an authority withdrawal
   moves it to **Denied**. A cancellation returns the relationship to the state
   it had before the request and publishes nothing.
5. **Obsolete replies.** A reply from an older generation than the current one
   is discarded. It cannot overwrite a newer result and cannot revive a denial.

A source notification schedules an automatic refresh by default. An instrument
may instead mark the relationship **Stale** and wait for an explicit refresh,
provided its own chapter declares that policy. The choice is recorded in the
instrument's contract, not left to the implementation.

## Recoverability is a transition, not a state

A relationship that can recover does not need a sixth label. Recovery is the
transition to **Refreshing** and then to **Current**. The interface should
preserve the last accepted value while that transition is possible and while
authority permits its display.

This rule matters most for **Broken** and **Denied**, where the temptation is
to erase the value and replace it with an error. Erasing destroys the user's
context and may destroy work. The correct behaviour is:

1. preserve the last accepted value in protected storage;
2. display it for **Broken** only when current authority permits that use, and
   never for **Denied**;
3. explain what failed in one sentence;
4. offer the action that can restore the relationship, if one exists;
5. move to **Refreshing** and then **Current** without a modal interruption
   when a validated refresh succeeds.

## Refresh

A refresh must be visible but quiet. The **Refreshing** state uses the teal
accent, which is reserved for motion and decoration and never used for
body-size text. A refresh that completes within 200 milliseconds may skip the
chip entirely, provided the value updates and the status line records the time.

Rules for refresh:

- A manual refresh must be available from the object's menu and the command
  palette.
- A background refresh must not move focus or steal a click.
- A refresh must not change a value the user is editing until the edit is
  committed or abandoned.
- The status line should show the last successful refresh time, not a countdown.
- Cancellation stops publication immediately. A separate cancelling state is
  shown only while cleanup remains in progress.

## Stale

Stale is the most commonly misunderstood state. It means the source is known to
have advanced, the cached value is still readable, and the user should decide
whether to refresh. Stale is not an error, and it is not the same as a source
becoming unavailable: a missing provider is **Broken**, not **Stale**.

- Use the amber-ink role for the chip and its label at body size.
- The amber accent role may be used for a large icon or a 3-pixel rule, never
  for small text.
- The stale value remains selectable, copyable and printable.
- The object's menu offers **Refresh now** as its first item.

## Broken and denied

Broken and denied look similar and mean different things. Broken says the
source is gone or unreachable. Denied says the source exists but current
authority does not permit the application to read it.

A denied object shows no protected value in any application-controlled surface:
not in text, a tooltip, a preview, a thumbnail, an accessible name, a
diagnostic, a search result or a manifest. It shows:

- a non-disclosing placeholder;
- the word **Denied**;
- a plain-language reason, subject to the metadata disclosure policy below;
- a way to request the capability or ask an administrator, where the host
  supports it.

A broken object shows the word **Broken**, a one-sentence diagnosis drawn from
the provider, and a retry action. If an authorised cached value exists, it is
shown with the state mark. It must not show a stack trace, an internal error
code as the primary message, or a blank rectangle with no explanation.

## Metadata disclosure

Content authorisation does not automatically authorise the metadata around it.
The runtime's disclosure policy classifies each of the following as public or
protected for the current grant: the object's name, its identity, its revision,
its type, its timestamps, its source chip, its backlinks, its row and cell
counts, its search keywords, and its diagnostic entries.

- A protected metadata class is redacted everywhere: interface, tooltips,
  accessibility names, command palette results, search results, backlinks,
  logs, diagnostics and manifests.
- A denial count or aggregate is disclosed only when the policy permits that
  class. Otherwise the summary says that some content is unavailable, with no
  count and no names.
- An opt-in diagnostic-content setting cannot override a denial. It can widen
  what is recorded for public metadata only.
- Deletion impact and referential completeness are scoped to references the
  runtime knows and the user may inspect. The interface discloses that the
  assessment may be incomplete rather than enumerating protected objects.

Publication is a disclosure. Authority is revalidated immediately before an
artefact leaves the runtime, including a print handoff or an export bundle
publication. A revocation during rendering prevents the affected artefact from
being published, and a cached value never becomes publishable merely because it
is cached. The output chapters define the staging and publication boundary.

## Aggregating child states

A document, note or project may contain children in different states. Its
single summary chip uses the precedence order already stated: any **Denied**
child makes the summary **Denied**; otherwise any **Broken** child makes it
**Broken**; otherwise any **Refreshing** child makes it **Refreshing**;
otherwise any **Stale** child makes it **Stale**; otherwise it is **Current**.

The summary is invariant under the order of the children. It reports the
classes that the disclosure policy permits, and it does not let a less severe
state hide a more severe one. An empty document with no external source has no
live relationship and therefore no relationship summary; the absence of a chip
is not **Current**, because there is nothing to be current against. Its save
state is reported separately.

Persistence state, draft validity, resolution and relationship freshness are
separate vocabularies. A document may be modified but **Current**, or saved but
**Stale**. A draft that does not parse does not mutate the last committed
result and does not make that result a fresh computation.

## Embeds that are not resolved

An embed has a resolution state, which is separate from both its live
relationship state and its authorisation state. Resolution asks whether this
machine can turn the envelope into a presentation at all.

| Resolution  | Meaning                                        | What the embed shows                     |
| ----------- | ---------------------------------------------- | ---------------------------------------- |
| Resolved    | A provider loaded the object                   | The presentation and its live state      |
| Opaque      | Bytes intact; no provider is installed         | Authorised preview or placeholder        |
| Unavailable | The provider exists but cannot load the object | Name or placeholder, identity, retry     |
| Malformed   | The provider exists and rejected the payload   | Name or placeholder, identity, diagnosis |

Only a **Resolved** embed has a live relationship state. An embed that is
Opaque, Unavailable or Malformed has no Current, Refreshing, Stale, Broken or
Denied chip; its resolution state takes the chip. The axes are never combined
into a single label.

Resolution does not grant authority and does not preserve it. Removing a
provider, crashing it or reinstalling it changes resolution and availability;
it does not change whether the payload may be disclosed. An unresolved embed
that is not authorised shows a non-disclosing placeholder and offers no
**Export original**, no cached preview, no clipboard copy and no diagnostic
bytes. **Export original** is offered only for an Opaque embed whose current
authority permits export of the original bytes.

Opaque is not an error. When export is authorised, it is a promise that the
document has kept the content even though this machine cannot show it. The
placeholder must say so, and must offer **Export original** so that the bytes
can leave the environment intact. When export is not authorised, the
placeholder says that the content exists but may not be shown.

## Testing the states

A state is correctly implemented when a reviewer can produce it on demand and
observe four things: the right word, the right colour, the value policy and the
correct recovery action. The value policy is part of the state: Stale and
Broken preserve and display the last value when authority permits; Denied
preserves it only in protected storage and displays none of it.

Test **Denied** by seeding a canary value in the source and confirming that it
appears in no text, tooltip, preview, thumbnail, accessibility label,
diagnostic, search result or manifest. Test revocation from every reachable
state, including **Refreshing**, and confirm that no subsequent output
discloses the canary. Crash a provider without starting a refresh and confirm
that the relationship leaves **Current**. Deliver a late successful reply after
a denial and confirm that it does not publish.

Exercise every transition in the table above. The [checklist](40-checklist.md)
lists the transitions that must be witnessed before release.
