from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import auth, evolution, memory, messages, providers, tenants, webhooks

app = FastAPI(title="Jeb Bot SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(evolution.router)
app.include_router(providers.router)
app.include_router(memory.router)
app.include_router(webhooks.router)
app.include_router(messages.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def health():
    return {"status": "ok"}
