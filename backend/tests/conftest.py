from __future__ import annotations

import pytest

from app.config import SEED_DIR, Settings
from app.graph.memory import InMemoryGraphClient
from app.state import AppState


@pytest.fixture
def settings() -> Settings:
    # Fixer Stichtag -> deterministische Planung/Optimierung.
    return Settings(reference_date_iso="2026-07-23", upn_domain="gymnasium-boeblingen.de")


@pytest.fixture
def client() -> InMemoryGraphClient:
    return InMemoryGraphClient.from_seed(SEED_DIR / "tenant_seed.json")


@pytest.fixture
def state(settings) -> AppState:
    return AppState(settings)
