from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app
from app.services.transcription import TranscriptionService, get_transcription_service


@pytest.fixture(autouse=True)
def _clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    settings = Settings(whisper_model="tiny", ui_password="test-password")
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_transcription_service] = lambda: TranscriptionService(
        settings
    )
    return TestClient(app)


@pytest.mark.integration
def test_health_endpoint_runs_real_transcription(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "bonjour" in body["transcribed_text"].lower()
