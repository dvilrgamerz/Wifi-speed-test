# PulseNet — Free-Only Stack

PulseNet can be developed, run, and self-hosted without paid APIs, paid SDKs, proprietary libraries, or required subscriptions.

## Components

- HTML/CSS/JavaScript: browser UI and measurements.
- Python + Flask: optional API/backend.
- PHP: optional shared-hosting compatibility endpoint.
- Java: optional native client/integration layer.
- SQL: open database standard; the included schema can run on free/open-source database engines.
- Git: source control.

## Cost boundary

The source code itself has no required paid service. Hosting is a separate infrastructure decision: a hosting provider may charge for compute, bandwidth, domains, or storage. A completely $0 deployment is possible only where the selected host's free allowance is sufficient and remains available under its current terms.

For a truly self-contained zero-subscription setup, run PulseNet locally or on hardware you already control. Do not assume any provider's free tier is permanent.

## No required paid APIs

PulseNet must not require a paid API key for its core speed test. Third-party metadata providers are optional and should never be required for the test to work.

## Security

"Free" does not mean insecure. Keep HTTPS, restrictive CORS, request limits, validation, secure headers, dependency updates, and secret-free frontend code enabled in production.
