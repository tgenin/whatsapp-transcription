from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.security import verify_credentials
from app.main import app
from app.services.transcription import TranscriptionService, get_transcription_service

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_fr.opus"


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
    app.dependency_overrides[verify_credentials] = lambda: None
    return TestClient(app)


@pytest.mark.integration
def test_transcript_endpoint_transcribes_real_audio(client: TestClient) -> None:
    with FIXTURE_PATH.open("rb") as audio_file:
        response = client.post(
            "/transcript",
            files={"audio": ("sample_fr.opus", audio_file, "audio/ogg")},
            data={"language": "fr"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "fr"
    assert body["segment_count"] >= 1
    assert body["duration_seconds"] > 0
    assert "bonjour" in body["text"].lower()
