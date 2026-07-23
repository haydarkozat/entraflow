"use client";

import { type CSSProperties } from "react";
import { api, type Compliance, type ComplianceFinding } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card } from "@/components/Card";
import { StatCard } from "@/components/StatCard";
import { SeverityBadge, Badge } from "@/components/Badge";
import { LoadingState, ErrorState, EmptyState } from "@/components/states";
import {
  IconRecords,
  IconAlert,
  IconCheck,
  IconGroup,
  IconChevron,
} from "@/components/icons";

function scoreColor(score: number): string {
  if (score >= 80) return "var(--success)";
  if (score >= 50) return "var(--warning)";
  return "var(--danger)";
}

function scoreLabel(score: number): string {
  if (score >= 80) return "Gut";
  if (score >= 50) return "Verbesserungswürdig";
  return "Kritisch";
}

export default function CompliancePage() {
  const { data, loading, error, reload } = useApi<Compliance>(() =>
    api.compliance()
  );

  if (loading && !data) return <LoadingState label="DSGVO-Auswertung wird geladen …" />;
  if (error || !data) return <ErrorState onRetry={reload} message={error ?? undefined} />;

  const col = scoreColor(data.score);
  const highCount = data.findings.filter((f) => f.severity === "hoch").length;

  return (
    <>
      <div className="page-head">
        <h1>DSGVO-Compliance</h1>
        <p>
          Datenschutz-Status des Mandanten nach Art. 5, 25 und 32 DSGVO:
          Datensparsamkeit, Zugriffskontrolle und fristgerechte Löschung
          personenbezogener Daten.
        </p>
      </div>

      <div className="stack">
        <Card>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 28,
              flexWrap: "wrap",
            }}
          >
            <div
              className="score-gauge"
              style={{ "--v": data.score, "--col": col } as CSSProperties}
            >
              <div className="score-gauge__inner">
                <strong>{data.score}</strong>
                <span>von 100</span>
              </div>
            </div>
            <div style={{ flex: 1, minWidth: 220 }}>
              <div className="section-title" style={{ marginTop: 0 }}>
                Datenschutz-Bewertung
              </div>
              <div
                style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: col,
                  marginBottom: 6,
                }}
              >
                {scoreLabel(data.score)}
              </div>
              <p className="muted" style={{ margin: 0, maxWidth: "52ch" }}>
                Der Score aggregiert Feststellungen aus Zugriffskontrolle,
                Aufbewahrung und Kontohygiene. Offene Feststellungen mit hoher
                Schwere reduzieren die Bewertung am stärksten.
              </p>
            </div>
            <div className="grid grid--kpi" style={{ minWidth: 260 }}>
              <StatCard
                label="Verarbeitungsverzeichnisse"
                value={data.processing_records}
                icon={<IconRecords />}
              />
              <StatCard
                label="Feststellungen (hoch)"
                value={highCount}
                hint={`${data.findings.length} gesamt`}
                icon={<IconAlert />}
              />
            </div>
          </div>
        </Card>

        <Card
          title="Feststellungen"
          subtitle="Erkannte Datenschutz-Risiken mit Rechtsgrundlage"
          bodyPadding={false}
        >
          {data.findings.length === 0 ? (
            <EmptyState
              icon={<IconCheck />}
              title="Keine Feststellungen"
              description="Es wurden keine Datenschutz-Risiken erkannt."
            />
          ) : (
            <FindingsTable findings={data.findings} />
          )}
        </Card>

        <Card
          title="Zur Löschung fällig"
          subtitle="Konten mit abgelaufener Aufbewahrungsfrist (Art. 17 DSGVO)"
          bodyPadding={false}
        >
          {data.deletions_due.length === 0 ? (
            <EmptyState
              icon={<IconCheck />}
              title="Keine überfälligen Löschungen"
              description="Alle Aufbewahrungsfristen werden aktuell eingehalten."
            />
          ) : (
            <FindingsTable findings={data.deletions_due} />
          )}
        </Card>

        <Card
          title="Zugriffsübersicht"
          subtitle="Mitgliedschaften sicherheitsrelevanter Gruppen"
        >
          {data.access_overview.length === 0 ? (
            <EmptyState
              icon={<IconGroup />}
              title="Keine Gruppen"
              description="Es sind keine überwachten Gruppen vorhanden."
            />
          ) : (
            <div>
              {data.access_overview.map((g) => (
                <details className="access" key={g.group}>
                  <summary>
                    <span
                      style={{ display: "flex", alignItems: "center", gap: 10 }}
                    >
                      <IconChevron className="chev" width={16} height={16} />
                      {g.nickname}
                      <span className="cell-mono">{g.group}</span>
                    </span>
                    <Badge variant="primary">{g.member_count} Mitglieder</Badge>
                  </summary>
                  <div className="access__members">
                    {g.members.length === 0 ? (
                      <span className="muted">Keine Mitglieder.</span>
                    ) : (
                      g.members.map((m) => (
                        <span className="chip" key={m}>
                          {m}
                        </span>
                      ))
                    )}
                  </div>
                </details>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  );
}

function FindingsTable({ findings }: { findings: ComplianceFinding[] }) {
  return (
    <div className="table-wrap">
      <table className="data">
        <thead>
          <tr>
            <th>Schwere</th>
            <th>Kategorie</th>
            <th>Betroffenes Konto</th>
            <th>Detail</th>
            <th>Artikel</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f, i) => (
            <tr key={`${f.upn}-${f.category}-${i}`}>
              <td>
                <SeverityBadge severity={f.severity} />
              </td>
              <td className="cell-strong">{f.category}</td>
              <td>
                <div className="cell-strong">{f.display_name}</div>
                <div className="cell-mono">{f.upn}</div>
              </td>
              <td className="cell-dim">{f.detail}</td>
              <td>
                <Badge variant="neutral">{f.article}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
