# LAB-02 Evidence – Joiner / CSV Onboarding

**Environment:** NordWerk GmbH – Enterprise IT Lab  
**Scenario:** LAB-02  
**Status:** Ready to execute  
**Date:** 2026-08-29

## Ziel

Mehrere fiktive Mitarbeitende reproduzierbar per PowerShell und Microsoft Graph in Microsoft Entra ID anlegen und anschließend die Duplikatvermeidung nachweisen.

## Geplanter Ablauf

1. `sample-data/users.csv` auf die echte Lab-Domain anpassen.
2. Verbindung mit Microsoft Graph herstellen.
3. `New-LabUsersFromCsv.ps1 -WhatIf` ausführen.
4. Geplante Änderungen prüfen.
5. Script ohne `-WhatIf` ausführen.
6. Benutzer im Entra-Portal verifizieren.
7. Script ein zweites Mal ausführen und nachweisen, dass vorhandene Benutzer übersprungen werden.
8. Benutzer anschließend ihren Department-Gruppen zuordnen.

## Sicherheitsprinzipien

- Ausschließlich fiktive Testidentitäten verwenden.
- Keine Initialkennwörter, Tenant-IDs oder personenbezogenen Daten committen.
- Schreibende Aktion immer zuerst mit `-WhatIf` prüfen.
- Höhere Entra-Rollen nur bei tatsächlichem Bedarf verwenden.
- Screenshots vor Veröffentlichung redigieren.

## Erfolgskriterien

- Vorgesehene Testbenutzer werden genau einmal angelegt.
- Zweiter Lauf erzeugt keine Duplikate.
- Alle Benutzer besitzen die erwarteten Attribute: Display Name, Department, Job Title, Usage Location.
- Ergebnis kann im Entra-Portal und per Microsoft Graph nachvollzogen werden.

## Evidence-Artefakte

- `LAB-02-01-whatif-terminal.png`
- `LAB-02-02-created-users.png`
- `LAB-02-03-idempotency-terminal.png`
- anonymisierter Ergebnisexport

> Keine Kennwörter oder unveränderten Object IDs in Evidence-Dateien veröffentlichen.
