from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, RedirectResponse

from app.core.security import verify_credentials

STATIC_DIR = Path(__file__).parent / "static"

router = APIRouter()


@router.get("/", dependencies=[Depends(verify_credentials)])
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/manifest.json")
def manifest() -> FileResponse:
    # Unauthenticated: Android's WebAPK minting service fetches the manifest
    # and icons from its own servers, with no way to send our Basic Auth
    # credentials. Gating these behind auth silently breaks PWA install
    # (Chrome falls back to a plain bookmark shortcut, which never
    # registers as an OS share target). No secrets live in this file.
    return FileResponse(
        STATIC_DIR / "manifest.json", media_type="application/manifest+json"
    )


@router.get("/sw.js", dependencies=[Depends(verify_credentials)])
def service_worker() -> FileResponse:
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript")


@router.get("/icon.svg")
def icon() -> FileResponse:
    # Unauthenticated for the same reason as /manifest.json above.
    return FileResponse(STATIC_DIR / "icon.svg", media_type="image/svg+xml")


@router.post("/share-target", dependencies=[Depends(verify_credentials)])
def share_target() -> RedirectResponse:
    # The service worker (sw.js) is expected to intercept this navigation
    # client-side before it reaches the network. This is a defensive
    # fallback for the rare case it hasn't taken control yet.
    return RedirectResponse(url="/", status_code=303)
