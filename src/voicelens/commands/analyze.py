"""VoiceLens CLI command: analyze."""

import concurrent.futures
import sys
import tempfile
import threading
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from voicelens.accent.classifier import AccentClassifier
from voicelens.alignment.aligner import WhisperAligner
from voicelens.metrics import SpeechMetricsAnalyzer
from voicelens.pronunciation import (
    MispronunciationAnalyzer,
    PronunciationAnalyzer,
    SpeechBrainBackend,
)
from voicelens.recorder.audio import AudioRecorder, AudioRecorderError
from voicelens.transcriber.whisper import WhisperTranscriber, WhisperTranscriberError

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
        "After recording, VoiceLens will automatically transcribe your audio.\n\n"
        "[bold green]Steps:[/bold green]\n"
        "1. Press [bold cyan]ENTER[/bold cyan] to start recording.\n"
        "2. Speak into your microphone.\n"
        "3. Press [bold cyan]ENTER[/bold cyan] again to stop the recording."
    )
    console.print(
        Panel(
            explanation,
            title="🎙️ [bold cyan]VoiceLens Audio Recorder & Transcriber[/bold cyan]",
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


def generate_overall_feedback(
    pron_score: float, wpm: float, filler_count: int, detected_accent: str
) -> str:
    """Helper to generate data-driven overall feedback based on the computed metrics."""
    feedback = [
        "[bold cyan]VoiceLens Comprehensive Assessment Feedback[/bold cyan]\n",
        f"• [bold]Accent Profile:[/bold] Detected accent is "
        f"[green]{detected_accent}[/green].",
    ]

    # Pronunciation feedback
    if pron_score >= 80.0:
        feedback.append(
            "• [bold]Pronunciation:[/bold] [green]Excellent clarity![/green] "
            "Your spoken acoustic features align closely with target speech standards."
        )
    elif pron_score >= 60.0:
        feedback.append(
            "• [bold]Pronunciation:[/bold] [yellow]Good clarity.[/yellow] "
            "Some words can be enunciated more clearly to improve similarity scores."
        )
    else:
        feedback.append(
            "• [bold]Pronunciation:[/bold] [red]Needs practice.[/red] "
            "Focus on vowel projection and distinct consonant closures."
        )

    # Pace feedback
    if wpm > 160.0:
        feedback.append(
            "• [bold]Pace (Speed):[/bold] [yellow]Fast speaking rate.[/yellow] "
            "Try slowing down slightly to make your speech easier to follow."
        )
    elif wpm < 110.0 and wpm > 0.0:
        feedback.append(
            "• [bold]Pace (Speed):[/bold] [yellow]Slow speaking rate.[/yellow] "
            "Increasing pace slightly can boost conversational naturalness."
        )
    elif wpm == 0.0:
        feedback.append(
            "• [bold]Pace (Speed):[/bold] No coherent conversational speech detected."
        )
    else:
        feedback.append(
            "• [bold]Pace (Speed):[/bold] [green]Natural pace.[/green] "
            "Your words-per-minute rate is in the ideal zone."
        )

    # Filler words feedback
    if filler_count > 4:
        feedback.append(
            "• [bold]Filler Words:[/bold] [yellow]High filler density.[/yellow] "
            "Try to reduce unconscious fillers to sound more authoritative."
        )
    else:
        feedback.append(
            "• [bold]Filler Words:[/bold] [green]Excellent discipline.[/green] "
            "Minimal or no filler words were detected."
        )

    return "\n".join(feedback)


# Define Typer Command
def analyze_command() -> None:
    """Record audio from the default microphone, save it, and transcribe it."""
    try:
        # 1. Record audio
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

        # 2. Transcribe audio
        transcript = ""
        transcriber = WhisperTranscriber()
        with console.status(
            "[bold cyan]Transcribing audio using Whisper...[/bold cyan]"
        ):
            transcript = transcriber.transcribe(saved_path)

        # 3. Display transcript in a Rich panel
        if not transcript:
            transcript = "[italic dim]No speech detected in the recording.[/italic dim]"

        console.print(
            Panel(
                transcript,
                title="📝 [bold cyan]Transcript[/bold cyan]",
                border_style="cyan",
                expand=False,
            )
        )

        # 4. Orchestrate backend analysis pipeline concurrently/asynchronously
        msg = (
            "[bold cyan]Analyzing speech metrics, pronunciation, and "
            "accent...[/bold cyan]"
        )
        with console.status(msg):
            aligner = WhisperAligner(transcriber=transcriber)
            metrics_analyzer = SpeechMetricsAnalyzer()
            pron_backend = SpeechBrainBackend()
            pron_analyzer = PronunciationAnalyzer(backend=pron_backend)
            accent_classifier = AccentClassifier()
            mis_analyzer = MispronunciationAnalyzer()

            # Execute pipeline concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_align = executor.submit(aligner.align, saved_path, transcript)
                future_metrics = executor.submit(
                    metrics_analyzer.analyze, saved_path, transcript
                )
                future_pron = executor.submit(
                    pron_analyzer.analyze, saved_path, transcript
                )
                future_accent = executor.submit(accent_classifier.classify, saved_path)

                # Fetch concurrent task results
                align_result = future_align.result()
                metrics = future_metrics.result()
                pron_result = future_pron.result()
                accent_result = future_accent.result()

            # Identify words likely mispronounced sorted worst first
            mispronounced_list = mis_analyzer.detect(
                align_result, pron_result.pronunciation_similarity
            )

        # 5. Render Beautiful Rich Console UI Layout
        ui_title = "📊 [bold cyan]VoiceLens Comprehensive Audio Analysis[/bold cyan]\n"
        console.print(f"\n{ui_title}")

        # Table for Accent, Overall Score, and Similarities
        accent_table = Table(
            title="Pronunciation & Accent Profile",
            show_header=True,
            header_style="bold magenta",
        )
        accent_table.add_column("Assessment Dimension", style="dim", width=25)
        accent_table.add_column("Result", justify="left")
        accent_table.add_column("Details / Confidence", justify="left")

        accent_table.add_row(
            "Predicted Accent",
            f"[bold green]{accent_result.predicted_accent}[/bold green]",
            f"Confidence: {accent_result.confidence * 100:.1f}%",
        )
        sim_percentage = pron_result.pronunciation_similarity * 100.0
        accent_table.add_row(
            "Phonetic Similarity",
            f"[bold green]{sim_percentage:.1f}%[/bold green]",
            "ECAPA-TDNN embedding match factor",
        )
        accent_table.add_row(
            "Overall Score",
            f"[bold cyan]{pron_result.overall_score:.1f} / 100[/bold cyan]",
            f"Confidence: {pron_result.confidence * 100:.1f}%",
        )
        console.print(accent_table)

        # Overall Pronunciation Score Progress Bar representation
        score_pct = int(pron_result.overall_score)
        filled_blocks = score_pct // 5
        bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
        console.print(
            f"\n[bold]Overall Pronunciation Score:[/bold] "
            f"[cyan]{pron_result.overall_score:.1f}/100[/cyan]  |{bar}|\n"
        )

        # Speaking Speed, Words Per Minute, and Pause Statistics
        metrics_table = Table(
            title="Speech Delivery Metrics",
            show_header=True,
            header_style="bold blue",
        )
        metrics_table.add_column("Speech Metric", style="dim", width=25)
        metrics_table.add_column("Value", justify="left")
        metrics_table.add_column("Interpretation", justify="left")

        metrics_table.add_row(
            "Words Per Minute (WPM)",
            f"[bold cyan]{metrics.words_per_minute:.1f}[/bold cyan]",
            "Pace speed indicator",
        )
        metrics_table.add_row(
            "Speaking Duration",
            f"{metrics.duration_seconds:.2f}s",
            "Total speaking time recorded",
        )
        metrics_table.add_row(
            "Total Words",
            str(metrics.word_count),
            f"Avg {metrics.average_words_per_sentence:.1f} words per sentence",
        )
        metrics_table.add_row(
            "Pause Count",
            f"[bold yellow]{metrics.pause_count}[/bold yellow]",
            f"Avg duration: {metrics.average_pause_duration:.2f}s",
        )
        metrics_table.add_row(
            "Longest Pause",
            f"{metrics.longest_pause:.2f}s",
            "Max non-speaking silent run",
        )
        console.print(metrics_table)

        # Filler words statistics
        fillers_str = (
            ", ".join([f"[bold red]{f}[/bold red]" for f in metrics.filler_words])
            if metrics.filler_words
            else "[green]None detected[/green]"
        )
        console.print(
            f"\n[bold]Detected Filler Words:[/bold] "
            f"[bold yellow]{metrics.filler_word_count}[/bold yellow] | {fillers_str}"
        )

        # Top 10 difficult/mispronounced words (worst first)
        diff_table = Table(
            title="Top 10 Difficult/Mispronounced Words (Sorted Worst First)",
            show_header=True,
            header_style="bold red",
        )
        diff_table.add_column("Word", justify="left")
        diff_table.add_column("Phonetic Score", justify="left")
        diff_table.add_column("Whisper Confidence", justify="left")
        diff_table.add_column("Spoken Timeframe", justify="left")

        # Take top 10 worst words
        top_10_worst = mispronounced_list[:10]
        if top_10_worst:
            for w_mis in top_10_worst:
                diff_table.add_row(
                    f"[bold red]{w_mis.word}[/bold red]",
                    f"{w_mis.score:.1f} / 100",
                    f"{w_mis.confidence * 100:.1f}%",
                    f"{w_mis.start_time:.2f}s - {w_mis.end_time:.2f}s",
                )
            console.print("\n")
            console.print(diff_table)
        else:
            diff_empty_msg = (
                "\n[bold green]✓ No major pronunciation difficulties "
                "detected for any spoken words![/bold green]"
            )
            console.print(diff_empty_msg)

        # Overall Feedback Panel
        border_col = "green" if pron_result.overall_score >= 75.0 else "yellow"
        if pron_result.overall_score < 50.0:
            border_col = "red"

        console.print("\n")
        console.print(
            Panel(
                generate_overall_feedback(
                    pron_result.overall_score,
                    metrics.words_per_minute,
                    metrics.filler_word_count,
                    accent_result.predicted_accent,
                ),
                title="💡 [bold]Overall Audio Analysis Feedback[/bold]",
                border_style=border_col,
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
    except WhisperTranscriberError as e:
        msg = (
            "[yellow]The recording was saved successfully, "
            "but transcription failed.[/yellow]"
        )
        console.print(f"\n[bold red]❌ Transcription Error:[/bold red] {e}\n{msg}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        err_msg = f"\n[bold red]❌ Unexpected Error during analysis:[/bold red] {e}"
        console.print(err_msg)
        raise typer.Exit(code=1) from e
