import io
from functools import lru_cache

import av.error
import structlog
from faster_whisper import WhisperModel

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    AudioDecodingError,
    InvalidLanguageError,
    TranscriptionEngineError,
)
from app.models.schemas import TranscriptResponse

log = structlog.get_logger()


class TranscriptionService:
    def __init__(self, settings: Settings) -> None:
        model_source = settings.whisper_model_path or settings.whisper_model
        log.info("whisper_model_loading", source=model_source)
        self._model = WhisperModel(
            model_source,
            device="cpu",
            compute_type=settings.whisper_compute_type,
        )

    def transcribe(self, audio_bytes: bytes, language: str) -> TranscriptResponse:
        try:
            segments, info = self._model.transcribe(
                io.BytesIO(audio_bytes), language=language
            )
            segment_list = list(segments)
        except av.error.FFmpegError as exc:
            raise AudioDecodingError("Could not decode the uploaded audio") from exc
        except ValueError as exc:
            raise InvalidLanguageError(
                f"'{language}' is not a valid language code"
            ) from exc
        except Exception as exc:
            raise TranscriptionEngineError("Transcription failed") from exc

        text = " ".join(segment.text.strip() for segment in segment_list).strip()

        log.info(
            "transcription_completed",
            language=info.language,
            duration_seconds=info.duration,
            segment_count=len(segment_list),
        )

        return TranscriptResponse(
            text=text,
            language=info.language,
            duration_seconds=info.duration,
            segment_count=len(segment_list),
        )


@lru_cache
def get_transcription_service() -> TranscriptionService:
    return TranscriptionService(get_settings())
