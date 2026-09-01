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


def test_service_worker_rejects_missing_credentials(client: TestClient) -> None:
    response = client.get("/sw.js")

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/manifest.json", "application/manifest+json"),
        ("/sw.js", "application/javascript"),
        ("/icon.svg", "image/svg+xml"),
    ],
)
def test_static_pwa_asset_served_with_correct_password(
    client: TestClient, path: str, content_type: str
) -> None:
    response = client.get(path, auth=("user", "correct-password"))

    assert response.status_code == 200
    assert response.headers["content-type"] == content_type


@pytest.mark.parametrize("path", ["/manifest.json", "/icon.svg"])
def test_manifest_and_icon_are_publicly_reachable(
    client: TestClient, path: str
) -> None:
    # Unauthenticated on purpose: Android's WebAPK minting service fetches
    # these from its own servers and cannot send our Basic Auth credentials.
    response = client.get(path)

    assert response.status_code == 200


def test_share_target_rejects_missing_credentials(client: TestClient) -> None:
    response = client.post("/share-target", follow_redirects=False)

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


def test_share_target_redirects_to_index_with_correct_password(
    client: TestClient,
) -> None:
    response = client.post(
        "/share-target", auth=("user", "correct-password"), follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
