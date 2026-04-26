"""Command-line interface for md2cv.

Examples:
    python -m app.cli cv.md --format pdf
    python -m app.cli cv.md --format docx --template ats_classic
    python -m app.cli cv.md --format all
    python -m app.cli --list-templates
"""

import argparse
import sys
from pathlib import Path

from app import __version__
from app.core.converter import DEFAULT_TEMPLATE, SUPPORTED_FORMATS, CVConverter
from app.core.renderer import TEMPLATES_DIR, TemplateRenderer

DEFAULT_OUTPUT_DIR = Path.cwd() / "output"


def list_templates(templates_dir: Path = TEMPLATES_DIR) -> None:
    print("\nAvailable templates:")
    print("-" * 40)
    if not templates_dir.exists():
        print("  No templates directory found.")
        return
    for name in TemplateRenderer.list_templates(templates_dir):
        template_dir = templates_dir / name
        has_html = (template_dir / "template.html").exists()
        marker = "OK" if has_html else "!!"
        print(f"  [{marker}] {name}")
        if not has_html:
            print("      missing: template.html")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2cv",
        description="md2cv — Convert Markdown CVs to PDF and DOCX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m app.cli cv.md --format pdf\n"
            "  python -m app.cli cv.md --format docx --template ats_classic\n"
            "  python -m app.cli cv.md --format all\n"
            "  python -m app.cli --list-templates\n"
        ),
    )
    parser.add_argument("input", nargs="?", help="Input Markdown file path")
    parser.add_argument(
        "-f",
        "--format",
        choices=[*SUPPORTED_FORMATS, "all"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "-t",
        "--template",
        default=DEFAULT_TEMPLATE,
        help=f"Template name (default: {DEFAULT_TEMPLATE})",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"md2cv {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_templates:
        list_templates()
        return 0

    if not args.input:
        parser.error("Input file is required (unless using --list-templates)")

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR

    try:
        converter = CVConverter(
            input_path=args.input,
            template_name=args.template,
            output_dir=output_dir,
        )
        formats = list(SUPPORTED_FORMATS) if args.format == "all" else [args.format]
        created = converter.convert(formats)
        for path in created:
            print(f"OK created: {path}")
        print(f"\nDone. {len(created)} file(s) created.")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
