class TranscriptionAPIError(Exception):
    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EmptyFileError(TranscriptionAPIError):
    status_code = 400
    error_code = "empty_file"


class UnsupportedAudioFormatError(TranscriptionAPIError):
    status_code = 400
    error_code = "unsupported_audio_format"


class FileTooLargeError(TranscriptionAPIError):
    status_code = 400
    error_code = "file_too_large"


class InvalidLanguageError(TranscriptionAPIError):
    status_code = 400
    error_code = "invalid_language"


class AudioDecodingError(TranscriptionAPIError):
    status_code = 422
    error_code = "audio_decoding_error"


class TranscriptionEngineError(TranscriptionAPIError):
    status_code = 500
    error_code = "transcription_engine_error"


class ModelUnavailableError(TranscriptionAPIError):
    status_code = 503
    error_code = "model_unavailable"
