"""CLI smoke tests — exercise app.cli.main directly."""

import sys
from pathlib import Path

import pytest

from app.cli import main


def test_list_templates_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--list-templates"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "ats_classic" in captured.out


def test_missing_input_errors(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2
    err = capsys.readouterr().err
    assert "Input file is required" in err


def test_convert_pdf_only(tmp_path: Path, fixtures_dir: Path) -> None:
    out_dir = tmp_path / "out"
    rc = main(
        [
            str(fixtures_dir / "minimal_cv.md"),
            "--format",
            "pdf",
            "--template",
            "ats_classic",
            "--output-dir",
            str(out_dir),
        ]
    )
    assert rc == 0
    pdfs = list(out_dir.glob("*.pdf"))
    assert len(pdfs) == 1
    assert pdfs[0].read_bytes()[:4] == b"%PDF"


def test_convert_invalid_template_returns_one(
    tmp_path: Path, fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(
        [
            str(fixtures_dir / "minimal_cv.md"),
            "--format",
            "pdf",
            "--template",
            "missing_xyz",
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert rc == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_convert_missing_input_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(
        [
            str(tmp_path / "nope.md"),
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert rc == 1


def test_version_flag_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "md2cv" in out


def test_module_invocation_works(tmp_path: Path, fixtures_dir: Path) -> None:
    """Ensure ``python -m app.cli`` style invocation still produces output."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.cli",
            str(fixtures_dir / "minimal_cv.md"),
            "--format",
            "pdf",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    pdfs = list(tmp_path.glob("*.pdf"))
    assert pdfs
