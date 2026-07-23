"use client";

import { useEffect, useState } from "react";
import { api, formatDate } from "@/lib/api";

export function TopBar() {
  const [online, setOnline] = useState<boolean | null>(null);
  const [graphMode, setGraphMode] = useState<string>("–");
  const [refDate, setRefDate] = useState<string | null>(null);
  const [domain, setDomain] = useState<string>("–");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const health = await api.health();
        if (cancelled) return;
        setOnline(health.status === "ok");
        setGraphMode(health.graph_mode);
        try {
          const s = await api.summary();
          if (cancelled) return;
          setRefDate(s.reference_date);
          setDomain(s.upn_domain);
        } catch {
          /* Zusammenfassung optional – Verbindung steht trotzdem */
        }
      } catch {
        if (!cancelled) setOnline(false);
      }
    }

    load();
    const id = setInterval(load, 30000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <header className="topbar">
      <div className="topbar__meta">
        <div className="topbar__item">
          <span className="label">Stichtag</span>
          <span className="value">{refDate ? formatDate(refDate) : "–"}</span>
        </div>
        <div className="topbar__item">
          <span className="label">UPN-Domäne</span>
          <span className="value">{domain}</span>
        </div>
        <div className="topbar__item">
          <span className="label">Graph-Modus</span>
          <span className="value" style={{ textTransform: "capitalize" }}>
            {graphMode}
          </span>
        </div>
      </div>

      {online === false ? (
        <span className="status status--offline">
          <span className="status__dot" />
          Offline
        </span>
      ) : (
        <span className="status status--online">
          <span className="status__dot" />
          {online === null ? "Verbinde …" : "Verbunden"}
        </span>
      )}
    </header>
  );
}
