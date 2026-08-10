# whatsapp-transcription

A single-endpoint FastAPI service that transcribes WhatsApp voice notes (Opus audio) to text, running fully locally via [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

No `ffmpeg` system install is needed — audio decoding is handled by PyAV, which bundles its own FFmpeg libraries.

## Setup

```bash
uv sync
cp .env.example .env
```

The first transcription request needs internet access once, to download the Whisper model weights (cached locally afterwards under `~/.cache/huggingface`). Every request after that — including the model inference itself — runs fully offline; no audio or transcript ever leaves the machine.

## Configuration

Settings are read from environment variables (see `.env.example`):

| Variable                | Default    | Description                                          |
| ------------------------ | ---------- | ----------------------------------------------------- |
| `WHISPER_MODEL`          | `small`    | faster-whisper model size                              |
| `WHISPER_COMPUTE_TYPE`   | `int8`     | CTranslate2 compute type                               |
| `MAX_UPLOAD_SIZE_BYTES`  | `26214400` | Upload size cap (25 MB)                                |
| `LOG_LEVEL`              | `INFO`     | structlog log level                                    |

## Running

```bash
make run
```

Starts the API at `http://127.0.0.1:8000` with auto-reload.

## Usage

```bash
curl -X POST http://127.0.0.1:8000/transcript \
  -F "audio=@voice_note.opus" \
  -F "language=en"
```

Response:

```json
{
  "text": "...",
  "language": "en",
  "duration_seconds": 3.2,
  "segment_count": 1
}
```

`language` is required and never auto-detected — a valid ISO 639-1 code must be supplied. Accepted audio extensions: `.opus`, `.ogg`.

## Development

```bash
make test        # full test suite (unit + integration)
make test-unit    # unit tests only, no model inference
make lint          # ruff check
make typecheck     # mypy
make format        # ruff format
```

The integration test (`@pytest.mark.integration`) runs a real transcription with the `tiny` model and downloads its weights on first run.

## Known limitations

- **No concurrency limit**: nothing bounds the number of simultaneous transcriptions; CTranslate2 releases the GIL, so FastAPI's threadpool gives some real parallelism, but there's no queue or semaphore. Fine for personal use; a shared multi-user deployment would need one.
- **No duration guard**: only a byte-size cap is enforced on upload. A long, low-bitrate recording could pass the size check but still be slow to transcribe.
- **No request timeout**: a stuck or very long transcription will hold the connection open indefinitely.
