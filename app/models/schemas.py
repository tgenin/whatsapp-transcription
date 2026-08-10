from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    text: str
    language: str
    duration_seconds: float
    segment_count: int


class ErrorResponse(BaseModel):
    error_code: str
    message: str
