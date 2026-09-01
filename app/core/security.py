import secrets

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError

security = HTTPBasic(auto_error=False)


def verify_credentials(
    credentials: HTTPBasicCredentials | None = Depends(security),
    settings: Settings = Depends(get_settings),
) -> None:
    if credentials is None or not secrets.compare_digest(
        credentials.password, settings.ui_password.get_secret_value()
    ):
        raise UnauthorizedError("Invalid credentials")
