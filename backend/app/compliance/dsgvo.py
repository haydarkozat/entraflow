"""DSGVO-Berichte: Zugriffsübersicht, Datenminimierung und Löschkonzept.

Bündelt die Nachweise, die eine Schule / ein Schulträger gegenüber der oder dem
Datenschutzbeauftragten erbringen muss – aus dem tatsächlichen Tenant-Zustand
abgeleitet, nicht aus einer Excel-Tabelle.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from ..config import Settings
from ..graph.client import GraphClient
from ..licensing.optimizer import _is_catalog


class GroupAccess(BaseModel):
    group: str
    nickname: str
    member_count: int
    members: list[str]  # displayName-Liste


class Finding(BaseModel):
    severity: str        # hoch | mittel | niedrig
    category: str
    upn: str
    display_name: str
    detail: str
    article: str         # relevanter DSGVO-Artikel


class DsgvoReport(BaseModel):
    reference_date: date
    processing_records: int          # Anzahl verwalteter Konten (Verzeichnis Art. 30)
    access_overview: list[GroupAccess] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    deletions_due: list[Finding] = Field(default_factory=list)

    @property
    def score(self) -> int:
        """Grobe Ampel 0–100: je weniger offene Befunde je Konto, desto höher."""
        if self.processing_records == 0:
            return 100
        weight = {"hoch": 3, "mittel": 2, "niedrig": 1}
        penalty = sum(weight.get(f.severity, 1) for f in self.findings)
        raw = 100 - int(100 * penalty / max(self.processing_records, 1))
        return max(0, min(100, raw))


class DsgvoReporter:
    def __init__(self, client: GraphClient, settings: Settings) -> None:
        self._client = client
        self._s = settings

    def report(self) -> DsgvoReport:
        users = self._client.list_users()
        by_id = {u.id: u for u in users}
        managed = [u for u in users if u.employeeId]

        access = []
        for g in self._client.list_groups():
            names = [by_id[m].displayName for m in g.members if m in by_id]
            access.append(
                GroupAccess(group=g.displayName, nickname=g.mailNickname,
                            member_count=len(names), members=sorted(names))
            )
        access.sort(key=lambda a: a.nickname)

        findings: list[Finding] = []
        deletions: list[Finding] = []
        ref = self._s.reference_date

        for u in users:
            has_catalog = any(_is_catalog(l.skuId) for l in u.assignedLicenses)

            # Datenminimierung: deaktiviert, aber weiterhin lizenziert.
            if not u.accountEnabled and has_catalog:
                findings.append(Finding(
                    severity="mittel", category="Datenminimierung",
                    upn=u.userPrincipalName, display_name=u.displayName,
                    detail="Deaktiviertes Konto hält noch eine Lizenz.",
                    article="Art. 5 Abs. 1 lit. c (Datenminimierung)",
                ))

            # Herrenlose Konten: keine Herkunft im Quellsystem (employeeId fehlt).
            if not u.employeeId and u.userType == "Member":
                findings.append(Finding(
                    severity="hoch", category="Rechenschaftspflicht",
                    upn=u.userPrincipalName, display_name=u.displayName,
                    detail="Konto ohne Herkunftsschlüssel – keine nachvollziehbare Grundlage.",
                    article="Art. 5 Abs. 2 (Rechenschaftspflicht)",
                ))

            # Löschkonzept: Frist erreicht -> zur Löschung fällig.
            if u.deletionScheduledFor:
                try:
                    due = date.fromisoformat(u.deletionScheduledFor[:10])
                except ValueError:
                    due = None
                if due and due <= ref:
                    deletions.append(Finding(
                        severity="hoch", category="Löschkonzept",
                        upn=u.userPrincipalName, display_name=u.displayName,
                        detail=f"Aufbewahrungsfrist am {due.isoformat()} abgelaufen – Löschung fällig.",
                        article="Art. 17 (Recht auf Vergessenwerden)",
                    ))

        return DsgvoReport(
            reference_date=ref,
            processing_records=len(managed),
            access_overview=access,
            findings=findings,
            deletions_due=deletions,
        )
