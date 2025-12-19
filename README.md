# Jeb Bot SaaS (Evolution API + FastAPI + Next.js)

Multi-tenant dashboard where each customer can:
- Create an Evolution API instance (WhatsApp connection)
- Generate QR Code to connect their phone
- Configure a bot provider (OpenAI / Ollama / Rules) and store their tokens securely
- Receive WhatsApp messages via Evolution webhook and auto-reply

## Quick start (VPS with Docker)
1) Copy env:
```bash
cp .env.example .env
cp services/api/.env.example services/api/.env
cp apps/web/.env.example apps/web/.env.local
```

2) Edit `.env` and set:
- `DOMAIN=bot.jebmedeiros.com.br`
- `EVOLUTION_APIKEY=...` (the apikey you set for Evolution)
- `EVOLUTION_SERVER_URL=https://bot.jebmedeiros.com.br/evo` (public URL)
- `WEBHOOK_GLOBAL_URL=https://bot.jebmedeiros.com.br/api/webhooks/evolution/global`

3) Start:
```bash
docker compose up -d --build
```

4) Open:
- https://bot.jebmedeiros.com.br (web)
- https://bot.jebmedeiros.com.br/evo (Evolution API)

## Notes
- This repo ships with a minimal auth (email/password + JWT).
- Tokens (OpenAI, etc.) are encrypted at rest in Postgres using AES-GCM (key in API env).
- Evolution webhook is configured globally via env (WEBHOOK_GLOBAL_URL). See Evolution docs.
