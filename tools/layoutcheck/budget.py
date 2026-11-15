"""Derive and validate each configuration against the declared tokens.

The module provides `bands`, `pane_width`, `side_width`, `derive` and
`validate`, which compute a configuration's band total and document plane.
`layoutcheck.chapter`, `layoutcheck.cli` and `layoutcheck.selftest` import
these functions; tokens come from `tools/layout-budgets.json`.
"""

from __future__ import annotations

from layoutcheck.contract import BUDGETS, number


def bands(tokens: dict[str, int], profiles: dict[str, list[str]], name: str) -> int:
    """Return the summed height of the profile's declared bands.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    profiles : dict[str, list[str]]
        The declared band profiles, keyed by profile name.
    name : str
        The profile whose bands are summed.

    Returns
    -------
    int
        The summed height of the profile's bands.
    """
    return sum(tokens[band] for band in profiles[name])


def pane_width(tokens: dict[str, int], name: str) -> int:
    """Return a pane's width; a collapsed strip includes its splitter.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    name : str
        The pane token whose width is read.

    Returns
    -------
    int
        The pane's width in layout units.
    """
    return tokens[name]


def side_width(tokens: dict[str, int], configuration: dict[str, object]) -> int:
    """Return the width both side panes and their splitters consume.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    configuration : dict[str, object]
        The configuration whose left and right panes are measured.

    Returns
    -------
    int
        The combined width of both side panes and their splitters.
    """
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
    """Derive the band total and the document plane for a configuration.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    profiles : dict[str, list[str]]
        The declared band profiles, keyed by profile name.
    configuration : dict[str, object]
        The configuration whose band total and document plane are derived.

    Returns
    -------
    tuple[int, int, int]
        The band total, document width and document height, in that order.
    """
    height = number(tokens, configuration["height"])
    width = number(tokens, configuration["width"])
    band_total = bands(tokens, profiles, str(configuration["profile"]))
    document_width = width - side_width(tokens, configuration)
    document_height = height - band_total
    return band_total, document_width, document_height


def expected_plane(
    tokens: dict[str, int], configuration: dict[str, object]
) -> tuple[int, int]:
    """Return the worked document plane that a configuration declares.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    configuration : dict[str, object]
        The configuration whose worked plane is read.

    Returns
    -------
    tuple[int, int]
        The declared document width and height, in that order.

    Raises
    ------
    SystemExit
        If the configuration's worked plane is not a pair of entries.
    """
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
    """Validate one configuration against the declared tokens.

    Parameters
    ----------
    configuration : dict[str, object]
        The configuration whose derived values are checked.
    tokens : dict[str, int] | None
        The token table to check against; the declared table is used when
        this is ``None``.
    profiles : dict[str, list[str]] | None
        The band profiles to check against; the declared profiles are used
        when this is ``None``.

    Returns
    -------
    list[str]
        One diagnostic per failed check, empty when the configuration
        validates.
    """
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
