# PulseNet v3 — Free deployment

PulseNet is designed so the core application can run without paid APIs or licenses.

## Frontend

The root `index.html` is static and can be served by GitHub Pages or another free static host.

## Python API

Run locally:

```bash
cd backend/python
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API is intentionally small and can also be self-hosted on a machine you control.

## Database

`database/schema.sql` contains the persistent schema. MySQL/MariaDB-compatible SQL is used by the current schema. A database is optional for the basic browser speed test.

## PHP

`backend/php/api.php` is a lightweight compatibility endpoint for PHP hosting. It is not a second copy of the Python business logic.

## Java

`backend/java/src/PulseNetHealth.java` is a dependency-free Java integration component. It can be used by a future native Android/client application without requiring a paid SDK.

## Cost boundary

Software in this repository does not require a subscription, paid API key, or commercial SDK. Hosting, bandwidth, a custom domain, or a third-party provider may still have independent pricing.
