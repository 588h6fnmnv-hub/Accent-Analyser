"""Tests for the VoiceLens 'analyze' command and audio recording functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from typer.testing import CliRunner

from voicelens.cli import app
from voicelens.recorder.audio import AudioRecorder, AudioRecorderError


class MockInputStream:
    """Mock for sounddevice.InputStream to simulate live microphone recording."""

    def __init__(self, samplerate, channels, dtype, callback):
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.callback = callback
        self._running = False

    def start(self):
        self._running = True
        # Simulate incoming mock audio data chunk immediately
        # Float32 array of shape (frames, channels)
        mock_data = np.zeros((1024, self.channels), dtype=np.float32)
        # Add some mock sine wave audio
        mock_data[:, 0] = np.sin(np.linspace(0, 10 * np.pi, 1024))
        self.callback(mock_data, 1024, None, None)

    def stop(self):
        self._running = False

    def close(self):
        self._running = False


@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice module successfully."""
    mock_sd = MagicMock()
    # Mock query_devices to return a simulated microphone
    mock_sd.query_devices.return_value = [
        {"name": "Mock Microphone", "max_input_channels": 2}
    ]
    mock_sd.InputStream = MockInputStream

    with (
        patch("voicelens.recorder.audio._SOUNDDEVICE_AVAILABLE", True),
        patch("voicelens.recorder.audio.sd", mock_sd),
    ):
        yield mock_sd


def test_audio_recorder_happy_path(mock_sounddevice):
    """Verify standard happy-path of starting, stopping, and saving audio."""
    assert mock_sounddevice is not None
    recorder = AudioRecorder(sample_rate=16000, channels=1)

    # Initial state
    assert recorder.get_duration() == 0.0

    # Start recording
    recorder.start_recording()
    assert recorder._recording is True

    # Check duration (we populated 1024 frames at 16000 sample rate = 0.064s)
    duration = recorder.get_duration()
    assert duration > 0.0
    assert abs(duration - 0.064) < 1e-4

    # Stop recording
    recorder.stop_recording()
    assert recorder._recording is False

    # Stop again should be safe and do nothing
    recorder.stop_recording()

    # Save to wav
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "recording.wav"
        recorder.save_wav(file_path)

        assert file_path.exists()
        # Verify it has some file size
        assert file_path.stat().st_size > 44  # WAV header is 44 bytes


def test_audio_recorder_errors(mock_sounddevice):
    """Test exceptions and boundary conditions on AudioRecorder."""
    assert mock_sounddevice is not None
    recorder = AudioRecorder()

    # Saving when empty should raise an error
    with pytest.raises(AudioRecorderError, match="No audio data was recorded"):
        recorder.save_wav("test.wav")

    # Start recording twice
    recorder.start_recording()
    with pytest.raises(AudioRecorderError, match="already in progress"):
        recorder.start_recording()

    recorder.stop_recording()


def test_audio_recorder_no_devices(mock_sounddevice):
    """Test when no audio devices are found on the system."""
    mock_sounddevice.query_devices.return_value = []
    recorder = AudioRecorder()

    with pytest.raises(AudioRecorderError, match="No audio input/output devices"):
        recorder.start_recording()


def test_audio_recorder_no_input_channels(mock_sounddevice):
    """Test when only output devices (speakers) are found, but no microphone."""
    mock_sounddevice.query_devices.return_value = [
        {"name": "Speakers Only", "max_input_channels": 0}
    ]
    recorder = AudioRecorder()

    with pytest.raises(AudioRecorderError, match="No default microphone/input"):
        recorder.start_recording()


def test_audio_recorder_device_query_error(mock_sounddevice):
    """Test general error querying devices."""
    mock_sounddevice.query_devices.side_effect = Exception("Hardware failure")
    recorder = AudioRecorder()

    with pytest.raises(AudioRecorderError, match="Failed to query system audio"):
        recorder.start_recording()


