import structlog

from app.core.constants import (
    HEALTH_CHECK_EXPECTED_TEXT,
    HEALTH_CHECK_SAMPLE_LANGUAGE,
    HEALTH_CHECK_SAMPLE_PATH,
)
from app.core.exceptions import ModelUnavailableError
from app.models.schemas import HealthResponse
from app.services.transcription import TranscriptionService

log = structlog.get_logger()


def check_health(service: TranscriptionService) -> HealthResponse:
    audio_bytes = HEALTH_CHECK_SAMPLE_PATH.read_bytes()

    try:
        result = service.transcribe(audio_bytes, HEALTH_CHECK_SAMPLE_LANGUAGE)
    except Exception as exc:
        log.error("health_check_transcription_failed", error=str(exc))
        raise ModelUnavailableError(
            "Transcription model failed the health check"
        ) from exc

    if HEALTH_CHECK_EXPECTED_TEXT not in result.text.lower():
        log.error("health_check_unexpected_output", text=result.text)
        raise ModelUnavailableError(
            "Transcription model returned unexpected output during health check"
        )

    return HealthResponse(status="ok", transcribed_text=result.text)
