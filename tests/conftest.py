"""Shared pytest fixtures."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def minimal_md(fixtures_dir: Path) -> str:
    return (fixtures_dir / "minimal_cv.md").read_text(encoding="utf-8")


@pytest.fixture
def no_frontmatter_md(fixtures_dir: Path) -> str:
    return (fixtures_dir / "no_frontmatter.md").read_text(encoding="utf-8")


@pytest.fixture
def bad_yaml_md(fixtures_dir: Path) -> str:
    return (fixtures_dir / "bad_yaml.md").read_text(encoding="utf-8")


@pytest.fixture
def api_client():
    app = create_app()
    if hasattr(app.state, "limiter"):
        app.state.limiter.enabled = False
    with TestClient(app) as client:
        yield client
