"""Loader: Read resume.json with UTF-8 encoding (prevents cp874 issues on Windows Thai locale)"""

from __future__ import annotations

import json
from pathlib import Path


def load_resume(path: str | Path) -> dict:
    """Load resume.json into a dict (always using UTF-8)"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Resume file not found: {p.resolve()}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)
