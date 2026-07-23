"use client";

import { useState, type CSSProperties } from "react";
import { api, formatEuro, type Compliance, type LicenseOptimize, type TenantSummary } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card } from "@/components/Card";
import { StatCard } from "@/components/StatCard";
import { Bar } from "@/components/Bar";
import { Badge } from "@/components/Badge";
import { LoadingState, ErrorState } from "@/components/states";
import {
  IconUsers,
  IconUserCheck,
  IconGroup,
  IconRecords,
  IconReset,
} from "@/components/icons";

export default function DashboardPage() {
  const summary = useApi<TenantSummary>(() => api.summary());
  const optimize = useApi<LicenseOptimize>(() => api.optimize());
  const compliance = useApi<Compliance>(() => api.compliance());
  const [resetting, setResetting] = useState(false);

  async function handleReset() {
    setResetting(true);
    try {
      await api.reset();
      await Promise.all([summary.reload(), optimize.reload(), compliance.reload()]);
    } catch {
      /* Fehler wird über die Kartenzustände sichtbar */
    } finally {
      setResetting(false);
    }
  }

  if (summary.loading && !summary.data) {
    return <LoadingState label="Mandanten-Übersicht wird geladen …" />;
  }
  if (summary.error || !summary.data) {
    return <ErrorState onRetry={summary.reload} message={summary.error ?? undefined} />;
  }

  const s = summary.data;
  const score = compliance.data?.score ?? null;
  const saving = optimize.data?.total_monthly_saving_eur ?? null;

  return (
    <>
      <div className="toolbar toolbar--between">
        <div className="page-head" style={{ marginBottom: 0 }}>
          <h1>Übersicht</h1>
          <p>
            Zentrale Kennzahlen zum Microsoft-365-Mandanten, zur Lizenzauslastung
            und zum Datenschutz-Status Ihrer Schule.
          </p>
        </div>
        <button className="btn" onClick={handleReset} disabled={resetting}>
          {resetting ? <span className="spin-sm" /> : <IconReset />}
          Demo zurücksetzen
        </button>
      </div>

      <div className="stack">
        {/* Hero-Karten */}
        <div className="hero">
          <div className="hero-card hero-card--dsgvo">
            {score !== null && (
              <div className="gauge" style={{ "--v": score } as CSSProperties}>
                <span>{score}</span>
              </div>
            )}
            <div className="hero-card__label">DSGVO-Score</div>
            <div className="hero-card__value">
              {score !== null ? score : "…"}
              <span style={{ fontSize: 18, opacity: 0.7 }}> / 100</span>
            </div>
            <div className="hero-card__sub">
              {compliance.data
                ? `${compliance.data.processing_records} Verarbeitungsverzeichnisse · ${compliance.data.findings.length} offene Feststellungen`
                : "Compliance-Auswertung wird geladen …"}
            </div>
          </div>

          <div className="hero-card hero-card--savings">
            <div className="hero-card__label">Einsparpotenzial</div>
            <div className="hero-card__value">
              {saving !== null ? formatEuro(saving) : "…"}
            </div>
            <div className="hero-card__sub">
              {optimize.data
                ? `${optimize.data.reclaimable_seats} rückgewinnbare Lizenzplätze · ${optimize.data.recommendations.length} Empfehlungen`
                : "Lizenz-Optimierung wird geladen …"}
            </div>
          </div>
        </div>

        {/* KPI-Karten */}
        <div className="grid grid--kpi">
          <StatCard
            label="Konten gesamt"
            value={s.total_users}
            hint={`${s.roles.student} Schüler · ${s.roles.teacher} Lehrkräfte`}
            icon={<IconUsers />}
          />
          <StatCard
            label="Aktive Konten"
            value={s.enabled_users}
            hint={`${s.total_users - s.enabled_users} deaktiviert`}
            icon={<IconUserCheck />}
          />
          <StatCard
            label="Gruppen"
            value={s.groups}
            hint="Sicherheits- & Klassengruppen"
            icon={<IconGroup />}
          />
          <StatCard
            label="Verwaltete Datensätze"
            value={s.roles.student + s.roles.teacher + s.roles.staff}
            hint={`${s.roles.shared} Shared · ${s.roles.unmanaged} unverwaltet`}
            icon={<IconRecords />}
          />
        </div>

        <div className="grid grid--2">
          {/* SKU-Auslastung */}
          <Card
            title="Lizenzauslastung"
            subtitle="Belegte und freie Plätze je Microsoft-365-SKU"
          >
            {s.skus.length === 0 ? (
              <p className="muted">Keine SKUs im Mandanten vorhanden.</p>
            ) : (
              s.skus.map((sku) => (
                <Bar
                  key={sku.skuPartNumber}
                  label={sku.skuPartNumber}
                  consumed={sku.consumed}
                  capacity={sku.capacity}
                />
              ))
            )}
          </Card>

          {/* Rollenverteilung */}
          <Card
            title="Rollenverteilung"
            subtitle="Konten nach Zuordnung im Verzeichnis"
          >
            <div className="stack" style={{ gap: 12 }}>
              <RoleRow label="Schülerinnen & Schüler" value={s.roles.student} total={s.total_users} variant="primary" />
              <RoleRow label="Lehrkräfte" value={s.roles.teacher} total={s.total_users} variant="info" />
              <RoleRow label="Verwaltung / Personal" value={s.roles.staff} total={s.total_users} variant="success" />
              <RoleRow label="Shared Mailboxes" value={s.roles.shared} total={s.total_users} variant="warning" />
              <RoleRow label="Unverwaltet" value={s.roles.unmanaged} total={s.total_users} variant="neutral" />
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}

function RoleRow({
  label,
  value,
  total,
  variant,
}: {
  label: string;
  value: number;
  total: number;
  variant: "primary" | "info" | "success" | "warning" | "neutral";
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <span style={{ flex: 1, fontSize: 13 }}>{label}</span>
      <span className="cell-num" style={{ minWidth: 34, textAlign: "right" }}>
        {value}
      </span>
      <Badge variant={variant}>{pct}%</Badge>
    </div>
  );
}
