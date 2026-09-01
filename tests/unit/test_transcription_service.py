from types import SimpleNamespace
from unittest.mock import MagicMock

import av.error
import pytest

from app.core.config import Settings
from app.core.exceptions import (
    AudioDecodingError,
    InvalidLanguageError,
    TranscriptionEngineError,
)
from app.services import transcription as transcription_module
from app.services.transcription import TranscriptionService, get_transcription_service


def make_segment(text: str) -> SimpleNamespace:
    return SimpleNamespace(text=text)


@pytest.fixture
def mock_model(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    model = MagicMock()
    monkeypatch.setattr(
        transcription_module, "WhisperModel", MagicMock(return_value=model)
    )
    return model


@pytest.fixture
def service(mock_model: MagicMock) -> TranscriptionService:
    return TranscriptionService(Settings(_env_file=None, ui_password="test-password"))


def test_transcribe_returns_joined_text_and_metadata(
    service: TranscriptionService, mock_model: MagicMock
) -> None:
    segments = [make_segment("Hello"), make_segment("world.")]
    info = SimpleNamespace(language="en", duration=3.5)
    mock_model.transcribe.return_value = (segments, info)

    result = service.transcribe(b"audio-bytes", "en")

    assert result.text == "Hello world."
    assert result.language == "en"
    assert result.duration_seconds == 3.5
    assert result.segment_count == 2


def test_transcribe_empty_audio_returns_empty_text(
    service: TranscriptionService, mock_model: MagicMock
) -> None:
    info = SimpleNamespace(language="en", duration=0.0)
    mock_model.transcribe.return_value = ([], info)

    result = service.transcribe(b"silence", "en")

    assert result.text == ""
    assert result.segment_count == 0


@pytest.mark.parametrize(
    ("raised_exception", "expected_error"),
    [
        (av.error.InvalidDataError(1, "bad data"), AudioDecodingError),
        (ValueError("'xx' is not a valid language code"), InvalidLanguageError),
        (RuntimeError("boom"), TranscriptionEngineError),
    ],
)
def test_transcribe_maps_engine_exceptions(
    service: TranscriptionService,
    mock_model: MagicMock,
    raised_exception: Exception,
    expected_error: type[Exception],
) -> None:
    mock_model.transcribe.side_effect = raised_exception

    with pytest.raises(expected_error):
        service.transcribe(b"audio-bytes", "en")


def test_get_transcription_service_is_a_singleton(mock_model: MagicMock) -> None:
    get_transcription_service.cache_clear()

    first = get_transcription_service()
    second = get_transcription_service()

    assert first is second

    get_transcription_service.cache_clear()
