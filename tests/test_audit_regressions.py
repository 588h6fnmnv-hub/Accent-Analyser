"""Regression tests for VoiceLens accuracy audit requirements."""

from unittest.mock import MagicMock, patch

from voicelens.accent.classifier import AccentClassifier
from voicelens.alignment.aligner import WhisperAligner
from voicelens.pipeline import run_voicelens_pipeline
from voicelens.pronunciation.speechbrain_backend import SpeechBrainBackend


class MockWord:
    """Mock for faster-whisper word object."""

    def __init__(self, word: str, start: float, end: float, probability: float):
        self.word = word
        self.start = start
        self.end = end
        self.probability = probability


class MockSegment:
    """Mock for faster-whisper segment object."""

    def __init__(self, words: list[MockWord]):
        self.words = words


class MockWhisperModel:
    """Mock model that returns both correct words and a hallucinated word."""

    def transcribe(
        self, _audio_path: str, word_timestamps: bool = True
    ) -> tuple[list[MockSegment], None]:
        # Unused argument word_timestamps accepted to match signature
        _ = word_timestamps
        words = [
            MockWord("Hello", 0.1, 0.5, 0.98),
            # Hallucinated word from Whisper that isn't in original transcript
            MockWord(
                "Ahmad", 0.6, 1.0, 1.5
            ),  # Out of bounds probability/confidence too!
            MockWord("world", 1.1, 1.5, -0.2),  # Under bounds probability/confidence
        ]
        return [MockSegment(words)], None


def test_confidence_scaling_and_hallucination_filtering():
    """Verify confidence/scores never exceed 100%.

    Also verify that hallucinated tokens are filtered out.
    """
    mock_transcriber = MagicMock()
    mock_transcriber._get_model.return_value = MockWhisperModel()

    aligner = WhisperAligner(transcriber=mock_transcriber)

    with patch("pathlib.Path.exists", return_value=True):
        # The user transcript only has "Hello world"
        res = aligner.align("fake_path.wav", "Hello world!")

        # 1. Verify "Ahmad" is filtered out because it is not in the transcript
        aligned_words = [w.word for w in res.words]
        assert "Ahmad" not in aligned_words
        assert len(res.words) == 2

        # 2. Verify confidence is correctly bounded between 0.0 and 1.0
        # "Hello" should have 0.98
        assert res.words[0].word == "Hello"
        assert res.words[0].confidence == 0.98

        # "world" had probability -0.2, which should be bounded to 0.0
        assert res.words[1].word == "world"
        assert res.words[1].confidence == 0.0


def test_accent_classifier_disclaimer_and_bounds():
    """Verify accent classifier has a scientific disclaimer.

    Also verify it bounds confidence between 0.0 and 1.0.
    """
    classifier = AccentClassifier(min_duration_seconds=0.0)
    mock_classifier = MagicMock()
    mock_embeddings = MagicMock()

    import numpy as np
    import torch

    mock_embeddings.squeeze.return_value.cpu.return_value.numpy.return_value = np.array(
        [1.0, 2.0, 3.0, 4.0, 5.0]
    )
    mock_classifier.encode_batch.return_value = mock_embeddings
    classifier._classifier = mock_classifier

    # Pass 5 seconds of audio signal (80000 samples at 16kHz)
    dummy_signal = torch.ones((1, 80000))
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch.object(
            classifier,
            "_load_audio",
            return_value=(dummy_signal, 16000),
        ),
    ):
        result = classifier.classify("dummy.wav")

        # Verify predicted accent confidence is strictly between 0.0 and 1.0
        assert 0.0 <= result.confidence <= 1.0

        # Verify disclaimer is in notes
        disclaimer_found = any(
            "not clinically or scientifically validated" in note
            for note in result.notes
        )
        assert disclaimer_found, (
            "Scientific disclaimer missing in accent classification result"
        )


def test_pronunciation_backend_bounds():
    """Verify SpeechBrainBackend bounds results properly.

    Verify that overall_score, similarity, and confidence are correctly bounded.
    """
    backend = SpeechBrainBackend()
    mock_classifier = MagicMock()

    import torch

    mock_posterior = torch.tensor([1.2])
    mock_embeddings = torch.tensor([[0.5, 0.5]])  # mean is 0.5
    mock_classifier.classify_batch.return_value = (
        "en",
        None,
        mock_posterior,
        ["en"],
    )
    mock_classifier.encode_batch.return_value = mock_embeddings
    backend._classifier = mock_classifier

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch.object(
            backend,
            "_load_audio",
            return_value=(torch.zeros(1, 16000), 16000),
        ),
    ):
        result = backend.analyze("dummy.wav", "Hello world")

        # Confidence should be rounded to 1.0 fraction
        assert result.confidence == 1.0
        assert result.overall_score <= 100.0
        assert 0.0 <= result.pronunciation_similarity <= 1.0


def test_pipeline_overall_score_reflects_low_accent_confidence():
    """Verify that overallScore reflects uncertainty in accent classification."""
    mock_tx = MagicMock()
    mock_tx.transcribe.return_value = "Hello world"

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "voicelens.pipeline.AccentClassifier.classify",
            return_value=MagicMock(
                predicted_accent="American English",
                confidence=0.354,  # Low confidence 35.4%
                top_3_accents=[
                    ("American English", 0.354),
                    ("British English", 0.255),
                    ("Indian English", 0.176),
                ],
                notes=[],
            ),
        ),
        patch(
            "voicelens.pipeline.PronunciationAnalyzer.analyze",
            return_value=MagicMock(
                overall_score=85.0,
                pronunciation_similarity=0.85,
                confidence=0.90,
                backend="speechbrain",
                notes=[],
            ),
        ),
        patch(
            "voicelens.pipeline.WhisperAligner.align",
            return_value=MagicMock(words=[]),
        ),
    ):
        res = run_voicelens_pipeline("dummy.wav", transcriber=mock_tx)

        # Confirm confidence is strictly in [0.0, 1.0]
        assert res["accent"]["confidence"] == 0.354
        assert res["pronunciation"]["confidence"] == 0.90

        # Confirm overallScore reflects low accent confidence (< 90.0)
        assert res["pronunciation"]["overallScore"] < 90.0
        assert res["pronunciation"]["overallScore"] == 75.64
