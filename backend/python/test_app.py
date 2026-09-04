import os
os.environ["CORS_ORIGINS"] = ""
from app import app


def test_health():
    client=app.test_client()
    r=client.get('/api/health')
    assert r.status_code==200
    assert r.get_json()['status']=='ok'
    assert r.headers['X-Content-Type-Options']=='nosniff'


def test_download_bounds():
    client=app.test_client()
    assert client.get('/api/download?bytes=0').status_code==400
    r=client.get('/api/download?bytes=64')
    assert r.status_code==200
    assert r.data and len(r.data)==64


def test_analyze_validation():
    client=app.test_client()
    r=client.post('/api/analyze',json={'ping':20,'jitter':3,'download':100,'upload':20,'loss':0})
    assert r.status_code==200
    assert 0 <= r.get_json()['score'] <= 100
    assert client.post('/api/analyze',json={'ping':-1}).status_code==400


def test_upload():
    client=app.test_client()
    r=client.post('/api/upload',data=b'abc')
    assert r.status_code==200
    assert r.get_json()['bytes']==3


def test_frontend_served():
    client=app.test_client()
    r=client.get('/')
    assert r.status_code==200
    assert b'PulseNet' in r.data
