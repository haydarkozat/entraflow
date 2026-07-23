"""HTTP-API von EntraFlow (FastAPI)."""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter
from pydantic import BaseModel

from .domain import Plan
from .sources.csv_source import load_desired_from_text
from .state import app_state

router = APIRouter(prefix="/api")


class ApplyRequest(BaseModel):
    dry_run: bool = True
    actor: str = "entraflow-service"
    # Optionaler CSV-Override (Semikolon-getrennt); sonst werden die Seed-Exporte genutzt.
    csv: str | None = None


class ResetResponse(BaseModel):
    ok: bool
    message: str


def _desired():
    return app_state.desired_users()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "graph_mode": app_state.settings.graph_mode}


@router.get("/tenant/summary")
def tenant_summary() -> dict:
    client = app_state.client
    users = client.list_users()
    roles = Counter()
    for u in users:
        if u.userType == "SharedMailbox":
            roles["shared"] += 1
        elif u.employeeId and u.employeeId.startswith("S-"):
            roles["student"] += 1
        elif u.employeeId and u.employeeId.startswith("L-"):
            roles["teacher"] += 1
        elif u.employeeId and u.employeeId.startswith("V-"):
            roles["staff"] += 1
        else:
            roles["unmanaged"] += 1
    skus = [
        {
            "skuPartNumber": s.skuPartNumber,
            "capacity": s.prepaidUnits.enabled,
            "consumed": s.consumedUnits,
            "available": s.prepaidUnits.enabled - s.consumedUnits,
        }
        for s in client.list_subscribed_skus()
    ]
    return {
        "reference_date": app_state.settings.reference_date.isoformat(),
        "upn_domain": app_state.settings.upn_domain,
        "total_users": len(users),
        "enabled_users": sum(1 for u in users if u.accountEnabled),
        "roles": dict(roles),
        "groups": len(client.list_groups()),
        "skus": skus,
    }


@router.get("/users")
def list_users() -> list[dict]:
    out = []
    for u in app_state.client.list_users():
        out.append({
            "id": u.id,
            "userPrincipalName": u.userPrincipalName,
            "displayName": u.displayName,
            "accountEnabled": u.accountEnabled,
            "employeeId": u.employeeId,
            "userType": u.userType,
            "licenses": [l.skuId for l in u.assignedLicenses],
            "lastSignIn": u.signInActivity.lastSignInDateTime if u.signInActivity else None,
            "deletionScheduledFor": u.deletionScheduledFor,
        })
    return out


@router.post("/plan", response_model=Plan)
def build_plan(body: ApplyRequest | None = None) -> Plan:
    desired = load_desired_from_text(body.csv) if body and body.csv else _desired()
    return app_state.planner().build_plan(desired)


@router.post("/apply")
def apply(body: ApplyRequest) -> dict:
    desired = load_desired_from_text(body.csv) if body.csv else _desired()
    plan = app_state.planner().build_plan(desired)
    results = app_state.executor().apply(plan, dry_run=body.dry_run, actor=body.actor)
    return {
        "dry_run": body.dry_run,
        "planned": plan.counts,
        "applied": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [
            {"op": r.action.op.value, "phase": r.action.phase.value, "upn": r.action.upn,
             "summary": r.action.summary, "success": r.success, "message": r.message}
            for r in results
        ],
    }


@router.get("/licenses/optimize")
def optimize() -> dict:
    return app_state.optimizer().analyze().model_dump()


@router.get("/compliance/dsgvo")
def dsgvo() -> dict:
    report = app_state.dsgvo().report()
    data = report.model_dump()
    data["score"] = report.score
    return data


@router.get("/audit")
def audit(limit: int = 200) -> list[dict]:
    return [e.model_dump() for e in app_state.audit.tail(limit)]


@router.post("/reset", response_model=ResetResponse)
def reset() -> ResetResponse:
    app_state.reset()
    return ResetResponse(ok=True, message="Demo-Tenant zurückgesetzt.")
