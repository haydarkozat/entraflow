from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def api():
    client = TestClient(app)
    client.post("/api/reset")  # sauberer Demo-Tenant je Test
    yield client
    client.post("/api/reset")


def test_health(api):
    r = api.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_tenant_summary(api):
    data = api.get("/api/tenant/summary").json()
    assert data["total_users"] == 13
    assert data["roles"]["student"] >= 1
    assert any(s["skuPartNumber"] == "ENTERPRISEPACKPLUS_FACULTY" for s in data["skus"])


def test_plan_endpoint_covers_all_phases(api):
    plan = api.post("/api/plan", json={}).json()
    phases = {a["phase"] for a in plan["actions"]}
    assert {"joiner", "mover", "leaver"} <= phases


def test_apply_dry_run_then_real(api):
    dry = api.post("/api/apply", json={"dry_run": True}).json()
    assert dry["dry_run"] is True
    assert dry["failed"] == 0
    # nach Dry-Run ist der Tenant unverändert
    assert api.get("/api/tenant/summary").json()["total_users"] == 13

    real = api.post("/api/apply", json={"dry_run": False}).json()
    assert real["failed"] == 0
    # Joiner wurden angelegt
    assert api.get("/api/tenant/summary").json()["total_users"] > 13
    # Audit-Log gefüllt
    assert len(api.get("/api/audit").json()) == real["applied"]


def test_apply_is_idempotent(api):
    api.post("/api/apply", json={"dry_run": False})
    second = api.post("/api/apply", json={"dry_run": False}).json()
    assert second["planned"]["total"] == 0


def test_optimize_endpoint(api):
    data = api.get("/api/licenses/optimize").json()
    assert data["total_monthly_saving_eur"] == 11.0


def test_dsgvo_endpoint(api):
    data = api.get("/api/compliance/dsgvo").json()
    assert "score" in data
    assert data["processing_records"] == 12


def test_custom_csv_override(api):
    csv = "quell_id;vorname;nachname;rolle;klasse;aktiv\nS-9999;Test;Person;student;7b;1\n"
    plan = api.post("/api/plan", json={"csv": csv}).json()
    # ein neuer Joiner + viele Leaver (Seed-Konten fehlen in diesem CSV)
    assert any(a["display_name"] == "Test Person" for a in plan["actions"])
