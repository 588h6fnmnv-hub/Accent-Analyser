"""Tests for VoiceLens FastAPI HTTP endpoints."""

import io
import wave
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient

from voicelens.api.app import app

client = TestClient(app)


def create_dummy_wav_bytes(
    duration_sec: float = 1.0, sample_rate: int = 16000
) -> bytes:
    """Generates a dummy 16-bit mono WAV file in memory."""
    num_samples = int(duration_sec * sample_rate)
    samples = (
        np.sin(2 * np.pi * 440 * np.arange(num_samples) / sample_rate) * 32767
    ).astype(np.int16)

    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

    return wav_io.getvalue()


def test_health_check_endpoint():
    """Verify GET /api/health returns HTTP 200 OK status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "VoiceLens API"


def test_analyze_empty_file():
    """Verify POST /api/analyze returns 400 Bad Request for empty uploads."""
    response = client.post(
        "/api/analyze",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_analyze_valid_audio():
    """Verify POST /api/analyze returns real structured JSON pipeline analysis."""
    wav_bytes = create_dummy_wav_bytes(1.0)

    # Mock WhisperTranscriber inside pipeline
    mock_pipeline_result = {
        "id": "vl-20250815-test",
        "createdAt": "2025-08-15T10:00:00Z",
        "audioDurationSeconds": 1.0,
        "transcript": {
            "text": "Testing real VoiceLens API analysis endpoint",
            "language": "English (Detected)",
            "wordCount": 6,
        },
        "accent": {
            "predictedAccent": "American English",
            "confidence": 0.95,
            "top3Accents": [{"accent": "American English", "confidence": 0.95}],
            "notes": [],
        },
        "pronunciation": {
            "overallScore": 88.0,
            "pronunciationSimilarity": 0.88,
            "confidence": 0.92,
            "backend": "speechbrain",
            "notes": [],
        },
        "metrics": {
            "durationSeconds": 1.0,
            "wordCount": 6,
            "wordsPerMinute": 360.0,
            "pauseCount": 0,
            "averagePauseDuration": 0.0,
            "longestPause": 0.0,
            "fillerWordCount": 0,
            "fillerWords": [],
            "sentenceCount": 1,
            "averageWordsPerSentence": 6.0,
        },
        "fillerWordsList": [],
        "difficultWordsList": [],
        "overallFeedback": ["• Accent Profile: American English"],
    }

    with patch(
        "voicelens.api.app.run_voicelens_pipeline", return_value=mock_pipeline_result
    ):
        response = client.post(
            "/api/analyze",
            files={"file": ("recording.wav", wav_bytes, "audio/wav")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "vl-20250815-test"
        assert (
            data["transcript"]["text"] == "Testing real VoiceLens API analysis endpoint"
        )
        assert data["accent"]["predictedAccent"] == "American English"
        assert data["pronunciation"]["overallScore"] == 88.0
