import typer

from beaverdam.builder import build_database
from beaverdam.viewer import run_ui

# Create subcommand apps
# build = typer.Typer()
# view = typer.Typer()

# Create main app
app = typer.Typer()

@app.command()
def build(config_file_name):
    build_database(config_file_name)

@app.command()
def view(config_file_name):
    run_ui(config_file_name)