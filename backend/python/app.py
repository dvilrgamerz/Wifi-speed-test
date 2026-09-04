from __future__ import annotations

import os
import secrets
import threading
import time
from collections import defaultdict
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

ROOT = Path(__file__).resolve().parents[2]
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
MAX_BODY = int(os.getenv("MAX_BODY_BYTES", "8192"))
MAX_SPEEDTEST_BYTES = int(os.getenv("MAX_SPEEDTEST_BYTES", str(50 * 1024 * 1024)))
RATE_WINDOW = int(os.getenv("RATE_WINDOW_SECONDS", "60"))
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "40"))
ALLOW_CORS = os.getenv("CORS_ORIGINS", "").strip()

_hits: dict[str, list[float]] = defaultdict(list)
_lock = threading.Lock()
PAYLOAD = secrets.token_bytes(1024 * 1024)

if ALLOW_CORS:
    CORS(app, resources={r"/api/*": {"origins": [x.strip() for x in ALLOW_CORS.split(",") if x.strip()]}})


def client_key() -> str:
    # Do not trust spoofable forwarding headers unless the deployment explicitly enables proxy mode.
    if os.getenv("TRUST_PROXY_HEADERS", "0") == "1":
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


@app.before_request
def guard():
    if not request.path.startswith("/api/"):
        return None
    if request.content_length:
        limit = MAX_SPEEDTEST_BYTES if request.path == "/api/upload" else MAX_BODY
        if request.content_length > limit:
            return jsonify(error="request too large"), 413
    now = time.monotonic()
    key = client_key()
    with _lock:
        values = [t for t in _hits[key] if now - t < RATE_WINDOW]
        if len(values) >= RATE_LIMIT:
            return jsonify(error="rate limit exceeded"), 429
        values.append(now)
        _hits[key] = values
        if len(_hits) > 10000:
            for k in list(_hits)[:1000]:
                if not _hits[k]:
                    _hits.pop(k, None)
    return None


@app.after_request
def headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-PulseNet-Version"] = "4"
    if request.path.startswith("/api/"):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok", service="pulsenet-python", version="4", timestamp=time.time())


@app.get("/api/servers")
def servers():
    return jsonify(servers=[{
        "id": "self-hosted-python",
        "name": "PulseNet Self-Hosted",
        "region": os.getenv("SERVER_REGION", "Local"),
        "endpoint": "/api",
        "active": True,
    }])


@app.get("/api/download")
def download():
    try:
        size = int(request.args.get("bytes", "1048576"))
    except ValueError:
        return jsonify(error="invalid bytes"), 400
    if size < 1:
        return jsonify(error="bytes must be positive"), 400
    size = min(size, MAX_SPEEDTEST_BYTES)

    def stream():
        remaining = size
        while remaining:
            part_size = min(remaining, len(PAYLOAD))
            yield PAYLOAD[:part_size]
            remaining -= part_size

    return Response(stream(), mimetype="application/octet-stream", headers={
        "Content-Length": str(size),
        "Cache-Control": "no-store, no-transform",
        "X-Accel-Buffering": "no",
        "X-PulseNet-Test": "download",
    })


@app.post("/api/upload")
def upload():
    total = 0
    while True:
        chunk = request.stream.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_SPEEDTEST_BYTES:
            return jsonify(error="upload too large"), 413
    return jsonify(bytes=total, received=True)


def score_metrics(ping: float, jitter: float, download: float, upload: float, loss: float):
    score = max(0, min(100, round(
        100 - min(35, ping / 4) - min(20, jitter * 1.5)
        - min(20, loss * 2) - max(0, 30 - min(30, download)) / 1.5
    )))
    grade = (
        "Excellent" if score >= 90 else "Very good" if score >= 75 else
        "Good" if score >= 55 else "Fair" if score >= 35 else "Poor"
    )
    return score, grade


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    try:
        values = {k: float(data.get(k, 0)) for k in ("ping", "jitter", "download", "upload", "loss")}
    except (TypeError, ValueError):
        return jsonify(error="invalid metrics"), 400
    if any(v < 0 for v in values.values()) or values["ping"] > 60000 or values["jitter"] > 60000 or values["download"] > 100000 or values["upload"] > 100000 or values["loss"] > 100:
        return jsonify(error="metrics outside allowed range"), 400
    score, grade = score_metrics(**values)
    return jsonify(score=score, grade=grade)


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="request too large"), 413


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")), debug=False)
