"""VoiceLens Pronunciation Dummy Backend."""

from pathlib import Path

from voicelens.pronunciation.backend import PronunciationBackend, PronunciationResult


class DummyBackend(PronunciationBackend):
    """Placeholder pronunciation assessment backend returning structured defaults."""

    def analyze(self, _audio_path: str | Path, _transcript: str) -> PronunciationResult:
        """Returns placeholder pronunciation assessment results.

        Args:
            _audio_path: Path to the recorded audio file.
            _transcript: Expected text transcription.

        Returns:
            PronunciationResult: Default placeholder results with score=None.
        """
        return PronunciationResult(
            pronunciation_score=None,
            confidence=None,
            backend="dummy",
            notes=[],
        )
