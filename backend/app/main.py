"""EntraFlow – FastAPI-Einstiegspunkt."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router

app = FastAPI(
    title="EntraFlow",
    version="1.0.0",
    description=(
        "Automatisierter Microsoft-365-/Entra-ID-Lebenszyklus für Schulen: "
        "Joiner-Mover-Leaver, Lizenz-Governance und DSGVO-Berichte."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"service": "EntraFlow", "docs": "/docs", "api": "/api"}
