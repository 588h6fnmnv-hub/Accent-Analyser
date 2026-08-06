"""Tests for the VoiceLens Whisper transcriber."""

from unittest.mock import MagicMock, patch

import pytest

from voicelens.transcriber.whisper import WhisperTranscriber, WhisperTranscriberError


class MockSegment:
    """Mock Whisper segment representing transcribed text."""

    def __init__(self, text: str) -> None:
        self.text = text


class MockWhisperModel:
    """Mock for faster-whisper.WhisperModel."""

    def __init__(self, model_size_or_path: str, device: str, compute_type: str) -> None:
        self.model_size_or_path = model_size_or_path
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path: str, beam_size: int = 1):
        # Reference arguments to avoid ARG002 unused argument warning
        assert audio_path is not None
        assert beam_size is not None

        # Return segments list and a dummy transcription info
        segments = [
            MockSegment("Hello world"),
            MockSegment("this is a test transcript."),
        ]
        info = MagicMock()
        return segments, info


@pytest.fixture
def mock_whisper_model():
    """Fixture to mock WhisperModel."""
    with patch(
        "voicelens.transcriber.whisper.WhisperModel",
        new=MockWhisperModel,
    ):
        yield


def test_transcribe_success(mock_whisper_model):
    """Verify transcription parses segments and returns concatenated string."""
    assert mock_whisper_model is None
    transcriber = WhisperTranscriber()

    with patch("pathlib.Path.exists", return_value=True):
        transcript = transcriber.transcribe("fake_recording.wav")
        assert transcript == "Hello world this is a test transcript."


def test_transcribe_file_not_found():
    """Verify transcriber raises error if audio file doesn't exist."""
    transcriber = WhisperTranscriber()
    with pytest.raises(WhisperTranscriberError, match="Audio file does not exist"):
        transcriber.transcribe("non_existent_file.wav")


def test_transcribe_model_load_error():
    """Verify error is raised if WhisperModel fails to load."""
    transcriber = WhisperTranscriber()

    with patch("pathlib.Path.exists", return_value=True):
        with patch(
            "voicelens.transcriber.whisper.WhisperModel",
            side_effect=Exception("Out of GPU memory"),
        ):
            msg = "Failed to load Whisper model"
            with pytest.raises(WhisperTranscriberError, match=msg):
                transcriber.transcribe("fake_recording.wav")


def test_transcribe_inference_error(mock_whisper_model):
    """Verify transcription failures are caught and wrapped cleanly."""
    assert mock_whisper_model is None
    transcriber = WhisperTranscriber()

    # Make transcribe raise an exception
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(
            MockWhisperModel,
            "transcribe",
            side_effect=Exception("Failed processing audio"),
        ):
            msg = "Error during Whisper transcription"
            with pytest.raises(WhisperTranscriberError, match=msg):
                transcriber.transcribe("fake_recording.wav")
