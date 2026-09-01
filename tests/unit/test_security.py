import pytest
from fastapi.security import HTTPBasicCredentials

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError
from app.core.security import verify_credentials


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, ui_password="secret")


def test_verify_credentials_accepts_correct_password(settings: Settings) -> None:
    credentials = HTTPBasicCredentials(username="anyone", password="secret")

    assert verify_credentials(credentials, settings) is None


def test_verify_credentials_rejects_wrong_password(settings: Settings) -> None:
    credentials = HTTPBasicCredentials(username="anyone", password="wrong")

    with pytest.raises(UnauthorizedError):
        verify_credentials(credentials, settings)


def test_verify_credentials_rejects_missing_credentials(settings: Settings) -> None:
    with pytest.raises(UnauthorizedError):
        verify_credentials(None, settings)
