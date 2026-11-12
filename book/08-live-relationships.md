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
whether the runtime's capability broker currently authorises the read; whether
a provider is present; whether an accepted value exists; which source revisions
that value was validated against; the latest source revision the provider has
reported; whether an interruption has invalidated an earlier validation; and
whether an authorised request generation is in flight. No single fact is
allowed to stand in for another. In particular, resolution and authorisation
are independent: an object can be unresolved and still denied, or resolved and
still denied.

The release has one typed transition source, `live_transitions` in
`tools/figure-data.json`. The table below, the state plate and the event
fixtures in `tools/state-fixtures.json` are all checked against it, so an edge
cannot be changed in one place and left stale in another.

## The five states

| State      | Meaning                                                                           | Colour role        | Mark          |
| ---------- | --------------------------------------------------------------------------------- | ------------------ | ------------- |
| Current    | An accepted value satisfies the freshness condition.                              | Pine text or chip. | Filled dot.   |
| Refreshing | An authorised request is in flight; an accepted value may show.                   | Refresh text chip. | Rotation arc. |
| Stale      | The source is ahead of the accepted value, or validation lapsed.                  | Amber ink chip.    | Triangle.     |
| Broken     | No request is in flight and the provider is absent or no value has been accepted. | Oxide chip.        | Broken link.  |
| Denied     | Current authority does not permit the read.                                       | Oxide chip.        | Padlock.      |

The states are exhaustive for the first batch. An application must not invent a
sixth state, and must not use colour alone to distinguish them. Every chip
carries a word and the state's own shape mark. The mark is drawn in the state's
colour role, but its form is what survives a monochrome display, a
colour-vision difference or a screenshot reproduced without colour.

**Projection.** When several facts hold at once, the visible state is computed
in this order. The order is exhaustive and total; it is not a severity ranking.

1. **Denied** if current authority does not permit the read. A request in
   flight does not mask a denial. Denial is not a variety of failure and never
   renders as Broken.
2. **Refreshing** if an authorised request generation is in flight. This holds
   even when no accepted value exists yet, so first load is Refreshing and not
   Broken. Revocation and provider loss terminate the request before the
   projection runs.
3. **Broken** if no request is in flight and either the provider is not
   present or no value has been accepted.
4. **Stale** if an accepted value exists, the provider is present, and the
   value does not satisfy the freshness condition below.
5. **Current** if an accepted value satisfies the freshness condition.

The freshness condition treats two independent records. The *known-source
vector* is the latest revision the provider has reported for each source. The
*invalidation epoch* is a counter advanced whenever authority is revoked or the
provider is lost, because either event breaks the chain of observation. An
accepted value records both the vector it was validated against and the epoch
at validation. It satisfies the freshness condition only when its validated
vector covers every component of the current known-source vector, its
validation epoch is the current epoch, no request is in flight, and current
authority still permits the read.

