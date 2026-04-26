# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-26

### Added

- **REST API** built on FastAPI with auto-generated Swagger / ReDoc:
  - `GET /api/health`, `GET /api/version`, `GET /api/templates`
  - `POST /api/preview` — renders Markdown to HTML with template CSS inlined.
  - `POST /api/convert` — returns PDF, DOCX, or a ZIP archive when both formats are requested.
- **Web UI** at `/` — Markdown editor (EasyMDE), live preview, template picker, format selection, one-click download. Built with Tabler CSS / Tabler Icons; no build step required.
- **Multi-stage Dockerfile** with non-root user, baked-in `HEALTHCHECK`, and OCI image labels.
- **`docker-compose.yml`** for one-command local startup.
- **Test suite** (`tests/`) with `pytest` + `pytest-cov` + `httpx` covering parser, renderer, both exporters, converter orchestration, every API endpoint, and the CLI. Coverage gate enforced at **85%**.
- **SonarCloud coverage integration** — `coverage.xml` is now produced in CI and uploaded as a build artifact.
- **GitHub Actions release workflow** — pushing a `v*` tag publishes the image to `ghcr.io/cagatayuresin/md2cv` (`latest`, `<major.minor>`, `<full version>`) for both `linux/amd64` and `linux/arm64`.
- **Pre-commit configuration** with `black`, `ruff`, `isort`, and standard hygiene hooks.
- **DOCX table support** — Markdown pipe tables now render as native Word tables with the `Table Grid` style.
- **Rate limiting** (slowapi) on `/api/preview` (120/min) and `/api/convert` (30/min).
- **Body-size guard** — payloads larger than 1 MiB are rejected with `413`.
- **CORS configuration** via `MD2CV_CORS_ORIGINS` env var (comma-separated; default `*`).

### Changed

- Codebase reorganised under the `app/` package: `app.core` (parser, renderer, exporters, converter), `app.api` (routes, schemas, dependencies), `app.cli`, `app.main`. Library users should import from `app.core.converter` (e.g. `from app.core.converter import CVConverter`).
- CLI is now invoked as `python -m app.cli` (or via `./md2cv.sh cli ...`). The Docker image's default entry point is the API server (`uvicorn app.main:app` on port `8000`).
- `CVConverter` now accepts an explicit `output_dir` parameter, eliminating the previous module-level `OUTPUT_DIR` global. Two new methods, `export_bytes()` (on `PDFExporter` / `DOCXExporter`) and `convert_to_bytes()` (on `CVConverter`), enable in-memory conversion paths used by the API.
- `md2cv.sh` now drives both `server` and `cli` modes against the new image.
- `sonar-project.properties` now declares `sources`, `tests`, coverage report path, and exclusion globs.
- README rewritten around Docker / API / Web UI as the primary entry points.

### Removed

- Module-level `OUTPUT_DIR` global (replaced by constructor argument on `CVConverter`).
- Top-level `converter.py` script entry point (use `python -m app.cli` instead).

### Known limitations

- DOCX export does not yet render nested lists, blockquotes, or horizontal rules. Tracked for v2.1.0. PDF export already supports them via WeasyPrint.

## [1.0.0] - 2026-01-13

### Added (1.0.0)

- Initial release
- Markdown to PDF conversion using WeasyPrint
- Markdown to DOCX conversion using python-docx
- YAML frontmatter support for CV metadata
- Template system with multiple themes:
  - `ats_classic` - Clean, ATS-friendly design
  - `modern` - Contemporary design with accent colors
  - `minimal` - Simple, elegant layout
- Docker support for easy deployment
- CLI with format and template selection options
