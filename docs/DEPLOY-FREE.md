# PulseNet v4 — Free deployment

PulseNet's active web stack is **Python/Flask + HTML/CSS/vanilla JavaScript**. SQL and PHP are intentionally not required.

## Easiest local run

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r backend/python/requirements.txt
python backend/python/app.py
```

Open `http://127.0.0.1:8000`.

## Docker

```bash
docker compose up --build
```

Open `http://localhost:8000`.

The image runs as a non-root user and serves both the frontend and API from the same origin.

## Public deployment

Use HTTPS and a production WSGI server/reverse proxy. Set:

```text
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://your-frontend.example
SERVER_REGION=Your region
```

If frontend and API are same-origin, leave `CORS_ORIGINS` empty. Only set `TRUST_PROXY_HEADERS=1` when a trusted reverse proxy sanitizes `X-Forwarded-For`.

## GitHub Pages note

GitHub Pages can serve the static frontend, but it cannot run the Python API. A real speed test against PulseNet's self-hosted endpoint therefore needs a separate Python-capable host. Do not pretend a static page is connected to a backend that is not deployed.

## Cost boundary

The application does not require a paid API, database, PHP runtime or commercial SDK. Hosting, bandwidth, a domain and some cloud providers can still have independent costs.
