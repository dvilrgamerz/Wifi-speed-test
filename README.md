# PulseNet v4 — Internet Diagnostics ⚡

PulseNet is a free, privacy-first browser speed test and connection diagnostics platform. The current web stack is intentionally simple: **HTML + CSS + vanilla JavaScript + Python/Flask**. SQL and PHP are removed from the active architecture.

## What works
- Live download and upload measurement against the self-hosted Python endpoint
- Repeated latency probes with jitter and packet-loss estimation
- Server-side metric validation and connection quality score
- Gaming, streaming and video-call grades
- Browser network information when the browser exposes it
- Local test history (up to 30 results)
- Copy result and JSON export
- Native share support where available
- Responsive mobile/desktop UI
- PWA manifest/service worker
- Security headers, request limits and rate limiting
- Docker deployment
- Automated Python regression tests and CI

## Architecture

```text
PulseNet
├── index.html                 # accessible app shell
├── assets/
│   ├── styles.css             # responsive UI
│   └── app.js                 # speed-test engine + dashboard
├── backend/python/
│   ├── app.py                 # Flask API + static frontend server
│   ├── requirements.txt
│   └── test_app.py
├── backend/java/              # optional future native integration
├── Dockerfile
└── docker-compose.yml
```

There is **no SQL database and no PHP runtime** in the active web application. Results are intentionally stored only in the user's browser.

## Run locally

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r backend/python/requirements.txt
python backend/python/app.py
```

Open `http://127.0.0.1:8000`.

### Run tests

```bash
python -m pip install pytest
cd backend/python
pytest -q
```

### Docker

```bash
docker compose up --build
```

Then open `http://localhost:8000`.

## Configuration

Use `backend/.env.example` as a reference. Important environment variables include:

- `HOST` — bind address; use `0.0.0.0` in a container.
- `PORT` — HTTP port, default `8000`.
- `CORS_ORIGINS` — optional explicit origins for a separately hosted frontend. Same-origin deployment does not need CORS.
- `TRUST_PROXY_HEADERS=1` — only when running behind a trusted reverse proxy that correctly sanitizes forwarding headers.
- `RATE_LIMIT` / `RATE_WINDOW_SECONDS` — API rate-limit controls.
- `MAX_SPEEDTEST_BYTES` — maximum single speed-test transfer.

## Security

No application can honestly guarantee that it is impossible to hack. PulseNet reduces avoidable risk through a small attack surface, no database credentials, no PHP runtime, bounded request sizes, rate limiting, strict browser CSP, security headers, non-root Docker execution and automated tests.

For public deployment:
1. Put the service behind HTTPS.
2. Keep `CORS_ORIGINS` explicit if cross-origin access is required.
3. Only enable `TRUST_PROXY_HEADERS` behind a trusted proxy.
4. Use a production WSGI server/reverse proxy rather than Flask's development server for serious public traffic.
5. Keep dependencies updated and never commit secrets.
6. Monitor abuse because a public speed-test endpoint can consume bandwidth.

## Accuracy and privacy

Speed results are estimates of the browser-to-test-server path. Wi-Fi conditions, router load, device performance, VPNs, congestion and endpoint distance can change results. A normal website cannot reliably read Wi-Fi passwords, router administration data, channel information or signal strength.

PulseNet does not ask for Wi-Fi credentials and does not require an account. History is local browser storage. The optional public-IP/ISP enrichment from earlier versions is intentionally not part of the new core test path.

## Free deployment

The software and its dependencies can be used without paid APIs. Hosting, a custom domain, bandwidth and some cloud providers may still have independent costs; the project does not require a paid API or database to run.

See `docs/DEPLOY-FREE.md` for deployment guidance.

## Legal / responsible use

PulseNet is an independent project and is not affiliated with Ookla or Speedtest. Only test networks and infrastructure you are authorized to test. Review the terms of any hosting provider and applicable laws before public/commercial deployment.

## License

MIT — see `LICENSE`.
