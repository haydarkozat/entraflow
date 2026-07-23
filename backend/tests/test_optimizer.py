from __future__ import annotations

from app.licensing.optimizer import LicenseOptimizer


def _report(state):
    return LicenseOptimizer(state.client, state.settings).analyze()


def test_detects_inactive_paid_license(state):
    report = _report(state)
    inactive = [r for r in report.recommendations if r.kind == "inactive"]
    # Michael Ebert: A3, seit 2026-01-10 inaktiv (> 90 Tage)
    assert any(r.display_name == "Michael Ebert" for r in inactive)


def test_detects_disabled_but_licensed(state):
    report = _report(state)
    disabled = {r.display_name for r in report.recommendations if r.kind == "disabled_licensed"}
    assert {"Tim Rossbach", "Thomas Reinhardt"} <= disabled


def test_total_saving_is_summed(state):
    report = _report(state)
    # Thomas (A3, deaktiviert) 5,50 € + Michael (A3, inaktiv) 5,50 €; Tim (A1) 0 €
    assert report.total_monthly_saving_eur == 11.0
    assert report.reclaimable_seats == 3


def test_usage_reports_capacity(state):
    report = _report(state)
    faculty = next(u for u in report.usage if u.sku_part_number == "ENTERPRISEPACKPLUS_FACULTY")
    assert faculty.capacity == 120
    assert faculty.consumed == faculty.capacity - faculty.available
