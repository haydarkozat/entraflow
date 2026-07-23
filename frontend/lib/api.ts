// Zentrale API-Anbindung für das EntraFlow-Dashboard.
// Basis-URL kommt aus NEXT_PUBLIC_API_BASE, Fallback ist der lokale Backend-Port.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Typen des Backend-Vertrags
// ---------------------------------------------------------------------------

export interface Health {
  status: string;
  graph_mode: string;
}

export interface Sku {
  skuPartNumber: string;
  capacity: number;
  consumed: number;
  available: number;
}

export interface TenantSummary {
  reference_date: string;
  upn_domain: string;
  total_users: number;
  enabled_users: number;
  roles: {
    student: number;
    teacher: number;
    staff: number;
    shared: number;
    unmanaged: number;
  };
  groups: number;
  skus: Sku[];
}

export interface UserRecord {
  id: string;
  userPrincipalName: string;
  displayName: string;
  accountEnabled: boolean;
  employeeId: string | null;
  userType: string;
  licenses: string[];
  lastSignIn: string | null;
  deletionScheduledFor: string | null;
}

export type PlanPhase = "joiner" | "mover" | "leaver" | "license" | "compliance";
export type PlanOp =
  | "create_user"
  | "enable_user"
  | "disable_user"
  | "assign_license"
  | "remove_license"
  | "add_to_group"
  | "remove_from_group"
  | "convert_to_shared_mailbox"
  | "schedule_deletion";

export interface PlanAction {
  op: PlanOp;
  phase: PlanPhase;
  upn: string;
  display_name: string;
  summary: string;
  reason: string;
  dsgvo_note: string | null;
  payload: Record<string, unknown>;
}

export interface Plan {
  reference_date: string;
  actions: PlanAction[];
}

export interface ApplyResult {
  dry_run: boolean;
  planned: {
    joiner: number;
    mover: number;
    leaver: number;
    license: number;
    compliance: number;
    total: number;
  };
  applied: number;
  failed: number;
  results: {
    op: PlanOp;
    phase: PlanPhase;
    upn: string;
    summary: string;
    success: boolean;
    message: string;
  }[];
}

export type OptimizerKind = "inactive" | "disabled_licensed" | "duplicate_license";

export interface LicenseOptimize {
  reference_date: string;
  usage: {
    sku_part_number: string;
    label: string;
    capacity: number;
    consumed: number;
    available: number;
    monthly_price_eur: number;
    monthly_cost_eur: number;
  }[];
  recommendations: {
    kind: OptimizerKind;
    upn: string;
    display_name: string;
    sku_part_number: string;
    detail: string;
    monthly_saving_eur: number;
  }[];
  total_monthly_saving_eur: number;
  reclaimable_seats: number;
}

export type Severity = "hoch" | "mittel" | "niedrig";

export interface ComplianceFinding {
  severity: Severity;
  category: string;
  upn: string;
  display_name: string;
  detail: string;
  article: string;
}

export interface Compliance {
  reference_date: string;
  processing_records: number;
  score: number;
  access_overview: {
    group: string;
    nickname: string;
    member_count: number;
    members: string[];
  }[];
  findings: ComplianceFinding[];
  deletions_due: ComplianceFinding[];
}

export interface AuditEntry {
  seq: number;
  timestamp: string;
  actor: string;
  op: PlanOp;
  phase: PlanPhase;
  upn: string;
  display_name: string;
  summary: string;
  reason: string;
  dsgvo_note: string | null;
  success: boolean;
  message: string;
}

// ---------------------------------------------------------------------------
// Fetch-Helfer
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new ApiError(`Anfrage fehlgeschlagen (${res.status})`, res.status);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => request<Health>("/api/health"),
  summary: () => request<TenantSummary>("/api/tenant/summary"),
  users: () => request<UserRecord[]>("/api/users"),
  plan: () => request<Plan>("/api/plan", { method: "POST", body: "{}" }),
  apply: (dryRun: boolean) =>
    request<ApplyResult>("/api/apply", {
      method: "POST",
      body: JSON.stringify({ dry_run: dryRun }),
    }),
  optimize: () => request<LicenseOptimize>("/api/licenses/optimize"),
  compliance: () => request<Compliance>("/api/compliance/dsgvo"),
  audit: (limit = 200) => request<AuditEntry[]>(`/api/audit?limit=${limit}`),
  reset: () =>
    request<{ ok: boolean; message: string }>("/api/reset", {
      method: "POST",
      body: "{}",
    }),
};

// Hilfsfunktionen für die Darstellung
export function formatEuro(value: number): string {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
  }).format(value);
}

export function formatDate(value: string | null): string {
  if (!value) return "–";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return new Intl.DateTimeFormat("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(d);
}

export function formatDateTime(value: string | null): string {
  if (!value) return "–";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return new Intl.DateTimeFormat("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}
