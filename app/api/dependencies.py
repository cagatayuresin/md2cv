"""Shared API dependencies — rate limiter, body size guard."""

from fastapi import HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.schemas import MAX_MARKDOWN_BYTES

limiter = Limiter(key_func=get_remote_address, default_limits=["240/minute"])


async def enforce_body_size(request: Request) -> None:
    """Reject requests whose Content-Length exceeds the markdown size cap."""
    content_length = request.headers.get("content-length")
    if content_length is None:
        return
    try:
        size = int(content_length)
    except ValueError:
        return
    if size > MAX_MARKDOWN_BYTES:
        too_large = getattr(
            status, "HTTP_413_CONTENT_TOO_LARGE", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
        raise HTTPException(
            status_code=too_large,
            detail=f"Request body too large (max {MAX_MARKDOWN_BYTES} bytes).",
        )
