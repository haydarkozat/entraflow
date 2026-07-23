"""Governance-Regeln der Schule: Wer bekommt welche Lizenz und welche Gruppen?

Zentral und deklarativ – Änderungen an der Lizenzstrategie sind hier eine
Datenänderung, kein Eingriff in die Engine. Das entspricht dem Prinzip
„Policy as Data".
"""

from __future__ import annotations

from .domain import LicensePlan, Role

# --- Microsoft-365-Education-Lizenzkatalog ---------------------------------
# skuId / skuPartNumber entsprechen dem realen Microsoft-Lizenzkatalog.
# Preise: A1 ist für Bildungseinrichtungen kostenfrei; A3 ist der Referenzpreis
# für die Kostenrechnung der Lizenz-Optimierung (Bildungs-Listenpreis, EUR/Monat).
LICENSE_CATALOG: dict[str, LicensePlan] = {
    "A1_STUDENT": LicensePlan(
        sku_id="314c4481-f395-4525-be8b-2ec4bb1e9d91",
        sku_part_number="STANDARDWOFFPACK_STUDENT",
        label="Office 365 A1 for students",
        monthly_price_eur=0.0,
    ),
    "A1_FACULTY": LicensePlan(
        sku_id="94763226-9b3c-4e75-a931-5c89701abe66",
        sku_part_number="STANDARDWOFFPACK_FACULTY",
        label="Office 365 A1 for faculty",
        monthly_price_eur=0.0,
    ),
    "A3_STUDENT": LicensePlan(
        sku_id="e578b273-6db4-4691-bba0-8d691f4da603",
        sku_part_number="ENTERPRISEPACKPLUS_STUDENT",
        label="Office 365 A3 for students",
        monthly_price_eur=2.75,
    ),
    "A3_FACULTY": LicensePlan(
        sku_id="98b6e773-24d4-4c0d-a968-6e787a1f8204",
        sku_part_number="ENTERPRISEPACKPLUS_FACULTY",
        label="Office 365 A3 for faculty",
        monthly_price_eur=5.50,
    ),
}

# Primäre Lizenz je Rolle (Soll-Zuweisung beim Joiner).
ROLE_LICENSE: dict[Role, str] = {
    Role.STUDENT: "A1_STUDENT",   # SuS: kostenfreies A1
    Role.TEACHER: "A3_FACULTY",   # Lehrkräfte: A3 (volle Desktop-Apps)
    Role.STAFF: "A3_FACULTY",     # Verwaltung: A3
}

# Rollenweite Gruppen (Verteiler/Teams), die jede:r der Rolle erhält.
ROLE_GROUPS: dict[Role, list[tuple[str, str, str]]] = {
    # (displayName, mailNickname, groupType)
    Role.STUDENT: [("Alle Schüler:innen", "alle-sus", "Unified")],
    Role.TEACHER: [("Kollegium", "kollegium", "Unified")],
    Role.STAFF: [("Verwaltung", "verwaltung", "Security")],
}


def sku_id_for_role(role: Role) -> str:
    return LICENSE_CATALOG[ROLE_LICENSE[role]].sku_id


def plan_key_for_sku_id(sku_id: str) -> str | None:
    for key, plan in LICENSE_CATALOG.items():
        if plan.sku_id == sku_id:
            return key
    return None


def price_for_sku_id(sku_id: str) -> float:
    key = plan_key_for_sku_id(sku_id)
    return LICENSE_CATALOG[key].monthly_price_eur if key else 0.0


def class_group(school_class: str) -> tuple[str, str, str]:
    """Gruppe (Team) einer Klasse, z. B. Klasse 8a -> Nickname ``klasse-8a``."""
    nick = f"klasse-{school_class.lower()}"
    return (f"Klasse {school_class}", nick, "Unified")