The order above is the projection. The separate order used to summarise
children in [Aggregating child states](#aggregating-child-states) is a severity
ranking: Denied, Broken, Refreshing, Stale, Current. A summary may therefore be
more severe than any individual projection rule would suggest for one child,
but it never invents a state.

## Authority and availability are events in their own right

Authority and availability change on their own schedule. They are not refresh
requests, and they do not wait for one.

- A grant is revoked or expires. Every affected relationship moves to
  **Denied** immediately, from every state, including **Current**,
  **Refreshing** and **Broken**. Any request generation in flight is terminated
  and its replies are discarded. The invalidation epoch advances.
- A provider crashes, is uninstalled or loses its transport. Every affected
  relationship that is not **Denied** moves to **Broken** immediately. Any
  request generation in flight is terminated and its replies are discarded. The
  invalidation epoch advances, so a later recovery cannot assert **Current**
  from a value validated before the gap.
- A source reports a newer revision. The known-source vector advances. A
  **Current** relationship moves to **Stale**; a relationship already **Stale**
  stays **Stale**. If **Refreshing**, the in-flight generation is superseded by
  a new request and the relationship stays **Refreshing**. A **Broken**
  relationship with no provider receives no notification, because no provider
  is present to send one. A **Broken** relationship that has a provider but no
  accepted value is still notified and schedules a refresh.

The runtime's capability broker owns the authority decision. A host-resource
decision enters through the broker's adapter; it does not bypass the broker.
Redaction is applied before the next presentation, export or diagnostic
projection of the protected value. A late reply from an older request cannot
reverse a later denial and cannot publish a value that authority no longer
permits.

The reverse direction is deliberately not automatic. A new grant, a restarted
provider or a recovered transport makes recovery possible but does not by
itself assert **Current**. When an accepted value exists, the relationship
projects as **Stale**, because the revocation or loss advanced the invalidation
epoch. With no accepted value it projects as **Broken**. Recovery requires a
dispatched refresh, whose result must satisfy the freshness condition, as
described under [The logical refresh lifecycle](#the-logical-refresh-lifecycle).

## Transitions

A state change names its event and its owner. The first batch permits only the
following transitions.

| From                    | Event                                                                      | To         | Owner                                   |
| ----------------------- | -------------------------------------------------------------------------- | ---------- | --------------------------------------- |
| Any state               | The grant is revoked or expires                                            | Denied     | Capability broker                       |
| Any state except Denied | The provider or transport is lost                                          | Broken     | Runtime                                 |
| Current                 | The source reports a newer revision                                        | Stale      | Provider                                |
| Refreshing              | The source reports a newer revision                                        | Refreshing | Provider                                |
| Broken                  | The provider returns; an accepted value exists                             | Stale      | Runtime                                 |
| Denied                  | A grant is issued; an accepted value exists                                | Stale      | Capability broker                       |
| Denied                  | A grant is issued; no value has been accepted                              | Broken     | Capability broker                       |
| Current, Stale, Broken  | A refresh request is dispatched while authorised and a provider is present | Refreshing | Application                             |
| Denied                  | A grant is issued, then a refresh is dispatched with a provider present    | Refreshing | Application after the Capability broker |
| Refreshing              | A validated result satisfies the freshness condition                       | Current    | Application                             |
| Refreshing              | The transport fails or the request times out                               | Broken     | Application                             |
| Refreshing              | The read is refused or authority is withdrawn                              | Denied     | Capability broker                       |
| Refreshing              | The request is cancelled                                                   | Recomputed | Application                             |
| Refreshing              | A superseded reply arrives                                                 | No change  | Application                             |

A refresh enters **Refreshing** logically when an authorised request is
dispatched, even when it completes within 200 milliseconds, too quickly to
paint the chip. A relationship does not move from **Current** to **Broken** by
inventing a refresh first: the availability event moves it directly. A
**Broken** relationship does not become **Stale** through a notification,
because no provider is present to report a newer revision.

**Recomputed** and **No change** are outcomes, not sixth states. **Recomputed**
means the request ends and the projection is evaluated again from the current
facts; a cancellation never restores the label that preceded the request. **No
change** means the reply belongs to a superseded generation and is discarded.

A source notification is itself a scheduling event. When it arrives with no
request in flight, the default is to dispatch a refresh. The relationship then
moves to **Refreshing**, and the freshest accepted value remains visible. An
instrument may instead expose **Stale** and wait for an explicit refresh, but
only when its own chapter declares that policy and records it in the
instrument's contract.

## The logical refresh lifecycle

The visible chip is the last step of a lifecycle that exists even when nothing
paints.

1. **Request.** The application allocates a monotonically increasing request
   generation and records the identity, the known-source vector at dispatch and
   the authority decision. No accepted value is discarded. A dispatch is
   refused while authority or a provider is absent; the relationship then stays
   **Denied** or **Broken**.
2. **In flight.** The relationship is **Refreshing**. If an authorised cached
   value exists, it remains visible and selectable. If none exists, the object
   shows a non-disclosing loading placeholder, not an empty value and not a
   zero. A first load with no cached value is therefore **Refreshing**, not
   **Broken**.
3. **Completion.** A result is accepted only when its generation is the current
   generation, authority is still valid, the provider is still present and its
   validated vector covers the known-source vector at completion. Acceptance
   replaces the accepted value and vector, records the current invalidation
   epoch, and projects as **Current**. A result that is behind the known source
   is superseded: it is not accepted and does not publish.
4. **Rejection.** A transport failure or timeout ends the request, records the
   reason and marks availability uncertain, so the projection is **Broken**. A
   refusal or an authority withdrawal moves the relationship to **Denied**. A
   cancellation ends the request and recomputes the projection from the facts;
   if the source advanced during the request, the result is **Stale**, not the
   label that preceded it.
5. **Obsolete replies.** A reply from an older generation than the current one
   is discarded. It cannot overwrite a newer result, cannot revive a denial and
   cannot settle a superseded request.

A source notification advances the known-source vector before any refresh is
scheduled. If it arrives during a request, that generation is superseded and a
new generation is dispatched, because the older request may have read the
previous revision. Only the newest generation may complete.

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

A refresh must be visible but quiet. The **Refreshing** state uses the refresh
mark role for its rotation arc and rule, and the refresh text role for any
word. Decorative teal is never used for text. The refresh text role is a
separate, darker tint that meets contrast at body size. A refresh that
completes within 200 milliseconds may skip the chip entirely, provided the
value updates and the status line records the time.

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

Stale is the most commonly misunderstood state. It means the cached value is
still readable, but it is not known to be current: either the source reports a
newer revision, or a revocation or provider gap has invalidated an earlier
validation. The user should decide whether to refresh. Stale is not an error,
and it is not the same as a source becoming unavailable: a missing provider is
**Broken**, not **Stale**.

- Use the stale role for the chip and its label at body size; it is the
  readable amber tint, not the decorative amber accent.
- The amber accent role may be used for a large icon or a 3-unit rule, never
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
- Count disclosure binds every consumer: a visible status string, an accessible
  name or description, a shortened or localized status line, a fallback
  placeholder, an error message and a manifest. A consumer that loses the count
  keeps a meaningful non-count form, such as the worst state and a generic
  phrase, rather than dropping the status or inventing a number.
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
single summary chip uses the severity order: any **Denied** child makes the
summary **Denied**; otherwise any **Broken** child makes it **Broken**;
otherwise any **Refreshing** child makes it **Refreshing**; otherwise any
**Stale** child makes it **Stale**; otherwise it is **Current**. Severity ranks
the children's visible states; it does not replace the projection that computes
each child's state.

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

Exercise every transition in the table above. The fixture set in
`tools/state-fixtures.json` covers first load without a cached value, a source
advance during a refresh, cancellation after that advance, supersession, a
timeout, a grant change during a request and a late completion after denial.
`make states` runs the fixtures and compares the chapter and figure with the
typed transition source. The [checklist](40-checklist.md) lists the transitions
that must be witnessed before release.
