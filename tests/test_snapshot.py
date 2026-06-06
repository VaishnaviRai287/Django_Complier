"""
Phase 8 — Snapshot persistence tests.
"""

import json
from pathlib import Path
from click.testing import CliRunner
import pytest

from apiforge.cli.main import cli
from apiforge.compiler.snapshot import save_snapshot, load_snapshot, SNAPSHOT_FILE


@pytest.fixture(autouse=True)
def clean_snapshot_env():
    """Ensure tests run in a clean environment and clean up files after execution."""
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()
    yield
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()


class TestSnapshotStorage:
    """Test standard save and load operations."""

    def test_saves_and_loads_dict(self):
        mock_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "name", "type": "string"}]
            }]
        }

        save_snapshot(mock_schema)
        
        # Verify file is created in directory
        assert SNAPSHOT_FILE.exists()

        loaded = load_snapshot()
        assert loaded == mock_schema

    def test_returns_none_if_missing(self):
        assert load_snapshot() is None


class TestSnapshotCLI:
    """Test CLI subcommand integration."""

    def test_cli_error_when_no_snapshot(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["snapshot"])
        
        assert result.exit_code == 1
        assert "Error: No schema snapshot found" in result.output

    def test_cli_outputs_snapshot_json(self):
        mock_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "name", "type": "string"}]
            }]
        }
        save_snapshot(mock_schema)

        runner = CliRunner()
        result = runner.invoke(cli, ["snapshot"])
        
        assert result.exit_code == 0
        parsed_output = json.loads(result.output)
        assert parsed_output == mock_schema
