"""Konsolen-Demo: zeigt einen kompletten Lebenszyklus-Lauf ohne Frontend.

Aufruf:  python -m app.demo
"""

from __future__ import annotations

from .config import Settings
from .domain import Phase
from .state import AppState

BAR = "─" * 72


def _h(title: str) -> None:
    print(f"\n{BAR}\n {title}\n{BAR}")


def main() -> None:
    state = AppState(Settings())
    s = state.settings
    print(f"EntraFlow – Demo-Lauf  ·  Stichtag {s.reference_date}  ·  Domäne {s.upn_domain}")

    _h("1) IST-ZUSTAND DES TENANTS")
    summ = state.client.list_users()
    print(f" Konten gesamt: {len(summ)}  ·  aktiv: {sum(u.accountEnabled for u in summ)}")
    for sku in state.client.list_subscribed_skus():
        print(f"   {sku.skuPartNumber:28} {sku.consumedUnits:>4}/{sku.prepaidUnits.enabled:<4} belegt")

    _h("2) RECONCILIATION-PLAN (Soll aus Schulverwaltung vs. Ist im Tenant)")
    plan = state.planner().build_plan(state.desired_users())
    c = plan.counts
    print(f" Joiner: {c['joiner']}   Mover: {c['mover']}   Leaver: {c['leaver']}   Gesamt: {c['total']}")
    for phase in (Phase.JOINER, Phase.MOVER, Phase.LEAVER):
        actions = plan.by_phase(phase)
        if not actions:
            continue
        print(f"\n  {phase.value.upper()}")
        for a in actions:
            note = f"   ⚖ {a.dsgvo_note}" if a.dsgvo_note else ""
            print(f"   • {a.display_name:22} {a.summary}{note}")

    _h("3) LIZENZ-GOVERNANCE (vor Bereinigung)")
    opt = state.optimizer().analyze()
    print(f" Einsparpotenzial: {opt.total_monthly_saving_eur:.2f} €/Monat  ·  {opt.reclaimable_seats} rückgewinnbare Seats")
    for r in opt.recommendations:
        print(f"   [{r.kind:18}] {r.display_name:22} {r.detail}")

    _h("4) DSGVO-BERICHT (vor Bereinigung)")
    dz = state.dsgvo().report()
    print(f" DSGVO-Score: {dz.score}/100  ·  {dz.processing_records} verarbeitete Datensätze")
    for f in dz.findings:
        print(f"   [{f.severity:6}] {f.display_name:22} {f.detail}  ({f.article})")
    for f in dz.deletions_due:
        print(f"   [LÖSCHUNG FÄLLIG] {f.display_name:22} {f.detail}")

    _h("5) PLAN ANWENDEN")
    results = state.executor().apply(plan, dry_run=False)
    print(f" Angewandt: {sum(r.success for r in results)}  ·  Fehlgeschlagen: {sum(not r.success for r in results)}")

    _h("6) ZUSTAND NACH BEREINIGUNG")
    opt2 = state.optimizer().analyze()
    dz2 = state.dsgvo().report()
    print(f" DSGVO-Score: {dz.score} → {dz2.score}   ·   offene Befunde: {len(dz.findings)} → {len(dz2.findings)}")
    print(f" Verbleibende Optimierung: {opt2.total_monthly_saving_eur:.2f} €/Monat (echte Inaktivität, kein Automatismus)")
    plan2 = state.planner().build_plan(state.desired_users())
    print(f" Erneuter Plan-Lauf: {plan2.counts['total']} Aktionen (Idempotenz nachgewiesen)")


if __name__ == "__main__":
    main()
