"""PDFExporter tests."""

from pathlib import Path

from app.core.exporters import PDFExporter
from app.core.parser import MarkdownParser
from app.core.renderer import TemplateRenderer


def _build_html(markdown_text: str, template: str = "ats_classic") -> tuple[str, TemplateRenderer]:
    parser = MarkdownParser(markdown_text)
    renderer = TemplateRenderer(template)
    return renderer.render(parser.meta, parser.to_html()), renderer


def test_export_bytes_produces_pdf_magic_header(minimal_md: str) -> None:
    html, renderer = _build_html(minimal_md)
    data = PDFExporter(renderer).export_bytes(html)
    assert data[:4] == b"%PDF"
    assert len(data) > 1000


def test_export_to_path_writes_file(tmp_path: Path, minimal_md: str) -> None:
    html, renderer = _build_html(minimal_md)
    out = tmp_path / "out.pdf"
    result = PDFExporter(renderer).export_to_path(html, out)
    assert result == out
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"


def test_export_bytes_works_without_css(tmp_path: Path) -> None:
    template_dir = tmp_path / "nocss"
    template_dir.mkdir()
    (template_dir / "template.html").write_text(
        "<html><body>{{ meta.name }}{{ content | safe }}</body></html>",
        encoding="utf-8",
    )
    renderer = TemplateRenderer("nocss", templates_dir=tmp_path)
    html = renderer.render({"name": "Jane"}, "<p>Body</p>")
    data = PDFExporter(renderer).export_bytes(html)
    assert data[:4] == b"%PDF"
