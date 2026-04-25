"""POST /api/preview tests."""


def test_preview_returns_html(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/preview",
        json={"markdown": minimal_md, "template": "ats_classic"},
    )
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    body = res.text
    assert "Jane Doe" in body
    assert "<style>" in body


def test_preview_invalid_template_returns_404(api_client, minimal_md: str) -> None:
    res = api_client.post(
        "/api/preview",
        json={"markdown": minimal_md, "template": "no_such_template_xyz"},
    )
    assert res.status_code == 404


def test_preview_empty_markdown_returns_422(api_client) -> None:
    res = api_client.post(
        "/api/preview",
        json={"markdown": "", "template": "ats_classic"},
    )
    assert res.status_code == 422


def test_preview_oversize_returns_413(api_client) -> None:
    huge = "a" * (1_048_577)
    res = api_client.post(
        "/api/preview",
        json={"markdown": huge, "template": "ats_classic"},
    )
    assert res.status_code == 413
