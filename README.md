# PulseNet v3 — Full-Stack Internet Diagnostics ⚡

PulseNet v3 evolves the browser speed test into a full-stack diagnostics platform while keeping the frontend fast and privacy-conscious.

## Architecture

```text
PulseNet v3
├── Frontend: HTML5 + CSS3 + Vanilla JavaScript
├── Python API: Flask diagnostics / health / scoring
├── PHP API: lightweight compatibility endpoint
├── SQL: test results, server registry, service events
└── Java: native integration/health model for future clients
```

## Dashboard
- Live download and upload throughput
- Latency, jitter and packet-loss sampling
- Connection quality score
- Gaming / streaming / video-call grades
- Browser network intelligence
- Public IP / ISP / region enrichment
- Test history and trends
- Share, copy and JSON export
- Server/connection status
- Responsive premium dashboard
- Settings and diagnostics explanations

## Backend
The Python service in `backend/python/` exposes `/api/health` and `/api/analyze`. It validates metric ranges, uses production-safe defaults, limits request bodies and sends defensive headers.

The PHP service in `backend/php/` provides a small compatibility health endpoint. It does not store credentials or accept arbitrary server-side commands.

The SQL schema in `database/schema.sql` defines speed-test results, test servers and service events. Production database access must use parameterized queries and least-privilege credentials.

The Java source in `backend/java/` is intentionally lightweight: Java is useful for a future Android/native companion, not as an unnecessary web-server dependency.

## Security
No application can honestly guarantee that it is impossible to hack. PulseNet reduces avoidable risk by keeping secrets out of the frontend, bounding API input, using security headers, limiting the backend surface and documenting a secure deployment boundary.

Before production backend exposure, configure HTTPS, strict CORS, authentication/authorization for private endpoints, rate limiting, CSRF protection where applicable, secure cookies, parameterized SQL, dependency updates, monitoring and least-privilege database access.

**Never commit `.env` files, passwords, API keys, private keys or tokens.** Use `backend/.env.example` as a template only.

## Technology
HTML5, CSS3, JavaScript, Python/Flask, PHP, SQL and Java are now represented with a real role in the architecture. The browser remains responsible for the actual controlled network measurement because it measures the user's browser-to-test-endpoint path.

## Accuracy
Results are estimates. Wi-Fi conditions, router load, device performance, VPNs, congestion, browser limits and endpoint distance can all affect measurements.

## Legal / responsible use
PulseNet is independently designed and is not affiliated with Ookla or Speedtest. It does not intentionally copy proprietary code or branding. Review third-party service terms and applicable laws before commercial deployment. Only test networks and infrastructure you are authorized to test.

## Local development
Frontend:

```bash
python -m http.server 8000
```

Python API:

```bash
cd backend/python
python -m venv .venv
# activate .venv, then:
pip install -r requirements.txt
python app.py
```

For production, put the Python/PHP services behind a properly configured HTTPS reverse proxy and firewall. Do not expose development servers directly to the public internet.

## License
MIT — see `LICENSE`.
