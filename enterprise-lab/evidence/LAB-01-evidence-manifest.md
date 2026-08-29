# LAB-01 – Evidence Manifest

**Scenario:** Tenant Baseline & RBAC  
**Evidence state:** Documentation prepared; capture pending  
**Sensitive data policy:** No tenant IDs, account identifiers, e-mail addresses, secrets or personal data

| Artefakt | Status | Akzeptanzkriterium |
|---|---|---|
| `LAB-01-01-tenant-overview.png` | Pending capture | Erreichbarer Testtenant; sensitive Felder redigiert |
| `LAB-01-02-baseline-groups.png` | Pending capture | Genau sieben erwartete Gruppen; keine Objekt-IDs |
| `LAB-01-03-whatif.png` | Pending original evidence | Originaler Preflight-Nachweis; nicht nachgestellt |
| `LAB-01-04-created.png` | Pending original evidence | Sieben `Created`-Resultate ohne Objekt-IDs |
| `LAB-01-05-idempotency.png` | Pending capture | Sieben `Existing / None`-Resultate und PASS |
| `LAB-01-baseline.md` | Complete | Technische Bewertung und Ergebnis dokumentiert |
| `LAB-01-RBAC-MATRIX.md` | Complete | Least-Privilege-Zielmodell dokumentiert |
| `LAB-01-BREAK-GLASS.md` | Complete | Notfallzugang konzeptionell dokumentiert |

## Abschlussregel

LAB-01 wird erst auf `Complete` gesetzt, wenn alle fünf PNG-Artefakte:

1. aus der realen Testtenant-Ausführung stammen,
2. anhand von `docs/LAB-01-EVIDENCE-CAPTURE.md` geprüft wurden,
3. keine sensitiven Daten enthalten und
4. in dieser Tabelle als `Captured and redacted` markiert sind.

Fehlt eine historische Originalaufnahme des `-WhatIf`- oder Erstlaufs, bleibt dies transparent dokumentiert. Evidence darf nicht rekonstruiert oder nachgestellt werden.
