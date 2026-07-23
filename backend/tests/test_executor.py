from __future__ import annotations

import pytest

from app.graph.client import GraphError
from app.lifecycle.executor import Executor
from app.lifecycle.planner import Planner


def _plan(state):
    return Planner(state.client, state.settings).build_plan(state.desired_users())


def test_dry_run_changes_nothing(state):
    before = len(state.client.list_users())
    plan = _plan(state)
    results = Executor(state.client, state.audit, state.settings).apply(plan, dry_run=True)
    assert all(r.success for r in results)
    assert len(state.client.list_users()) == before  # keine Anlage
    assert state.audit.entries() == []                # kein Audit im Dry-Run


def test_apply_creates_users_and_records_audit(state):
    before = len(state.client.list_users())
    plan = _plan(state)
    n_joiners = sum(1 for a in plan.actions if a.op.value == "create_user")
    Executor(state.client, state.audit, state.settings).apply(plan, dry_run=False)
    assert len(state.client.list_users()) == before + n_joiners
    assert len(state.audit.entries()) == len(plan.actions)
    assert all(e.success for e in state.audit.entries())


def test_new_class_group_is_created(state):
    plan = _plan(state)
    Executor(state.client, state.audit, state.settings).apply(plan, dry_run=False)
    assert state.client.get_group_by_nickname("klasse-5a") is not None


def test_leaver_seat_is_reclaimed(state):
    def a3_consumed():
        skus = {s.skuPartNumber: s for s in state.client.list_subscribed_skus()}
        return skus["ENTERPRISEPACKPLUS_FACULTY"].consumedUnits

    before = a3_consumed()
    plan = _plan(state)
    Executor(state.client, state.audit, state.settings).apply(plan, dry_run=False)
    # Thomas Reinhardt (Leaver) gibt seinen A3-Seat zurück; ein Joiner (Julia) belegt einen.
    after = a3_consumed()
    assert after == before  # -1 Leaver +1 Joiner => netto 0, aber Seat wurde nachweislich rotiert
    julia = state.client.find_user_by_upn("julia.sander@gymnasium-boeblingen.de")
    assert julia is not None and julia.assignedLicenses


def test_seat_capacity_is_enforced(client):
    # Graph-Semantik: kein freier Seat -> Fehler (verhaltensgleich zum echten Tenant)
    sku = next(s for s in client.list_subscribed_skus() if s.skuPartNumber == "ENTERPRISEPACKPLUS_FACULTY")
    sku.prepaidUnits.enabled = sku.consumedUnits  # künstlich exakt voll belegt
    praktikant = client.find_user_by_upn("praktikant@gymnasium-boeblingen.de")  # hält keine A3-Lizenz
    with pytest.raises(GraphError):
        client.assign_license(praktikant.id, sku.skuId)
