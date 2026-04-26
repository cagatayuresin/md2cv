"""Markdown + YAML frontmatter parser."""

import re

import markdown
import yaml


class MarkdownParser:
    """Parse Markdown content with YAML frontmatter and HTML support."""

    # Anchored at the start of the document; bounded by literal `\n---...\n`
    # delimiters and uses `[^\n]*` for the trailing whitespace on the fence
    # lines (handles CRLF safely while staying linear-time, S5852).
    FRONTMATTER_PATTERN = re.compile(r"\A---[^\n]*\n([\s\S]*?)\n---[^\n]*\n")

    def __init__(self, content: str):
        self.raw_content = content
        self.meta: dict = {}
        self.body: str = ""
        self._parse()

    def _parse(self) -> None:
        match = self.FRONTMATTER_PATTERN.match(self.raw_content)
        if match:
            yaml_content = match.group(1)
            try:
                self.meta = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError:
                self.meta = {}
            if not isinstance(self.meta, dict):
                self.meta = {}
            self.body = self.raw_content[match.end():]
        else:
            self.meta = {}
            self.body = self.raw_content

    def to_html(self) -> str:
        md = markdown.Markdown(
            extensions=[
                "extra",
                "meta",
                "nl2br",
                "sane_lists",
                "smarty",
            ]
        )
        return md.convert(self.body)
