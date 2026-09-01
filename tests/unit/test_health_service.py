from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ModelUnavailableError
from app.models.schemas import TranscriptResponse
from app.services.health import check_health
from app.services.transcription import TranscriptionService


@pytest.fixture
def mock_service() -> MagicMock:
    return MagicMock(spec=TranscriptionService)


def test_check_health_returns_ok_when_transcription_matches(
    mock_service: MagicMock,
) -> None:
    mock_service.transcribe.return_value = TranscriptResponse(
        text="Bonjour", language="fr", duration_seconds=4.2, segment_count=1
    )

    result = check_health(mock_service)

    assert result.status == "ok"
    assert result.transcribed_text == "Bonjour"


def test_check_health_raises_when_transcription_fails(mock_service: MagicMock) -> None:
    mock_service.transcribe.side_effect = RuntimeError("model not loaded")

    with pytest.raises(ModelUnavailableError):
        check_health(mock_service)


def test_check_health_raises_when_output_does_not_match(
    mock_service: MagicMock,
) -> None:
    mock_service.transcribe.return_value = TranscriptResponse(
        text="something else", language="fr", duration_seconds=4.2, segment_count=1
    )

    with pytest.raises(ModelUnavailableError):
        check_health(mock_service)
