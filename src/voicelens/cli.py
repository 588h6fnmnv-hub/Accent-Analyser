"""VoiceLens Command Line Interface core app."""

import typer
from rich.console import Console

from voicelens import __version__
from voicelens.commands.analyze import analyze_command
from voicelens.commands.doctor import perform_system_checks

# Initialize Rich Console
console = Console()

# Initialize Typer App
app = typer.Typer(
    name="voicelens",
    help=(
        "VoiceLens: A production-ready open-source Python CLI "
        "for audio and voice analysis."
    ),
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Callback to print the VoiceLens version and exit."""
    if value:
        console.print(
            f"[bold cyan]VoiceLens[/bold cyan] CLI version "
            f"[bold green]{__version__}[/bold green]"
        )
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """VoiceLens: Capture, analyze, and inspect your voice and audio features."""
    pass


@app.command()
def doctor() -> None:
    """Run a system check to diagnose environmental issues."""
    perform_system_checks()


@app.command()
def analyze() -> None:
    """Record audio from the default microphone and analyze speaker characteristics."""
    analyze_command()


if __name__ == "__main__":
    app()
