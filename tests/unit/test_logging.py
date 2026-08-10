import structlog

from app.core.logging import configure_logging


def test_configure_logging_produces_a_working_logger() -> None:
    configure_logging()

    log = structlog.get_logger()

    log.info("test_event", key="value")
