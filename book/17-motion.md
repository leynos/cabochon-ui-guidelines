---
title: Motion
part: Visual language
figure: fig-12-motion.svg
summary: Three durations, one easing curve and the rule that motion never delays work.
---

# Motion

![Motion timing chart.](../figures/fig-12-motion.svg)

Motion explains a change of state. It does not perform. A transition that
cannot be explained in one sentence does not need to exist.

## Durations

Cabochon uses three durations.

| Duration | Use                                            |
| -------- | ---------------------------------------------- |
| 80 ms    | A state change: hover, press, check, selection |
| 140 ms   | A pane reveal, a popover, a command palette    |
| 180 ms   | A window or sheet entering or leaving          |

The durations are ceilings, not targets. A transition that can complete sooner
should do so. Anything longer than 180 milliseconds belongs to a progress
indicator, not to a transition.

## Timing events

A timing promise names its start and its end. A duration without both is not
testable.

- The **start** is the moment the user's action is accepted.
- The **end** is the first frame that shows the new state, not the moment an
  internal task finishes.
- A state word changes at the start of a transition, not at its end, so that a
  user who looks away mid-transition still sees the truth.
- A background operation's duration is measured from its own declared trigger,
  not from the last frame the user saw.

## Easing

All transitions use ease-out: fast at the start, settling at the end. The curve
is `cubic-bezier(0.2, 0.7, 0.3, 1)`. No bounce, no overshoot, no elastic, no
spring.

A transition that changes both position and opacity should animate opacity
slightly ahead of position, so that the surface is legible before it settles.

## What may animate

- The appearance and disappearance of a popover, menu or sheet.
- The expansion and collapse of a pane or disclosure.
- The change of a state chip from Refreshing to Current.
- The movement of a progress rule.
- The scroll position of a document when the user invokes a navigation
  command.

## What must not animate

- Text that is being read.
- A control the user is about to press.
- A layout that reflows while the user is typing.
- A window that the user has just closed and expects to be gone. A closed
  window disappears immediately; it has no exit animation.
- Decoration that runs continuously in the background.

A hover transition must not delay the hover state: the control changes
immediately and the transition only softens the change. A pressed control must
respond within one frame: one refresh interval, no more than 16.7 milliseconds
at 60 hertz.

The continuous-decoration ban does not forbid a bounded activity indicator. A
progress rule, a refresh pulse or a busy mark is allowed while the operation it
describes is running, provided it stops when the operation stops, respects
reduced motion and does not imply progress the work has not made. The ban is on
motion that has no start, no end and no state to report.

## Progress

Progress is not a transition. A determinate progress rule advances with the
work and never runs backwards. An indeterminate rule moves at a constant speed
and does not imply completion. Neither uses a spinner when a rule will fit.

A background refresh may pulse gently, but the pulse is bounded by the refresh
it describes. It stops when the refresh stops, it does not run while the
relationship is idle, and it respects reduced motion.

## Cancellation

Cancellation is a timing promise with a precise meaning.

- Cancellation is **acknowledged** within 200 milliseconds: the interface shows
  that the request was received and suppresses any further publication.
- Publication of a cancelled operation's result never happens, even if the
  result arrives later.
- Cleanup may take longer than 200 milliseconds. While it continues, the
  interface shows a separate **Cancelling** state and does not present the
  operation as finished.
- Rollback is complete when the committed state has returned to its prior
  revision. That is a separate observable fact from acknowledgement.
- A cancelled external handoff, such as a print job already given to the host,
  may be beyond recall. The interface says so rather than promising a
  cancellation it cannot perform.

## Reduced motion

When the system reports a preference for reduced motion, every finite
transition collapses to 0.01 milliseconds. Progress indicators become static
rules with a text label. An indefinitely repeating animation becomes static; it
is never sped up to a near-zero duration to satisfy the rule. No information
may depend on motion; the state word and the colour carry the meaning.

Reduced motion is a setting of the environment, not of an application. Every
Cabochon surface must honour it.

## Motion and state

A state change must be complete when the transition ends. If a chip fades from
Refreshing to Current, the word must change at the start of the fade, not at
the end, so that a user who looks away mid-transition still sees the truth.

## Testing motion

A reviewer should be able to answer three questions for every transition: what
changed, how long it took and what happens under reduced motion. A transition
that cannot answer all three is decoration, and should be removed.

Timing tests use an injected clock and controlled completions, not wall-clock
sleeps. They cross the progress threshold and verify visibility and
announcement; they cancel an operation and deliver a late reply, then verify
that nothing was published; they change the reduced-motion setting and verify
that state and keyboard availability survive the loss of movement. Expectations
are derived from the declared policy values, not from a particular build's
observed delay.
