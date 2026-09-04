# PulseNet — Internet Speed Test ⚡

A polished, browser-based internet diagnostics project inspired by the category of tools such as Speedtest.net, but independently designed and implemented.

## Features
- Download and upload throughput tests over HTTPS
- Latency and jitter measurements
- Connection-quality score and practical advice
- Live animated gauge, progress meter, and throughput graph
- Browser connection API information when supported
- Optional public IP / ISP / region enrichment
- Local test history stored only in the browser
- Copy/share result and JSON export
- Responsive mobile/desktop UI
- Reduced-motion-friendly design
- No login, password, Wi-Fi credentials, or account system

## Accuracy
Browser speed tests measure the path between the browser and the selected test endpoint. Results can vary with Wi-Fi signal, router load, device load, browser limits, VPNs, congestion, and endpoint location. PulseNet does not guarantee an ISP's advertised speed.

## Security
PulseNet intentionally avoids collecting passwords, Wi-Fi credentials, authentication tokens, or payment information. History is stored in browser `localStorage` only.

The page includes a restrictive Content Security Policy, `no-referrer`, `frame-ancestors 'none'`, `object-src 'none'`, `form-action 'none'`, HTTPS test endpoints, cache-busting requests, and no unnecessary server-side credential handling.

**Never commit secrets.** Do not add API keys, database passwords, private tokens, certificates, `.env` files, or credentials. If a backend is added later, keep secrets in environment variables and add authentication, authorization, rate limiting, input validation, CSRF protections where applicable, secure cookies, and privacy-conscious logging.

## Technology
The current app is deliberately client-first:
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch/XHR and browser Performance APIs
- Cloudflare Speed endpoint for controlled byte transfer
- Optional IP metadata endpoint

Python, PHP, Java, and SQL are **not required** for this static browser app. Adding an unnecessary backend would increase attack surface without improving the browser's basic measurement. If a server/API is introduced later, keep it minimal and define its security boundary clearly.

## Legal / trademark note
PulseNet is an independent project and is not Speedtest.net, Ookla, or an affiliated product. Speedtest and related marks belong to their respective owners. This repository does not intentionally copy Speedtest branding, logos, proprietary code, or trade dress.

No software can honestly promise that its owner "cannot be hacked" or "cannot be sued." This project aims to reduce avoidable security risk, respect third-party services and licenses, and avoid misleading guarantees. Review deployment configuration, third-party terms, and applicable laws before commercial use.

## Run locally
Serve the folder over HTTP rather than opening the HTML file directly:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`.

## Deployment
Deploy as a static HTTPS site using GitHub Pages, Netlify, Cloudflare Pages, or another static host. Keep HTTPS enabled in production.

## Responsible use
Only test networks and devices you are authorized to use. Do not intentionally generate abusive traffic or attempt to overwhelm test infrastructure.

## License
MIT — see `LICENSE`.
