"""
Phase 11 — Watcher tests.
"""

from click.testing import CliRunner
import pytest
from unittest.mock import patch, MagicMock

from apiforge.cli.main import cli
from apiforge.compiler.watcher import watch_file


class TestWatcherCLI:
    """Test watch mode CLI wrapper and execution loops."""

    @patch("apiforge.compiler.watcher.trigger_reload")
    @patch("os.path.getmtime")
    @patch("time.sleep")
    def test_watch_polling_triggers_on_file_change(self, mock_sleep, mock_mtime, mock_trigger):
        # Setup mock file times to trigger reload once, then KeyboardInterrupt
        mock_mtime.side_effect = [100.0, 200.0, KeyboardInterrupt]
        
        # Run watcher which loops until KeyboardInterrupt
        watch_file("dummy.api")
        
        # Verify reload was triggered
        mock_trigger.assert_called_once_with("dummy.api")
