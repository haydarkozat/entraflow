# LAB-01 Evidence – Tenant Baseline & RBAC

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-01  
**Status:** In progress  
**Date:** YYYY-MM-DD

## Problem

Eine neue Microsoft-Enterprise-Testumgebung benötigt vor Benutzer-, Geräte- und Conditional-Access-Konfigurationen eine kontrollierte Ausgangsbasis mit klaren Gruppen, Pilot-Scope und nachvollziehbaren Namenskonventionen.

## Maßnahme

- Microsoft-Entra-/Intune-Testtenant bereitgestellt.
- Fünf Abteilungs-Sicherheitsgruppen angelegt.
- Separate Pilotgruppen für Conditional Access und Intune-Geräte-Policies angelegt.
- Baseline per PowerShell/Microsoft Graph reproduzierbar umgesetzt.
- Schreibende Aktion zunächst mit `-WhatIf` geprüft.

## Ergebnis

Nach Abschluss hier dokumentieren:

- Tenant erfolgreich erreichbar: `Ja/Nein`
- Erwartete Gruppen: `7`
- Tatsächlich vorhandene Gruppen: `<Anzahl>`
- Zweiter Script-Lauf ohne Duplikate: `Ja/Nein`
- Verwendete Script-Datei: `Initialize-TenantBaseline.ps1`

## Sicherheitsaspekt

- Keine Secrets oder Kennwörter im Repository.
- Conditional Access wird in LAB-01 noch nicht produktiv aktiviert.
- Änderungen zunächst über Pilot-Scope und `-WhatIf` validiert.
- Rollenvergabe nach Least-Privilege-Prinzip weiterentwickelt.

## Evidence-Dateien

Nach eigener Durchführung ergänzen:

- `LAB-01-01-tenant-overview.png`
- `LAB-01-02-baseline-groups.png`
- `LAB-01-03-whatif-terminal.png`
- `LAB-01-04-created-terminal.png`
- `LAB-01-05-idempotency-terminal.png`

> Vor dem Commit Screenshots auf Tenant-IDs, E-Mail-Adressen, QR-Codes, Secrets, Telefonnummern und andere personenbezogene bzw. sicherheitsrelevante Daten prüfen und nötigenfalls redigieren.
