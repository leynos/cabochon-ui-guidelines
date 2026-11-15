"""Derive and validate each configuration against the declared tokens.

The module provides `bands`, `pane_width`, `side_width`, `derive` and
`validate`, which compute a configuration's band total and document plane.
`layoutcheck.chapter`, `layoutcheck.cli` and `layoutcheck.selftest` import
these functions; tokens come from `tools/layout-budgets.json`.
"""

from __future__ import annotations

from layoutcheck.contract import BUDGETS, number


def bands(tokens: dict[str, int], profiles: dict[str, list[str]], name: str) -> int:
    """Return the summed height of the profile's declared bands."""
    return sum(tokens[band] for band in profiles[name])


def pane_width(tokens: dict[str, int], name: str) -> int:
    """Return a pane's width; a collapsed strip includes its splitter."""
    return tokens[name]


def side_width(tokens: dict[str, int], configuration: dict[str, object]) -> int:
    """Return the width both side panes and their splitters consume."""
    total = 0
    for side in ("left", "right"):
        pane = str(configuration[side])
        total += pane_width(tokens, pane)
        if pane != "collapsed_strip":
            total += tokens["splitter"]
    return total


def derive(
    tokens: dict[str, int],
    profiles: dict[str, list[str]],
    configuration: dict[str, object],
) -> tuple[int, int, int]:
    """Derive the band total and the document plane for a configuration."""
    height = number(tokens, configuration["height"])
    width = number(tokens, configuration["width"])
    band_total = bands(tokens, profiles, str(configuration["profile"]))
    document_width = width - side_width(tokens, configuration)
    document_height = height - band_total
    return band_total, document_width, document_height


def expected_plane(
    tokens: dict[str, int], configuration: dict[str, object]
) -> tuple[int, int]:
    """Return the worked document plane that a configuration declares."""
    declared = configuration["expected"]
    if not isinstance(declared, list) or len(declared) != 2:
        raise SystemExit(
            f"layout contract: {configuration['name']}: expected plane is malformed"
        )
    return number(tokens, declared[0]), number(tokens, declared[1])


def validate(
    configuration: dict[str, object],
    tokens: dict[str, int] | None = None,
    profiles: dict[str, list[str]] | None = None,
) -> list[str]:
    """Validate one configuration against the declared tokens."""
    errors: list[str] = []
    tokens = BUDGETS["tokens"] if tokens is None else tokens
    profiles = BUDGETS["profiles"] if profiles is None else profiles
    band_total, width, height = derive(tokens, profiles, configuration)
    expected_width, expected_height = expected_plane(tokens, configuration)
    if (width, height) != (expected_width, expected_height):
        errors.append(
            f"{configuration['name']}: derives {width} × {height}, "
            f"worked value is {expected_width} × {expected_height}"
        )
    if width < tokens["document_width_min"]:
        errors.append(
            f"{configuration['name']}: document width {width} is below "
            f"the {tokens['document_width_min']}-unit minimum"
        )
    viewport_min = (
        tokens["compact_viewport_min"]
        if configuration.get("compact")
        else tokens["document_viewport_min"]
    )
    if height < viewport_min:
        errors.append(
            f"{configuration['name']}: viewport {height} is below "
            f"the {viewport_min}-unit minimum"
        )
    if band_total + viewport_min > number(tokens, configuration["height"]):
        errors.append(
            f"{configuration['name']}: {band_total} units of bands plus a "
            f"{viewport_min}-unit viewport do not fit the window"
        )
    content = tokens["document_content_height"]
    if configuration.get("compact") and height >= content:
        errors.append(
            f"{configuration['name']}: compact viewport {height} does not "
            f"require the {content}-unit content extent to scroll"
        )
    return errors
