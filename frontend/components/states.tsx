import React from "react";
import { IconCloudOff } from "./icons";

export function LoadingState({ label = "Daten werden geladen …" }: { label?: string }) {
  return (
    <div className="state">
      <div className="spinner" />
      <p className="muted">{label}</p>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="state state--error">
      <div className="state__icon">
        <IconCloudOff />
      </div>
      <h3>Backend nicht erreichbar</h3>
      <p>
        {message ??
          "Die Verbindung zum EntraFlow-Backend ist fehlgeschlagen. Bitte prüfen Sie, ob der Dienst unter der konfigurierten API-Adresse läuft."}
      </p>
      {onRetry && (
        <button className="btn" onClick={onRetry}>
          Erneut versuchen
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  icon,
}: {
  title: string;
  description?: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="state">
      {icon && <div className="state__icon">{icon}</div>}
      <h3>{title}</h3>
      {description && <p>{description}</p>}
    </div>
  );
}
