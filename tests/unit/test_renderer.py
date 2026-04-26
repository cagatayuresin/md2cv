"""TemplateRenderer tests."""

from pathlib import Path

import pytest

from app.core.renderer import TEMPLATES_DIR, TemplateRenderer


def test_invalid_template_raises_value_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        TemplateRenderer("does_not_exist_xyz")
    assert "not found" in str(exc_info.value).lower()


def test_render_includes_meta_name() -> None:
    renderer = TemplateRenderer("ats_classic")
    html = renderer.render({"name": "Jane Doe"}, "<p>Body</p>")
    assert "Jane Doe" in html
    assert "Body" in html


def test_get_css_path_points_to_style_css() -> None:
    renderer = TemplateRenderer("ats_classic")
    css_path = renderer.get_css_path()
    assert css_path.name == "style.css"
    assert css_path.exists()


def test_render_inline_embeds_css() -> None:
    renderer = TemplateRenderer("ats_classic")
    html = renderer.render_inline({"name": "Jane"}, "<p>Body</p>")
    assert "<style>" in html
    assert "Jane" in html


def test_list_templates_returns_known_set() -> None:
    names = TemplateRenderer.list_templates(TEMPLATES_DIR)
    assert "ats_classic" in names
    assert "modern" in names
    assert "minimal" in names


def test_list_templates_missing_dir(tmp_path: Path) -> None:
    assert TemplateRenderer.list_templates(tmp_path / "missing") == []


def test_render_inline_without_css(tmp_path: Path) -> None:
    template_dir = tmp_path / "plain"
    template_dir.mkdir()
    (template_dir / "template.html").write_text(
        "<html><body>{{ meta.name }} {{ content | safe }}</body></html>",
        encoding="utf-8",
    )
    renderer = TemplateRenderer("plain", templates_dir=tmp_path)
    out = renderer.render_inline({"name": "X"}, "<p>Y</p>")
    assert "X" in out
    assert "<style>" not in out
