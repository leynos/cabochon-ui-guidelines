"""Paths, patterns and the profile order shared by the registry checks.

The module defines `ROOT`, the requirement and owner regular expressions, and
the `PROFILE_ORDER` ranking. The checklist, registry, mutation and command-line
modules import it.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")

PROFILE_ORDER = {"substrate": 0, "semantic": 1, "studio": 2}
