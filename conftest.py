"""Makes the project root importable so the import of mst_project works for the tests. Was required for a permanent fix."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
