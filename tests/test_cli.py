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
        assert "Phase: 14" in result.output


class TestCLIApply:
    """Verify the apiforge apply execution command."""

    def test_apply_fails_when_directory_missing(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["apply", "--dir", "non_existent_folder_xyz"])
        assert result.exit_code == 1
        assert "Error: Could not locate generated Django project" in result.output

    def test_apply_success_calls_subprocess(self, tmp_path):
        from unittest.mock import patch, MagicMock
        
        # Scaffold a mock generated directory structure
        manage_py = tmp_path / "manage.py"
        manage_py.write_text("dummy")
        
        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            # Setup successful runs for makemigrations and migrate
            mock_make = MagicMock(returncode=0, stdout="Mock makemigrations successful\n", stderr="")
            mock_migrate = MagicMock(returncode=0, stdout="Mock migrate successful\n", stderr="")
            mock_run.side_effect = [mock_make, mock_migrate]
            
            result = runner.invoke(cli, ["apply", "--dir", str(tmp_path)])
            
            assert result.exit_code == 0
            assert "Running makemigrations..." in result.output
            assert "Mock makemigrations successful" in result.output
            assert "Running migrate..." in result.output
            assert "Mock migrate successful" in result.output
            assert "Migration successfully applied!" in result.output
            assert mock_run.call_count == 2

