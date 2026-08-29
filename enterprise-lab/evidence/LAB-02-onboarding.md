# LAB-02 Evidence – Joiner / CSV Onboarding

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-02  
**Status:** Completed  
**Date:** 2026-08-29

## Ziel

Mehrere fiktive Mitarbeitende reproduzierbar per PowerShell und Microsoft Graph in Microsoft Entra ID anlegen, ihre Attribute und Portal-Sichtbarkeit prüfen, sie den passenden Department-Gruppen zuordnen und Duplikatvermeidung nachweisen.

## Durchführung

1. `sample-data/users.csv` wurde als `users-lab.csv` für die Lab-Domain vorbereitet.
2. Microsoft Graph wurde per delegierter Authentifizierung verbunden.
3. `New-LabUsersFromCsv.ps1 -WhatIf` zeigte exakt acht geplante Benutzeranlagen.
4. Das Onboarding-Skript wurde gegen den Testtenant ausgeführt.
5. Ein erneuter Lauf erkannte alle acht Benutzer und übersprang sie ohne Duplikate.
6. Die acht Testbenutzer wurden im Entra-Portal verifiziert.
7. `Set-DepartmentGroupMemberships.ps1 -WhatIf` zeigte acht geplante Department-Zuordnungen.
8. Die acht Benutzer wurden entsprechend ihrer CSV-Department-Werte den fünf `SG-Dept-*` Gruppen zugeordnet.
9. Ein erneuter Membership-Lauf erkannte alle acht vorhandenen Mitgliedschaften und fügte keine Duplikate hinzu.

## Ergebnis

- Geplante Testbenutzer: `8`
- `-WhatIf` Benutzeranlage validiert: `Ja`
- Testbenutzer im Entra-Portal sichtbar: `8`
- Benutzer-Onboarding zweiter Lauf: `8 x Skipped`
- Grund: `Benutzer existiert bereits.`
- Department-Mitgliedschaften erster Lauf: `8 x Added`
- Department-Mitgliedschaften zweiter Lauf: `8 x Existing`
- Grund: `Membership already exists.`
- Verwendete Scripts:
  - `New-LabUsersFromCsv.ps1`
  - `Set-DepartmentGroupMemberships.ps1`

### Department-Zuordnung

| Testidentität | Zielgruppe | Erstlauf | Zweitlauf |
|---|---|---|---|
| Anna Berger | `SG-Dept-HR` | `Added` | `Existing` |
| Jonas Weber | `SG-Dept-Finance` | `Added` | `Existing` |
| Sophie Wagner | `SG-Dept-Finance` | `Added` | `Existing` |
| Daniel Hoffmann | `SG-Dept-IT` | `Added` | `Existing` |
| Felix Braun | `SG-Dept-IT` | `Added` | `Existing` |
| Mia Schneider | `SG-Dept-Operations` | `Added` | `Existing` |
| Laura Klein | `SG-Dept-Sales` | `Added` | `Existing` |
| Lukas Fischer | `SG-Dept-Sales` | `Added` | `Existing` |

## Idempotenznachweis

Der wiederholte CSV-Onboarding-Lauf erzeugte keine doppelten Benutzer. Ebenso erzeugte der wiederholte Department-Membership-Lauf keine doppelten Gruppenmitgliedschaften. Damit sind sowohl Benutzerbereitstellung als auch gruppenbasierte Zugriffszuordnung reproduzierbar und idempotent umgesetzt.

## Sicherheitsprinzipien

- Ausschließlich fiktive Testidentitäten verwendet.
- Keine Initialkennwörter, Tenant-IDs, Object IDs oder personenbezogenen Echtdaten im Repository.
- Schreibende Aktionen vorab mit `-WhatIf` geprüft.
- Initialkennwörter werden nicht als Evidence gespeichert oder veröffentlicht.
- Screenshots werden vor Veröffentlichung redigiert.
- Administrative Berechtigungen werden nach Least-Privilege-Prinzip vergeben.

## Evidence-Artefakte

- `LAB-02-01-whatif-terminal.png` – optional, redigiert
- `LAB-02-02-created-users.png` – Portal-Verifikation vorhanden; vor Veröffentlichung redigieren
- `LAB-02-03-idempotency-terminal.png` – optional, redigiert
- `LAB-02-04-department-memberships.png` – optional, redigiert

> Keine Kennwörter, unveränderten Object IDs oder administrativen Kontokennungen in Evidence-Dateien veröffentlichen.
