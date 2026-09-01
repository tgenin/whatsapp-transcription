import pytest


@pytest.fixture(autouse=True)
def _default_ui_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UI_PASSWORD", "test-password")
