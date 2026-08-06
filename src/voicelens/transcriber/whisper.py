"""VoiceLens Whisper transcription implementation."""

from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel


class WhisperTranscriberError(Exception):
    """Base exception for all Whisper transcription errors."""

    pass


class WhisperTranscriber:
    """Handles speech-to-text transcription using faster-whisper."""

    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "float32",
    ) -> None:
        """Initializes the WhisperTranscriber.

        Args:
            model_size: Size of the Whisper model to use (e.g. "tiny", "base").
            device: Computing device to use ("cpu", "cuda", etc.).
            compute_type: Precision type ("float32", "float16", "int8", etc.).
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Any = None

    def _get_model(self) -> WhisperModel:
        """Lazily loads the Whisper model to optimize memory and startup times.

        Returns:
            WhisperModel: The initialized faster-whisper model.

        Raises:
            WhisperTranscriberError: If model loading fails.
        """
        if self._model is None:
            try:
                self._model = WhisperModel(
                    model_size_or_path=self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                )
            except Exception as e:
                raise WhisperTranscriberError(
                    f"Failed to load Whisper model '{self.model_size}': {e}"
                ) from e
        return self._model

    def transcribe(self, audio_path: Path | str) -> str:
        """Transcribes the given audio file and returns the full transcript string.

        Args:
            audio_path: Path to the WAV or supported audio file.

        Returns:
            str: The transcribed text.

        Raises:
            WhisperTranscriberError: If transcription or file reading fails.
        """
        path = Path(audio_path)
        if not path.exists():
            raise WhisperTranscriberError(
                f"Audio file does not exist: {path.resolve()}"
            )

        model = self._get_model()

        try:
            # transcribe returns generator of segments, and transcription info
            segments, _info = model.transcribe(str(path), beam_size=1)

            # Iterate through the segments and combine them
            text_segments = []
            for segment in segments:
                text_segments.append(segment.text)

            # Combine and strip extra whitespace
            transcript = " ".join(text_segments).strip()
            return transcript
        except Exception as e:
            raise WhisperTranscriberError(
                f"Error during Whisper transcription: {e}"
            ) from e
