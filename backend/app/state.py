"""Verdrahtung der Anwendung: Graph-Client, Dienste und Demo-Zustand.

Hält den Graph-Client (Mock oder echt) sowie das Audit-Log und stellt die
Fachdienste bereit. Der Soll-Zustand wird aus den beigelegten CSV-Exporten
gelesen; ``reset()`` stellt den Demo-Tenant wieder her.
"""

from __future__ import annotations

from .compliance.audit import AuditLog
from .compliance.dsgvo import DsgvoReporter
from .config import SEED_DIR, Settings, settings as default_settings
from .domain import DesiredUser
from .graph.memory import InMemoryGraphClient
from .licensing.optimizer import LicenseOptimizer
from .lifecycle.executor import Executor
from .lifecycle.planner import Planner
from .sources.csv_source import load_desired_from_csv


class AppState:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.audit = AuditLog()
        self._client = self._build_client()

    def _build_client(self):
        if self.settings.graph_mode == "graph":
            from .graph.http_client import HttpGraphClient

            return HttpGraphClient(self.settings)
        return InMemoryGraphClient.from_seed(SEED_DIR / "tenant_seed.json")

    def reset(self) -> None:
        """Demo-Tenant und Audit-Log zurücksetzen (nur Mock-Modus)."""
        self.audit = AuditLog()
        self._client = self._build_client()

    @property
    def client(self):
        return self._client

    def desired_users(self) -> list[DesiredUser]:
        users: list[DesiredUser] = []
        for name in ("schueler.csv", "lehrkraefte.csv"):
            path = SEED_DIR / name
            if path.exists():
                users.extend(load_desired_from_csv(path))
        return users

    # Fachdienste (frisch instanziiert – zustandslos bis auf Client/Audit)
    def planner(self) -> Planner:
        return Planner(self._client, self.settings)

    def executor(self) -> Executor:
        return Executor(self._client, self.audit, self.settings)

    def optimizer(self) -> LicenseOptimizer:
        return LicenseOptimizer(self._client, self.settings)

    def dsgvo(self) -> DsgvoReporter:
        return DsgvoReporter(self._client, self.settings)


app_state = AppState(default_settings)
