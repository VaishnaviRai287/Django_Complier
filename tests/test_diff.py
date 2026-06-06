"""
Phase 9 — Diff Engine tests.
"""

from click.testing import CliRunner
import pytest

from apiforge.cli.main import cli
from apiforge.compiler.diff import compute_diff, format_diff
from apiforge.compiler.snapshot import save_snapshot, SNAPSHOT_FILE


@pytest.fixture(autouse=True)
def clean_snapshot_env():
    """Ensure baseline is cleared before and after each test execution."""
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()
    yield
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()


class TestDiffCalculation:
    """Test difference engine logic."""

    def test_no_changes_detected(self):
        schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "name", "type": "string"}]
            }]
        }
        diff = compute_diff(schema, schema)
        assert format_diff(diff) == "No changes detected."

    def test_detects_added_and_removed_resources(self):
        old_schema = {
            "resources": [{
                "resource": "OldModel",
                "fields": [{"name": "id", "type": "integer"}]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "NewModel",
                "fields": [{"name": "id", "type": "integer"}]
            }]
        }

        diff = compute_diff(old_schema, new_schema)
        
        assert "NewModel" in diff["added_resources"]
        assert "OldModel" in diff["removed_resources"]
        assert not diff["added_fields"]

    def test_detects_added_and_removed_fields(self):
        old_schema = {
            "resources": [{
                "resource": "User",
                "fields": [
                    {"name": "username", "type": "string"},
                    {"name": "price", "type": "decimal"}
                ]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "User",
                "fields": [
                    {"name": "username", "type": "string"},
                    {"name": "stock", "type": "integer"}
                ]
            }]
        }

        diff = compute_diff(old_schema, new_schema)
        
        assert diff["added_fields"] == ["User.stock"]
        assert diff["removed_fields"] == ["User.price"]
        assert not diff["added_resources"]


class TestDiffCLI:
    """Test CLI subcommand difference integration."""

    def test_cli_diff_error_when_no_snapshot(self, tmp_path):
        api_file = tmp_path / "test.api"
        api_file.write_text("resource User { username string }")

        runner = CliRunner()
        result = runner.invoke(cli, ["diff", str(api_file)])
        
        assert result.exit_code == 1
        assert "Error: No previous schema snapshot found" in result.output

    def test_cli_diff_displays_output(self, tmp_path):
        # 1. Establish baseline
        old_schema = {
            "resources": [{
                "resource": "User",
                "fields": [{"name": "username", "type": "string"}]
            }]
        }
        save_snapshot(old_schema)

        # 2. Create updated file
        api_file = tmp_path / "test.api"
        api_file.write_text("resource User {\n    username string\n    age integer\n}")

        runner = CliRunner()
        result = runner.invoke(cli, ["diff", str(api_file)])
        
        assert result.exit_code == 0
        assert "Added field:" in result.output
        assert "User.age" in result.output
