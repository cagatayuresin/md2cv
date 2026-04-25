#!/usr/bin/env bash
# md2cv — Docker wrapper script.
#
# Usage:
#   ./md2cv.sh                          # Start the REST API + Web UI on :8000
#   ./md2cv.sh server [-p HOST_PORT]    # Same as above, with optional port mapping
#   ./md2cv.sh cli <args...>            # Run the CLI inside the container
#
# Examples:
#   ./md2cv.sh                          # http://localhost:8000
#   ./md2cv.sh server -p 3000           # http://localhost:3000
#   ./md2cv.sh cli my_resume.md --format all

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_NAME="${MD2CV_IMAGE:-md2cv}"

ensure_image() {
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        echo ">> Building $IMAGE_NAME image..."
        docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
    fi
}

run_server() {
    local host_port=8000
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -p|--port) host_port="$2"; shift 2 ;;
            *) echo "Unknown server arg: $1" >&2; exit 2 ;;
        esac
    done
    ensure_image
    echo ">> md2cv server on http://localhost:${host_port}"
    docker run --rm \
        -p "${host_port}:8000" \
        --name md2cv \
        "$IMAGE_NAME"
}

run_cli() {
    ensure_image
    docker run --rm \
        -v "$SCRIPT_DIR:/app/input:ro" \
        -v "$SCRIPT_DIR/templates:/app/templates:ro" \
        -v "$SCRIPT_DIR/output:/app/output" \
        --entrypoint python \
        "$IMAGE_NAME" \
        -m app.cli "$@"
}

cmd="${1:-server}"
case "$cmd" in
    server) shift || true; run_server "$@" ;;
    cli)    shift; run_cli "$@" ;;
    *)      run_server ;;
esac
