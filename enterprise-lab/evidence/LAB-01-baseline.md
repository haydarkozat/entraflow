# LAB-01 Evidence – Tenant Baseline & RBAC

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-01  
**Status:** Completed  
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
- Separates tägliches Administrationskonto angelegt und nach Least-Privilege-Prinzip mit `Groups Administrator` ausgestattet.
- Global-Administrator-Konto bleibt für Tenant-Setup und Break-Glass-/Notfallzwecke reserviert.

## Ergebnis

- Tenant erfolgreich erreichbar: `Ja`
- Erwartete Gruppen: `7`
- Tatsächlich erstellte Gruppen: `7`
- Zweiter Script-Lauf ohne Duplikate: `Ja`
- Verwendete Script-Datei: `Initialize-TenantBaseline.ps1`
- Separate Daily-Admin-Identität: `Ja`
- Least-Privilege-Rolle für tägliche Gruppenverwaltung: `Groups Administrator`

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

### RBAC-/Berechtigungsmatrix

| Administrationszweck | Rolle | Verwendung |
|---|---|---|
| Tenant-Setup / Notfall | `Global Administrator` | Nur für tenantweite Konfigurationen und Notfallzugriff |
| Tägliche Gruppenverwaltung | `Groups Administrator` | Standardkonto für Gruppenverwaltung |
| Benutzer-Lifecycle | `User Administrator` | Erst bei LAB-02/03/04 nach Bedarf zuweisen |
| Intune-Geräteverwaltung | `Intune Administrator` | Erst bei den Intune-Labs nach Bedarf zuweisen |

Die zusätzlichen Rollen werden bewusst **nicht vorab** dauerhaft vergeben. Sie werden erst dann aktiviert/zugewiesen, wenn ein konkretes Lab-Szenario sie benötigt.

### Technischer Nachweis

Der erste produktive Lauf lieferte für alle sieben Zielgruppen den Status `Created`. Der unmittelbar danach ausgeführte zweite Lauf erkannte dieselben Objekte und lieferte für alle Gruppen `Existing` mit `Action = None`. Damit wurde die Idempotenz des Baseline-Skripts in einem realen Microsoft-Entra-Testtenant nachgewiesen.

Die Gruppenliste wurde zusätzlich im Microsoft-Entra-Portal visuell geprüft. Für die veröffentlichte Evidence werden Object IDs, Tenant-IDs, Benutzer-E-Mail-Adressen und andere Identifikatoren nicht offengelegt.

## Sicherheitsaspekt

- Keine Secrets, Kennwörter, Tenant-IDs oder personenbezogenen Kontodaten im Repository.
- Schreibende Änderungen vorab mit `-WhatIf` validiert.
- Conditional Access wird in LAB-01 noch nicht produktiv aktiviert.
- Getrennte Pilotgruppen für spätere Conditional-Access- und Intune-Rollouts vorhanden.
- Tägliche Administration erfolgt nicht mit Global Administrator, sondern mit einer auf Gruppenverwaltung beschränkten Rolle.
- Höhere Rollen werden nur bei konkretem Bedarf und zeitlich/funktional begrenzt verwendet.

## Evidence-Artefakte

- Redigierte Gruppenübersicht: erstellt und geprüft
- `-WhatIf`-Ausführung: erfolgreich
- Produktiver Baseline-Lauf: erfolgreich
- Idempotenz-Nachweis: erfolgreich
- RBAC-/Berechtigungsmatrix: dokumentiert

> Vor dem Commit von Screenshots auf Tenant-IDs, E-Mail-Adressen, QR-Codes, Secrets, Telefonnummern und andere personenbezogene bzw. sicherheitsrelevante Daten prüfen und nötigenfalls redigieren.
