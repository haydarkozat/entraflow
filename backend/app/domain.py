"""Fachliche Domänenmodelle (rollen-, lizenz- und lebenszyklusbezogen).

Bewusst getrennt von den Microsoft-Graph-Ressourcen (siehe ``graph/client.py``):
Hier steht die *Soll-Welt* der Schule, dort die *Ist-Welt* des Tenants.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    STUDENT = "student"        # Schüler:in (SuS)
    TEACHER = "teacher"        # Lehrkraft
    STAFF = "staff"            # Verwaltung / Sekretariat


class DesiredUser(BaseModel):
    """Ein aus der Schulverwaltung (SchILD/ASV-Export) abgeleiteter Soll-Zustand."""

    given_name: str
    surname: str
    role: Role
    # Klassenbezeichnung, z. B. "8a"; bei Lehrkräften optional (Klassenleitung)
    school_class: str | None = None
    # Stabiler Schlüssel aus dem Quellsystem (verhindert Doppelanlage bei Namensgleichheit)
    source_id: str
    active: bool = True

    @property
    def upn_local(self) -> str:
        """Lokaler Teil des UPN: vorname.nachname, umlaut-/sonderzeichenbereinigt."""
        return f"{_slug(self.given_name)}.{_slug(self.surname)}"

    @property
    def display_name(self) -> str:
        return f"{self.given_name} {self.surname}"


class LicensePlan(BaseModel):
    """Ein Microsoft-365-Education-Plan inkl. Preis für die Kostenrechnung."""

    sku_id: str
    sku_part_number: str
    label: str
    # Monatlicher Listenpreis pro Seat in EUR (A1 = 0,00 €, kostenfrei für Bildung)
    monthly_price_eur: float = 0.0


class PlanActionType(str, Enum):
    CREATE_USER = "create_user"
    ENABLE_USER = "enable_user"
    DISABLE_USER = "disable_user"
    ASSIGN_LICENSE = "assign_license"
    REMOVE_LICENSE = "remove_license"
    ADD_TO_GROUP = "add_to_group"
    REMOVE_FROM_GROUP = "remove_from_group"
    CONVERT_TO_SHARED_MAILBOX = "convert_to_shared_mailbox"
    SCHEDULE_DELETION = "schedule_deletion"


class Phase(str, Enum):
    JOINER = "joiner"
    MOVER = "mover"
    LEAVER = "leaver"
    LICENSE = "license"      # Governance / Rückgewinnung
    COMPLIANCE = "compliance"


class PlanAction(BaseModel):
    """Eine einzelne, idempotente Änderung – vergleichbar mit einem Terraform-Plan-Eintrag."""

    op: PlanActionType
    phase: Phase
    upn: str
    display_name: str
    summary: str
    reason: str
    # Optionaler DSGVO-/Governance-Hinweis (Rechtsgrundlage, Frist, Löschkonzept …)
    dsgvo_note: str | None = None
    # Freie, op-spezifische Nutzlast (skuId, groupId, deleteAfter …)
    payload: dict = Field(default_factory=dict)


class Plan(BaseModel):
    actions: list[PlanAction] = Field(default_factory=list)
    reference_date: date

    @property
    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {p.value: 0 for p in Phase}
        for a in self.actions:
            out[a.phase.value] += 1
        out["total"] = len(self.actions)
        return out

    def by_phase(self, phase: Phase) -> list[PlanAction]:
        return [a for a in self.actions if a.phase == phase]


class ExecutionResult(BaseModel):
    action: PlanAction
    success: bool
    message: str


def _slug(value: str) -> str:
    table = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "ae", "Ö": "oe", "Ü": "ue",
        "é": "e", "è": "e", "â": "a", "î": "i",
        "ş": "s", "ı": "i", "ğ": "g", "ç": "c",  # türkische Sonderzeichen
    }
    out = "".join(table.get(ch, ch) for ch in value.strip().lower())
    return "".join(ch for ch in out if ch.isalnum() or ch == "-")
