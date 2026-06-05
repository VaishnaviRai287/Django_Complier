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
    click.echo(f"Phase: 4 — Support More Field Types")
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

    try:
        # 1. Parse the DSL file
        parsed = parse_api_file(file_path)

        # 2. Write all project components to output directory
        written_path = write_generated_code(parsed, output_dir)
        
        click.echo(f"Successfully generated Django app at: {written_path}")
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
