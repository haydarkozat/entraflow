"use client";

import { useState } from "react";
import { api, type ApplyResult, type Plan, type PlanAction, type PlanPhase } from "@/lib/api";
import { Card } from "@/components/Card";
import { OpBadge, PhaseBadge } from "@/components/Badge";
import { EmptyState } from "@/components/states";
import {
  IconPlus,
  IconPlay,
  IconRocket,
  IconLock,
  IconCheck,
  IconAlert,
  IconLifecycle,
} from "@/components/icons";

const TABS: { key: PlanPhase | "all"; label: string }[] = [
  { key: "all", label: "Alle" },
  { key: "joiner", label: "Joiner" },
  { key: "mover", label: "Mover" },
  { key: "leaver", label: "Leaver" },
  { key: "license", label: "Lizenz" },
  { key: "compliance", label: "Compliance" },
];

type Notice = { kind: "success" | "danger" | "info"; text: string } | null;

export default function LifecyclePage() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [busy, setBusy] = useState<"" | "plan" | "dry" | "apply">("");
  const [tab, setTab] = useState<PlanPhase | "all">("all");
  const [result, setResult] = useState<ApplyResult | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [error, setError] = useState<string | null>(null);

  async function createPlan() {
    setBusy("plan");
    setError(null);
    setResult(null);
    try {
      const p = await api.plan();
      setPlan(p);
      setNotice({
        kind: "info",
        text: `Plan erstellt: ${p.actions.length} geplante Aktionen zum Stichtag.`,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend nicht erreichbar");
    } finally {
      setBusy("");
    }
  }

  async function apply(dryRun: boolean) {
    setBusy(dryRun ? "dry" : "apply");
    setError(null);
    try {
      const r = await api.apply(dryRun);
      setResult(r);
      if (dryRun) {
        setNotice({
          kind: "info",
          text: `Simulation abgeschlossen: ${r.planned.total} Aktionen würden ausgeführt (${r.failed} Warnungen).`,
        });
      } else {
        setNotice({
          kind: r.failed > 0 ? "danger" : "success",
          text: `Anwendung abgeschlossen: ${r.applied} Aktionen ausgeführt, ${r.failed} fehlgeschlagen.`,
        });
        // Nach dem Anwenden ist der Plan leer – neu laden.
        const p = await api.plan();
        setPlan(p);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend nicht erreichbar");
    } finally {
      setBusy("");
    }
  }

  const counts = countByPhase(plan?.actions ?? []);
  const filtered =
    plan?.actions.filter((a) => tab === "all" || a.phase === tab) ?? [];

  return (
    <>
      <div className="page-head">
        <h1>Lebenszyklus-Automatisierung (JML)</h1>
        <p>
          Joiner-, Mover- und Leaver-Prozesse werden aus den Quelldaten
          abgeleitet. Erstellen Sie einen Plan, simulieren Sie ihn gefahrlos und
          wenden Sie ihn anschließend an.
        </p>
      </div>

      <div className="toolbar">
        <button className="btn btn--primary" onClick={createPlan} disabled={busy !== ""}>
          {busy === "plan" ? <span className="spin-sm" /> : <IconPlus />}
          Plan erstellen
        </button>
        <button
          className="btn"
          onClick={() => apply(true)}
          disabled={busy !== "" || !plan || plan.actions.length === 0}
        >
          {busy === "dry" ? <span className="spin-sm" /> : <IconPlay />}
          Simulieren (Dry-Run)
        </button>
        <button
          className="btn btn--success"
          onClick={() => apply(false)}
          disabled={busy !== "" || !plan || plan.actions.length === 0}
        >
          {busy === "apply" ? <span className="spin-sm" /> : <IconRocket />}
          Anwenden
        </button>
      </div>

      {error && (
        <div className="banner banner--danger">
          <IconAlert />
          <div>
            <strong>Fehler</strong>
            {error}
          </div>
        </div>
      )}

      {notice && (
        <div className={`banner banner--${notice.kind}`}>
          {notice.kind === "success" ? <IconCheck /> : notice.kind === "danger" ? <IconAlert /> : <IconLifecycle />}
          <div>{notice.text}</div>
        </div>
      )}

      {result && (
        <Card
          title={result.dry_run ? "Simulationsergebnis" : "Anwendungsergebnis"}
          subtitle={
            result.dry_run
              ? "Es wurden keine Änderungen am Mandanten vorgenommen."
              : "Die Änderungen wurden am Mandanten angewendet."
          }
        >
          <div className="summary-grid">
            <SummaryPill n={result.planned.joiner} l="Joiner" />
            <SummaryPill n={result.planned.mover} l="Mover" />
            <SummaryPill n={result.planned.leaver} l="Leaver" />
            <SummaryPill n={result.planned.license} l="Lizenz" />
            <SummaryPill n={result.planned.compliance} l="Compliance" />
            <SummaryPill n={result.applied} l="Angewendet" />
            <SummaryPill n={result.failed} l="Fehlerhaft" />
          </div>
        </Card>
      )}

      {!plan ? (
        <Card>
          <EmptyState
            icon={<IconLifecycle />}
            title="Noch kein Plan erstellt"
            description="Klicken Sie auf „Plan erstellen“, um die anstehenden Lebenszyklus-Aktionen aus den Quelldaten zu berechnen."
          />
        </Card>
      ) : plan.actions.length === 0 ? (
        <Card>
          <EmptyState
            icon={<IconCheck />}
            title="Keine offenen Aktionen"
            description="Alle Konten sind auf dem aktuellen Stand. Es sind keine Lebenszyklus-Änderungen erforderlich."
          />
        </Card>
      ) : (
        <>
          <div className="tabs">
            {TABS.map((t) => {
              const n = t.key === "all" ? plan.actions.length : counts[t.key] ?? 0;
              if (t.key !== "all" && n === 0) return null;
              return (
                <button
                  key={t.key}
                  className={`tab${tab === t.key ? " active" : ""}`}
                  onClick={() => setTab(t.key)}
                >
                  {t.label}
                  <span className="tab__count">{n}</span>
                </button>
              );
            })}
          </div>

          <div>
            {filtered.map((a, i) => (
              <ActionRow key={`${a.upn}-${a.op}-${i}`} action={a} />
            ))}
          </div>
        </>
      )}
    </>
  );
}

function ActionRow({ action }: { action: PlanAction }) {
  return (
    <div className="action">
      <div className="action__main">
        <div className="action__title">
          <OpBadge op={action.op} />
          <PhaseBadge phase={action.phase} />
          <strong>{action.display_name}</strong>
          <span className="cell-mono">{action.upn}</span>
        </div>
        <p className="action__summary">{action.summary}</p>
        <p className="action__reason">Grund: {action.reason}</p>
        {action.dsgvo_note && (
          <div className="dsgvo-note">
            <IconLock />
            <span>{action.dsgvo_note}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryPill({ n, l }: { n: number; l: string }) {
  return (
    <div className="summary-pill">
      <div className="n">{n}</div>
      <div className="l">{l}</div>
    </div>
  );
}

function countByPhase(actions: PlanAction[]): Record<string, number> {
  return actions.reduce<Record<string, number>>((acc, a) => {
    acc[a.phase] = (acc[a.phase] ?? 0) + 1;
    return acc;
  }, {});
}
