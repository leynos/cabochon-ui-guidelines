---
title: The formula tool
part: The workspace
figure: fig-26-formula.svg
summary: A tool at the point of use, with named sources, visible authority and a live result.
---

# The formula tool

![Formula tool popover over a selected table.](../figures/fig-26-formula.svg)

The formula tool is Cabochon's proof that a tool can act across object types
without ambient authority. It appears beside a compatible selection, names what
it will read, shows what it is allowed to do and returns a live value with its
own identity.

## Where it appears

The tool is offered when the selection exposes an addressable scalar selector
and the application holds the capabilities the tool requires.

- A numeric cell in a dataframe.
- A currency value.
- An addressable note entity, such as a defined term.
- A diagram element with a declared value.

An incompatible selection does not show the tool. It is not greyed in a global
services menu, because the environment does not have one.

## The popover

The formula popover is anchored to the selection. It is 430 pixels wide and
contains:

- a **Formula** kicker and an Escape hint;
- an expression field, focused, with the current expression selected;
- a **Sources** block listing every object and selector the expression reads;
- an **Authority** block listing the capabilities used and their outcome;
- the computed result in large metadata type, with its state chip;
- **Insert live value** as the primary action and **Cancel** as the way out.

The popover must not cover the selected cells. It flips above or beside the
selection as space allows.

## Sources

Every source is named explicitly.

- A source chip carries the object's name and the selector, such as
  **TABLE B2:B9** or **RATE · GBP**.
- Selecting a source chip reveals the object in its own instrument without
  closing the popover.
- A source that is stale or broken is marked on its chip with the same state
  vocabulary as the rest of the environment.
- The expression may not read a source that is not listed. If the user types
  an undeclared reference, the tool offers to add it before evaluating.

## Authority

The authority block shows each capability the expression needs and whether it
is granted.

- **Granted** appears in pine 2.
- **Denied** appears in oxide and names the capability.
- A denied read must not reveal the value, not even as a partially computed
  result.
- The tool must not request a broader capability than the expression uses.

The grant that authorizes the preview is scoped to the invocation. It permits
the computation the user is about to see and the insertion that follows, and
the tool does not retain it after the popover closes.

Preview authority and object authority are different. An inserted value
receives its own delegated grant, recorded with its identity, which the host
may revoke at any time. The interface must never imply that insertion preserves
the popover's grant.

## The result

The result is computed before insertion, so that the user can see what will
enter the document. It uses the result's declared type and format.

- A currency result shows its currency code.
- A number result shows its unit and precision.
- A result that is still computing shows **Refreshing** and the last value.
- A result that cannot be computed shows the state and the reason, with
  **Insert live value** disabled.

The result must never be a value that the authority block does not justify.

## Inserting

**Insert live value** inserts a live value object into the document at the
selection, or into the focused note at the caret.

- The inserted value records the expression, its sources and the capabilities
  it needs.
- Those capabilities are delegated to the new object, not borrowed from the
  popover. The object may refresh only while the host grants them; a refusal
  moves it to **Denied**.
- It has its own identity and can be inspected, refreshed and exported.
- It is not a pasted number.
- It is not a private macro that only this application can evaluate.

If the document does not accept a live value at the caret, the primary action
becomes **Copy result** and the reason is stated.

## Failure and recovery

- If a source moves, the value becomes **Stale** and keeps its last result.
- If a grant is withdrawn, the value becomes **Denied** and hides its result.
- If a provider crashes, the value becomes **Broken** and offers **Retry**.
- Recovery returns the value to **Current** without a modal dialog and
  without changing its identity.

## Keyboard

| Key           | Action                                       |
| ------------- | -------------------------------------------- |
| Enter         | Insert the live value                        |
| Escape        | Cancel and restore the selection             |
| Control+Space | Offer selector completions                   |
| Tab           | Move between expression, sources and actions |

The expression field supports the usual editing keys and must not swallow Tab,
so that the user can reach the actions without a pointer.

## What the tool is not

- A global calculator.
- A scripting console.
- A way to read a value the application was not granted.
- A converter that flattens a live result into text on insertion.
- A service menu that lists tools the selection cannot use.
