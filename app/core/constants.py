from pathlib import Path

ALLOWED_AUDIO_EXTENSIONS = frozenset({".opus", ".ogg"})

HEALTH_CHECK_SAMPLE_PATH = (
    Path(__file__).parent.parent / "resources" / "health_check_sample.opus"
)
HEALTH_CHECK_SAMPLE_LANGUAGE = "fr"
HEALTH_CHECK_EXPECTED_TEXT = "bonjour"
