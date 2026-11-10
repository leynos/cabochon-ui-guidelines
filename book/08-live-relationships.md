---
title: Live relationships
part: The document world
figure: fig-06-state.svg
summary: Five states for a live object, and the rule that failure never invents a value.
---

# Live relationships

![Five live-relationship states.](../figures/fig-06-state.svg)

An object that reads from a source — a currency rate, a dataframe cell, a note
entity, a diagram element — has a relationship with that source. The
relationship can be current, refreshing, stale, broken or denied. Each state
has a distinct appearance and a distinct promise.

## The five states

| State      | Meaning                                             | Appearance            |
| ---------- | --------------------------------------------------- | --------------------- |
| Current    | The value matches the source at its known revision. | Pine text or chip.    |
| Refreshing | A refresh is in progress; the last value is shown.  | Teal chip, no alarm.  |
| Stale      | The source changed and the value has not refreshed. | Amber ink chip.       |
| Broken     | The source cannot be reached or no longer exists.   | Oxide chip.           |
| Denied     | The capability to read the source was refused.      | Oxide chip, no value. |

The states are exhaustive for the first batch. An application must not invent a
sixth state, and must not use colour alone to distinguish them. Every chip
carries a word.

## Recoverability is a transition, not a state

A relationship that can recover does not need a sixth label. Recovery is the
transition back to **Current**, and the interface should preserve the last
successful value while that transition is possible.

This rule matters most for **Broken** and **Denied**, where the temptation is
to erase the value and replace it with an error. Erasing destroys the user's
context and may destroy work. The correct behaviour is:

1. keep the last committed value, marked with its state;
2. explain what failed in one sentence;
3. offer the action that can restore the relationship, if one exists;
4. return to **Current** without a modal interruption when the source
   recovers.

## Refresh

A refresh must be visible but quiet. The **Refreshing** state uses the teal
accent, which is reserved for motion and decoration and never used for
body-size text. A refresh that completes quickly may skip the chip entirely,
provided the value updates and the status line records the time.

Rules for refresh:

- A manual refresh must be available from the object's menu and the command
  palette.
- A background refresh must not move focus or steal a click.
- A refresh must not change a value the user is editing until the edit is
  committed or abandoned.
- The status line should show the last successful refresh time, not a
  countdown.

## Stale

Stale is the most commonly misunderstood state. It means the source is known to
have changed, the cached value is still readable, and the user should decide
whether to refresh. Stale is not an error.

- Use amber ink `#8A5B24` for the chip and its label at body size.
- Amber `#B8792E` may be used for a large icon or a 3-pixel rule, never for
  small text.
- The stale value remains selectable, copyable and printable.
- The object's menu offers **Refresh now** as its first item.

## Broken and denied

Broken and denied look similar and mean different things. Broken says the
source is gone or unreachable. Denied says the source exists but the
application may not read it.

The interface must not reveal a denied value, not even in a tooltip, a preview,
a thumbnail or an accessibility label. A denied object shows:

- the object's name, if the name itself is not protected;
- the word **Denied**;
- the name of the capability that was refused, in plain language;
- a way to request the capability or ask an administrator, where the host
  supports it.

A broken object shows the word **Broken**, a one-sentence diagnosis drawn from
the provider, and a retry action. It must not show a stack trace, an internal
error code as the primary message, or a blank rectangle with no explanation.

## Embeds that are not live

An embedded object may be readable but not interpretable. The first batch adds
three placeholder states for embeds, which are orthogonal to the five live
states:

- **Opaque** — the bytes are present and intact, but no provider is installed
  to render them. The object can be exported and preserved.
- **Unavailable** — the provider exists but the object cannot be loaded.
- **Malformed** — the provider exists and rejected the payload.

Opaque is not an error. It is a promise that the document has kept the content
even though this machine cannot show it. The placeholder must say so, and must
offer **Export original** so that the bytes can leave the environment intact.

## Testing the states

A state is correctly implemented when a reviewer can produce it on demand and
observe four things: the right word, the right colour, the preserved value and
the correct recovery action. The [checklist](40-checklist.md) lists the
transitions that must be exercised before release.
