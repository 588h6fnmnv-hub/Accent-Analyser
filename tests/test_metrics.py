"""Tests for the VoiceLens Speech Metrics Analyzer."""

import tempfile
import wave
from pathlib import Path

import numpy as np
import pytest

from voicelens.metrics import (
    SpeechMetrics,
    SpeechMetricsAnalyzer,
    SpeechMetricsAnalyzerError,
)


def create_test_wav(
    filepath: Path,
    sections: list[tuple[float, str]],
    sample_rate: int = 16000,
    sampwidth: int = 2,
    channels: int = 1,
) -> None:
    """Helper to generate a WAV file with specific silence and tone sections."""
    total_data = []

    for duration, sect_type in sections:
        num_samples = int(sample_rate * duration)
        if sect_type == "silence":
            if sampwidth == 2:
                data = np.zeros(num_samples * channels, dtype=np.int16)
            elif sampwidth == 1:
                data = np.ones(num_samples * channels, dtype=np.uint8) * 128
            elif sampwidth == 4:
                data = np.zeros(num_samples * channels, dtype=np.int32)
            else:
                data = np.zeros(num_samples * channels, dtype=np.int16)
        else:
            # Generate a 440Hz sine wave tone
            t = np.linspace(0, duration, num_samples, endpoint=False)
            tone = np.sin(2 * np.pi * 440 * t)
            if channels > 1:
                tone = np.repeat(tone, channels)
            if sampwidth == 2:
                data = (tone * 16384).astype(np.int16)
            elif sampwidth == 1:
                data = ((tone * 127) + 128).astype(np.uint8)
            elif sampwidth == 4:
                data = (tone * 1073741824).astype(np.int32)
            else:
                data = (tone * 16384).astype(np.int16)
        total_data.append(data)

    if not total_data:
        full_signal = np.array([], dtype=np.int16)
    else:
        full_signal = np.concatenate(total_data)

    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(full_signal.tobytes())


@pytest.fixture
def test_audio_file():
    """Fixture to generate a temporary multi-section WAV file."""
    # Sections of the audio:
    # 1. 0.5s silence -> Valid pause (>= 0.40s)
    # 2. 0.5s tone -> Speech/sound signal
    # 3. 0.1s silence -> Ignored (< 0.15s)
    # 4. 0.5s tone -> Speech/sound signal
    # 5. 0.6s silence -> Valid pause (>= 0.40s)
    # Total duration: 2.2 seconds.
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)

    sections = [
        (0.5, "silence"),
        (0.5, "tone"),
        (0.1, "silence"),
        (0.5, "tone"),
        (0.6, "silence"),
    ]
    create_test_wav(path, sections)

    yield path

    if path.exists():
        path.unlink()


def test_missing_audio_file():
    """Verify that SpeechMetricsAnalyzer raises errors for non-existent files."""
    analyzer = SpeechMetricsAnalyzer()
    with pytest.raises(SpeechMetricsAnalyzerError, match="Audio file does not exist"):
        analyzer.analyze("non_existent_file.wav", "some text")


def test_corrupt_audio_file():
    """Verify that SpeechMetricsAnalyzer handles corrupt/invalid files gracefully."""
    analyzer = SpeechMetricsAnalyzer()
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        # Write some junk bytes that are not a valid WAV file
        with Path(tmp.name).open("wb") as f:
            f.write(b"NOT A WAV FILE")
        with pytest.raises(SpeechMetricsAnalyzerError, match="Failed to load WAV file"):
            analyzer.analyze(tmp.name, "some text")


def test_empty_transcript(test_audio_file):
    """Verify that empty transcripts return zero metrics, but valid duration/pauses."""
    analyzer = SpeechMetricsAnalyzer()
    metrics = analyzer.analyze(test_audio_file, "   ")

    assert isinstance(metrics, SpeechMetrics)
    assert metrics.duration_seconds == 2.2
    assert metrics.word_count == 0
    assert metrics.words_per_minute == 0.0
    assert metrics.average_words_per_sentence == 0.0
    assert metrics.pause_count == 2
    assert metrics.average_pause_duration == 0.55
    assert metrics.longest_pause == 0.6
    assert metrics.filler_word_count == 0
    assert metrics.filler_words == []


