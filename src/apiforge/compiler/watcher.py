"""
Phase 11 — Live Schema Watch Mode.

Monitors a target .api file for changes, automatically validating
and printing evolution plans on save.
"""

import os
import time
import click

from apiforge.compiler.parser import parse_api_file
from apiforge.compiler.snapshot import load_snapshot
from apiforge.compiler.diff import compute_diff, format_diff
from apiforge.compiler.planner import generate_migration_plan, format_migration_plan


def watch_file(file_path: str, interval: float = 1.0) -> None:
    """Watch target file for modifications, printing changes live."""
    click.echo(f"Watching '{file_path}' for changes... Press Ctrl+C to stop.")
    
    try:
        last_mtime = os.path.getmtime(file_path)
    except FileNotFoundError:
        click.echo(f"Error: File '{file_path}' not found.", err=True)
        raise SystemExit(1)

    while True:
        time.sleep(interval)
        try:
            current_mtime = os.path.getmtime(file_path)
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                trigger_reload(file_path)
        except KeyboardInterrupt:
            click.echo("\nStopping watcher.")
            break
        except FileNotFoundError:
            continue


def trigger_reload(file_path: str) -> None:
    """Recompile, diff, and plan migrations for the updated schema."""
    click.clear()
    click.echo(f"--- Change detected at {time.strftime('%H:%M:%S')} ---")
    
    try:
        # 1. Recompile and Validate
        new_schema = parse_api_file(file_path)
        
        # 2. Load Snapshot Baseline
        old_schema = load_snapshot()
        if old_schema is None:
            click.echo("Warning: No snapshot baseline found. Run 'apiforge generate' to establish one.")
            return

        # 3. Output Diff Report
        click.echo("\n[Schema Diff]")
        changes = compute_diff(old_schema, new_schema)
        click.echo(format_diff(changes))

        # 4. Output Migration Plan
        click.echo("\n[Migration Plan]")
        plan = generate_migration_plan(old_schema, new_schema)
        click.echo(format_migration_plan(plan))
        click.echo("\n" + "=" * 40)
        
    except ValueError as e:
        click.echo(f"\nValidation Error: {e}", err=True)
    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
