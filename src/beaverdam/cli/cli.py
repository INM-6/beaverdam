import typer

from beaverdam.builder import build_database
from beaverdam.viewer import run_ui

# Create subcommand apps
# build = typer.Typer()
# view = typer.Typer()

# Create main app
app = typer.Typer()
# app.add_typer(build, name="build")
# app.add_typer(view, name="view")

@app.command()
def build():
    build_database()

@app.command()
def view():
    run_ui()