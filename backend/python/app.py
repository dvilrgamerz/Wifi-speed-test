from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os, time, uuid, threading
from collections import defaultdict

app = Flask(__name__)
MAX_BODY = 4096
WINDOW = 60
LIMIT = 30
MAX_SPEEDTEST_BYTES = 50 * 1024 * 1024
_hits = defaultdict(list)
_lock = threading.Lock()

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",") if x.strip()]
CORS(app, resources={r"/api/*": {"origins": origins or ["*"]}})

@app.before_request
def guard():
    if not request.path.startswith('/api/'):
        return
    if request.path == '/api/upload':
        if request.content_length and request.content_length > MAX_SPEEDTEST_BYTES:
            return jsonify(error="upload too large"), 413
    elif request.content_length and request.content_length > MAX_BODY:
        return jsonify(error="request too large"), 413
    now = time.time()
    key = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
    with _lock:
        values = [t for t in _hits[key] if now - t < WINDOW]
        if len(values) >= LIMIT:
            return jsonify(error="rate limit exceeded"), 429
        values.append(now)
        _hits[key] = values

@app.after_request
def headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "DENY"
    r.headers["Referrer-Policy"] = "no-referrer"
    r.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    r.headers["Cache-Control"] = "no-store"
    r.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return r

@app.get('/api/health')
def health():
    return jsonify(status='ok', service='pulsenet-python', version='3', timestamp=time.time())

@app.get('/api/servers')
def servers():
    return jsonify(servers=[{
        'id': 'self-hosted-python', 'name': 'PulseNet Self-Hosted',
        'region': os.getenv('SERVER_REGION', 'Local'), 'endpoint': '/api', 'active': True
    }])

@app.get('/api/download')
def download():
    raw = request.args.get('bytes', '1048576')
    try: size = int(raw)
    except ValueError: return jsonify(error='invalid bytes'), 400
    size = max(1, min(size, MAX_SPEEDTEST_BYTES))
    chunk = b'PULSENET' * 8192
    def stream():
        remaining = size
        while remaining:
            part = chunk if remaining >= len(chunk) else chunk[:remaining]
            yield part
            remaining -= len(part)
    return Response(stream(), mimetype='application/octet-stream', headers={'Content-Length': str(size), 'X-PulseNet-Test': 'download'})

@app.post('/api/upload')
def upload():
    total = 0
    while True:
        chunk = request.stream.read(1024 * 1024)
        if not chunk: break
        total += len(chunk)
        if total > MAX_SPEEDTEST_BYTES:
            return jsonify(error='upload too large'), 413
    return jsonify(bytes=total, received=True)

def score_metrics(ping, jitter, download, upload, loss):
    score=max(0,min(100,round(100-min(35,ping/4)-min(20,jitter*1.5)-min(20,loss*2)-max(0,30-min(30,download))/1.5)))
    grade='Excellent' if score>=90 else 'Very good' if score>=75 else 'Good' if score>=55 else 'Fair' if score>=35 else 'Poor'
    return score,grade

@app.post('/api/analyze')
def analyze():
    data=request.get_json(silent=True) or {}
    try: values={k:float(data.get(k,0)) for k in ('ping','jitter','download','upload','loss')}
    except (TypeError,ValueError): return jsonify(error='invalid metrics'),400
    if any(v<0 for v in values.values()) or values['ping']>60000 or values['jitter']>60000 or values['download']>100000 or values['upload']>100000 or values['loss']>100:
        return jsonify(error='metrics outside allowed range'),400
    score,grade=score_metrics(**values)
    return jsonify(score=score,grade=grade)

@app.post('/api/results/validate')
def validate_result():
    data=request.get_json(silent=True) or {}
    required=('download','upload','ping','jitter','loss')
    if any(k not in data for k in required): return jsonify(error='missing metrics'),400
    try: values={k:float(data[k]) for k in required}
    except (TypeError,ValueError): return jsonify(error='invalid metrics'),400
    if any(v<0 for v in values.values()) or values['loss']>100: return jsonify(error='invalid metric range'),400
    score,grade=score_metrics(**values)
    return jsonify(id=str(uuid.uuid4()),score=score,grade=grade,validated_at=time.time())

if __name__=='__main__': app.run(host=os.getenv('HOST','127.0.0.1'),port=int(os.getenv('PORT','8000')),debug=False)
