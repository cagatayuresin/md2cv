"""MarkdownParser tests."""

from app.core.parser import MarkdownParser


def test_parses_frontmatter_and_body(minimal_md: str) -> None:
    parser = MarkdownParser(minimal_md)
    assert parser.meta["name"] == "Jane Doe"
    assert parser.meta["email"] == "jane@example.com"
    assert "# Summary" in parser.body


def test_no_frontmatter_returns_empty_meta(no_frontmatter_md: str) -> None:
    parser = MarkdownParser(no_frontmatter_md)
    assert parser.meta == {}
    assert parser.body.startswith("# Heading")


def test_bad_yaml_falls_back_to_empty_meta(bad_yaml_md: str) -> None:
    parser = MarkdownParser(bad_yaml_md)
    assert parser.meta == {}
    assert "# Body" in parser.body


def test_to_html_renders_basic_markdown() -> None:
    parser = MarkdownParser("# Heading\n\nSome **bold** text.\n")
    html = parser.to_html()
    assert "<h1>" in html
    assert "<strong>bold</strong>" in html


def test_to_html_handles_table() -> None:
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    parser = MarkdownParser(md)
    html = parser.to_html()
    assert "<table>" in html
    assert "<td>1</td>" in html


def test_frontmatter_with_unicode() -> None:
    md = '---\nname: "Çağatay"\n---\n\n# CV\n'
    parser = MarkdownParser(md)
    assert parser.meta["name"] == "Çağatay"


def test_non_dict_yaml_falls_back_to_empty() -> None:
    md = "---\n- just a list\n- not a mapping\n---\n\n# Body\n"
    parser = MarkdownParser(md)
    assert parser.meta == {}
