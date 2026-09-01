import io
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.security import verify_credentials
from app.main import app
from app.models.schemas import TranscriptResponse
from app.services.transcription import get_transcription_service


class FakeTranscriptionService:
    def __init__(self, response: TranscriptResponse | None = None) -> None:
        self.response = response or TranscriptResponse(
            text="hello world", language="en", duration_seconds=1.2, segment_count=1
        )
        self.calls: list[tuple[bytes, str]] = []

    def transcribe(self, audio_bytes: bytes, language: str) -> TranscriptResponse:
        self.calls.append((audio_bytes, language))
        return self.response


@pytest.fixture(autouse=True)
def _clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[verify_credentials] = lambda: None
    return TestClient(app)


def test_transcript_returns_transcription_result(client: TestClient) -> None:
    fake_service = FakeTranscriptionService()
    app.dependency_overrides[get_transcription_service] = lambda: fake_service

    response = client.post(
        "/transcript",
        files={"audio": ("note.opus", io.BytesIO(b"fake-audio-bytes"), "audio/opus")},
        data={"language": "en"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "text": "hello world",
        "language": "en",
        "duration_seconds": 1.2,
        "segment_count": 1,
    }
    assert fake_service.calls == [(b"fake-audio-bytes", "en")]


def test_transcript_defaults_to_french_when_language_omitted(
    client: TestClient,
) -> None:
    fake_service = FakeTranscriptionService()
    app.dependency_overrides[get_transcription_service] = lambda: fake_service

    response = client.post(
        "/transcript",
        files={"audio": ("note.opus", io.BytesIO(b"fake-audio-bytes"), "audio/opus")},
    )

    assert response.status_code == 200
    assert fake_service.calls == [(b"fake-audio-bytes", "fr")]


@pytest.mark.parametrize(
    ("filename", "content", "settings_override", "expected_error_code"),
    [
        ("note.opus", b"", None, "empty_file"),
        ("note.mp3", b"fake-audio-bytes", None, "unsupported_audio_format"),
        (
            "note.opus",
            b"fake-audio-bytes",
            Settings(max_upload_size_bytes=4, ui_password="test-password"),
            "file_too_large",
        ),
    ],
)
def test_transcript_rejects_invalid_upload(
    client: TestClient,
    filename: str,
    content: bytes,
    settings_override: Settings | None,
    expected_error_code: str,
) -> None:
    app.dependency_overrides[get_transcription_service] = FakeTranscriptionService
    if settings_override is not None:
        app.dependency_overrides[get_settings] = lambda: settings_override

    response = client.post(
        "/transcript",
        files={"audio": (filename, io.BytesIO(content), "audio/opus")},
        data={"language": "en"},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == expected_error_code


def test_transcript_rejects_missing_credentials() -> None:
    app.dependency_overrides[get_transcription_service] = FakeTranscriptionService
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, ui_password="correct-password"
    )
    client = TestClient(app)

    response = client.post(
        "/transcript",
        files={"audio": ("note.opus", io.BytesIO(b"fake-audio-bytes"), "audio/opus")},
        data={"language": "en"},
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


def test_transcript_rejects_wrong_password() -> None:
    app.dependency_overrides[get_transcription_service] = FakeTranscriptionService
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, ui_password="correct-password"
    )
    client = TestClient(app)

    response = client.post(
        "/transcript",
        files={"audio": ("note.opus", io.BytesIO(b"fake-audio-bytes"), "audio/opus")},
        data={"language": "en"},
        auth=("user", "wrong-password"),
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


def test_transcript_accepts_correct_password() -> None:
    app.dependency_overrides[get_transcription_service] = FakeTranscriptionService
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, ui_password="correct-password"
    )
    client = TestClient(app)

    response = client.post(
        "/transcript",
        files={"audio": ("note.opus", io.BytesIO(b"fake-audio-bytes"), "audio/opus")},
        data={"language": "en"},
        auth=("user", "correct-password"),
    )

    assert response.status_code == 200
