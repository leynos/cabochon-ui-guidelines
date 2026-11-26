"""Tests for the figure generator's atomic SVG writer.

`figuregen.cli._write_svg` must publish a destination through a per-call
scratch file, so concurrent generator runs never replace the same scratch path
twice or leave a partial document behind.
"""

from __future__ import annotations

import threading
import typing as typ

from figuregen.cli import _write_svg

if typ.TYPE_CHECKING:
    from pathlib import Path

SVG_TEXT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">\n'
    '  <rect width="10" height="10" fill="#285E50"/>\n'
    "</svg>\n"
)


def test_write_svg_survives_two_concurrent_writers(tmp_path: Path) -> None:
    """Two threads writing one destination leave complete text and no scratch."""
    destination = tmp_path / "nested" / "figure.svg"
    destination.parent.mkdir()
    barrier = threading.Barrier(2)
    errors: list[Exception] = []

    def write() -> None:
        """Write the SVG once both writers reach the barrier."""
        try:
            barrier.wait(timeout=5)
            _write_svg(destination, SVG_TEXT)
        except Exception as error:  # ruff: ignore[blind-except] - reported below
            errors.append(error)

    threads = [threading.Thread(target=write) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors, f"concurrent _write_svg raised: {errors!r}"
    assert destination.read_text(encoding="utf-8") == SVG_TEXT, (
        "the destination must hold the complete SVG text"
    )
    assert destination.stat().st_mode & 0o777 == 0o644, (
        "the destination must be readable with mode 0o644"
    )
    leftovers = [
        path for path in destination.parent.iterdir() if path.name.endswith(".tmp")
    ]
    assert not leftovers, f"no scratch file may remain: {leftovers!r}"
