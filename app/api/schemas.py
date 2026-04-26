"""Pydantic schemas for the REST API."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MARKDOWN_BYTES = 1_048_576  # 1 MiB

# Template names map directly to a directory under templates/. Restrict to a
# safe character class so a crafted name (e.g. "../something") can't escape
# the templates root and surface arbitrary file content via the API
# (defense-in-depth for python:S5131).
TEMPLATE_NAME_PATTERN = r"^[A-Za-z0-9_-]+$"


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class VersionResponse(BaseModel):
    version: str


class TemplateInfo(BaseModel):
    name: str
    has_html: bool
    has_css: bool


class TemplatesResponse(BaseModel):
    templates: list[TemplateInfo]


class PreviewRequest(BaseModel):
    markdown: str = Field(..., min_length=1, max_length=MAX_MARKDOWN_BYTES)
    template: str = Field(
        default="ats_classic",
        min_length=1,
        max_length=64,
        pattern=TEMPLATE_NAME_PATTERN,
    )


class ConvertRequest(BaseModel):
    markdown: str = Field(..., min_length=1, max_length=MAX_MARKDOWN_BYTES)
    template: str = Field(
        default="ats_classic",
        min_length=1,
        max_length=64,
        pattern=TEMPLATE_NAME_PATTERN,
    )
    formats: list[Literal["pdf", "docx"]] = Field(default_factory=lambda: ["pdf"])
