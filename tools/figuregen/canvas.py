"""Provide SVG element builders and text helpers for every figure module.

Each function returns a fragment as a string, so a figure builder composes
geometry without escaping markup by hand, and `svg_doc` wraps a body in a
titled document. `figuregen.glyphs`, `figuregen.ornaments`,
`figuregen.production`, `figuregen.widgets` and every `figuregen.figures.*`
builder import it.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.
# pylint: disable=too-many-arguments

from __future__ import annotations

import typing as typ
from html import escape
from textwrap import dedent

from figuregen.palette import F_UI, INK, PAPER, SOFT


def attrs(**values: object) -> str:
    """Render SVG attributes, converting snake_case names to kebab-case."""
    rendered: list[str] = []
    for key, value in values.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        rendered.append(f'{name}="{escape(str(value), quote=True)}"')
    return " ".join(rendered)


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str = "none",
    stroke: str | None = INK,
    sw: float = 1,
    rx: float = 0,
    dash: str | None = None,
    opacity: float | None = None,
) -> str:
    """Draw a rectangle, optionally rounded, filled and stroked."""
    return f"<rect {attrs(x=x, y=y, width=w, height=h, fill=fill, stroke=stroke, stroke_width=sw, rx=rx, stroke_dasharray=dash, opacity=opacity)}/>"


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = INK,
    sw: float = 1,
    dash: str | None = None,
    opacity: float | None = None,
) -> str:
    """Draw a line between two points."""
    return f"<line {attrs(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=sw, stroke_dasharray=dash, opacity=opacity)}/>"


def path(
    d: str,
    *,
    fill: str = "none",
    stroke: str | None = INK,
    sw: float = 1,
    dash: str | None = None,
    opacity: float | None = None,
) -> str:
    """Draw an SVG path from its data string."""
    return f"<path {attrs(d=d, fill=fill, stroke=stroke, stroke_width=sw, stroke_dasharray=dash, opacity=opacity)}/>"


def circle(
    cx: float,
    cy: float,
    r: float,
    *,
    fill: str = "none",
    stroke: str | None = INK,
    sw: float = 1,
) -> str:
    """Draw a circle."""
    return f"<circle {attrs(cx=cx, cy=cy, r=r, fill=fill, stroke=stroke, stroke_width=sw)}/>"


def ellipse(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    *,
    fill: str = "none",
    stroke: str | None = INK,
    sw: float = 1,
) -> str:
    """Draw an ellipse."""
    return f"<ellipse {attrs(cx=cx, cy=cy, rx=rx, ry=ry, fill=fill, stroke=stroke, stroke_width=sw)}/>"


def txt(
    x: float,
    y: float,
    value: str,
    *,
    size: float = 14,
    fill: str = INK,
    family: str = F_UI,
    weight: str = "normal",
    anchor: str = "start",
    style: str = "normal",
    spacing: float | None = None,
    opacity: float | None = None,
    data_state: str | None = None,
) -> str:
    """Draw one run of text with optional weight, spacing and anchor."""
    return f"<text {attrs(x=x, y=y, fill=fill, font_family=family, font_size=size, font_weight=weight, text_anchor=anchor, font_style=style, letter_spacing=spacing, opacity=opacity, data_state=data_state)}>{escape(value)}</text>"


class TextStyle(typ.TypedDict, total=False):
    """The optional text attributes that :func:`lines` forwards to :func:`txt`."""

    family: str
    weight: str
    anchor: str
    style: str
    spacing: float | None
    opacity: float | None
    data_state: str | None


class FilledTextStyle(TextStyle, total=False):
    """A text style that also chooses the ink, for callers that set their own."""

    fill: str


def lines(
    x: float,
    y: float,
    values: list[str],
    *,
    size: float = 14,
    leading: float = 20,
    **kwargs: typ.Unpack[FilledTextStyle],
) -> str:
    """Draw several text lines at a fixed leading."""
    return "".join(
        txt(x, y + index * leading, value, size=size, **kwargs)
        for index, value in enumerate(values)
    )


def svg_doc(
    width: int, height: int, title: str, desc: str, *, body: str, bg: str = PAPER
) -> str:
    """Wrap a body in a complete SVG document with a title and description."""
    return dedent(
        f"""\
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="title desc">
          <title id="title">{escape(title)}</title>
          <desc id="desc">{escape(desc)}</desc>
          <rect width="{width}" height="{height}" fill="{bg}"/>
        {body}
        </svg>
        """
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    """Wrap text into lines of at most ``max_chars`` characters."""
    wrapped: list[str] = []
    current = ""
    for word in value.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            wrapped.append(current)
            current = word
    if current:
        wrapped.append(current)
    return wrapped


def para(
    x: float,
    y: float,
    width: float,
    value: str,
    *,
    size: float = 11,
    leading: float = 16,
    fill: str = SOFT,
    **kwargs: typ.Unpack[TextStyle],
) -> str:
    """Draw a wrapped paragraph of text."""
    return lines(
        x,
        y,
        wrap_words(value, max(8, int(width / (size * 0.52)))),
        size=size,
        leading=leading,
        fill=fill,
        **kwargs,
    )
