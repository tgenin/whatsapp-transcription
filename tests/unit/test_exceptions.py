import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exception_handlers import register_exception_handlers
from app.core.exceptions import (
    AudioDecodingError,
    EmptyFileError,
    FileTooLargeError,
    InvalidLanguageError,
    ModelUnavailableError,
    TranscriptionAPIError,
    TranscriptionEngineError,
    UnsupportedAudioFormatError,
)


@pytest.mark.parametrize(
    ("exc_class", "expected_status_code", "expected_error_code"),
    [
        (EmptyFileError, 400, "empty_file"),
        (UnsupportedAudioFormatError, 400, "unsupported_audio_format"),
        (FileTooLargeError, 400, "file_too_large"),
        (InvalidLanguageError, 400, "invalid_language"),
        (AudioDecodingError, 422, "audio_decoding_error"),
        (TranscriptionEngineError, 500, "transcription_engine_error"),
        (ModelUnavailableError, 503, "model_unavailable"),
    ],
)
def test_exception_status_code_and_error_code(
    exc_class: type[TranscriptionAPIError],
    expected_status_code: int,
    expected_error_code: str,
) -> None:
    exc = exc_class("something went wrong")

    assert exc.status_code == expected_status_code
    assert exc.error_code == expected_error_code
    assert exc.message == "something went wrong"


def test_all_exceptions_are_transcription_api_errors() -> None:
    for exc_class in (
        EmptyFileError,
        UnsupportedAudioFormatError,
        FileTooLargeError,
        InvalidLanguageError,
        AudioDecodingError,
        TranscriptionEngineError,
        ModelUnavailableError,
    ):
        assert issubclass(exc_class, TranscriptionAPIError)


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/empty-file")
    def raise_empty_file() -> None:
        raise EmptyFileError("audio file is empty")

    @app.get("/model-unavailable")
    def raise_model_unavailable() -> None:
        raise ModelUnavailableError("model is not loaded")

    @app.get("/validation")
    def raise_validation(required_param: int) -> None:
        pass

    @app.get("/unhandled")
    def raise_unhandled() -> None:
        raise RuntimeError("boom")

    return TestClient(app, raise_server_exceptions=False)


def test_transcription_api_error_handler_returns_mapped_status(
    client: TestClient,
) -> None:
    response = client.get("/empty-file")

    assert response.status_code == 400
    assert response.json() == {
        "error_code": "empty_file",
        "message": "audio file is empty",
    }


def test_transcription_api_error_handler_maps_503(client: TestClient) -> None:
    response = client.get("/model-unavailable")

    assert response.status_code == 503
    assert response.json() == {
        "error_code": "model_unavailable",
        "message": "model is not loaded",
    }


def test_validation_error_handler_returns_422(client: TestClient) -> None:
    response = client.get("/validation")

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert isinstance(body["errors"], list)


def test_unhandled_exception_handler_returns_500(client: TestClient) -> None:
    response = client.get("/unhandled")

    assert response.status_code == 500
    assert response.json() == {
        "error_code": "internal_error",
        "message": "An unexpected error occurred",
    }
