"""Pydantic schemas for the REST API."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MARKDOWN_BYTES = 1_048_576  # 1 MiB


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
    template: str = Field(default="ats_classic", min_length=1, max_length=64)


class ConvertRequest(BaseModel):
    markdown: str = Field(..., min_length=1, max_length=MAX_MARKDOWN_BYTES)
    template: str = Field(default="ats_classic", min_length=1, max_length=64)
    formats: list[Literal["pdf", "docx"]] = Field(default_factory=lambda: ["pdf"])
