---
title: Cabochon Press
part: The studio and the contracts
figure: fig-24-press.svg
summary: Pages, preflight and a print path that reports what it will do before it does it.
---

# Cabochon Press

![Cabochon Press with pages and preflight.](../figures/fig-24-press.svg)

Cabochon Press is the studio's page-layout instrument. It arranges pages,
places live objects and prepares print-bound output. Its defining promise is
that it reports what it will do before it does it.

## Layout

- Pages panel: 150 logical units, listing every page with a thumbnail, a number
  and its size or kind. This is the **page navigator** variant of the navigator
  role, not the standard 210-unit navigator; it inherits the navigator's row,
  selection and collapse behaviour and declares its narrower default.
- Page plane: the flexible remainder, showing the current page with its bleed
  and crop marks.
- Preflight panel: 300 logical units, listing checks and their outcomes.
- Status line: page number, output intent and bleed.

The page plane is the document. The pages panel and preflight are panes; they
may be collapsed but not hidden entirely while a print operation runs. The
layout budget is derived from the bands and panes actually present, as
[Spacing and metrics](14-spacing-metrics.md) requires.

## Pages

A page declares a size, an orientation and a bleed.

- The default page is A4 portrait with a 3-millimetre bleed.
- The pages panel shows the current page with a 2-pixel oxide keyline and the
  others with a 1-pixel line.
- A page's number is metadata; its name is optional.
- Reordering pages is a drag in the panel and one undoable transaction.
- A page may be a plate, a spread or a cover, and the panel says which.

The page plane draws the bleed as a teal dashed rule outside the trim and the
crop marks as ink hairlines. Neither bleed nor crop marks are part of the
document's visible design; they are production marks.

## Placing objects

A page may contain:

- drawn objects from Burin Draw;
- embedded objects, such as a dataframe or a currency value;
- text frames;
- images with a declared resolution and intent.

A placed object keeps its identity. The page stores its placement and its
presentation, not a flattened copy. A live object prints through its print
presentation, and the preflight reports which presentation will be used. The
chosen print presentation is recorded in the manifest as an intent choice, not
treated as an unreported substitution.

## Preflight

Preflight runs on demand and before every export. It checks:

- fonts embedded, or a substitution declared in advance;
- images at the required resolution;
- colour intent supported by the output;
- bleed sufficient for the trim;
- live objects that will use a print presentation;
- live objects whose provider is unavailable;
- live objects whose current authority does not permit the output;
- objects outside the trim area that may be clipped.

Each check has three outcomes: pass, warning and failure.

- Pass uses a pine check mark.
- Warning uses the amber-ink role and a short explanation.
- Failure uses the oxide role and blocks the export until it is resolved or,
  where the rule permits, explicitly overridden.

Every rule declares its override policy.

- A **quality warning** may be acknowledged and recorded.
- A **policy warning** may be overridden only by a user with the relevant
  authority, and the override is recorded in the manifest.
- An **authorisation failure** cannot be overridden. A warning acknowledgement
  does not grant authority.
- A **structural failure** cannot be overridden. Corrupt output, an unsupported
  mandatory feature or a missing required font is not made valid by
  acknowledgement.

A warning must not be phrased as a failure, and a failure must not be
dismissible without a record in the export manifest. A permitted font
substitution still has to satisfy the destination's embedding and text
requirements; a substituted font is not left unembedded in a profile that
requires embedding.

## Export

The primary action is **Export PDF**, with **Proof** beside it.

- **Proof** renders the current page at screen resolution with marks and a
  preflight summary, for review only.
- **Export PDF** writes the full document at the declared intent, with an
  accompanying manifest.
- The export surface names the intent, the resolution, the bleed and the
  colour conversion it will apply.
- The manifest records each page, each placed object, its instance identity,
  its accepted revision and the presentation used.

The export reads one accepted snapshot. Every page, the manifest and any
accompanying artefact identify the same document revision, source-revision
vector and authority decision. The bundle is written to a staging location and
published as a unit; an interruption leaves the previous published bundle
intact rather than pairing new pages with an old manifest.

The export must not silently flatten a live object that could have been
rendered from its provider. If flattening is necessary, the preflight says so
and the manifest records it.

## Print

Printing uses the host's print portal. Cabochon Press prepares the scene and
the manifest; the host owns the printer dialog.

Press must not imitate a printer driver. It may show a preview and a summary,
but the choice of printer, paper source and host-specific options belongs to
the portal.

The last point at which Cabochon can prevent delivery is the handoff to the
host portal. Authority is revalidated immediately before that handoff. After
handoff, the host owns the job and Cabochon cannot recall a physical print or
an external copy; the interface says so rather than promising a recall it
cannot perform.

## Failure

- A missing font blocks export unless the user chooses a recorded substitution;
  either way, the message names the missing font and, where one was chosen, the
  substitute.
- An image below the required resolution warns and reports its effective
  resolution.
- An unavailable provider warns, prints the last cached presentation with a
  state mark and records the substitution, but only when current authority
  permits that use. A denied object is not printed from cache.
- A failed write leaves the previous export intact and reports the path and
  the reason.
- A revocation during rendering prevents publication of the affected artefact.
  The bundle is not published with a redacted page silently substituted for a
  protected one; the export fails and says which object lost authority.

## What Cabochon Press is not

- A word processor. Long-form writing belongs to Facet Notes.
- A bitmap editor.
- A printer driver.
- A way to export a screenshot of the screen. Every page is rendered from its
  scene.

## Testing

A reviewer should place a live object, run preflight with the provider present
and absent, export both times, and confirm that the manifest tells the truth in
each case.
