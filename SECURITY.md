# Security Policy

## Supported version

The `main` branch is the active version.

## Reporting a vulnerability

Please do not publish exploitable details in a public issue. Use GitHub's private vulnerability reporting/security-advisory mechanism when available for the repository, or contact the repository owner privately through GitHub.

When reporting, include the affected file/feature, impact, reproduction steps, and a suggested mitigation if known. Do not include passwords, tokens, private keys, or other secrets.

## Security boundaries

PulseNet is primarily a static browser application. The browser's same-origin and Content Security Policy controls are part of its security boundary. Third-party network endpoints can change independently and are not controlled by this repository.

Never add credentials or sensitive data to the frontend. Anything shipped in JavaScript can be inspected by visitors.

## Deployment checklist

- Serve the site over HTTPS.
- Keep the Content Security Policy restrictive.
- Do not add wildcard network permissions unless required.
- Do not store secrets in frontend code.
- Review third-party endpoints and their terms before production use.
- Keep dependencies minimal and updated.
- Add server-side rate limiting if a custom backend is introduced.
- Validate and authorize every server-side request if a backend is introduced.
