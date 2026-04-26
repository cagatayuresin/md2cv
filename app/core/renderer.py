"""Jinja2 template renderer for CV templates."""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Defense-in-depth against path traversal — the API layer also validates this
# pattern, but enforcing it here means direct library callers can't read
# arbitrary files via crafted template names (S5131).
_SAFE_TEMPLATE_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


class TemplateRenderer:
    """Render CV content using Jinja2 templates."""

    def __init__(self, template_name: str, templates_dir: Path | None = None):
        if not isinstance(template_name, str) or not _SAFE_TEMPLATE_NAME.match(template_name):
            raise ValueError(
                f"Template '{template_name}' not found. "
                "Template names may only contain letters, digits, '_' or '-'."
            )
        self.template_name = template_name
        self.templates_root = Path(templates_dir) if templates_dir else TEMPLATES_DIR
        self.template_dir = self.templates_root / template_name

        if not self.template_dir.exists():
            available = self.list_templates(self.templates_root)
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {', '.join(available) if available else '(none)'}"
            )

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )

    @staticmethod
    def list_templates(templates_root: Path | None = None) -> list[str]:
        root = Path(templates_root) if templates_root else TEMPLATES_DIR
        if not root.exists():
            return []
        return sorted(d.name for d in root.iterdir() if d.is_dir())

    def render(self, meta: dict, content: str) -> str:
        template = self.env.get_template("template.html")
        return template.render(meta=meta, content=content)

    def get_css_path(self) -> Path:
        return self.template_dir / "style.css"

    def read_css(self) -> str:
        css_path = self.get_css_path()
        if css_path.exists():
            return css_path.read_text(encoding="utf-8")
        return ""

    def render_inline(self, meta: dict, content: str) -> str:
        """Render with CSS inlined into a <style> tag (for iframe srcdoc preview)."""
        html = self.render(meta, content)
        css = self.read_css()
        if not css:
            return html
        style_tag = f"<style>\n{css}\n</style>"
        if "</head>" in html:
            return html.replace("</head>", f"{style_tag}\n</head>", 1)
        return f"{style_tag}\n{html}"
