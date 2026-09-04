# PulseNet Security Policy

PulseNet is designed to minimize unnecessary attack surface. No web application can honestly guarantee that it can never be hacked.

## Security rules
- Keep secrets and database credentials server-side only.
- Use HTTPS in production.
- Restrict CORS to the deployed frontend origin.
- Keep CSP and security headers enabled at the web-server layer.
- Validate and bound every API input on the server.
- Use parameterized SQL queries only.
- Add authentication, authorization, rate limiting and CSRF protection before exposing private/admin APIs.
- Do not store Wi-Fi passwords, browser passwords or unnecessary personal data.
- Keep dependencies patched and review third-party services.

## Reporting
Please report suspected vulnerabilities privately through GitHub's security reporting mechanism when available. Do not include passwords, tokens, API keys or other secrets in a report.
