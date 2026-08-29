# LAB-01 – Break-Glass-Konzept

Dieses Dokument beschreibt ausschließlich das Sicherheits- und Betriebsmodell. Kontonamen, Domains, Telefonnummern, Kennwörter, Tenant-IDs, Recovery-Codes und andere Zugangsdaten werden außerhalb des öffentlichen Repositorys geschützt verwaltet.

## Zweck

Ein Notfallkonto stellt den administrativen Zugang zum Testtenant wieder her, wenn reguläre administrative Konten oder Authentifizierungswege nicht verfügbar sind.

## Design

- Ein dediziertes, cloud-only Notfallkonto wird ausschließlich für den Testtenant vorgesehen.
- Das Konto ist nicht mit einem persönlichen Alltagskonto identisch.
- Es wird nicht für Routineadministration, Skriptausführung oder Browser-Sitzungen verwendet.
- Zugangsdaten werden in einem geeigneten Passwortmanager bzw. einem kontrollierten Offline-Verfahren gespeichert.
- Eine konkrete Conditional-Access-Ausnahme wird erst zusammen mit den späteren CA-Labs implementiert und gegen Lockout-Risiken geprüft.
- Das Konto erhält keine produktiven Lizenzen oder fachlichen Gruppenmitgliedschaften, sofern technisch nicht erforderlich.
- Nutzung und Änderungen werden kontrolliert und dokumentiert.

## Kontrollprozess

1. Verfügbarkeit in einem festgelegten Intervall prüfen.
2. Nur einen interaktiven Test im Testtenant durchführen.
3. Anmelde- und Audit-Ereignisse kontrollieren.
4. Prüfung intern protokollieren, ohne sensitive Felder öffentlich zu speichern.
5. Bei jeder Nutzung reguläre Adminzugänge und betroffene Policies prüfen.
6. Zugangsdaten nach einem echten Notfalleinsatz rotieren.

## Öffentliche Evidence

Im öffentlichen Repository werden nur folgende Aussagen dokumentiert:

- Konzept vorhanden: `Ja`
- Routineeinsatz ausgeschlossen: `Ja`
- Sensible Zugangsdaten im Repository: `Nein`
- Test- und Review-Prozess definiert: `Ja`

Ein Screenshot des Kontos, seiner Adresse, Objekt-ID oder Authentifizierungsmethoden ist ausdrücklich kein öffentliches LAB-01-Artefakt.
