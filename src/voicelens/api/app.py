"""VoiceLens FastAPI HTTP API Server.

Exposes REST endpoints for speech audio analysis and health monitoring.
"""

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from voicelens.pipeline import run_voicelens_pipeline
from voicelens.transcriber.whisper import WhisperTranscriberError

app = FastAPI(
    title="VoiceLens API",
    description="HTTP REST API for VoiceLens voice analysis engine.",
    version="0.1.0",
)

# Enable CORS for Next.js frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify API server availability."""
    return {"status": "ok", "service": "VoiceLens API", "version": "0.1.0"}


@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)) -> dict:  # noqa: B008
    """Upload audio file (WAV, WEBM, MP3, OGG, FLAC) and run VoiceLens analysis.

    Args:
        file: Uploaded audio file via multipart/form-data.

    Returns:
        dict: Complete VoiceLens analysis results JSON matching domain contract.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload request.",
        )

    # Determine file extension
    ext = Path(file.filename).suffix.lower() or ".wav"

    # Save uploaded bytes to a temporary audio file
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded audio file is empty.",
            )

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded file: {e}",
        ) from e

    # Execute VoiceLens pipeline on the temporary audio file
    try:
        result = run_voicelens_pipeline(tmp_path)
        return result
    except WhisperTranscriberError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Whisper transcription failed: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"VoiceLens analysis engine failed: {e}",
        ) from e
    finally:
        # Cleanup temporary audio file
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
