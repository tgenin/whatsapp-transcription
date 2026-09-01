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

To avoid any Hugging Face Hub dependency at runtime (e.g. a server with no outbound internet access), pre-download the CTranslate2 model files on a machine that has internet access and point `WHISPER_MODEL_PATH` at that local directory instead — see [Offline deployment](#offline-deployment).

## Configuration

Settings are read from environment variables (see `.env.example`):

| Variable                | Default    | Description                                          |
| ------------------------ | ---------- | ----------------------------------------------------- |
| `WHISPER_MODEL`          | `small`    | faster-whisper model size (used when `WHISPER_MODEL_PATH` is unset) |
| `WHISPER_MODEL_PATH`     | _unset_    | Local directory with a pre-downloaded CTranslate2 model; takes priority over `WHISPER_MODEL` |
| `WHISPER_COMPUTE_TYPE`   | `int8`     | CTranslate2 compute type                               |
| `MAX_UPLOAD_SIZE_BYTES`  | `26214400` | Upload size cap (25 MB)                                |
| `LOG_LEVEL`              | `INFO`     | structlog log level                                    |
| `UI_PASSWORD`            | _required_ | Password protecting the web UI and the API             |

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

### Web UI

A minimal upload page is served at `http://127.0.0.1:8000/`. Both the page and the `/transcript` API are protected by HTTP Basic Auth: the browser will prompt for a username and password — the username is ignored, only the password (`UI_PASSWORD`) is checked.

## Offline deployment

To deploy without giving the server access to the Hugging Face Hub, download the model on a machine that does have internet access, then ship the resulting directory alongside the app (e.g. baked into the Docker image or mounted as a volume):

```bash
uv run huggingface-cli download Systran/faster-whisper-small --local-dir ./models/faster-whisper-small
```

On the server, set:

```bash
WHISPER_MODEL_PATH=/path/to/models/faster-whisper-small
```

`WHISPER_MODEL_PATH` takes priority over `WHISPER_MODEL` and is passed straight to faster-whisper as a local model directory, so no network call to the Hub is made at startup.

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
