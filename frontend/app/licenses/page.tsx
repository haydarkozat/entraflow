"use client";

import { api, formatEuro, type LicenseOptimize } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card } from "@/components/Card";
import { StatCard } from "@/components/StatCard";
import { KindBadge } from "@/components/Badge";
import { Bar } from "@/components/Bar";
import { LoadingState, ErrorState, EmptyState } from "@/components/states";
import { IconEuro, IconSeats, IconCheck } from "@/components/icons";

export default function LicensesPage() {
  const { data, loading, error, reload } = useApi<LicenseOptimize>(() =>
    api.optimize()
  );

  if (loading && !data) return <LoadingState label="Lizenzdaten werden geladen …" />;
  if (error || !data) return <ErrorState onRetry={reload} message={error ?? undefined} />;

  return (
    <>
      <div className="page-head">
        <h1>Lizenz-Governance</h1>
        <p>
          Analyse der Microsoft-365-Lizenzen: ungenutzte, doppelte und auf
          deaktivierten Konten liegende Zuweisungen werden erkannt und zur
          Rückgewinnung vorgeschlagen.
        </p>
      </div>

      <div className="stack">
        <div className="grid grid--kpi">
          <StatCard
            label="Einsparpotenzial / Monat"
            value={formatEuro(data.total_monthly_saving_eur)}
            hint="Bei Umsetzung aller Empfehlungen"
            icon={<IconEuro />}
          />
          <StatCard
            label="Rückgewinnbare Plätze"
            value={data.reclaimable_seats}
            hint="Freigebbare Lizenzplätze"
            icon={<IconSeats />}
          />
          <StatCard
            label="Empfehlungen"
            value={data.recommendations.length}
            hint="Offene Optimierungsvorschläge"
            icon={<IconCheck />}
          />
        </div>

        <Card
          title="SKU-Auslastung & Kosten"
          subtitle="Belegung und monatliche Kosten je Lizenztyp"
          bodyPadding={false}
        >
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Bezeichnung</th>
                  <th className="right">Belegt / Kapazität</th>
                  <th className="right">Frei</th>
                  <th className="right">Preis / Platz</th>
                  <th className="right">Kosten / Monat</th>
                </tr>
              </thead>
              <tbody>
                {data.usage.map((u) => (
                  <tr key={u.sku_part_number}>
                    <td className="cell-mono">{u.sku_part_number}</td>
                    <td className="cell-strong">{u.label}</td>
                    <td className="right">
                      <div style={{ minWidth: 160, marginLeft: "auto" }}>
                        <Bar
                          label=""
                          consumed={u.consumed}
                          capacity={u.capacity}
                        />
                      </div>
                    </td>
                    <td className="right cell-num">{u.available}</td>
                    <td className="right cell-num">
                      {formatEuro(u.monthly_price_eur)}
                    </td>
                    <td className="right cell-num">
                      {formatEuro(u.monthly_cost_eur)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card
          title="Optimierungsempfehlungen"
          subtitle="Konkrete Maßnahmen zur Lizenz-Rückgewinnung"
          bodyPadding={false}
        >
          {data.recommendations.length === 0 ? (
            <EmptyState
              icon={<IconCheck />}
              title="Keine Empfehlungen"
              description="Die Lizenzvergabe ist optimal – es wurde kein Einsparpotenzial gefunden."
            />
          ) : (
            <div className="table-wrap">
              <table className="data">
                <thead>
                  <tr>
                    <th>Art</th>
                    <th>Konto</th>
                    <th>SKU</th>
                    <th>Detail</th>
                    <th className="right">Einsparung / Monat</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recommendations.map((r, i) => (
                    <tr key={`${r.upn}-${r.sku_part_number}-${i}`}>
                      <td>
                        <KindBadge kind={r.kind} />
                      </td>
                      <td>
                        <div className="cell-strong">{r.display_name}</div>
                        <div className="cell-mono">{r.upn}</div>
                      </td>
                      <td className="cell-mono">{r.sku_part_number}</td>
                      <td className="cell-dim">{r.detail}</td>
                      <td className="right saving">
                        {formatEuro(r.monthly_saving_eur)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
