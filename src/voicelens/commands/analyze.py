"""VoiceLens CLI command: analyze."""

import sys
import tempfile
import threading
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from voicelens.recorder.audio import AudioRecorder, AudioRecorderError

# Initialize Rich Console
console = Console()


def perform_analysis_recording() -> Path:
    """Handles user flow for recording audio from default microphone.

    Returns:
        Path: The path to the saved recording.wav file.

    Raises:
        AudioRecorderError: If there's an error starting/stopping the recorder.
    """
    # 1. Display Rich Panel explaining what will happen
    explanation = (
        "VoiceLens will record audio from your default microphone.\n"
        "This tool only captures raw audio and does not perform speech-to-text "
        "yet.\n\n"
        "[bold green]Steps:[/bold green]\n"
        "1. Press [bold cyan]ENTER[/bold cyan] to start recording.\n"
        "2. Speak into your microphone.\n"
        "3. Press [bold cyan]ENTER[/bold cyan] again to stop the recording."
    )
    console.print(
        Panel(
            explanation,
            title="🎙️ [bold cyan]VoiceLens Audio Recorder[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )

    recorder = AudioRecorder()

    # Pre-check audio availability before asking user to press ENTER.
    # This gives immediate feedback if PortAudio or devices are missing.
    recorder.check_system_availability()

    # 2. Ask user to press ENTER to start
    console.print(
        "\nPress [bold green]ENTER[/bold green] when you are ready to start..."
    )
    sys.stdin.readline()

    # 3. Start recording
    console.print("[bold yellow]Initializing audio stream...[/bold yellow]")
    recorder.start_recording()

    start_time = time.time()
    stop_timer = threading.Event()

    # 4. Display live recording timer
    # Use Rich's Live display updated by a daemon thread
    with Live(
        Text("Initializing live timer...", style="bold red"),
        refresh_per_second=10,
        transient=True,
    ) as live:

        def update_timer() -> None:
            while not stop_timer.is_set():
                elapsed = time.time() - start_time
                timer_text = (
                    f"🔴 Recording... {elapsed:.1f}s  [dim](Press ENTER to stop)[/dim]"
                )
                live.update(Text(timer_text, style="bold red"))
                time.sleep(0.1)

        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()

        # 5. Wait for second ENTER to stop recording
        sys.stdin.readline()
        stop_timer.set()
        timer_thread.join()

    # Stop recording
    recorder.stop_recording()
    duration = recorder.get_duration()
    console.print(
        f"[bold green]✓ Recording stopped successfully![/bold green] "
        f"Captured [bold cyan]{duration:.2f} seconds[/bold cyan] of audio."
    )

    # 6. Save recording to temporary directory
    temp_dir = Path(tempfile.gettempdir()) / "voicelens"
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_path = temp_dir / "recording.wav"

    console.print("[dim]Saving audio data to WAV file...[/dim]")
    recorder.save_wav(output_path)

    return output_path


# Define Typer Command
def analyze_command() -> None:
    """Record audio from the default microphone and save it as a WAV file."""
    try:
        saved_path = perform_analysis_recording()
        console.print(
            Panel(
                f"[bold green]Success![/bold green] Recording saved to:\n"
                f"[bold cyan]{saved_path.resolve()}[/bold cyan]",
                title="💾 [bold green]File Saved[/bold green]",
                border_style="green",
                expand=False,
            )
        )
    except AudioRecorderError as e:
        msg = (
            "[yellow]Please check your system audio settings, "
            "microphone connection, and permissions.[/yellow]"
        )
        console.print(f"\n[bold red]❌ Audio Recording Error:[/bold red] {e}\n{msg}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=1) from e
