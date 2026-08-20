"""Tests for the VoiceLens Accent Classification module."""

import tempfile
import wave
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import torch

from voicelens.accent import AccentClassifier, AccentResult


class MockClassifier:
    """Mock for SpeechBrain EncoderClassifier."""

    def encode_batch(self, _signal):
        # Return mock speech brain embedding vector (192 dim)
        vec = torch.zeros((1, 1, 192))
        return vec

    def classify_batch(self, _signal):
        # Returns prediction, log_softmax, posterior, text_lab
        posterior = torch.tensor([[0.95]])
        text_lab = ["en"]
        return None, None, posterior, text_lab


@pytest.fixture
def mock_accent_classifier():
    """Fixture to patch AccentClassifier's classifier loading."""
    mock_sb_cl = MockClassifier()
    with (
        patch(
            "voicelens.accent.classifier._SPEECHBRAIN_AVAILABLE",
            True,
        ),
        patch(
            "voicelens.accent.classifier.EncoderClassifier.from_hparams",
            return_value=mock_sb_cl,
        ),
    ):
        yield mock_sb_cl


def test_accent_structures():
    """Verify AccentResult dataclass attributes."""
    res = AccentResult(
        predicted_accent="American English",
        confidence=0.88,
        top_3_accents=[
            ("American English", 0.88),
            ("Canadian English", 0.08),
            ("British English", 0.04),
        ],
        notes=["Acoustics processed."],
    )
    assert res.predicted_accent == "American English"
    assert res.confidence == 0.88
    assert len(res.top_3_accents) == 3


def test_accent_classifier_short_clip_guard(mock_accent_classifier):
    """Verify clips under 5.0 seconds return 'Uncertain — clip too short'."""
    assert mock_accent_classifier is not None
    classifier = AccentClassifier(min_duration_seconds=5.0)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)

    # Write 1-second audio file (16000 samples at 16kHz)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(np.zeros(16000, dtype=np.int16).tobytes())

    try:
        res = classifier.classify(path)
        assert res.predicted_accent == "Uncertain — clip too short"
        assert res.confidence == 0.0
        assert "Audio duration" in res.notes[0]
    finally:
        if path.exists():
            path.unlink()


def test_accent_classifier_low_confidence_guard(mock_accent_classifier):
    """Verify classifications under confidence_threshold return uncertain status."""
    assert mock_accent_classifier is not None
    # Set high threshold (e.g. 0.99) so top match (which softmaxes to ~0.20-0.35) fails
    classifier = AccentClassifier(min_duration_seconds=0.0, confidence_threshold=0.99)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(np.zeros(16000, dtype=np.int16).tobytes())

    try:
        res = classifier.classify(path)
        assert res.predicted_accent == "Uncertain — accent not clearly identifiable"
        assert res.confidence < 0.99
    finally:
        if path.exists():
            path.unlink()


def test_accent_classifier_success(mock_accent_classifier):
    """Verify accent classification succeeds for valid long audio."""
    assert mock_accent_classifier is not None
    # Disable min_duration_seconds for quick test execution
    classifier = AccentClassifier(min_duration_seconds=0.0, confidence_threshold=0.10)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)

    # Write wave signal
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(np.zeros(16000, dtype=np.int16).tobytes())

    try:
        res = classifier.classify(path)

        assert res.predicted_accent in AccentClassifier.SUPPORTED_ACCENTS
        assert res.confidence > 0.0
        assert len(res.top_3_accents) == 3
        assert res.top_3_accents[0][0] == res.predicted_accent
    finally:
        if path.exists():
            path.unlink()


def test_accent_classifier_missing_file():
    """Verify that classifier raises FileNotFoundError if file is missing."""
    classifier = AccentClassifier()
    with pytest.raises(FileNotFoundError, match="Audio file does not exist"):
        classifier.classify("non_existent_file.wav")
