# LAB-01 – NordWerk GmbH Tenant Baseline

## Ziel

Eine saubere, reproduzierbare Ausgangsbasis für das EntraFlow Enterprise IT Lab schaffen. Dieses Lab wird ausschließlich mit Testkonten und Testgeräten betrieben.

## 1. Testtenant bereitstellen

Empfohlener Weg: Microsoft Intune 30-Tage-Testversion. Die Registrierung erstellt einen neuen Microsoft-Entra-Tenant und stellt die für das Intune-Lab benötigte Umgebung bereit.

Bei der Registrierung:

- Firmenname: `NordWerk GmbH`
- Land/Region: eigenes tatsächliches Land auswählen
- Tenant-Domain: einen verfügbaren neutralen Lab-Namen verwenden
- Das zuerst angelegte Administratorkonto ausschließlich für die Lab-Verwaltung verwenden
- Kennwörter, Tenant-IDs, Client-Secrets und Zertifikate niemals in GitHub speichern

## 2. PowerShell vorbereiten

```powershell
pwsh --version
Install-Module Microsoft.Graph -Scope CurrentUser
```

Repository klonen bzw. aktualisieren:

```bash
git clone https://github.com/haydarkozat/entraflow.git
cd entraflow/enterprise-lab/scripts
```

Microsoft Graph verbinden:

```powershell
./Connect-EntraLab.ps1 | Out-Null
```

Die Verbindung für eine öffentliche Evidence-Aufnahme nicht mit `Get-MgContext` ausgeben: Dieser Kontext enthält Tenant-, Client- und Kontoinformationen.

## 3. Baseline-Gruppen zunächst simulieren

```powershell
./Initialize-TenantBaseline.ps1 -WhatIf |
    Select-Object DisplayName, Status, Action |
    Format-Table -AutoSize
```

Erwartete Zielgruppen:

- `SG-Dept-IT`
- `SG-Dept-HR`
- `SG-Dept-Finance`
- `SG-Dept-Sales`
- `SG-Dept-Operations`
- `GRP-CA-Pilot`
- `GRP-Devices-Pilot`

## 4. Baseline-Gruppen erstellen

Nach Kontrolle der `-WhatIf`-Ausgabe:

```powershell
$result = ./Initialize-TenantBaseline.ps1
$result |
    Select-Object DisplayName, Status, Action |
    Sort-Object DisplayName |
    Format-Table -AutoSize
```

## 5. Idempotenz verifizieren

```powershell
$check = ./Initialize-TenantBaseline.ps1
$check |
    Select-Object DisplayName, Status, Action |
    Sort-Object DisplayName |
    Format-Table -AutoSize
```

Erfolgskriterium: Genau sieben eindeutige Gruppen liefern `Status = Existing` und `Action = None`. Der vollständige maschinenlesbare PASS-Check steht in [`LAB-01-EVIDENCE-CAPTURE.md`](LAB-01-EVIDENCE-CAPTURE.md).

## 6. Evidence

LAB-01 benötigt fünf echte, redigierte PNG-Artefakte:

1. `LAB-01-01-tenant-overview.png`
2. `LAB-01-02-baseline-groups.png`
3. `LAB-01-03-whatif.png`
4. `LAB-01-04-created.png`
5. `LAB-01-05-idempotency.png`

Zusätzliche Dokumentation:

- `evidence/LAB-01-baseline.md`
- `evidence/LAB-01-RBAC-MATRIX.md`
- `evidence/LAB-01-BREAK-GLASS.md`
- `evidence/LAB-01-evidence-manifest.md`

Das sichere Capture- und Redaction-Verfahren steht in [`LAB-01-EVIDENCE-CAPTURE.md`](LAB-01-EVIDENCE-CAPTURE.md). LAB-01 gilt erst als abgeschlossen, wenn alle fünf Originalbilder geprüft, abgelegt und im Manifest als `Captured and redacted` markiert sind.

## Sicherheitsentscheidung

LAB-01 aktiviert keine Conditional-Access-Policy. Zuerst werden Pilotgruppen, RBAC-Zielmodell und Notfallkonzept dokumentiert. Spätere Policies werden kontrolliert und soweit verfügbar zunächst im Report-only-Modus getestet. Global Administrator ist keine Rolle für tägliche Administration.
