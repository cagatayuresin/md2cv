# syntax=docker/dockerfile:1.6

# --- Stage 1: builder -----------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# --- Stage 2: runtime -----------------------------------------------------
FROM python:3.11-slim AS runtime

ARG VERSION=2.0.0
LABEL org.opencontainers.image.title="md2cv" \
      org.opencontainers.image.description="Convert Markdown CVs to ATS-friendly PDF and DOCX." \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.source="https://github.com/cagatayuresin/md2cv" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# WeasyPrint native dependencies + sane fallback fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        libcairo2 \
        libglib2.0-0 \
        fonts-liberation \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 md2cv

WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=md2cv:md2cv app/ ./app/
COPY --chown=md2cv:md2cv templates/ ./templates/

USER md2cv

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import sys, urllib.request; \
sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health', timeout=3).status == 200 else 1)"

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
