# Enterprise Lab – 12 Praxis-Szenarien

Jedes Szenario wird in einem **eigenen Testtenant** bzw. mit Testkonten/-geräten durchgeführt. Vor schreibenden oder destruktiven Schritten immer Zielobjekt, Scope und Auswirkungen prüfen.

## LAB-01 – Tenant Baseline & RBAC

**Ziel:** Eine saubere Ausgangsbasis für die fiktive NordWerk GmbH schaffen.

**Aufgaben**
- Testgruppen für `IT`, `HR`, `Finance`, `Sales`, `Operations` anlegen.
- Eine Pilotgruppe `GRP-CA-Pilot` und eine Geräte-Pilotgruppe `GRP-Devices-Pilot` anlegen.
- Admin-Aufgaben mit möglichst kleinen Rollen durchführen; Global Administrator nur dort verwenden, wo er technisch notwendig ist.
- Ein Notfall-/Break-Glass-Konzept dokumentieren, ohne Zugangsdaten im Repository zu speichern.
- Namenskonventionen für Gruppen und Policies definieren.

**Evidence**
- Gruppenübersicht
- Rollen-/Berechtigungsmatrix
- `LAB-01-baseline.md` mit Designentscheidungen

---

## LAB-02 – Joiner: CSV-Onboarding per PowerShell

**Ziel:** Mehrere neue Mitarbeitende reproduzierbar anlegen.

**Aufgaben**
- `sample-data/users.csv` an den eigenen Testtenant anpassen.
- `New-LabUsersFromCsv.ps1 -WhatIf` ausführen.
- Erst nach Prüfung ohne `-WhatIf` ausführen.
- Benutzer nach Department gruppieren.
- Ergebnis anonymisiert exportieren.

**Erfolgskriterium:** Alle vorgesehenen Testbenutzer existieren genau einmal; ein zweiter Lauf erzeugt keine Duplikate.

**Evidence**
- Terminalausgabe `-WhatIf`
- Entra-Benutzerübersicht
- anonymisierter Ergebnisexport

---

## LAB-03 – Mover: Abteilungswechsel

**Ziel:** Einen realistischen Rollenwechsel abbilden.

**Beispiel:** Eine Testperson wechselt von Sales nach Finance.

**Aufgaben**
- Department/Job Title anpassen.
- alte fachliche Gruppen entfernen, neue Gruppen hinzufügen.
- effektive Gruppenmitgliedschaften kontrollieren.
- dokumentieren, welche Zugriffsrechte sich dadurch ändern.

**Evidence**
- Vorher-/Nachher-Vergleich
- Gruppenmitgliedschaften
- kurze Least-Privilege-Begründung

---

## LAB-04 – Leaver: Sicheres Offboarding

**Ziel:** Ein Benutzerkonto kontrolliert stilllegen.

**Aufgaben**
- `Invoke-LeaverOffboarding.ps1 -UserPrincipalName <test-user> -WhatIf` ausführen.
- Auswirkungen prüfen.
- Konto deaktivieren und Testlizenzen entfernen.
- optionale Gruppenbereinigung nur im Testtenant durchführen.
- Nachweis erzeugen, dass der Benutzer nicht mehr aktiv ist.

**Evidence**
- `-WhatIf`-Ausgabe
- deaktivierter Account
- Lizenzstatus vorher/nachher
- Offboarding-Runbook

---

## LAB-05 – Conditional Access: MFA-Pilot

**Ziel:** MFA für eine kontrollierte Pilotgruppe erzwingen.

**Aufgaben**
- Policy nur auf `GRP-CA-Pilot` zielen.
- Administrator-/Notfallzugänge sorgfältig berücksichtigen.
- Policy zunächst in Report-only/Testmodus bewerten, soweit für den verwendeten Tenant verfügbar.
- Sign-in-Auswertung und What-If-Analyse dokumentieren.

**Evidence**
- Policy-Konfiguration
- Zielgruppe und Ausschlüsse
- Testergebnis / Sign-in-Auswertung

**Erfolgskriterium:** Pilotbenutzer muss die definierte zusätzliche Authentifizierungsanforderung erfüllen; nicht adressierte Testbenutzer bleiben unbeeinflusst.

---

## LAB-06 – Conditional Access + Compliant Device

**Ziel:** Zugriff auf ausgewählte Unternehmensressourcen an Gerätekonformität koppeln.

**Aufgaben**
- Pilotgruppe verwenden.
- Zugriffskontrolle `Require device to be marked as compliant` für einen kontrollierten Scope konfigurieren.
- compliant und noncompliant Testzustände vergleichen.
- Lockout-Risiko dokumentieren.

**Evidence**
- CA-Policy
- compliant/noncompliant Ergebnis
- Sign-in-Log

