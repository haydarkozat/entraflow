import React from "react";

// Reine CSS-Auslastungsleiste (keine Chart-Bibliothek).
export function Bar({
  label,
  consumed,
  capacity,
}: {
  label: string;
  consumed: number;
  capacity: number;
}) {
  const pct =
    capacity > 0 ? Math.min(100, Math.round((consumed / capacity) * 100)) : 0;
  const available = Math.max(0, capacity - consumed);
  const fillClass =
    pct >= 90 ? "bar__fill--danger" : pct >= 75 ? "bar__fill--warn" : "";

  return (
    <div className="bar-row">
      <div className="bar-row__head">
        <span className="bar-row__name">{label}</span>
        <span className="bar-row__count">
          <b>{consumed}</b> / {capacity} belegt · {available} frei · {pct}%
        </span>
      </div>
      <div className="bar">
        <div
          className={`bar__fill ${fillClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
