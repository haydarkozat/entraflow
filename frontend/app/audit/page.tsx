"use client";

import { api, formatDateTime, type AuditEntry } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card } from "@/components/Card";
import { OpBadge, PhaseBadge, Badge } from "@/components/Badge";
import { LoadingState, ErrorState, EmptyState } from "@/components/states";
import { IconAudit } from "@/components/icons";

export default function AuditPage() {
  const { data, loading, error, reload } = useApi<AuditEntry[]>(() =>
    api.audit(200)
  );

  if (loading && !data) return <LoadingState label="Audit-Log wird geladen …" />;
  if (error || !data) return <ErrorState onRetry={reload} message={error ?? undefined} />;

  return (
    <>
      <div className="page-head">
        <h1>Audit-Log</h1>
        <p>
          Revisionssichere Aufzeichnung aller angewendeten Änderungen –
          nachvollziehbar mit Zeitstempel, Akteur und Datenschutzhinweis.
        </p>
      </div>

      <Card
        title="Änderungsprotokoll"
        subtitle={`${data.length} Einträge`}
        bodyPadding={false}
      >
        {data.length === 0 ? (
          <EmptyState
            icon={<IconAudit />}
            title="Noch keine Änderungen angewendet."
            description="Sobald ein Lebenszyklus-Plan angewendet wird, erscheinen die Aktionen hier im Protokoll."
          />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th className="right">#</th>
                  <th>Zeitpunkt</th>
                  <th>Aktion</th>
                  <th>Phase</th>
                  <th>Konto</th>
                  <th>Zusammenfassung</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.map((e) => (
                  <tr key={e.seq}>
                    <td className="right cell-num">{e.seq}</td>
                    <td className="nowrap cell-dim">
                      {formatDateTime(e.timestamp)}
                    </td>
                    <td>
                      <OpBadge op={e.op} />
                    </td>
                    <td>
                      <PhaseBadge phase={e.phase} />
                    </td>
                    <td>
                      <div className="cell-strong">{e.display_name}</div>
                      <div className="cell-mono">{e.upn}</div>
                    </td>
                    <td className="cell-dim">{e.summary}</td>
                    <td>
                      {e.success ? (
                        <Badge variant="success" dot>
                          Erfolg
                        </Badge>
                      ) : (
                        <Badge variant="danger" dot>
                          Fehler
                        </Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}
