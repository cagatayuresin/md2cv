"""CVConverter tests — orchestration."""

from pathlib import Path

import pytest

from app.core.converter import CVConverter


def test_convert_to_bytes_pdf_only(minimal_md: str) -> None:
    result = CVConverter(template_name="ats_classic").convert_to_bytes(minimal_md, ["pdf"])
    assert set(result) == {"pdf"}
    assert result["pdf"][:4] == b"%PDF"


def test_convert_to_bytes_docx_only(minimal_md: str) -> None:
    result = CVConverter(template_name="ats_classic").convert_to_bytes(minimal_md, ["docx"])
    assert set(result) == {"docx"}
    assert len(result["docx"]) > 0


def test_convert_to_bytes_both(minimal_md: str) -> None:
    result = CVConverter(template_name="ats_classic").convert_to_bytes(
        minimal_md, ["pdf", "docx"]
    )
    assert set(result) == {"pdf", "docx"}


def test_convert_to_bytes_all_keyword(minimal_md: str) -> None:
    result = CVConverter().convert_to_bytes(minimal_md, ["all"])
    assert set(result) == {"pdf", "docx"}


def test_convert_to_bytes_empty_formats_raises(minimal_md: str) -> None:
    with pytest.raises(ValueError):
        CVConverter().convert_to_bytes(minimal_md, [])


def test_convert_to_bytes_unknown_format_raises(minimal_md: str) -> None:
    with pytest.raises(ValueError):
        CVConverter().convert_to_bytes(minimal_md, ["html"])


def test_convert_to_bytes_invalid_template_raises(minimal_md: str) -> None:
    with pytest.raises(ValueError):
        CVConverter(template_name="does_not_exist").convert_to_bytes(minimal_md, ["pdf"])


def test_convert_file_based(tmp_path: Path, fixtures_dir: Path) -> None:
    out_dir = tmp_path / "out"
    converter = CVConverter(
        input_path=fixtures_dir / "minimal_cv.md",
        template_name="ats_classic",
        output_dir=out_dir,
    )
    created = converter.convert(["pdf", "docx"])
    assert {p.suffix for p in created} == {".pdf", ".docx"}
    for p in created:
        assert p.exists()


def test_convert_file_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        CVConverter(input_path=tmp_path / "nope.md", output_dir=tmp_path)


def test_convert_without_input_raises(tmp_path: Path) -> None:
    converter = CVConverter(output_dir=tmp_path)
    with pytest.raises(ValueError):
        converter.convert(["pdf"])


def test_convert_without_output_dir_raises(fixtures_dir: Path) -> None:
    converter = CVConverter(input_path=fixtures_dir / "minimal_cv.md")
    with pytest.raises(ValueError):
        converter.convert(["pdf"])
