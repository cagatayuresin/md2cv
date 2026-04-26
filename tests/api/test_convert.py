"""POST /api/convert tests."""

import io
import zipfile


def test_convert_pdf_returns_pdf_bytes(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/convert",
        json={"markdown": minimal_md, "template": "ats_classic", "formats": ["pdf"]},
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:4] == b"%PDF"
    assert "attachment" in res.headers.get("content-disposition", "")


def test_convert_docx_returns_office_doc(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/convert",
        json={"markdown": minimal_md, "template": "ats_classic", "formats": ["docx"]},
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )
    assert zipfile.is_zipfile(io.BytesIO(res.content))


def test_convert_both_returns_zip(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/convert",
        json={"markdown": minimal_md, "template": "ats_classic", "formats": ["pdf", "docx"]},
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(res.content)) as archive:
        names = set(archive.namelist())
        assert names == {"cv.pdf", "cv.docx"}


def test_convert_invalid_template_returns_404(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/convert",
        json={"markdown": minimal_md, "template": "does_not_exist", "formats": ["pdf"]},
    )
    assert res.status_code == 404


def test_convert_unknown_format_returns_422(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/convert",
        json={"markdown": minimal_md, "template": "ats_classic", "formats": ["html"]},
    )
    assert res.status_code == 422


def test_convert_oversize_returns_413(api_client) -> None:
    huge = "a" * (1_048_577)
    res = api_client.post(
        "/api/convert",
        json={"markdown": huge, "template": "ats_classic", "formats": ["pdf"]},
    )
    assert res.status_code == 413


def test_convert_missing_payload_returns_422(api_client) -> None:
    res = api_client.post("/api/convert", json={})
    assert res.status_code == 422
