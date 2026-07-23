"""Wendet einen Plan gegen den Graphen an – Aktion für Aktion, mit Audit-Eintrag.

Trennung von Planung und Anwendung ist Absicht: Der Planer ist rein lesend und
gefahrlos wiederholbar; erst der Executor schreibt. ``dry_run=True`` liefert das
erwartete Ergebnis, ohne den Tenant zu verändern.
"""

from __future__ import annotations

from ..compliance.audit import AuditLog
from ..config import Settings
from ..domain import ExecutionResult, Plan, PlanAction, PlanActionType
from ..graph.client import GraphClient, GraphError, GraphUser


class Executor:
    def __init__(self, client: GraphClient, audit: AuditLog, settings: Settings) -> None:
        self._client = client
        self._audit = audit
        self._s = settings

    def apply(self, plan: Plan, *, dry_run: bool = False, actor: str = "entraflow-service") -> list[ExecutionResult]:
        results: list[ExecutionResult] = []
        # Innerhalb eines Plans neu angelegte Konten müssen für Folgeaktionen auflösbar sein.
        created_upn_to_id: dict[str, str] = {}
        ts = f"{self._s.reference_date.isoformat()}T00:00:00Z"

        for action in plan.actions:
            if dry_run:
                results.append(ExecutionResult(action=action, success=True, message="geplant (dry-run)"))
                continue
            try:
                message = self._apply_one(action, created_upn_to_id)
                success = True
            except GraphError as exc:
                message = f"Fehler: {exc}"
                success = False
            results.append(ExecutionResult(action=action, success=success, message=message))
            self._audit.record(action, timestamp=ts, actor=actor, success=success, message=message)
        return results

    def _apply_one(self, action: PlanAction, created: dict[str, str]) -> str:
        op = action.op
        p = action.payload

        if op == PlanActionType.CREATE_USER:
            user = GraphUser(
                id="",
                userPrincipalName=action.upn,
                displayName=action.display_name,
                givenName=p.get("givenName"),
                surname=p.get("surname"),
                accountEnabled=True,
                usageLocation=p.get("usageLocation", self._s.usage_location),
                employeeId=p.get("employeeId"),
                userType="Member",
                createdDateTime=f"{self._s.reference_date.isoformat()}T00:00:00Z",
            )
            created_user = self._client.create_user(user)
            created[action.upn.lower()] = created_user.id
            return f"Konto angelegt: {created_user.id}"

        user_id = self._resolve_user_id(action, created)

        if op == PlanActionType.ENABLE_USER:
            self._client.set_account_enabled(user_id, True)
            return "Konto aktiviert"
        if op == PlanActionType.DISABLE_USER:
            self._client.set_account_enabled(user_id, False)
            return "Konto deaktiviert"
        if op == PlanActionType.ASSIGN_LICENSE:
            self._client.assign_license(user_id, p["skuId"])
            return f"Lizenz zugewiesen: {p['skuId']}"
        if op == PlanActionType.REMOVE_LICENSE:
            self._client.remove_license(user_id, p["skuId"])
            return f"Lizenz entfernt: {p['skuId']}"
        if op == PlanActionType.ADD_TO_GROUP:
            group = self._client.ensure_group(p["displayName"], p["nickname"], p.get("groupType", "Unified"))
            self._client.add_member(group.id, user_id)
            return f"Aufgenommen in {p['nickname']}"
        if op == PlanActionType.REMOVE_FROM_GROUP:
            group = self._client.get_group_by_nickname(p["nickname"])
            if group:
                self._client.remove_member(group.id, user_id)
            return f"Entfernt aus {p['nickname']}"
        if op == PlanActionType.CONVERT_TO_SHARED_MAILBOX:
            self._client.convert_to_shared_mailbox(user_id)
            return "In Shared Mailbox umgewandelt"
        if op == PlanActionType.SCHEDULE_DELETION:
            self._client.schedule_deletion(user_id, p["deleteAfter"])
            return f"Löschung vorgemerkt zum {p['deleteAfter']}"

        raise GraphError(f"Unbekannte Operation: {op}")

    def _resolve_user_id(self, action: PlanAction, created: dict[str, str]) -> str:
        if "userId" in action.payload:
            return action.payload["userId"]
        if action.upn.lower() in created:
            return created[action.upn.lower()]
        user = self._client.find_user_by_upn(action.upn)
        if not user:
            raise GraphError(f"Nutzer nicht auflösbar: {action.upn}")
        return user.id
