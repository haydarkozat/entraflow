# LAB-01 Evidence – Tenant Baseline & RBAC

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-01  
**Status:** Baseline completed; RBAC documentation in progress  
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

## Sicherheitsaspekt

- Keine Secrets, Kennwörter, Tenant-IDs oder personenbezogenen Kontodaten im Repository.
- Schreibende Änderungen vorab mit `-WhatIf` validiert.
- Conditional Access wird in LAB-01 noch nicht produktiv aktiviert.
- Getrennte Pilotgruppen für spätere Conditional-Access- und Intune-Rollouts vorhanden.
- Rollenvergabe und tägliche Administration werden im nächsten LAB-01-Schritt nach Least-Privilege-Prinzip dokumentiert.

## Noch offene Evidence-Artefakte

- `LAB-01-01-tenant-overview.png`
- `LAB-01-02-baseline-groups.png`
- optional redigierte Terminal-Screenshots für `-WhatIf`, Erstellung und Idempotenz
- RBAC-/Berechtigungsmatrix

> Vor dem Commit von Screenshots auf Tenant-IDs, E-Mail-Adressen, QR-Codes, Secrets, Telefonnummern und andere personenbezogene bzw. sicherheitsrelevante Daten prüfen und nötigenfalls redigieren.
