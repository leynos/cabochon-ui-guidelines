"""Load the shared figure catalogue from `tools/figure-data.json`.

The module parses the file once and exposes `OUT`, the committed `figures`
directory, along with the figure specs, live states, live transitions and
resolution states that the builders read. `figuregen.cli`, `figuregen.ornaments`
and `figuregen.production` import it, as do `figuregen.figures.embed` and
`figuregen.figures.live_state`.
"""

from __future__ import annotations

import json
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

OUT = ROOT / "figures"

DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))

LIVE_STATES: dict[str, dict[str, str]] = DATA["live_states"]

# ``from`` is a Python keyword, so the transition record is declared with the
# functional TypedDict syntax that keeps the document's own field name.
LiveTransition = typ.TypedDict(
    "LiveTransition",
    {
        "id": str,
        "from": list[str],
        "event": str,
        "to": str,
        "owner": str,
    },
)

LIVE_TRANSITIONS: list[LiveTransition] = DATA["live_transitions"]

RESOLUTION_STATES: dict[str, dict[str, str]] = DATA["resolution_states"]

FIGURE_SPECS: dict[str, dict[str, object]] = DATA["figures"]
