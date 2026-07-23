from __future__ import annotations

from app.compliance.dsgvo import DsgvoReporter


def _report(state):
    return DsgvoReporter(state.client, state.settings).report()


def test_flags_orphan_account(state):
    report = _report(state)
    orphan = [f for f in report.findings if f.category == "Rechenschaftspflicht"]
    assert any(f.display_name == "Praktikant IT" and f.severity == "hoch" for f in orphan)


def test_flags_disabled_but_licensed(state):
    report = _report(state)
    minimization = {f.display_name for f in report.findings if f.category == "Datenminimierung"}
    assert {"Tim Rossbach", "Thomas Reinhardt"} <= minimization


def test_lists_deletions_due(state):
    report = _report(state)
    # Lukas Ehrlich: Frist 2026-06-01 < Stichtag 2026-07-23
    assert any(f.display_name == "Lukas Ehrlich" for f in report.deletions_due)


def test_access_overview_covers_groups(state):
    report = _report(state)
    nicks = {a.nickname for a in report.access_overview}
    assert {"alle-sus", "kollegium", "klasse-8a", "klasse-9a", "verwaltung"} <= nicks


def test_processing_records_counts_only_managed(state):
    report = _report(state)
    # 13 Konten insgesamt, 1 herrenlos (ohne employeeId) -> 12 verarbeitete Datensätze
    assert report.processing_records == 12


def test_score_is_penalised_but_positive(state):
    report = _report(state)
    assert 0 < report.score < 100
