# Contributing to MD2CV

Thank you for your interest in contributing!

## Local Development

```bash
# 1. Clone & install dependencies
git clone https://github.com/cagatayuresin/md2cv.git
cd md2cv
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt

# 2. Install pre-commit hooks
pre-commit install

# 3. Run tests + coverage gate (85%)
pytest

# 4. Start the dev server with auto-reload
uvicorn app.main:app --reload
# UI:     http://localhost:8000
# Swagger: http://localhost:8000/docs
```

### System Dependencies (WeasyPrint)

WeasyPrint needs the Pango/Cairo stack. On Debian/Ubuntu:

```bash
sudo apt-get install -y \
  libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
  libffi-dev libcairo2 libglib2.0-0 fonts-liberation fonts-dejavu-core
```

On macOS use `brew install pango`. On Windows the simplest path is to develop inside the Docker image (`./md2cv.sh`).

## Reporting Bugs

1. Check existing [Issues](../../issues).
2. Open a new issue with reproduction steps, expected vs actual, and your environment (OS, Python version, Docker version).

## Suggesting Features

Open an issue with the `enhancement` label and describe the use case.

## Adding a Template

1. Create a folder under `templates/<your_theme>/`.
2. Add two files:
   - `template.html` — Jinja2 template
   - `style.css` — your styles
3. Available Jinja variables:
   - `meta.name`, `meta.title`, `meta.email`, `meta.phone`, `meta.location`
   - `meta.linkedin`, `meta.github`, `meta.website`
   - `content | safe` — rendered Markdown body
4. Add a screenshot or example PDF under `examples/<theme>_example.pdf` (optional but appreciated).
5. Open a pull request.

## Adding an API Endpoint

1. Define request/response models in [`app/api/schemas.py`](app/api/schemas.py).
2. Add the route to [`app/api/routes.py`](app/api/routes.py) with a `@router.<method>` decorator and any rate-limit or dependency you need.
3. Add unit tests under `tests/api/test_<feature>.py` using the shared `api_client` fixture from [`tests/conftest.py`](tests/conftest.py).
4. Run `pytest`. Coverage must stay above **85%**.

## Code Style

- Python 3.11, line length **100**.
- `black`, `ruff`, `isort` run via pre-commit; CI does not block on style but please keep diffs clean.
- Public classes and functions get a one-line docstring; reserve longer comments for non-obvious *why*.

## Commit / PR Hygiene

- One feature/fix per PR.
- Update `CHANGELOG.md` under the `## [Unreleased]` section (create one if needed) with what changed and why.
- For API changes, update `README.md` and any `curl` examples.

## Releasing

Maintainers only:

1. Bump `__version__` in [`app/__init__.py`](app/__init__.py) and `version` in `pyproject.toml`.
2. Move the `## [Unreleased]` block in `CHANGELOG.md` to a dated `## [x.y.z] - YYYY-MM-DD` section.
3. Tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. The `release` workflow builds and publishes `ghcr.io/cagatayuresin/md2cv:X.Y.Z` (and `latest`) automatically.

## Questions?

Open an issue with the `question` label.
