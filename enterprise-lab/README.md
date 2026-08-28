# EntraFlow Enterprise IT Lab v2

> **Microsoft 365 · Microsoft Entra ID · Microsoft Intune · Windows 11 · PowerShell · Microsoft Graph**
>
> Ein praxisorientiertes Portfolio-Lab, das typische Aufgaben eines IT-Systemadministrators in einem mittelständischen Unternehmen reproduzierbar dokumentiert.

## Ziel

Dieses Lab schließt die Lücke zwischen theoretischen Kenntnissen und **nachweisbarer praktischer Anwendung**. Es simuliert den IT-Betrieb der fiktiven **NordWerk GmbH** mit rund 100 Mitarbeitenden in den Bereichen IT, HR, Finance, Sales und Operations.

Das Lab ist bewusst als **Portfolio-/Testumgebung** gekennzeichnet. Es soll keine nicht vorhandene Produktionserfahrung vortäuschen. Der Nachweis entsteht durch selbst ausgeführte Konfigurationen, PowerShell-Skripte, Screenshots, Exportdateien, Audit-Logs und reproduzierbare Runbooks.

## Zielarchitektur

```mermaid
flowchart LR
    ADM[IT Administrator] --> PS[PowerShell 7]
    PS --> MG[Microsoft Graph PowerShell SDK]
    MG --> ENTRA[Microsoft Entra ID]
    MG --> INTUNE[Microsoft Intune]
    ENTRA --> M365[Microsoft 365]
    INTUNE --> WIN[Windows 11 Endpoints]
    CA[Conditional Access] --> ENTRA
    COMP[Compliance Policies] --> INTUNE
    INTUNE --> APP[Win32 App Deployment]
    INTUNE --> UPD[Windows Update Rings]
    INTUNE --> SEC[Endpoint Security / BitLocker]
    LOG[Evidence & Reports] <-- PS
```

## Was praktisch nachgewiesen wird

| Kompetenz | Nachweis im Lab |
|---|---|
| Entra ID Administration | Benutzer, Gruppen, Rollenmodell, Joiner/Mover/Leaver |
| Microsoft 365 Administration | Identitäts- und Lizenz-Lifecycle, Governance-Reports |
| Intune | Enrollment, Compliance, Konfigurationsprofile, App-Deployment, Update Rings |
| Conditional Access | MFA, compliant device, Report-only/Test-Rollout |
| PowerShell | Wiederholbare Admin-Skripte, CSV-Onboarding, Reports, Offboarding |
| Microsoft Graph | Delegated/App-only Authentication, Benutzer- und Gerätereports |
| Security | Least Privilege, MFA, BitLocker, Noncompliance-Reaktion |
| Operations | Incident-/Leaver-Runbooks, Audit-Trail, Evidence-Paket |

## Die 12 Enterprise-Szenarien

1. **Tenant Baseline & RBAC** – Adminrollen, Notfallkonto, Testgruppen und Namenskonventionen.
2. **Joiner** – Benutzer aus CSV per PowerShell anlegen.
3. **Mover** – Abteilungs-/Rollenwechsel mit Gruppen- und Zugriffsanpassung.
4. **Leaver** – Konto sperren, Lizenzen zurückgeben und Gruppenmitgliedschaften bereinigen.
5. **MFA mit Conditional Access** – kontrollierter Rollout über eine Pilotgruppe.
6. **Compliant Device Access** – Zugriff auf Unternehmensressourcen nur von compliant Devices.
7. **Windows 11 Compliance** – Mindestanforderungen und Noncompliance-Aktionen.
8. **BitLocker / Endpoint Security** – Verschlüsselungsrichtlinie für Unternehmensgeräte.
9. **Windows Update Ring** – gestaffeltes Update-Management für Pilot und Produktion.
10. **Win32 App Deployment** – Paketierung, Detection Rule, Zuweisung und Monitoring.
11. **Lost Device Incident** – Gerät identifizieren und Retire/Wipe-Prozess in einer Testumgebung dokumentieren.
12. **Operations Reporting** – Inaktive Benutzer, Lizenzverbrauch und Device Compliance per PowerShell auswerten.

