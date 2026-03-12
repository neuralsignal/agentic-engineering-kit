"""Pytest configuration — add scripts/ to the import path."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