---

## LAB-07 – Windows 11 Compliance Policy

**Ziel:** Mindestanforderungen für verwaltete Windows-Geräte definieren.

**Beispiele**
- Firewall aktiv
- Antivirus/Antispyware aktiv, soweit die Testumgebung dies unterstützt
- Mindestbetriebssystemversion
- BitLocker-/Verschlüsselungsanforderung, soweit im gewählten Profil verfügbar
- Aktion bei Noncompliance

**Evidence**
- Policy-Einstellungen
- Device Compliance Status
- Noncompliance-Grund

---

## LAB-08 – Endpoint Security / BitLocker

**Ziel:** Unternehmensdaten auf einem Windows-11-Testgerät verschlüsseln.

**Aufgaben**
- BitLocker-/Disk-Encryption-Richtlinie für Testgeräte konfigurieren.
- Zuweisung ausschließlich an Pilotgeräte.
- Verschlüsselungsstatus kontrollieren.
- Recovery-Key-Prozess und Schutz der Recovery-Informationen dokumentieren; niemals Recovery Keys im öffentlichen Repository speichern.

**Evidence**
- Policy-Zuweisung
- Verschlüsselungsstatus ohne Recovery Key
- kurzer Recovery-Prozess

---

## LAB-09 – Windows Update Ring

**Ziel:** Kontrolliertes Patch-/Update-Management simulieren.

**Aufgaben**
- Pilot- und Produktionsring konzipieren.
- Update-Deadlines, Active Hours und Restart-Verhalten dokumentieren.
- Pilotgruppe zuerst adressieren.
- Status-/Fehlerauswertung aufnehmen.

**Evidence**
- Ring-Konfiguration
- Zuweisungsmodell
- Update-Status

---

## LAB-10 – Win32 App Deployment

**Ziel:** Eine Desktop-Anwendung wie in einem Unternehmensbetrieb paketieren und verteilen.

**Aufgaben**
- Einen legal bezogenen Testinstaller verwenden; keine Binärdateien dieses Installers ins Repo committen.
- `.intunewin`-Paket erstellen.
- Install-/Uninstall-Kommandos dokumentieren.
- Requirement- und Detection-Rule definieren.
- App an Pilotgerät/-benutzer zuweisen.
- Installation und Monitoring prüfen.

**Evidence**
- App-Konfiguration
- Detection Rule
- Intune Installationsstatus
- Anwendung auf dem Testgerät

---

## LAB-11 – Lost Device Incident

**Ziel:** Einen Geräteverlust als Incident-Runbook behandeln.

**Aufgaben**
- betroffenes **Testgerät** anhand Inventarinformationen identifizieren.
- letzte Synchronisation und Compliance prüfen.
- Retire/Wipe-Entscheidung anhand eines kurzen Entscheidungsbaums dokumentieren.
- eine destruktive Aktion nur auf einem explizit dafür vorgesehenen Testgerät durchführen.
- Incident-Zeitlinie erfassen.

**Evidence**
- Inventar-/Device-Daten
- Incident-Runbook
- Ergebnis der Testaktion

---

## LAB-12 – Operations Reporting mit PowerShell

**Ziel:** Wiederkehrende Admin-Aufgaben messbar automatisieren.

**Aufgaben**

```powershell
./scripts/Get-InactiveUsers.ps1 -InactiveDays 30
./scripts/Get-LicenseReport.ps1
./scripts/Get-DeviceComplianceReport.ps1
```

Optional CSV-Exporte erzeugen und in einer lokalen, nicht öffentlichen Evidence-Ablage speichern, falls Tenantdaten enthalten sind.

**Erfolgskriterien**
- inaktive Benutzer nachvollziehbar erkennen
- Lizenzkapazität und -verbrauch zusammenfassen
- compliant/noncompliant Geräte auswerten
- manuelle Portal-Klicks durch reproduzierbare Befehle ersetzen

**Evidence**
- Script-Ausgaben
- Laufzeit/Arbeitsersparnis grob dokumentieren
- Beispiel einer aus dem Report abgeleiteten Admin-Maßnahme

---

# Abschlusskriterium

Das Enterprise Lab ist recruiter-ready, wenn mindestens **8 der 12 Szenarien mit echten eigenen Evidence-Artefakten** abgeschlossen sind und darunter zwingend folgende Szenarien liegen:

- LAB-02 Joiner
- LAB-04 Leaver
- LAB-05 Conditional Access
- LAB-07 Intune Compliance
- LAB-10 Win32 Deployment
- LAB-12 PowerShell Reporting

Damit ist das Projekt nicht nur ein Code-Repository, sondern ein nachvollziehbarer Nachweis praktischer Systemadministration.