Die vollständigen Runbooks stehen in [`docs/SCENARIOS.md`](docs/SCENARIOS.md).

## Repository-Struktur

```text
enterprise-lab/
├── README.md
├── docs/
│   └── SCENARIOS.md
├── evidence/
│   └── README.md
├── sample-data/
│   └── users.csv
└── scripts/
    ├── Connect-EntraLab.ps1
    ├── New-LabUsersFromCsv.ps1
    ├── Get-InactiveUsers.ps1
    ├── Get-LicenseReport.ps1
    ├── Get-DeviceComplianceReport.ps1
    └── Invoke-LeaverOffboarding.ps1
```

## Voraussetzungen

- PowerShell 7
- Ein eigener Microsoft-365-/Entra-Testtenant mit den für die jeweilige Funktion erforderlichen Lizenzen
- Microsoft Graph PowerShell SDK
- Für Intune-Szenarien mindestens ein **Testgerät** oder eine dafür vorgesehene Windows-11-Test-VM
- Keine produktiven Konten oder Geräte für destruktive Tests verwenden

Module installieren:

```powershell
Install-Module Microsoft.Graph -Scope CurrentUser
```

Lab-Verbindung herstellen:

```powershell
./scripts/Connect-EntraLab.ps1
```

Benutzeranlage zunächst sicher simulieren:

```powershell
./scripts/New-LabUsersFromCsv.ps1 `
  -CsvPath ./sample-data/users.csv `
  -WhatIf
```

Danach bewusst ausführen:

```powershell
./scripts/New-LabUsersFromCsv.ps1 `
  -CsvPath ./sample-data/users.csv
```

## Evidence statt Behauptung

Jedes Szenario gilt erst dann als **abgeschlossen**, wenn mindestens folgende Artefakte vorhanden sind:

- Konfigurations-Screenshot ohne Secrets oder personenbezogene Echtdaten
- ausgeführter Befehl bzw. Script-Name
- anonymisierter Ergebnis-/CSV-Export
- kurze Beschreibung: **Problem → Maßnahme → Ergebnis → Sicherheitsaspekt**
- Datum und Lab-Szenario-ID

Siehe [`evidence/README.md`](evidence/README.md).

## Sicherheitsprinzipien

- Schreibende Skripte unterstützen `-WhatIf` bzw. `ShouldProcess`.
- Keine Client Secrets, Kennwörter, Zertifikate oder Tenant-Geheimnisse im Repository speichern.
- Für Automatisierung bevorzugt Zertifikatsauthentifizierung statt Klartext-Secrets verwenden.
- Conditional-Access-Änderungen zuerst auf Pilotgruppen bzw. im Report-only-Modus testen.
- Wipe/Retire ausschließlich auf expliziten Testgeräten durchführen.
- Berechtigungen nach dem Least-Privilege-Prinzip vergeben.

## Recruiter-relevanter Nachweis

Nach Abschluss kann dieses Projekt im Lebenslauf z. B. als **Praxisprojekt** beschrieben werden:

> **Enterprise Microsoft 365 / Entra ID / Intune Lab** – Aufbau und Administration einer reproduzierbaren Unternehmens-Testumgebung mit Entra ID, Intune, Conditional Access, Windows-11-Compliance, App Deployment und PowerShell-/Microsoft-Graph-Automatisierung. Dokumentation von Joiner/Mover/Leaver, Device Compliance, Lizenz-Governance und Security-Runbooks mit nachvollziehbaren Evidence-Artefakten.

Wichtig: Im CV sollte weiterhin **„Praxisprojekt / Enterprise Lab“** stehen, bis echte berufliche Produktionserfahrung vorliegt.
