"""CORS preflight check."""


def test_cors_preflight_allows_origin(api_client) -> None:
    res = api_client.options(
        "/api/health",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code in (200, 204)
    assert "access-control-allow-origin" in {k.lower() for k in res.headers.keys()}
