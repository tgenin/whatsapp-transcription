import pytest

from app.core.config import Settings, get_settings


def test_get_settings_returns_cached_instance() -> None:
    assert get_settings() is get_settings()


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("whisper_model", "small"),
        ("whisper_compute_type", "int8"),
        ("max_upload_size_bytes", 25 * 1024 * 1024),
        ("log_level", "INFO"),
    ],
)
def test_settings_defaults(field: str, expected: object) -> None:
    settings = Settings(_env_file=None, ui_password="test-password")
    assert getattr(settings, field) == expected


def test_settings_reads_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHISPER_MODEL", "tiny")

    settings = Settings(_env_file=None, ui_password="test-password")

    assert settings.whisper_model == "tiny"
