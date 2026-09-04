from flask import Flask, jsonify, request
from flask_cors import CORS
import os, time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})
MAX_BODY = 4096

@app.before_request
def guard():
    if request.content_length and request.content_length > MAX_BODY:
        return jsonify(error="request too large"), 413

@app.after_request
def headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "DENY"
    r.headers["Referrer-Policy"] = "no-referrer"
    r.headers["Cache-Control"] = "no-store"
    return r

@app.get("/api/health")
def health():
    return jsonify(status="ok", service="pulsenet-python", timestamp=time.time())

@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    try:
        ping=float(data.get("ping",0)); jitter=float(data.get("jitter",0)); down=float(data.get("download",0)); up=float(data.get("upload",0)); loss=float(data.get("loss",0))
    except (TypeError, ValueError):
        return jsonify(error="invalid metrics"),400
    if min(ping,jitter,down,up,loss) < 0 or max(ping, jitter) > 60000 or down > 100000 or up > 100000 or loss > 100:
        return jsonify(error="metrics outside allowed range"),400
    score=max(0,min(100,round(100-min(35,ping/4)-min(20,jitter*1.5)-min(20,loss*2)-max(0,30-min(30,down))/1.5)))
    return jsonify(score=score, grade="Excellent" if score>=90 else "Very good" if score>=75 else "Good" if score>=55 else "Fair" if score>=35 else "Poor")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8000")), debug=False)
