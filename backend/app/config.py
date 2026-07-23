"""Zentrale Konfiguration für EntraFlow.

Alle Werte lassen sich per Umgebungsvariable überschreiben. Der Schalter
``GRAPH_MODE`` entscheidet, ob gegen den mitgelieferten In-Memory-Graph-Mock
oder gegen einen echten Microsoft-365-Tenant gearbeitet wird.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEED_DIR = BASE_DIR / "seed"


@dataclass(frozen=True)
class Settings:
    # "memory" -> mitgelieferter Graph-Mock; "graph" -> echter Tenant via httpx/MSAL
    graph_mode: str = os.getenv("GRAPH_MODE", "memory")

    # Nur relevant für graph_mode == "graph"
    tenant_id: str = os.getenv("MS_TENANT_ID", "")
    client_id: str = os.getenv("MS_CLIENT_ID", "")
    client_secret: str = os.getenv("MS_CLIENT_SECRET", "")
    graph_base_url: str = os.getenv("GRAPH_BASE_URL", "https://graph.microsoft.com/v1.0")

    # UPN-/Domänenkonvention der Schule
    upn_domain: str = os.getenv("UPN_DOMAIN", "gymnasium-boeblingen.de")
    usage_location: str = os.getenv("USAGE_LOCATION", "DE")

    # DSGVO: Aufbewahrungsfrist (Tage) für Konten von Abgänger:innen (Art. 17 – Löschkonzept)
    leaver_retention_days: int = int(os.getenv("LEAVER_RETENTION_DAYS", "30"))
    # Inaktivitätsschwelle (Tage) für die Lizenz-Rückgewinnung
    inactivity_threshold_days: int = int(os.getenv("INACTIVITY_THRESHOLD_DAYS", "90"))

    # Fixer Stichtag macht Planung/Optimierung deterministisch (Demo & Tests).
    # In Produktion via REFERENCE_DATE="" auf das aktuelle Datum umstellen.
    reference_date_iso: str = os.getenv("REFERENCE_DATE", "2026-07-23")

    @property
    def reference_date(self) -> date:
        if self.reference_date_iso:
            return date.fromisoformat(self.reference_date_iso)
        return date.today()


settings = Settings()
