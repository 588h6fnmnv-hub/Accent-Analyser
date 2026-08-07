"""Tests for the VoiceLens Pronunciation Assessment module."""

import tempfile
from pathlib import Path

import pytest

from voicelens.pronunciation import (
    PronunciationAnalyzer,
    PronunciationAnalyzerError,
    PronunciationBackend,
    PronunciationResult,
)
from voicelens.pronunciation.dummy import DummyBackend


class MockCustomBackend(PronunciationBackend):
    """Mock pronunciation backend to test swappability (e.g., Azure or NeMo)."""

    def analyze(self, audio_path: str | Path, transcript: str) -> PronunciationResult:
        # Reference arguments to avoid ARG002
        assert audio_path is not None
        assert transcript is not None

        return PronunciationResult(
            overall_score=92.0,
            pronunciation_similarity=0.95,
            confidence=0.95,
            backend="mock_custom",
            notes=["High acoustic clarity.", "Phonetic matching succeeded."],
        )


class FaultyBackend(PronunciationBackend):
    """Mock backend that raises an unexpected exception during analysis."""

    def analyze(self, audio_path: str | Path, transcript: str) -> PronunciationResult:
        assert audio_path is not None
        assert transcript is not None
        raise RuntimeError("Severe backend connection failure.")


class PronunciationErrorBackend(PronunciationBackend):
    """Mock backend that raises an explicit PronunciationAnalyzerError."""

    def analyze(self, audio_path: str | Path, transcript: str) -> PronunciationResult:
        assert audio_path is not None
        assert transcript is not None
        raise PronunciationAnalyzerError("Custom backend error message.")


@pytest.fixture
def fake_audio_file():
    """Fixture returning a path to a temporary fake audio file."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(b"fake audio data")
        path = Path(tmp.name)
    yield path
    # Clean up the file
    if path.exists():
        path.unlink()


def test_dummy_backend_direct(fake_audio_file):
    """Verify that DummyBackend returns the correct structured placeholder results."""
    backend = DummyBackend()
    res = backend.analyze(fake_audio_file, "Hello world")

    assert res.overall_score == 85.0
    assert res.pronunciation_similarity == 0.88
    assert res.confidence == 0.92
    assert res.backend == "dummy"


def test_pronunciation_analyzer_default_dummy(fake_audio_file):
    """Verify PronunciationAnalyzer default initialization with DummyBackend."""
    analyzer = PronunciationAnalyzer()
    assert isinstance(analyzer.backend, DummyBackend)

    res = analyzer.analyze(fake_audio_file, "Some expected speech")
    assert res.overall_score == 85.0
    assert res.backend == "dummy"


def test_pronunciation_analyzer_input_validation():
    """Verify that input validation checks file existence and non-empty transcripts."""
    analyzer = PronunciationAnalyzer()

    # File does not exist
    with pytest.raises(PronunciationAnalyzerError, match="Audio file does not exist"):
        analyzer.analyze("non_existent_file.wav", "Hello")

    # Empty transcript
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        with pytest.raises(PronunciationAnalyzerError, match="empty transcript"):
            analyzer.analyze(tmp.name, "   ")


def test_pronunciation_backend_swappability(fake_audio_file):
    """Verify that we can easily swap backends without modifying the coordinator."""
    custom_backend = MockCustomBackend()
    analyzer = PronunciationAnalyzer(backend=custom_backend)

    res = analyzer.analyze(fake_audio_file, "Spoken text")
    assert res.overall_score == 92.0
    assert res.pronunciation_similarity == 0.95
    assert res.confidence == 0.95
    assert res.backend == "mock_custom"
    assert "High acoustic clarity." in res.notes


def test_pronunciation_analyzer_backend_failure_wrapping(fake_audio_file):
    """Verify backend exceptions are wrapped in PronunciationAnalyzerError."""
    analyzer = PronunciationAnalyzer(backend=FaultyBackend())

    with pytest.raises(
        PronunciationAnalyzerError,
        match="Pronunciation assessment failed via backend 'FaultyBackend'",
    ):
        analyzer.analyze(fake_audio_file, "Spoken text")


def test_pronunciation_analyzer_backend_reraise_error(fake_audio_file):
    """Verify direct PronunciationAnalyzerErrors are reraised directly."""
    analyzer = PronunciationAnalyzer(backend=PronunciationErrorBackend())

    with pytest.raises(
        PronunciationAnalyzerError,
        match="Custom backend error message",
    ):
        analyzer.analyze(fake_audio_file, "Spoken text")