def test_filler_word_detection(test_audio_file):
    """Verify regex-based filler word detection and word-boundary matching."""
    analyzer = SpeechMetricsAnalyzer()
    transcript = (
        "Um, basically actually, we are thinking uh, erm. "
        "Like, you know we had a likable ah umbrella that is basically cool."
    )
    metrics = analyzer.analyze(test_audio_file, transcript)

    assert metrics.word_count == 21
    expected_fillers = [
        "um",
        "basically",
        "actually",
        "uh",
        "erm",
        "like",
        "you know",
        "ah",
        "basically",
    ]
    assert metrics.filler_word_count == 9
    assert metrics.filler_words == expected_fillers


def test_speaking_rate_and_sentences(test_audio_file):
    """Verify speaking rate (WPM) and words-per-sentence calculations."""
    analyzer = SpeechMetricsAnalyzer()
    transcript = "This is first. How are you today? We are studying metrics."
    metrics = analyzer.analyze(test_audio_file, transcript)

    assert metrics.word_count == 11
    assert metrics.words_per_minute == 300.0
    assert metrics.average_words_per_sentence == round(11 / 3, 4)


def test_no_punctuation_sentence_fallback(test_audio_file):
    """Verify sentence splitting fallback when there is no punctuation."""
    analyzer = SpeechMetricsAnalyzer()
    transcript = "This is a single long sentence without punctuation"
    metrics = analyzer.analyze(test_audio_file, transcript)

    assert metrics.word_count == 8
    assert metrics.average_words_per_sentence == 8.0


def test_stereo_to_mono_downmixing():
    """Verify that multi-channel (stereo) signals are downmixed correctly."""
    analyzer = SpeechMetricsAnalyzer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)

    sections = [(0.5, "silence")]
    create_test_wav(path, sections, channels=2)

    try:
        metrics = analyzer.analyze(path, "Test")
        assert metrics.pause_count == 1
        assert metrics.average_pause_duration == 0.5
        assert metrics.longest_pause == 0.5
    finally:
        if path.exists():
            path.unlink()


def test_unsupported_sample_width():
    """Verify that unsupported sample widths raise custom exception."""
    analyzer = SpeechMetricsAnalyzer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)

    try:
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(3)  # Unsupported 24-bit
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00" * 300)

        msg = "Unsupported sample width"
        with pytest.raises(SpeechMetricsAnalyzerError, match=msg):
            analyzer.analyze(path, "Test")
    finally:
        if path.exists():
            path.unlink()


def test_8bit_and_32bit_pcm():
    """Verify that 8-bit and 32-bit PCM signals are processed correctly."""
    analyzer = SpeechMetricsAnalyzer()

    # 8-bit PCM
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path_8bit = Path(tmp.name)
    try:
        create_test_wav(path_8bit, [(0.5, "silence")], sampwidth=1)
        metrics_8bit = analyzer.analyze(path_8bit, "Test")
        assert metrics_8bit.pause_count == 1
    finally:
        if path_8bit.exists():
            path_8bit.unlink()

    # 32-bit PCM
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path_32bit = Path(tmp.name)
    try:
        create_test_wav(path_32bit, [(0.5, "silence")], sampwidth=4)
        metrics_32bit = analyzer.analyze(path_32bit, "Test")
        assert metrics_32bit.pause_count == 1
    finally:
        if path_32bit.exists():
            path_32bit.unlink()


def test_zero_samples_and_extremely_short_audio():
    """Verify handling of empty or extremely short audio signals."""
    analyzer = SpeechMetricsAnalyzer()

    # 1. 0 samples
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path_0 = Path(tmp.name)
    try:
        create_test_wav(path_0, [])
        metrics_0 = analyzer.analyze(path_0, "Test")
        assert metrics_0.pause_count == 0
        assert metrics_0.average_pause_duration == 0.0
    finally:
        if path_0.exists():
            path_0.unlink()

    # 2. Extremely short signal (1 sample)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path_short = Path(tmp.name)
    try:
        with wave.open(str(path_short), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00\x00")  # exactly 1 sample

        metrics_short = analyzer.analyze(path_short, "Test")
        assert metrics_short.pause_count == 0
    finally:
        if path_short.exists():
            path_short.unlink()
