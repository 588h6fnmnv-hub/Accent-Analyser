"""Tests for VoiceLens Audio Converter module."""

import wave
from pathlib import Path

import numpy as np
import pytest

from voicelens.audio_converter import AudioConversionError, convert_to_wav


def create_dummy_wav_file(
    path: Path, duration_sec: float = 0.5, sample_rate: int = 16000
) -> Path:
    """Helper to create a dummy WAV file."""
    num_samples = int(duration_sec * sample_rate)
    samples = (
        np.sin(2 * np.pi * 440 * np.arange(num_samples) / sample_rate) * 32767
    ).astype(np.int16)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

    return path


def test_convert_to_wav_happy_path(tmp_path):
    """Verify that convert_to_wav converts an audio file to 16kHz mono WAV."""
    input_wav = tmp_path / "input.wav"
    output_wav = tmp_path / "output.wav"
    create_dummy_wav_file(input_wav, duration_sec=0.5, sample_rate=44100)

    res_path = convert_to_wav(input_wav, output_wav, target_sample_rate=16000)

    assert res_path.exists()
    assert res_path == output_wav

    # Verify converted WAV specs
    with wave.open(str(output_wav), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 16000
        assert w.getnframes() > 0


def test_convert_to_wav_non_existent_input(tmp_path):
    """Verify convert_to_wav raises FileNotFoundError for missing input file."""
    input_wav = tmp_path / "missing.wav"
    output_wav = tmp_path / "output.wav"

    with pytest.raises(FileNotFoundError, match="Input audio file does not exist"):
        convert_to_wav(input_wav, output_wav)


def test_convert_to_wav_corrupted_input(tmp_path):
    """Verify convert_to_wav raises AudioConversionError for corrupted input."""
    input_corrupt = tmp_path / "corrupt.audio"
    input_corrupt.write_bytes(b"NOT_REAL_AUDIO_DATA_381902")
    output_wav = tmp_path / "output.wav"

    with pytest.raises(AudioConversionError, match="Failed to convert audio file"):
        convert_to_wav(input_corrupt, output_wav)
