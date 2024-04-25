"""Create command line entry points for Beaverdam."""

import typer

# Create main app

app = typer.Typer()

# Add commands for each functionality


@app.command()
def build(config_file_name):
    """Build database."""
    from beaverdam.builder import build_database

    build_database(config_file_name)


@app.command()
def view(config_file_name):
    """Generate dashboard."""
    from beaverdam.viewer import run_ui

    run_ui(config_file_name)
