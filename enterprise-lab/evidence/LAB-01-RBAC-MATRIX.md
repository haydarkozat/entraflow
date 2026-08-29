# LAB-01 – RBAC- und Berechtigungsmatrix

**Scope:** NordWerk GmbH Enterprise IT Lab  
**Prinzip:** Least Privilege, getrennte Admin- und Alltagskonten, keine Zugangsdaten im Repository

Diese Matrix dokumentiert das Zielmodell. Sie veröffentlicht weder konkrete Rollenzuweisungen noch Konto-, Tenant- oder Objekt-IDs.

| Administrative Aufgabe | Zielrolle | Einsatz | Nicht vorgesehen |
|---|---|---|---|
| Benutzer- und Gruppen-Lifecycle | User Administrator | Testbenutzer verwalten; Gruppenmitgliedschaften pflegen | Conditional Access, globale Tenant-Konfiguration |
| Gruppen-Baseline und Pilotgruppen | Groups Administrator | Sicherheitsgruppen erstellen und verwalten | Benutzerlizenzen, Authentifizierungsmethoden |
| Intune-Geräte und Policies | Intune Administrator | Testgeräte, Compliance und Gerätekonfiguration verwalten | Entra-weite Rollen- oder Domainverwaltung |
| Conditional-Access-Pilot | Conditional Access Administrator | Policies entwerfen, im kontrollierten Scope testen und später Report-only auswerten | Globale Administration außerhalb von CA |
| Security-Auswertung | Security Reader | Security-Signale und relevante Berichte lesen | Schreibende Änderungen |
| Audit- und Sign-in-Auswertung | Reports Reader | Audit-/Anmeldeberichte lesen | Benutzer-, Gruppen- oder Policy-Änderungen |
| Rollenverwaltung | Privileged Role Administrator | Rollen nur bei begründetem Lab-Schritt zuweisen und entfernen | tägliche Standardadministration |
| Tenant-Ersteinrichtung / Recovery | Global Administrator | Nur wenn technisch zwingend notwendig oder für dokumentierte Wiederherstellung | tägliche Administration |

## Betriebsentscheidungen

- Für tägliche Arbeit wird kein Global-Administrator-Konto verwendet.
- Administrative Tätigkeiten erfolgen mit einem separaten Lab-Administratorkonto.
- Rollen werden nur für den jeweiligen Aufgabenbereich vorgesehen.
- Wo Lizenz und Tenant-Funktionen dies unterstützen, sollen privilegierte Rollen zeitlich begrenzt aktiviert werden.
- Rollen- und Policy-Änderungen werden durch Audit-Logs und redigierte Evidence nachvollziehbar gemacht.
- Die Pilotgruppen `GRP-CA-Pilot` und `GRP-Devices-Pilot` begrenzen spätere Rollouts.
- LAB-01 aktiviert noch keine Conditional-Access-Policy.

## Verifikation

Die Dokumentation gilt als abgeschlossen, wenn:

- die sieben Baseline-Gruppen existieren,
- der zweite Script-Lauf keine Duplikate erzeugt,
- das Rollenmodell und das Break-Glass-Konzept dokumentiert sind,
- die fünf Evidence-Bilder geprüft und im Manifest als `Captured and redacted` markiert wurden.
