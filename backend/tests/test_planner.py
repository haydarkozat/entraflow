from __future__ import annotations

from app.domain import Phase, PlanActionType
from app.lifecycle.planner import Planner


def _plan(state):
    return Planner(state.client, state.settings).build_plan(state.desired_users())


def test_joiners_create_new_students_and_teacher(state):
    plan = _plan(state)
    created = {a.display_name for a in plan.actions if a.op == PlanActionType.CREATE_USER}
    assert {"Noah Kellermann", "Sophie Grünwald", "Ali Yıldız", "Julia Sander"} <= created


def test_joiner_gets_license_and_groups(state):
    plan = _plan(state)
    noah = [a for a in plan.actions if a.display_name == "Noah Kellermann"]
    ops = {a.op for a in noah}
    assert PlanActionType.CREATE_USER in ops
    assert PlanActionType.ASSIGN_LICENSE in ops
    # neue Klasse 5a + rollenweite Gruppe
    nicks = {a.payload.get("nickname") for a in noah if a.op == PlanActionType.ADD_TO_GROUP}
    assert nicks == {"klasse-5a", "alle-sus"}


def test_mover_changes_class_group(state):
    plan = _plan(state)
    mia = [a for a in plan.actions if a.display_name == "Mia Ostermann"]
    assert any(a.op == PlanActionType.ADD_TO_GROUP and a.payload["nickname"] == "klasse-9a" for a in mia)
    assert any(a.op == PlanActionType.REMOVE_FROM_GROUP and a.payload["nickname"] == "klasse-8a" for a in mia)
    # bleibt in alle-sus -> keine Entfernung dort
    assert not any(a.op == PlanActionType.REMOVE_FROM_GROUP and a.payload["nickname"] == "alle-sus" for a in mia)


def test_unchanged_user_produces_no_actions(state):
    plan = _plan(state)
    # Jonas Brinkmann bleibt in 8a, gleiche Rolle/Lizenz -> nichts zu tun
    assert not [a for a in plan.actions if a.display_name == "Jonas Brinkmann"]


def test_leaver_disables_reclaims_and_schedules_deletion(state):
    plan = _plan(state)
    emma = [a for a in plan.actions if a.display_name == "Emma Waldvogel"]
    ops = {a.op for a in emma}
    assert PlanActionType.DISABLE_USER in ops
    assert PlanActionType.REMOVE_LICENSE in ops
    assert PlanActionType.CONVERT_TO_SHARED_MAILBOX in ops
    assert PlanActionType.SCHEDULE_DELETION in ops
    sched = next(a for a in emma if a.op == PlanActionType.SCHEDULE_DELETION)
    assert sched.payload["deleteAfter"] == "2026-08-22"  # 2026-07-23 + 30 Tage


def test_disabled_leaver_not_disabled_again(state):
    plan = _plan(state)
    tim = [a for a in plan.actions if a.display_name == "Tim Rossbach"]
    assert not any(a.op == PlanActionType.DISABLE_USER for a in tim)  # war schon deaktiviert
    assert any(a.op == PlanActionType.REMOVE_LICENSE for a in tim)


def test_already_scheduled_account_is_noop(state):
    plan = _plan(state)
    # Lukas Ehrlich: deaktiviert, keine Lizenz, Shared Mailbox, Löschung vorgemerkt
    assert not [a for a in plan.actions if a.display_name == "Lukas Ehrlich"]


def test_plan_phases_are_populated(state):
    plan = _plan(state)
    assert plan.by_phase(Phase.JOINER)
    assert plan.by_phase(Phase.MOVER)
    assert plan.by_phase(Phase.LEAVER)


def test_plan_is_idempotent_after_apply(state):
    from app.lifecycle.executor import Executor

    plan = _plan(state)
    Executor(state.client, state.audit, state.settings).apply(plan, dry_run=False)
    # Zweiter Lauf gegen den nun angeglichenen Tenant -> leerer Plan
    plan2 = _plan(state)
    assert plan2.actions == []
