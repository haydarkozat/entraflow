# LAB-02 Evidence – Joiner / CSV Onboarding

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-02  
**Status:** Onboarding executed; portal verification pending  
**Date:** 2026-08-29

## Ziel

Mehrere fiktive Mitarbeitende reproduzierbar per PowerShell und Microsoft Graph in Microsoft Entra ID anlegen und anschließend die Duplikatvermeidung nachweisen.

## Durchführung

1. `sample-data/users.csv` wurde als `users-lab.csv` für die Lab-Domain vorbereitet.
2. Microsoft Graph wurde per delegierter Authentifizierung verbunden.
3. `New-LabUsersFromCsv.ps1 -WhatIf` wurde ausgeführt.
4. Die Simulation zeigte exakt acht geplante Benutzeranlagen.
5. Das Onboarding-Skript wurde anschließend gegen den Testtenant ausgeführt.
6. Ein weiterer Script-Lauf wurde unmittelbar danach zur Idempotenzprüfung durchgeführt.

## Ergebnis

- Geplante Testbenutzer: `8`
- `-WhatIf` validiert: `Ja`
- Benutzer im Tenant vorhanden: `Ja`
- Zweiter Lauf ohne Duplikate: `Ja`
- Zweiter Lauf: `8 x Skipped`
- Grund: `Benutzer existiert bereits.`
- Verwendete Script-Datei: `New-LabUsersFromCsv.ps1`

### Idempotenznachweis

Beim erneuten Lauf wurden alle acht vorgesehenen Testidentitäten erkannt und übersprungen. Für jeden Datensatz wurde `Status = Skipped` mit `Reason = Benutzer existiert bereits.` zurückgegeben. Damit ist nachgewiesen, dass ein wiederholter CSV-Onboarding-Lauf keine doppelten Microsoft-Entra-Benutzer erzeugt.

## Sicherheitsprinzipien

- Ausschließlich fiktive Testidentitäten verwendet.
- Keine Initialkennwörter, Tenant-IDs oder personenbezogenen Echtdaten im Repository.
- Schreibende Aktion vorab mit `-WhatIf` geprüft.
- Initialkennwörter werden nicht als Evidence gespeichert oder veröffentlicht.
- Höhere Entra-Rollen werden nur bei tatsächlichem Bedarf verwendet.
- Screenshots werden vor Veröffentlichung redigiert.

## Noch offene Verifikation

- Entra-Portal: acht Testbenutzer sichtbar
- Stichprobe der Benutzerattribute: Display Name, Department, Job Title, Usage Location
- Zuordnung der Benutzer zu den fünf Department-Gruppen

## Evidence-Artefakte

- `LAB-02-01-whatif-terminal.png` – optional, redigiert
- `LAB-02-02-created-users.png` – noch offen
- `LAB-02-03-idempotency-terminal.png` – optional, redigiert
- anonymisierter Ergebnisexport – optional

> Keine Kennwörter oder unveränderten Object IDs in Evidence-Dateien veröffentlichen.
