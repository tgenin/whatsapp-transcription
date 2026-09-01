from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import TranscriptResponse
from app.services.transcription import get_transcription_service


class FakeTranscriptionService:
    def __init__(
        self,
        response: TranscriptResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or TranscriptResponse(
            text="Bonjour", language="fr", duration_seconds=4.2, segment_count=1
        )
        self.error = error

    def transcribe(self, audio_bytes: bytes, language: str) -> TranscriptResponse:
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture(autouse=True)
def _clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_returns_ok_without_credentials(client: TestClient) -> None:
    app.dependency_overrides[get_transcription_service] = lambda: (
        FakeTranscriptionService()
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "transcribed_text": "Bonjour"}


@pytest.mark.parametrize(
    "fake_service",
    [
        FakeTranscriptionService(error=RuntimeError("model not loaded")),
        FakeTranscriptionService(
            response=TranscriptResponse(
                text="something else",
                language="fr",
                duration_seconds=4.2,
                segment_count=1,
            )
        ),
    ],
)
def test_health_returns_503_when_model_is_unhealthy(
    client: TestClient, fake_service: FakeTranscriptionService
) -> None:
    app.dependency_overrides[get_transcription_service] = lambda: fake_service

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["error_code"] == "model_unavailable"
