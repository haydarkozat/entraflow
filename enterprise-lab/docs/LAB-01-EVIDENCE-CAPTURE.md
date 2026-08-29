# LAB-01 – Evidence Capture Guide

Dieses Runbook erzeugt die fünf noch benötigten Evidence-Artefakte für LAB-01. Es werden ausschließlich Anzeigenamen und nicht sensitive Statuswerte gezeigt. Objekt-IDs, Tenant-IDs, Konten, E-Mail-Adressen, Tokens und Secrets dürfen nicht im Bild erscheinen.

## Benötigte Artefakte

| Nr. | Dateiname | Nachweis |
|---|---|---|
| 1 | `LAB-01-01-tenant-overview.png` | Testtenant ist erreichbar |
| 2 | `LAB-01-02-baseline-groups.png` | Alle sieben Baseline-Gruppen existieren |
| 3 | `LAB-01-03-whatif.png` | Schreibende Aktion wurde mit `-WhatIf` geprüft |
| 4 | `LAB-01-04-created.png` | Erstlauf hat die Zielgruppen erstellt |
| 5 | `LAB-01-05-idempotency.png` | Wiederholung meldet `Existing` / `None` |

Die PNG-Dateien werden erst nach einer echten Ausführung im Testtenant in `enterprise-lab/evidence/` gespeichert. Platzhalter oder nachgestellte Resultate gelten nicht als technische Evidence.

## 1. Sichere Vorbereitung

Repository aktualisieren und im Script-Verzeichnis arbeiten:

```powershell
Set-Location ./enterprise-lab/scripts
./Connect-EntraLab.ps1 | Out-Null
```

Vor jedem Screenshot:

- Browser- und Terminalfenster so zuschneiden, dass nur der relevante Bereich sichtbar ist.
- Profilmenüs, Adressleisten, Benachrichtigungen und andere Tabs schließen oder ausblenden.
- Keine Ausgabe von `Get-MgContext`, `TenantId`, `Account`, `ClientId`, `ObjectId` oder vollständigen URLs aufnehmen.
- Das Bild lokal prüfen und erst anschließend in Git aufnehmen.

## 2. Tenant-Übersicht

Im Microsoft Entra Admin Center die Übersichtsseite öffnen. Nur den Tenant-Anzeigenamen und den sichtbaren Erreichbarkeitszustand zeigen.

Vor dem Speichern vollständig redigieren:

- Tenant-ID und primäre Domain
- Konto- und E-Mail-Adresse
- Benutzer-/Objekt-IDs
- Profilbild, QR-Code und Benachrichtigungen

Speichern als `LAB-01-01-tenant-overview.png`.

## 3. Gruppenübersicht

Die Entra-Gruppenliste nach den Baseline-Namen filtern. Alternativ eine sichere Terminalansicht erzeugen:

```powershell
$expectedNames = @(
    'GRP-CA-Pilot',
    'GRP-Devices-Pilot',
    'SG-Dept-Finance',
    'SG-Dept-HR',
    'SG-Dept-IT',
    'SG-Dept-Operations',
    'SG-Dept-Sales'
)

Get-MgGroup -All -Property DisplayName |
    Where-Object DisplayName -In $expectedNames |
    Select-Object DisplayName |
    Sort-Object DisplayName |
    Format-Table -AutoSize
```

Die Ausgabe muss genau sieben eindeutige Anzeigenamen enthalten. Speichern als `LAB-01-02-baseline-groups.png`.

## 4. WhatIf-Nachweis

Hinweis: Bei einem bereits aufgebauten Tenant erkennt das Script vorhandene Gruppen vor `ShouldProcess`. Ein nachträglicher `-WhatIf`-Lauf kann daher `Existing` statt simulierter Erstellung zeigen. Für LAB-01 gilt der bereits vor dem Erstlauf durchgeführte `-WhatIf`-Nachweis; vorhandene Originalaufnahme verwenden.

Sicherer Befehl für einen neuen, leeren Testtenant:

```powershell
./Initialize-TenantBaseline.ps1 -WhatIf |
    Select-Object DisplayName, Status, Action |
    Format-Table -AutoSize
```

Speichern als `LAB-01-03-whatif.png`. Wenn keine Originalaufnahme existiert, im Manifest transparent als `Not captured` kennzeichnen; keinen Screenshot nachstellen.

## 5. Erstlauf

Die bereits beim produktiven Erstlauf erzeugte Ausgabe verwenden:

```powershell
$result |
    Select-Object DisplayName, Status, Action |
    Sort-Object DisplayName |
    Format-Table -AutoSize
```

Erwartung: sieben Zeilen mit `Status = Created`. Speichern als `LAB-01-04-created.png`.

## 6. Idempotenz erneut verifizieren

Dieser Schritt ist sicher wiederholbar, weil vorhandene Gruppen nicht neu angelegt werden:

```powershell
$check = ./Initialize-TenantBaseline.ps1
$check |
    Select-Object DisplayName, Status, Action |
    Sort-Object DisplayName |
    Format-Table -AutoSize

$expectedNames = @(
    'GRP-CA-Pilot',
    'GRP-Devices-Pilot',
    'SG-Dept-Finance',
    'SG-Dept-HR',
    'SG-Dept-IT',
    'SG-Dept-Operations',
    'SG-Dept-Sales'
)

$valid = (
    $check.Count -eq 7 -and
    @($check | Where-Object {
        $_.DisplayName -notin $expectedNames -or
        $_.Status -ne 'Existing' -or
        $_.Action -ne 'None'
    }).Count -eq 0 -and
    @($check.DisplayName | Sort-Object -Unique).Count -eq 7
)

if (-not $valid) {
    throw 'LAB-01 idempotency verification failed.'
}

'LAB-01 idempotency verification: PASS'
```

Speichern als `LAB-01-05-idempotency.png`. Der Screenshot darf nur `DisplayName`, `Status`, `Action` und die PASS-Zeile enthalten.

## 7. Prüfung vor dem Commit

Jedes Bild lokal bei 100 % Zoom kontrollieren. Nicht committen, wenn eines der folgenden Muster sichtbar ist:

- GUIDs oder andere Objekt-/Tenant-IDs
- E-Mail-Adressen oder User Principal Names
- Domains, Tokens, Secrets oder Zertifikatsdaten
- echte Namen, Telefonnummern oder personenbezogene Daten
- Browserprofil, offene Tabs oder lokale Dateipfade mit Benutzernamen

Nach der Prüfung die Statuswerte in `LAB-01-evidence-manifest.md` aktualisieren.
