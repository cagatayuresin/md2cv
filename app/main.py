"""FastAPI entrypoint — wires API routes, CORS, rate limiting, static UI."""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.api.dependencies import limiter
from app.api.routes import router as api_router

WEB_DIR = Path(__file__).resolve().parent / "web"
LOG_LEVEL = os.getenv("MD2CV_LOG_LEVEL", "INFO").upper()
CORS_ORIGINS = [o.strip() for o in os.getenv("MD2CV_CORS_ORIGINS", "*").split(",") if o.strip()]

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("md2cv")


def create_app() -> FastAPI:
    app = FastAPI(
        title="md2cv",
        version=__version__,
        description="Convert Markdown CVs to ATS-friendly PDF and DOCX.",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error."},
        )

    app.include_router(api_router, prefix="/api")

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="ui")
    else:
        logger.warning("Web UI directory not found at %s", WEB_DIR)

    return app


app = create_app()
