"""Property tests for the declared Escape order.

Chapter 18 fixes a total order over the layers Escape may consume: composition,
completion, the text draft, a transient surface and a tool gesture. These tests
draw every combination of the five layers and assert that one Escape clears
exactly the first applicable layer and leaves the rest untouched.
"""

from __future__ import annotations

import copy
import importlib.util
import typing as typ
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

TOOLS = Path(__file__).resolve().parent.parent / "tools"


def _load_keyboard() -> typ.ModuleType:
    """Load the hyphenated checker script as an importable module."""
    path = TOOLS / "check-keyboard.py"
    spec = importlib.util.spec_from_file_location("check_keyboard", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


KEYBOARD = _load_keyboard()
DEFAULTS: dict[str, object] = KEYBOARD.FIXTURES["defaults"]

LAYERS = st.fixed_dictionaries(
    {
        "composition": st.booleans(),
        "completion_open": st.booleans(),
        "text_mode": st.booleans(),
        "surface_open": st.booleans(),
        "tool_gesture": st.booleans(),
        "draft_dirty": st.booleans(),
    }
)


def facts_for(layers: dict[str, bool]) -> dict[str, object]:
    """Return the fact set that the drawn layers describe."""
    facts = copy.deepcopy(DEFAULTS)
    facts.update(
        {
            "mode": "text" if layers["text_mode"] else "navigation",
            "composition": layers["composition"],
            "completion_open": layers["completion_open"],
            "draft": "edited" if layers["draft_dirty"] else "",
            "committed": "",
            "draft_dirty": layers["draft_dirty"],
            "surface_open": layers["surface_open"],
            "tool_gesture": layers["tool_gesture"],
        }
    )
    return facts


@given(LAYERS)
def test_one_escape_clears_only_the_first_applicable_layer(
    layers: dict[str, bool],
) -> None:
    """Exactly the highest-priority set layer is consumed."""
    facts = facts_for(layers)
    expected = copy.deepcopy(facts)
    if layers["composition"]:
        expected["composition"] = False
    elif layers["completion_open"]:
        expected["completion_open"] = False
    elif layers["text_mode"]:
        expected["draft"] = expected["committed"]
        expected["draft_dirty"] = False
        expected["mode"] = "navigation"
    elif layers["surface_open"]:
        expected["surface_open"] = False
    elif layers["tool_gesture"]:
        expected["tool_gesture"] = False
    KEYBOARD.apply_escape(facts)
    assert facts == expected, (
        "Escape consumes exactly the highest-priority layer and leaves the rest"
    )


@given(LAYERS)
def test_dismissing_a_completion_leaves_the_draft_alone(
    layers: dict[str, bool],
) -> None:
    """The completion layer never edits or reverts the text draft."""
    facts = facts_for(layers)
    draft = copy.deepcopy(facts["draft"])
    dirty = copy.deepcopy(facts["draft_dirty"])
    KEYBOARD.apply_escape(facts)
    if layers["completion_open"] and not layers["composition"]:
        assert facts["draft"] == draft, (
            "dismissing a completion leaves the draft text unchanged"
        )
        assert facts["draft_dirty"] is dirty, (
            "dismissing a completion leaves the draft's dirty flag unchanged"
        )


def test_escape_with_no_open_layer_is_a_no_op() -> None:
    """An empty layer stack leaves every fact as it was."""
    facts = facts_for(
        {
            "composition": False,
            "completion_open": False,
            "text_mode": False,
            "surface_open": False,
            "tool_gesture": False,
            "draft_dirty": False,
        }
    )
    before = copy.deepcopy(facts)
    KEYBOARD.apply_escape(facts)
    assert facts == before, "Escape with no open layer leaves every fact unchanged"
