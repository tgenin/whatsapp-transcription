from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.transcript import router as transcript_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.services.transcription import get_transcription_service
from app.web.router import router as ui_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    get_transcription_service()
    yield


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
app.include_router(transcript_router)
app.include_router(health_router)
app.include_router(ui_router)
