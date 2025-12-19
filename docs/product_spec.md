# Multi-tenant Evolution WhatsApp Assistant - Product Specification

This document captures the functional and technical blueprint for a multi-tenant dashboard that orchestrates Evolution API (WhatsApp), pluggable bot providers, and chat memory.

## Goals
- Allow each customer to self-serve a dedicated Evolution API instance and connect their WhatsApp via QR code.
- Let customers choose a bot provider (OpenAI, Ollama, or rule-based) and store credentials securely.
- Provide Redis-backed conversational memory for WhatsApp chats.
- Deliver a colorful, purple-themed dashboard with clear onboarding.

## Core Use Cases
1. **Tenant onboarding**: Sign up/in with email & password, create an organization, and invite teammates.
2. **Evolution instance management**: Create, start/stop, and delete Evolution instances per tenant.
3. **QR code pairing**: Generate QR to pair a phone; show real-time status (awaiting scan, connected, expired).
4. **Bot provider setup**: Choose provider, enter tokens/urls, validate connectivity, and encrypt secrets at rest.
5. **Memory configuration**: Connect Redis, test connectivity, and enable conversation threading per WhatsApp number.
6. **Webhook handling**: Receive messages via Evolution webhook, route to the correct tenant/instance, run the bot, and auto-reply.
7. **Audit & observability**: Message logs, provider latency, webhook delivery stats, and per-tenant usage limits.

## High-level Architecture
- **Frontend (Next.js)**: Multi-tenant dashboard, purple-forward theme. Uses TRPC/REST to talk to the API.
- **Backend (FastAPI)**: Auth, tenant management, provider secrets, Redis setup, webhook receiver, and job queue triggers.
- **Evolution API service**: Runs per-tenant (isolated namespace) via docker compose with apikey per instance.
- **Redis**: Per-tenant logical DB for memory; connection info stored encrypted in Postgres.
- **Postgres**: Stores tenants, users, Evolution instances, provider configs, message logs, and audit events.
- **Queue (optional)**: Celery/RQ for async webhook handling.

## Data Model (conceptual)
- `Tenant(id, name, domain, plan, created_at)`
- `User(id, email, password_hash, tenant_id, role)`
- `EvolutionInstance(id, tenant_id, instance_key, status, webhook_url, qr_code_svg, last_sync)`
- `ProviderConfig(id, tenant_id, kind[openai|ollama|rules], display_name, secrets_encrypted, meta, enabled)`
- `RedisConfig(id, tenant_id, url, namespace, enabled, last_tested_at, status)`
- `ChatSession(id, tenant_id, whatsapp_number, provider_id, redis_config_id, thread_key)`
- `MessageLog(id, chat_session_id, direction[inbound|outbound], payload, tokens_used, latency_ms, created_at)`
- `AuditEvent(id, tenant_id, user_id, action, details, created_at)`

## API Surface (examples)
### Auth & tenants
- `POST /auth/register` — email/password signup.
- `POST /auth/login` — returns JWT.
- `GET /tenants/current` — tenant context for dashboard.
- `POST /tenants/invite` — invite teammates.

### Evolution instances
- `POST /evo/instances` — create instance; provisions apikey & webhook URL.
- `POST /evo/instances/{id}/start` — boot container/service.
- `POST /evo/instances/{id}/stop`
- `GET /evo/instances/{id}/qr` — returns QR SVG + expiry.
- `GET /evo/instances/{id}/status`

### Providers
- `PUT /providers/{id}` — upsert provider config; secrets encrypted with AES-GCM.
- `POST /providers/{id}/test` — make a sample call (OpenAI/Ollama) or rules dry-run.

### Redis memory
- `PUT /memory/redis` — save Redis URL/namespace (encrypted).
- `POST /memory/redis/test` — ping and run a sample read/write.

### Webhooks & messaging
- `POST /webhooks/evolution/global` — receives webhook, resolves tenant/instance, enqueues processing.
- `POST /messages/{chat_session_id}/send` — manual send/reply.

## Security & Secret Handling
- Secrets (provider tokens, Redis URLs, Evolution keys) encrypted with AES-GCM using a per-environment `SECRET_KEY`.
- JWT for user auth; tenant scoping enforced via middleware.
- Evolution instance keys never exposed in logs; masked in UI.
- Role-based access: Owner/Admin/Member.

## UI/UX Notes
- **Theme**: Vibrant purple primary (`#7C3AED`), gradients for headers, neon accents for call-to-action buttons, rounded cards, and glassmorphism for overlays.
- **Dashboard layout**:
  - **Getting Started** checklist with progress indicators.
  - **Evolution card**: status badge (Awaiting QR / Connected / Error), QR modal, restart/stop controls.
  - **Bot Provider card**: tabs for OpenAI, Ollama, Rules; token inputs with show/hide, connectivity test button.
  - **Memory card**: Redis URL input, namespace selector, test badge.
  - **Activity feed**: recent messages, auto-replies, and webhook health.
- **Onboarding**: guided steps with tooltips and inline docs, purple gradients, confetti on successful QR pairing.

## Webhook Processing Flow
1. Evolution sends webhook with instance key.
2. API resolves tenant & provider, loads secrets, and initializes a provider client.
3. Chat message stored in `MessageLog`; conversation state loaded from Redis (thread key per WhatsApp number).
4. Provider generates reply (or rules engine evaluates), message sent back through Evolution send API.
5. Metrics (latency, tokens) recorded for observability and billing.

## Deployment Notes
- Docker Compose already defines Postgres, Evolution, API, Web, and optional Ollama.
- Caddy handles TLS and reverse proxy; env vars provide domain/webhook URLs.
- Webhook URL configured globally via `WEBHOOK_GLOBAL_URL`; per-tenant resolution happens inside API.

## Next Steps
- Scaffold FastAPI service under `services/api` with SQLModel/SQLAlchemy models above and AES-GCM field type.
- Scaffold Next.js dashboard under `apps/web` with purple theme (Tailwind + shadcn/ui) and protected routes.
- Implement webhook processing worker and Redis integration.
- Add automated tests for provider validation and webhook routing.
