"""Reconciliation-Planer: vergleicht Soll (Schulverwaltung) mit Ist (Tenant).

Erzeugt einen *Plan* aus idempotenten Aktionen – ganz im Sinne von ``terraform plan``:
erst sichtbar machen, was passieren würde, dann bewusst anwenden. Der Planer
schreibt nichts; er liest nur den Graphen und leitet den Delta-Plan ab.
"""

from __future__ import annotations

from datetime import timedelta

from ..config import Settings
from ..domain import DesiredUser, Phase, Plan, PlanAction, PlanActionType, Role
from ..graph.client import GraphClient, GraphUser
from ..policies import (
    LICENSE_CATALOG,
    ROLE_GROUPS,
    class_group,
    sku_id_for_role,
)

_CATALOG_SKU_IDS = {plan.sku_id for plan in LICENSE_CATALOG.values()}


class Planner:
    def __init__(self, client: GraphClient, settings: Settings) -> None:
        self._client = client
        self._s = settings

    def build_plan(self, desired: list[DesiredUser]) -> Plan:
        actions: list[PlanAction] = []
        current = self._client.list_users()
        # Nur Konten mit Herkunftsschlüssel (employeeId) werden von EntraFlow verwaltet.
        current_by_source = {u.employeeId: u for u in current if u.employeeId}
        membership = self._current_managed_membership(current)

        desired_active = {d.source_id: d for d in desired if d.active}

        for d in desired:
            if not d.active:
                continue
            existing = current_by_source.get(d.source_id)
            if existing is None:
                actions.extend(self._joiner_actions(d, current))
            else:
                actions.extend(self._mover_actions(d, existing, membership.get(existing.id, set())))

        # Leaver: verwaltete Konten, die im Quellsystem fehlen ODER dort auf aktiv=0
        # stehen. Beides ist in desired_active bereits ausgeschlossen.
        for source_id, user in current_by_source.items():
            if source_id not in desired_active:
                actions.extend(self._leaver_actions(user, membership.get(user.id, set())))

        return Plan(actions=actions, reference_date=self._s.reference_date)

    # ---- Joiner ------------------------------------------------------------
    def _joiner_actions(self, d: DesiredUser, current: list[GraphUser]) -> list[PlanAction]:
        upn = self._resolve_upn(d, current)
        acts = [
            PlanAction(
                op=PlanActionType.CREATE_USER,
                phase=Phase.JOINER,
                upn=upn,
                display_name=d.display_name,
                summary=f"Konto anlegen ({_role_label(d.role)})",
                reason=f"Im Quellsystem neu ({d.source_id}), im Tenant nicht vorhanden.",
                dsgvo_note="Datenminimierung: nur Stammdaten aus dem Schulverwaltungssystem (Art. 5 Abs. 1 lit. c DSGVO).",
                payload={
                    "employeeId": d.source_id,
                    "givenName": d.given_name,
                    "surname": d.surname,
                    "usageLocation": self._s.usage_location,
                    "role": d.role.value,
                },
            )
        ]
        sku_id = sku_id_for_role(d.role)
        acts.append(
            PlanAction(
                op=PlanActionType.ASSIGN_LICENSE,
                phase=Phase.JOINER,
                upn=upn,
                display_name=d.display_name,
                summary=f"Lizenz zuweisen: {_sku_label(sku_id)}",
                reason=f"Standardlizenz für Rolle {_role_label(d.role)}.",
                payload={"skuId": sku_id},
            )
        )
        for grp in self._desired_groups(d):
            acts.append(
                PlanAction(
                    op=PlanActionType.ADD_TO_GROUP,
                    phase=Phase.JOINER,
                    upn=upn,
                    display_name=d.display_name,
                    summary=f"In Gruppe aufnehmen: {grp[0]}",
                    reason="Rollen-/Klassenzuordnung laut Soll-Zustand.",
                    payload={"displayName": grp[0], "nickname": grp[1], "groupType": grp[2]},
                )
            )
        return acts

    # ---- Mover -------------------------------------------------------------
    def _mover_actions(self, d: DesiredUser, user: GraphUser, current_nicks: set[str]) -> list[PlanAction]:
        acts: list[PlanAction] = []
        if not user.accountEnabled:
            acts.append(
                PlanAction(
                    op=PlanActionType.ENABLE_USER,
                    phase=Phase.MOVER,
                    upn=user.userPrincipalName,
                    display_name=d.display_name,
                    summary="Konto reaktivieren",
                    reason="Im Quellsystem wieder aktiv, im Tenant deaktiviert.",
                    payload={"userId": user.id},
                )
            )

        # Lizenz an Rolle angleichen (z. B. Rollenwechsel SuS -> Verwaltung).
        desired_sku = sku_id_for_role(d.role)
        held_catalog = [l.skuId for l in user.assignedLicenses if l.skuId in _CATALOG_SKU_IDS]
        if desired_sku not in held_catalog:
            acts.append(
                PlanAction(
                    op=PlanActionType.ASSIGN_LICENSE,
                    phase=Phase.MOVER,
                    upn=user.userPrincipalName,
                    display_name=d.display_name,
                    summary=f"Lizenz angleichen: {_sku_label(desired_sku)}",
                    reason=f"Rollenlizenz fehlt für {_role_label(d.role)}.",
                    payload={"skuId": desired_sku, "userId": user.id},
                )
            )
        for held in held_catalog:
            if held != desired_sku:
                acts.append(
                    PlanAction(
                        op=PlanActionType.REMOVE_LICENSE,
                        phase=Phase.MOVER,
                        upn=user.userPrincipalName,
                        display_name=d.display_name,
                        summary=f"Nicht mehr passende Lizenz entfernen: {_sku_label(held)}",
                        reason="Nach Rollenwechsel nicht mehr vorgesehen; Seat wird frei.",
                        payload={"skuId": held, "userId": user.id},
                    )
                )

        # Gruppen (Klasse/Rolle) abgleichen – nur EntraFlow-verwaltete Gruppen.
        desired_nicks = {g[1]: g for g in self._desired_groups(d)}
        for nick, grp in desired_nicks.items():
            if nick not in current_nicks:
                acts.append(
                    PlanAction(
                        op=PlanActionType.ADD_TO_GROUP,
                        phase=Phase.MOVER,
                        upn=user.userPrincipalName,
                        display_name=d.display_name,
                        summary=f"In Gruppe aufnehmen: {grp[0]}",
                        reason="Klassen-/Rollenwechsel laut Soll-Zustand.",
                        payload={"displayName": grp[0], "nickname": nick, "groupType": grp[2], "userId": user.id},
                    )
                )
        for nick in current_nicks:
            if nick not in desired_nicks and _is_class_nick(nick):
                acts.append(
                    PlanAction(
                        op=PlanActionType.REMOVE_FROM_GROUP,
                        phase=Phase.MOVER,
                        upn=user.userPrincipalName,
                        display_name=d.display_name,
                        summary=f"Aus alter Klassen-Gruppe entfernen: {nick}",
                        reason="Klassenwechsel – alte Klassenzuordnung nicht mehr gültig.",
                        payload={"nickname": nick, "userId": user.id},
                    )
                )
        return acts

    # ---- Leaver ------------------------------------------------------------
    def _leaver_actions(self, user: GraphUser, current_nicks: set[str]) -> list[PlanAction]:
        acts: list[PlanAction] = []
        if user.accountEnabled:
            acts.append(
                PlanAction(
                    op=PlanActionType.DISABLE_USER,
                    phase=Phase.LEAVER,
                    upn=user.userPrincipalName,
                    display_name=user.displayName,
                    summary="Konto deaktivieren",
                    reason="Im Quellsystem nicht mehr geführt (Abgang/Schulwechsel).",
                    dsgvo_note="Zugriff sofort entziehen (Art. 32 DSGVO – Integrität/Vertraulichkeit).",
                    payload={"userId": user.id},
                )
            )
        for l in user.assignedLicenses:
            if l.skuId in _CATALOG_SKU_IDS:
                acts.append(
                    PlanAction(
                        op=PlanActionType.REMOVE_LICENSE,
                        phase=Phase.LEAVER,
                        upn=user.userPrincipalName,
                        display_name=user.displayName,
                        summary=f"Lizenz zurückgeben: {_sku_label(l.skuId)}",
                        reason="Abgang – Seat wird zurückgewonnen.",
                        payload={"skuId": l.skuId, "userId": user.id},
                    )
                )
        for nick in sorted(current_nicks):
            acts.append(
                PlanAction(
                    op=PlanActionType.REMOVE_FROM_GROUP,
                    phase=Phase.LEAVER,
                    upn=user.userPrincipalName,
                    display_name=user.displayName,
                    summary=f"Aus Gruppe entfernen: {nick}",
                    reason="Abgang – Mitgliedschaften bereinigen.",
                    payload={"nickname": nick, "userId": user.id},
                )
            )
        if user.mailboxType != "SharedMailbox":
            acts.append(
                PlanAction(
                    op=PlanActionType.CONVERT_TO_SHARED_MAILBOX,
                    phase=Phase.LEAVER,
                    upn=user.userPrincipalName,
                    display_name=user.displayName,
                    summary="Postfach in Shared Mailbox umwandeln",
                    reason="Geschäftliche Kontinuität ohne kostenpflichtige Lizenz.",
                    dsgvo_note="Zweckbindung: nur zur Übergabe offener Vorgänge (Art. 5 Abs. 1 lit. b DSGVO).",
                    payload={"userId": user.id},
                )
            )
        if user.deletionScheduledFor is None:
            delete_after = self._s.reference_date + timedelta(days=self._s.leaver_retention_days)
            acts.append(
                PlanAction(
                    op=PlanActionType.SCHEDULE_DELETION,
                    phase=Phase.LEAVER,
                    upn=user.userPrincipalName,
                    display_name=user.displayName,
                    summary=f"Löschung vormerken zum {delete_after.isoformat()}",
                    reason=f"Aufbewahrungsfrist {self._s.leaver_retention_days} Tage.",
                    dsgvo_note="Löschkonzept nach Art. 17 DSGVO (Recht auf Vergessenwerden).",
                    payload={"userId": user.id, "deleteAfter": delete_after.isoformat()},
                )
            )
        return acts

    # ---- Helfer ------------------------------------------------------------
    def _desired_groups(self, d: DesiredUser) -> list[tuple[str, str, str]]:
        groups = list(ROLE_GROUPS.get(d.role, []))
        if d.school_class:
            groups.append(class_group(d.school_class))
        return groups

    def _current_managed_membership(self, current: list[GraphUser]) -> dict[str, set[str]]:
        managed_nicks = _managed_role_nicks()
        result: dict[str, set[str]] = {u.id: set() for u in current}
        for g in self._client.list_groups():
            if g.mailNickname in managed_nicks or _is_class_nick(g.mailNickname):
                for uid in g.members:
                    result.setdefault(uid, set()).add(g.mailNickname)
        return result

    def _resolve_upn(self, d: DesiredUser, current: list[GraphUser]) -> str:
        base = d.upn_local
        candidate = f"{base}@{self._s.upn_domain}"
        taken = {u.userPrincipalName.lower() for u in current}
        if candidate.lower() not in taken:
            return candidate
        # Kollision (Namensgleichheit): stabilen Suffix aus der Quell-ID anhängen.
        suffix = "".join(ch for ch in d.source_id if ch.isalnum())[-3:].lower()
        return f"{base}.{suffix}@{self._s.upn_domain}"


def _managed_role_nicks() -> set[str]:
    nicks: set[str] = set()
    for groups in ROLE_GROUPS.values():
        for _, nick, _ in groups:
            nicks.add(nick)
    return nicks


def _is_class_nick(nick: str) -> bool:
    return nick.startswith("klasse-")


def _role_label(role: Role) -> str:
    return {Role.STUDENT: "Schüler:in", Role.TEACHER: "Lehrkraft", Role.STAFF: "Verwaltung"}[role]


def _sku_label(sku_id: str) -> str:
    for plan in LICENSE_CATALOG.values():
        if plan.sku_id == sku_id:
            return plan.label
    return sku_id
