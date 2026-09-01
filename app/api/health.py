from fastapi import APIRouter, Depends

from app.models.schemas import HealthResponse
from app.services.health import check_health
from app.services.transcription import TranscriptionService, get_transcription_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(
    service: TranscriptionService = Depends(get_transcription_service),
) -> HealthResponse:
    return check_health(service)
