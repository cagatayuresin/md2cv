"""High-level orchestrator: markdown text or file → PDF/DOCX bytes or files."""

from pathlib import Path

from app.core.exporters import DOCXExporter, PDFExporter
from app.core.parser import MarkdownParser
from app.core.renderer import TemplateRenderer

DEFAULT_TEMPLATE = "ats_classic"
SUPPORTED_FORMATS = ("pdf", "docx")


class CVConverter:
    """Orchestrate the markdown → PDF/DOCX conversion pipeline."""

    def __init__(
        self,
        input_path: str | Path | None = None,
        template_name: str = DEFAULT_TEMPLATE,
        output_dir: Path | None = None,
        templates_dir: Path | None = None,
    ):
        self.input_path = Path(input_path) if input_path else None
        self.template_name = template_name
        self.output_dir = Path(output_dir) if output_dir else None
        self.templates_dir = Path(templates_dir) if templates_dir else None

        if self.input_path and not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

    def _renderer(self) -> TemplateRenderer:
        return TemplateRenderer(self.template_name, templates_dir=self.templates_dir)

    @staticmethod
    def _normalize_formats(formats: list[str]) -> list[str]:
        if not formats:
            raise ValueError("At least one output format is required.")
        if "all" in formats:
            return list(SUPPORTED_FORMATS)
        unknown = [f for f in formats if f not in SUPPORTED_FORMATS]
        if unknown:
            raise ValueError(
                f"Unsupported format(s): {', '.join(unknown)}. "
                f"Supported: {', '.join(SUPPORTED_FORMATS)}"
            )
        return list(formats)

    def convert_to_bytes(self, markdown_text: str, formats: list[str]) -> dict[str, bytes]:
        normalized = self._normalize_formats(formats)
        parser = MarkdownParser(markdown_text)
        renderer = self._renderer()
        result: dict[str, bytes] = {}

        if "pdf" in normalized:
            html = renderer.render(parser.meta, parser.to_html())
            result["pdf"] = PDFExporter(renderer).export_bytes(html)

        if "docx" in normalized:
            result["docx"] = DOCXExporter().export_bytes(parser.meta, parser.body)

        return result

    def convert(self, formats: list[str]) -> list[Path]:
        if not self.input_path:
            raise ValueError("input_path is required for file-based conversion.")
        if not self.output_dir:
            raise ValueError("output_dir is required for file-based conversion.")

        normalized = self._normalize_formats(formats)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        markdown_text = self.input_path.read_text(encoding="utf-8")
        parser = MarkdownParser(markdown_text)
        renderer = self._renderer()

        output_base = self.output_dir / self.input_path.stem
        created: list[Path] = []

        if "pdf" in normalized:
            html = renderer.render(parser.meta, parser.to_html())
            pdf_path = output_base.with_suffix(".pdf")
            PDFExporter(renderer).export_to_path(html, pdf_path)
            created.append(pdf_path)

        if "docx" in normalized:
            docx_path = output_base.with_suffix(".docx")
            DOCXExporter().export_to_path(parser.meta, parser.body, docx_path)
            created.append(docx_path)

        return created
