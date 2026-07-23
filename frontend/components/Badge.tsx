import React from "react";
import type {
  OptimizerKind,
  PlanOp,
  PlanPhase,
  Severity,
} from "@/lib/api";

type Variant =
  | "neutral"
  | "primary"
  | "success"
  | "warning"
  | "danger"
  | "info";

export function Badge({
  children,
  variant = "neutral",
  dot = false,
}: {
  children: React.ReactNode;
  variant?: Variant;
  dot?: boolean;
}) {
  return (
    <span className={`badge badge--${variant}`}>
      {dot && <span className="badge__dot" />}
      {children}
    </span>
  );
}

// --- Zuordnungen von Backend-Werten auf Beschriftung + Variante --------------

const OP_LABEL: Record<PlanOp, string> = {
  create_user: "Konto anlegen",
  enable_user: "Aktivieren",
  disable_user: "Deaktivieren",
  assign_license: "Lizenz zuweisen",
  remove_license: "Lizenz entziehen",
  add_to_group: "Gruppe +",
  remove_from_group: "Gruppe −",
  convert_to_shared_mailbox: "Shared Mailbox",
  schedule_deletion: "Löschung planen",
};

const OP_VARIANT: Record<PlanOp, Variant> = {
  create_user: "success",
  enable_user: "success",
  disable_user: "warning",
  assign_license: "info",
  remove_license: "warning",
  add_to_group: "primary",
  remove_from_group: "neutral",
  convert_to_shared_mailbox: "info",
  schedule_deletion: "danger",
};

export function OpBadge({ op }: { op: PlanOp }) {
  return <Badge variant={OP_VARIANT[op] ?? "neutral"}>{OP_LABEL[op] ?? op}</Badge>;
}

const PHASE_LABEL: Record<PlanPhase, string> = {
  joiner: "Joiner",
  mover: "Mover",
  leaver: "Leaver",
  license: "Lizenz",
  compliance: "Compliance",
};

const PHASE_VARIANT: Record<PlanPhase, Variant> = {
  joiner: "success",
  mover: "primary",
  leaver: "warning",
  license: "info",
  compliance: "danger",
};

export function PhaseBadge({ phase }: { phase: PlanPhase }) {
  return (
    <Badge variant={PHASE_VARIANT[phase] ?? "neutral"} dot>
      {PHASE_LABEL[phase] ?? phase}
    </Badge>
  );
}

const KIND_LABEL: Record<OptimizerKind, string> = {
  inactive: "Inaktiv",
  disabled_licensed: "Deaktiviert + lizenziert",
  duplicate_license: "Doppellizenz",
};

const KIND_VARIANT: Record<OptimizerKind, Variant> = {
  inactive: "warning",
  disabled_licensed: "danger",
  duplicate_license: "info",
};

export function KindBadge({ kind }: { kind: OptimizerKind }) {
  return (
    <Badge variant={KIND_VARIANT[kind] ?? "neutral"}>
      {KIND_LABEL[kind] ?? kind}
    </Badge>
  );
}

const SEVERITY_VARIANT: Record<Severity, Variant> = {
  hoch: "danger",
  mittel: "warning",
  niedrig: "neutral",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const label = severity.charAt(0).toUpperCase() + severity.slice(1);
  return (
    <Badge variant={SEVERITY_VARIANT[severity] ?? "neutral"} dot>
      {label}
    </Badge>
  );
}
