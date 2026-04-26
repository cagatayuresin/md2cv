"""REST API routes for md2cv."""

import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response

from app import __version__
from app.api.dependencies import enforce_body_size, limiter
from app.api.schemas import (
    ConvertRequest,
    HealthResponse,
    PreviewRequest,
    TemplateInfo,
    TemplatesResponse,
    VersionResponse,
)
from app.core.converter import CVConverter
from app.core.parser import MarkdownParser
from app.core.renderer import TEMPLATES_DIR, TemplateRenderer

router = APIRouter()

CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.get("/health", tags=["meta"])
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/version", tags=["meta"])
async def version() -> VersionResponse:
    return VersionResponse(version=__version__)


@router.get("/templates", tags=["templates"])
async def templates() -> TemplatesResponse:
    items: list[TemplateInfo] = []
    for name in TemplateRenderer.list_templates(TEMPLATES_DIR):
        template_dir = TEMPLATES_DIR / name
        items.append(
            TemplateInfo(
                name=name,
                has_html=(template_dir / "template.html").exists(),
                has_css=(template_dir / "style.css").exists(),
            )
        )
    return TemplatesResponse(templates=items)


@router.post(
    "/preview",
    response_class=HTMLResponse,
    tags=["convert"],
    dependencies=[Depends(enforce_body_size)],
)
@limiter.limit("120/minute")
async def preview(request: Request, payload: PreviewRequest) -> HTMLResponse:
    try:
        renderer = TemplateRenderer(payload.template)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    parser = MarkdownParser(payload.markdown)
    html = renderer.render_inline(parser.meta, parser.to_html())
    return HTMLResponse(content=html)


@router.post(
    "/convert",
    tags=["convert"],
    dependencies=[Depends(enforce_body_size)],
    responses={
        200: {
            "content": {
                "application/pdf": {},
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {},
                "application/zip": {},
            }
        }
    },
)
@limiter.limit("30/minute")
async def convert(request: Request, payload: ConvertRequest) -> Response:
    if not payload.formats:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one format must be requested.",
        )

    try:
        converter = CVConverter(template_name=payload.template)
        outputs = converter.convert_to_bytes(payload.markdown, list(payload.formats))
    except ValueError as exc:
        message = str(exc)
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message.lower()
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=code, detail=message)

    if len(outputs) == 1:
        fmt, data = next(iter(outputs.items()))
        return Response(
            content=data,
            media_type=CONTENT_TYPES[fmt],
            headers={"Content-Disposition": f'attachment; filename="cv.{fmt}"'},
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for fmt, data in outputs.items():
            archive.writestr(f"cv.{fmt}", data)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="cv.zip"'},
    )
