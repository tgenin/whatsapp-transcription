from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, RedirectResponse

from app.core.security import verify_credentials

STATIC_DIR = Path(__file__).parent / "static"

router = APIRouter()


@router.get("/", dependencies=[Depends(verify_credentials)])
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/manifest.json", dependencies=[Depends(verify_credentials)])
def manifest() -> FileResponse:
    return FileResponse(
        STATIC_DIR / "manifest.json", media_type="application/manifest+json"
    )


@router.get("/sw.js", dependencies=[Depends(verify_credentials)])
def service_worker() -> FileResponse:
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript")


@router.get("/icon.svg", dependencies=[Depends(verify_credentials)])
def icon() -> FileResponse:
    return FileResponse(STATIC_DIR / "icon.svg", media_type="image/svg+xml")


@router.post("/share-target", dependencies=[Depends(verify_credentials)])
def share_target() -> RedirectResponse:
    # The service worker (sw.js) is expected to intercept this navigation
    # client-side before it reaches the network. This is a defensive
    # fallback for the rare case it hasn't taken control yet.
    return RedirectResponse(url="/", status_code=303)
