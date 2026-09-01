from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.config import Settings, get_settings
from app.core.constants import ALLOWED_AUDIO_EXTENSIONS, DEFAULT_LANGUAGE
from app.core.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    UnsupportedAudioFormatError,
)
from app.core.security import verify_credentials
from app.models.schemas import TranscriptResponse
from app.services.transcription import TranscriptionService, get_transcription_service

router = APIRouter()


@router.post(
    "/transcript",
    response_model=TranscriptResponse,
    dependencies=[Depends(verify_credentials)],
)
def transcript(
    audio: UploadFile = File(...),
    language: str = Form(DEFAULT_LANGUAGE),
    settings: Settings = Depends(get_settings),
    service: TranscriptionService = Depends(get_transcription_service),
) -> TranscriptResponse:
    audio_bytes = audio.file.read()

    if not audio_bytes:
        raise EmptyFileError("Uploaded audio file is empty")

    extension = Path(audio.filename or "").suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise UnsupportedAudioFormatError(
            f"'{extension}' is not a supported audio format"
        )

    if len(audio_bytes) > settings.max_upload_size_bytes:
        max_size = settings.max_upload_size_bytes
        raise FileTooLargeError(f"Audio file exceeds the {max_size} byte limit")

    return service.transcribe(audio_bytes, language)
