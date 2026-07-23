"""Revisionssicheres Audit-Log für jede ausgeführte Änderung.

Jede vom Executor angewandte Aktion erzeugt einen unveränderlichen Eintrag. Das
Log ist die Grundlage für die Rechenschaftspflicht nach Art. 5 Abs. 2 DSGVO und
für das nach Art. 30 DSGVO geforderte Verzeichnis von Verarbeitungstätigkeiten.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..domain import PlanAction


class AuditEntry(BaseModel):
    seq: int
    timestamp: str
    actor: str
    op: str
    phase: str
    upn: str
    display_name: str
    summary: str
    reason: str
    dsgvo_note: str | None = None
    success: bool = True
    message: str = ""


class AuditLog:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(
        self,
        action: PlanAction,
        *,
        timestamp: str,
        actor: str,
        success: bool,
        message: str,
    ) -> AuditEntry:
        entry = AuditEntry(
            seq=len(self._entries) + 1,
            timestamp=timestamp,
            actor=actor,
            op=action.op.value,
            phase=action.phase.value,
            upn=action.upn,
            display_name=action.display_name,
            summary=action.summary,
            reason=action.reason,
            dsgvo_note=action.dsgvo_note,
            success=success,
            message=message,
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def tail(self, n: int = 100) -> list[AuditEntry]:
        return self._entries[-n:]
