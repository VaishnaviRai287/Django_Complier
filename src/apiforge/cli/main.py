"""
APIForge CLI — Main entrypoint.

This module defines the root Click group and registers all subcommands.
Running `apiforge --help` invokes this.
"""

import click
from apiforge import __version__

@click.group()
@click.version_option(version=__version__, prog_name="apiforge")
def cli():
    """APIForge — Incremental API Schema Compiler for Django.

    Compiles .api specification files into production-ready Django backends
    with built-in schema evolution tracking and migration planning.

    Get started:

        apiforge parse examples/product.api

    For more information on a command:

        apiforge <command> --help
    """
    pass


@cli.command()
def info():
    """Display project information and current build phase."""
    click.echo(f"APIForge v{__version__}")
    click.echo(f"Phase: 13 — Schema Evolution Intelligence")
    click.echo(f"Status: CLI operational")
    click.echo()
    click.echo("Run 'apiforge --help' to see available commands.")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def parse(file_path):
    """Parse a .api file and display its contents as JSON.

    FILE_PATH is the path to the .api specification file.

    Example:

        apiforge parse examples/product.api
    """
    from apiforge.compiler.parser import parse_to_json

    try:
        output = parse_to_json(file_path)
        click.echo(output)
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    default="generated",
    help="Directory to write the generated models.py file."
)
def generate(file_path, output_dir):
    """Generate a Django models.py file from a .api specification.

    FILE_PATH is the path to the .api specification file.

    Example:

        apiforge generate examples/product.api
    """
    from apiforge.compiler.parser import parse_api_file
    from apiforge.compiler.codegen import generate_django_model, write_generated_code
    from apiforge.compiler.snapshot import save_snapshot
    import time

    try:
        start_time = time.perf_counter()

        # 1. Parse the DSL file
        parsed = parse_api_file(file_path)

        # 2. Write all project components to output directory
        written_path = write_generated_code(parsed, output_dir)

        # 3. Save schema snapshot state
        save_snapshot(parsed)

        end_time = time.perf_counter()
        compilation_time_ms = int((end_time - start_time) * 1000)

        click.echo(f"Successfully generated Django app at: {written_path}")

        # Metrics
        resources_count = len(parsed.get("resources", []))
        fields_count = sum(len(r.get("fields", [])) for r in parsed.get("resources", []))
        relationships_count = sum(1 for r in parsed.get("resources", []) for f in r.get("fields", []) if f.get("type") == "belongs_to")

        click.echo()
        click.echo("Compilation Report")
        click.echo()
        click.echo(f"Resources: {resources_count}")
        click.echo(f"Fields: {fields_count}")
        click.echo(f"Relationships: {relationships_count}")
        click.echo()
        click.echo("Generated Files:")
        click.echo("✓ models.py")
        click.echo("✓ serializers.py")
        click.echo("✓ views.py")
        click.echo("✓ urls.py")
        click.echo()
        click.echo(f"Compilation Time: {compilation_time_ms} ms")
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

@cli.command()
def snapshot():
    """Display the last compiled schema snapshot from disk."""
    import json
    from apiforge.compiler.snapshot import load_snapshot

    snapshot_data = load_snapshot()
    if snapshot_data is None:
        click.echo("Error: No schema snapshot found. Run 'apiforge generate' first.", err=True)
        raise SystemExit(1)

    # Output formatted JSON snapshot structure
    click.echo(json.dumps(snapshot_data, indent=4))


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def diff(file_path):
    """Compare a .api file against the last compiled snapshot baseline."""
    from apiforge.compiler.parser import parse_api_file
    from apiforge.compiler.snapshot import load_snapshot
    from apiforge.compiler.diff import compute_diff, format_diff

    try:
        # 1. Parse the new active spec file
        new_schema = parse_api_file(file_path)

        # 2. Load the baseline snapshot
        old_schema = load_snapshot()
        if old_schema is None:
            click.echo("Error: No previous schema snapshot found. Run 'apiforge generate' first to establish a baseline.", err=True)
            raise SystemExit(1)

        # 3. Calculate and display modifications
        changes = compute_diff(old_schema, new_schema)
        click.echo(format_diff(changes))

        # 4. Dependency impact report
        from apiforge.compiler.planner import generate_migration_plan, format_impact_report
        plan_ops = generate_migration_plan(old_schema, new_schema)
        impact = format_impact_report(old_schema, new_schema, plan_ops)
        if impact:
            click.echo()
            click.echo(impact)
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def plan(file_path):
    """Compare a .api file against the snapshot baseline and generate a migration plan."""
    from apiforge.compiler.parser import parse_api_file
    from apiforge.compiler.snapshot import load_snapshot
    from apiforge.compiler.planner import generate_migration_plan, format_migration_plan, format_impact_report

    try:
        # 1. Parse the new active spec file
        new_schema = parse_api_file(file_path)

        # 2. Load the baseline snapshot
        old_schema = load_snapshot()
        if old_schema is None:
            click.echo("Error: No previous schema snapshot found. Run 'apiforge generate' first to establish a baseline.", err=True)
            raise SystemExit(1)

        # 3. Calculate and display migration plan
        migration_ops = generate_migration_plan(old_schema, new_schema)
        click.echo(format_migration_plan(migration_ops))

        # 4. Dependency impact report
        impact = format_impact_report(old_schema, new_schema, migration_ops)
        if impact:
            click.echo()
            click.echo(impact)
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def watch(file_path):
    """Monitor a .api file for live modifications and display evolution delta on save."""
    from apiforge.compiler.watcher import watch_file

    watch_file(file_path)