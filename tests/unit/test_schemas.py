import pytest
from pydantic import ValidationError

from app.models.schemas import ErrorResponse, TranscriptResponse


def test_transcript_response_accepts_valid_fields() -> None:
    response = TranscriptResponse(
        text="hello world",
        language="en",
        duration_seconds=3.5,
        segment_count=2,
    )

    assert response.text == "hello world"
    assert response.language == "en"
    assert response.duration_seconds == 3.5
    assert response.segment_count == 2


@pytest.mark.parametrize(
    "missing_field",
    ["text", "language", "duration_seconds", "segment_count"],
)
def test_transcript_response_requires_all_fields(missing_field: str) -> None:
    fields = {
        "text": "hello world",
        "language": "en",
        "duration_seconds": 3.5,
        "segment_count": 2,
    }
    del fields[missing_field]

    with pytest.raises(ValidationError):
        TranscriptResponse(**fields)


def test_error_response_accepts_valid_fields() -> None:
    response = ErrorResponse(error_code="empty_file", message="audio file is empty")

    assert response.error_code == "empty_file"
    assert response.message == "audio file is empty"


@pytest.mark.parametrize("missing_field", ["error_code", "message"])
def test_error_response_requires_all_fields(missing_field: str) -> None:
    fields = {"error_code": "empty_file", "message": "audio file is empty"}
    del fields[missing_field]

    with pytest.raises(ValidationError):
        ErrorResponse(**fields)
