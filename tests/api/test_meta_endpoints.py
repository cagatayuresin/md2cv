"""Meta endpoints — health, version, templates."""

from app import __version__


def test_health_returns_ok(api_client) -> None:
    res = api_client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_version_returns_current_version(api_client) -> None:
    res = api_client.get("/api/version")
    assert res.status_code == 200
    assert res.json() == {"version": __version__}


def test_templates_list_includes_known_themes(api_client) -> None:
    res = api_client.get("/api/templates")
    assert res.status_code == 200
    payload = res.json()
    names = {t["name"] for t in payload["templates"]}
    assert {"ats_classic", "modern", "minimal"}.issubset(names)
    for tpl in payload["templates"]:
        assert tpl["has_html"] is True
