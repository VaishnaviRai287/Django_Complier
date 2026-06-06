"""
Phase 0 — CLI Smoke Tests.

Verifies that the CLI entrypoint is functional:
- `apiforge --help` exits cleanly
- `apiforge --version` prints the correct version
- `apiforge info` prints project status
"""

from click.testing import CliRunner

from apiforge import __version__
from apiforge.cli.main import cli


class TestCLIHelp:
    """Verify that --help works and shows expected content."""

    def test_help_exits_successfully(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_help_contains_project_name(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "APIForge" in result.output

    def test_help_contains_description(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "Incremental API Schema Compiler" in result.output


class TestCLIVersion:
    """Verify that --version prints the correct version."""

    def test_version_exits_successfully(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_version_shows_correct_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert __version__ in result.output


class TestCLIInfo:
    """Verify the info subcommand works."""

    def test_info_exits_successfully(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        assert result.exit_code == 0

    def test_info_shows_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        assert __version__ in result.output

    def test_info_shows_phase(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        assert "Phase: 8" in result.output
