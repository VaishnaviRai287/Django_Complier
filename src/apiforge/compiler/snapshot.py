"""
Phase 8 — Compiler State Persistence (Snapshots).

Handles local caching and retrieval of compiled resource schemas
inside the .apiforge directory.
"""

import json
from pathlib import Path

SNAPSHOT_DIR = Path(".apiforge")
SNAPSHOT_FILE = SNAPSHOT_DIR / "schema.json"


def save_snapshot(schema: dict) -> None:
    """Save the parsed schema dictionary as the project's current snapshot."""
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(schema, indent=4))


def load_snapshot() -> dict | None:
    """Load the current schema snapshot from disk.

    Returns:
        The deserialized JSON schema dictionary, or None if no snapshot exists.
    """
    if not SNAPSHOT_FILE.exists():
        return None
    
    try:
        return json.loads(SNAPSHOT_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return None
