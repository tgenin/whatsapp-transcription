from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


@pytest.fixture(autouse=True)
def _clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, ui_password="correct-password"
    )
    return TestClient(app)


def test_index_rejects_missing_credentials(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


def test_index_rejects_wrong_password(client: TestClient) -> None:
    response = client.get("/", auth=("user", "wrong-password"))

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


def test_index_serves_page_with_correct_password(client: TestClient) -> None:
    response = client.get("/", auth=("user", "correct-password"))

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
