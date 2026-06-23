# openclaw-aivan

OpenClaw channel-event-handler plugin for the AIVAN procurement AI (Giraffe JP).

Intercepts every inbound channel event (WeChat, Email, WhatsApp, etc.) and forwards
it to the AIVAN backend at `POST /api/skill/invoke`. AIVAN handles B-side (buyer)
and M-side (supplier) procurement workflows and returns a reply for OpenClaw to
deliver through the originating channel.

## Quick start

```bash
export AIVAN_BASE_URL=http://localhost:8000   # or GIRAFFE_API_BASE
npm install
npm run build
openclaw plugins install .
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `AIVAN_BASE_URL` | `http://localhost:8000` | AIVAN/Giraffe JP backend base URL |
| `GIRAFFE_API_BASE` | — | Alias for `AIVAN_BASE_URL` |

No WeChat, OpenClaw Gateway, or external credentials are required for CI or unit
tests. The plugin forwards events over HTTP only; credentials are managed by
OpenClaw at runtime.
