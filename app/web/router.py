from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.core.security import verify_credentials

STATIC_DIR = Path(__file__).parent / "static"

router = APIRouter()


@router.get("/", dependencies=[Depends(verify_credentials)])
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