def test_audio_recorder_stream_start_error(mock_sounddevice):
    """Test when opening stream raises an exception."""
    mock_sounddevice.InputStream = MagicMock(side_effect=Exception("Permission denied"))
    recorder = AudioRecorder()

    with pytest.raises(AudioRecorderError, match="Could not open microphone/input"):
        recorder.start_recording()


def test_audio_recorder_stop_stream_error(mock_sounddevice):
    """Test when stopping the audio stream raises an exception."""
    assert mock_sounddevice is not None
    recorder = AudioRecorder()
    recorder.start_recording()

    # Mock stream stop to fail
    recorder._stream.stop = MagicMock(side_effect=Exception("Hardware release error"))
    with pytest.raises(AudioRecorderError, match="Error stopping stream"):
        recorder.stop_recording()


def test_audio_recorder_save_wav_error(mock_sounddevice):
    """Test when saving WAV file fails due to write/system issues."""
    assert mock_sounddevice is not None
    recorder = AudioRecorder()
    recorder.start_recording()
    recorder.stop_recording()

    with patch("wave.open", side_effect=Exception("Disk full")):
        with pytest.raises(AudioRecorderError, match="Failed to write recording"):
            recorder.save_wav("test.wav")


def test_audio_recorder_status_callback(mock_sounddevice):
    """Verify sounddevice callback handles status flags correctly."""
    assert mock_sounddevice is not None
    recorder = AudioRecorder()
    # Capture the callback
    captured_callback = None

    def mock_input_stream_init(samplerate, channels, dtype, callback):
        nonlocal captured_callback
        captured_callback = callback
        return MockInputStream(samplerate, channels, dtype, callback)

    mock_sounddevice.InputStream = mock_input_stream_init
    recorder.start_recording()

    # Call with non-empty status flag
    assert captured_callback is not None
    captured_callback(np.zeros((10, 1), dtype=np.float32), 10, None, "overflow")


def test_audio_recorder_missing_sounddevice():
    """Test when sounddevice is missing (PortAudio missing on system)."""
    with (
        patch("voicelens.recorder.audio._SOUNDDEVICE_AVAILABLE", False),
        patch(
            "voicelens.recorder.audio._SOUNDDEVICE_ERROR_MSG",
            "PortAudio not found",
        ),
    ):
        recorder = AudioRecorder()
        with pytest.raises(AudioRecorderError, match="PortAudio not found"):
            recorder.start_recording()


def test_cli_analyze_command_success(mock_sounddevice):
    """Verify that 'voicelens analyze' completes happily with mocked user inputs."""
    assert mock_sounddevice is not None
    runner = CliRunner()
    # Simulate user pressing ENTER twice: once to start, once to stop
    result = runner.invoke(app, ["analyze"], input="\n\n")

    assert result.exit_code == 0
    assert "VoiceLens Audio Recorder" in result.output
    assert "Recording stopped successfully" in result.output
    assert "Success! Recording saved to" in result.output


def test_cli_analyze_command_error_handling():
    """Verify that 'voicelens analyze' handles recording errors gracefully."""
    runner = CliRunner()
    # Simulate PortAudio missing to trigger AudioRecorderError
    with patch("voicelens.recorder.audio._SOUNDDEVICE_AVAILABLE", False):
        result = runner.invoke(app, ["analyze"], input="\n\n")

        assert result.exit_code == 1
        assert "Audio Recording Error" in result.output
        assert "Please check your system audio settings" in result.output


def test_cli_analyze_command_unexpected_error(mock_sounddevice):
    """Verify that 'voicelens analyze' handles unexpected exceptions gracefully."""
    assert mock_sounddevice is not None
    runner = CliRunner()
    with patch(
        "voicelens.commands.analyze.perform_analysis_recording",
        side_effect=Exception("Unknown fatal error"),
    ):
        result = runner.invoke(app, ["analyze"], input="\n\n")

        assert result.exit_code == 1
        assert "Unexpected Error" in result.output
