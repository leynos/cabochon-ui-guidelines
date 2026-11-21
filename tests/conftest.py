"""Make the tools directory importable for the property tests.

pytest loads this file automatically and prepends the repository's `tools/`
directory to `sys.path`. The property tests then import the `statecheck`
package, which lives in that directory rather than on the installed path.
"""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
