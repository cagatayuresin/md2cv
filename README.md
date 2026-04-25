# MD2CV

> Convert Markdown resumes to ATS-friendly PDF and DOCX — REST API + Web UI + CLI.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](Dockerfile)
[![Build](https://github.com/cagatayuresin/md2cv/actions/workflows/build.yml/badge.svg)](https://github.com/cagatayuresin/md2cv/actions/workflows/build.yml)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=cagatayuresin_md2cv&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cagatayuresin_md2cv)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cagatayuresin_md2cv&metric=coverage)](https://sonarcloud.io/summary/new_code?id=cagatayuresin_md2cv)

## What's New in v2.0.0

- **REST API** — `POST /api/convert`, `POST /api/preview`, `GET /api/templates`, auto-generated Swagger at `/docs`.
- **Web UI** — Markdown editor + live preview + one-click download (Tabler CSS / Icons, EasyMDE) at `http://localhost:8000/`.
- **Hardened image** — Multi-stage Dockerfile, non-root user, baked-in healthcheck.
- **Test suite >85% coverage**, reported to SonarCloud.
- **Auto-publish to GHCR** on every `v*` tag.
- **DOCX table support**, plus the existing parser is fully covered by tests.

## Quick Start (Docker)

```bash
# Pull and run the image — UI on http://localhost:8000, Swagger on /docs
docker run --rm -p 8000:8000 ghcr.io/cagatayuresin/md2cv:latest
```

Or use the helper script:

```bash
./md2cv.sh                 # build (if needed) and start the server
./md2cv.sh server -p 3000  # different host port
./md2cv.sh cli my_cv.md --format all   # CLI mode inside the container
```

Or `docker compose`:

```bash
docker compose up -d
curl http://localhost:8000/api/health   # {"status":"ok"}
```

## REST API

| Method | Path             | Description                                                      |
|--------|------------------|------------------------------------------------------------------|
| GET    | `/api/health`    | Liveness probe                                                   |
| GET    | `/api/version`   | Reports `{"version":"2.0.0"}`                                    |
| GET    | `/api/templates` | Lists installed templates and asset availability                 |
| POST   | `/api/preview`   | Returns rendered HTML (CSS inlined for iframe srcdoc)            |
| POST   | `/api/convert`   | Returns PDF, DOCX, or a ZIP archive when both formats are asked  |

Full schema and try-it-out UI: **`http://localhost:8000/docs`**.

### Example: curl

```bash
# Preview HTML
curl -X POST http://localhost:8000/api/preview \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Test\n\nHello.","template":"ats_classic"}'

# Convert to PDF
curl -X POST http://localhost:8000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Test\n\nHello.","template":"ats_classic","formats":["pdf"]}' \
  -o cv.pdf

# Convert to PDF + DOCX bundle
curl -X POST http://localhost:8000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Test","template":"modern","formats":["pdf","docx"]}' \
  -o cv.zip
```

### Limits

- Markdown payload max **1 MiB** (`413 Request Entity Too Large` otherwise).
- Rate limits: `120/min` for `/api/preview`, `30/min` for `/api/convert` (per client IP). Override via your reverse proxy if you need more.
- CORS origins via `MD2CV_CORS_ORIGINS` env var (comma-separated, default `*`).
- Log level via `MD2CV_LOG_LEVEL` (default `INFO`).

## Web UI

Open `http://localhost:8000` after starting the container.

- Type Markdown on the left, see a live preview on the right.
- Pick a template and one or more output formats.
- Click **Convert & Download** — single format streams directly, multiple formats arrive as a ZIP.

## Writing Your CV

```markdown
---
name: "Jane Doe"
title: "Senior Software Engineer"
email: "jane@example.com"
phone: "+1 555 010 0101"
location: "Remote"
linkedin: "linkedin.com/in/janedoe"
github: "github.com/janedoe"
website: "janedoe.dev"
---

# Professional Summary

Backend engineer with a focus on distributed systems...

# Experience

## Senior Software Engineer
**ExampleCo** | Remote | 2022 — Present

- Migrated billing service to event-driven architecture.
- Reduced p99 API latency by 38%.

# Skills

| Area      | Tools                  |
|-----------|------------------------|
| Languages | Python, Go             |
| Cloud     | AWS, Docker, Kubernetes |
```

A complete example lives in [`examples/template_cv.md`](examples/template_cv.md).

## Templates

| Template      | Description                                |
|---------------|--------------------------------------------|
| `ats_classic` | Traditional, ATS-optimized (default)       |
| `modern`      | Contemporary with subtle accent colors     |
| `minimal`     | Clean, single-column layout                |

Adding a new template: see [CONTRIBUTING.md](CONTRIBUTING.md#adding-a-template).

## CLI

```bash
python -m app.cli my_resume.md --format all
python -m app.cli --list-templates
python -m app.cli --version
```

You can also run the CLI through the Docker image:

```bash
./md2cv.sh cli my_resume.md --format all
```

## Project Structure

```text
md2cv/
├── app/
│   ├── api/            # REST endpoints (FastAPI)
│   ├── core/           # parser, renderer, exporters, converter
│   ├── web/            # Web UI (Tabler + EasyMDE, no build step)
│   ├── cli.py          # Argparse CLI
│   └── main.py         # FastAPI app factory
├── templates/          # CV themes (HTML + CSS)
├── tests/              # unit + api + cli tests (>85% coverage)
├── Dockerfile          # multi-stage, non-root
├── docker-compose.yml
└── pyproject.toml      # pytest + coverage + black/ruff/isort config
```

## Known Limitations

DOCX export currently does **not** render nested lists, blockquotes, or horizontal rules.
PDF export uses WeasyPrint and supports the full Markdown feature set.
Both are tracked for v2.1.0.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). TL;DR:

```bash
pip install -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
pytest
```

## License

MIT — see [LICENSE](LICENSE).
