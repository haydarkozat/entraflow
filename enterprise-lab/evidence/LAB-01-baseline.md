# LAB-01 Evidence – Tenant Baseline & RBAC

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-01  
**Status:** Baseline and governance documentation complete; screenshot capture pending  
**Date:** 2026-08-29

## Problem

Eine neue Microsoft-Enterprise-Testumgebung benötigt vor Benutzer-, Geräte- und Conditional-Access-Konfigurationen eine kontrollierte Ausgangsbasis mit klaren Gruppen, Pilot-Scope und nachvollziehbaren Namenskonventionen.

## Maßnahme

- Microsoft-Entra-/Intune-Testtenant bereitgestellt und Microsoft Graph erfolgreich per delegierter Authentifizierung verbunden.
- Schreibende Baseline-Aktion zunächst mit `-WhatIf` geprüft.
- Fünf Abteilungs-Sicherheitsgruppen angelegt.
- Separate Pilotgruppen für Conditional Access und Intune-Geräte-Policies angelegt.
- Baseline per PowerShell/Microsoft Graph reproduzierbar umgesetzt.
- Script unmittelbar ein zweites Mal ausgeführt, um Duplikatvermeidung und Idempotenz zu prüfen.
- Least-Privilege-RBAC-Zielmodell und Break-Glass-Konzept dokumentiert.

## Ergebnis

- Tenant erfolgreich erreichbar: `Ja`
- Erwartete Gruppen: `7`
- Tatsächlich erstellte Gruppen: `7`
- Zweiter Script-Lauf ohne Duplikate: `Ja`
- Verwendete Script-Datei: `Initialize-TenantBaseline.ps1`

### Erstellte Gruppen

| Gruppe | Erstlauf | Zweitlauf |
|---|---|---|
| `GRP-CA-Pilot` | `Created` | `Existing / None` |
| `GRP-Devices-Pilot` | `Created` | `Existing / None` |
| `SG-Dept-Finance` | `Created` | `Existing / None` |
| `SG-Dept-HR` | `Created` | `Existing / None` |
| `SG-Dept-IT` | `Created` | `Existing / None` |
| `SG-Dept-Operations` | `Created` | `Existing / None` |
| `SG-Dept-Sales` | `Created` | `Existing / None` |

### Technischer Nachweis

Der erste produktive Lauf lieferte für alle sieben Zielgruppen den Status `Created`. Der unmittelbar danach ausgeführte zweite Lauf erkannte dieselben Objekte und lieferte für alle Gruppen `Existing` mit `Action = None`. Damit wurde die Idempotenz des Baseline-Skripts in einem realen Microsoft-Entra-Testtenant nachgewiesen.

Die ursprünglichen Terminalresultate wurden anhand ausschließlich nicht sensitiver Felder dokumentiert. Objekt- und Tenant-IDs gehören nicht in die öffentliche Evidence.

## RBAC und Notfallzugang

- Das Least-Privilege-Zielmodell ist in [`LAB-01-RBAC-MATRIX.md`](LAB-01-RBAC-MATRIX.md) dokumentiert.
- Das öffentliche, secretsfreie Notfallkonzept ist in [`LAB-01-BREAK-GLASS.md`](LAB-01-BREAK-GLASS.md) dokumentiert.
- Global Administrator ist nicht als Rolle für tägliche Administration vorgesehen.
- Conditional Access wird in LAB-01 noch nicht produktiv aktiviert.

## Evidence-Status

Die Baseline-Ausführung und die Governance-Dokumentation sind abgeschlossen. Die fünf Originalbilder werden mit dem [sicheren Capture-Runbook](../docs/LAB-01-EVIDENCE-CAPTURE.md) erstellt und im [Evidence-Manifest](LAB-01-evidence-manifest.md) nachverfolgt.

LAB-01 bleibt bis zur Aufnahme, Redaction-Prüfung und Ablage aller fünf echten PNG-Artefakte formal offen. Historische Evidence wird nicht nachgestellt.

## Sicherheitsaspekt

- Keine Secrets, Kennwörter, Tenant-IDs, Objekt-IDs oder personenbezogenen Kontodaten im Repository.
- Schreibende Änderungen vorab mit `-WhatIf` validiert.
- Getrennte Pilotgruppen begrenzen spätere Conditional-Access- und Intune-Rollouts.
- Rollenmodell folgt Least Privilege; tägliche Administration nutzt keine pauschale Global-Administrator-Rolle.
