from __future__ import annotations

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import auth, credits, intel, push, subscriptions, templates

if settings.APP_ENV != "development" and settings.APP_ENV != "test":
    sentry_sdk.init(send_default_pii=True)

app = FastAPI(
    title="AI Intelligence Platform",
    description="AI情报平台后端API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(intel.router, prefix="/api/intel", tags=["Intel"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(credits.router, prefix="/api/credits", tags=["Credits"])
app.include_router(push.router, prefix="/api/push", tags=["Push"])


@app.on_event("startup")
async def on_startup() -> None:
    from backend.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
