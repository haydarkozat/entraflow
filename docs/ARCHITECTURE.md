# Architektur & Entwurfsentscheidungen

Dieses Dokument beschreibt die Bausteine von EntraFlow und die Gründe hinter den
wichtigsten technischen Entscheidungen.

## Leitidee: Reconciliation statt Skripten

Klassische Onboarding-Skripte sind imperativ („lege Konto X an, weise Lizenz Y zu")
und dadurch nicht wiederholbar: Läuft ein Skript zweimal, entstehen Fehler oder Duplikate.
EntraFlow folgt stattdessen dem **deklarativen Reconciliation-Modell** (wie Terraform
oder Kubernetes-Controller):

1. **Soll-Zustand** wird aus dem Schulverwaltungsexport abgeleitet (`DesiredUser`).
2. **Ist-Zustand** wird aus Microsoft Graph gelesen (`GraphUser`, `GraphGroup`, `SubscribedSku`).
3. Der **Planner** bildet die Differenz und erzeugt einen `Plan` aus idempotenten `PlanAction`s.
4. Der **Executor** wendet den Plan an — oder zeigt ihn nur (`dry_run`).

Kern-Eigenschaft: **Idempotenz**. Nach einem `apply` liefert ein erneuter `plan`-Lauf
gegen den nun angeglichenen Tenant *null Aktionen*. Das ist als Test hinterlegt
(`test_plan_is_idempotent_after_apply`).

## Die Graph-Abstraktion (eine Schnittstelle, zwei Implementierungen)

```
GraphClient (Protocol)
├── InMemoryGraphClient   → verhaltensgleicher Mock, lädt aus seed/tenant_seed.json
└── HttpGraphClient       → echter Tenant via httpx + OAuth2-Client-Credentials
```

Warum ein `typing.Protocol` und keine Vererbung? Strukturelle Typisierung entkoppelt die
Fachlogik vollständig von der Transportschicht. Die gesamte Lebenszyklus-Engine kennt nur
`GraphClient` und ist damit ohne Netzwerk, ohne Tenant und ohne Secrets testbar.

Der Mock ist bewusst **kein** naives Dictionary: Er führt `consumedUnits` je SKU konsistent
mit — beim Zuweisen/Entziehen von Lizenzen genauso wie der echte Graph es serverseitig tut.
Dadurch greift dieselbe Kontingent-Semantik (kein freier Seat → Fehler), gegen die auch
Produktion läuft.

## Datenmodelle: Soll-Welt vs. Ist-Welt

Bewusst getrennt gehalten:

- `app/domain.py` — die **Soll-Welt** der Schule: `Role`, `DesiredUser`, `Plan`, `PlanAction`.
- `app/graph/client.py` — die **Ist-Welt** des Tenants: `GraphUser`, `GraphGroup`, `SubscribedSku`
  (Feldnamen 1:1 wie Microsoft Graph, z. B. `userPrincipalName`, `assignedLicenses`, `accountEnabled`).

Die Übersetzung zwischen beiden Welten passiert ausschließlich im Planner/Executor —
nirgends sonst.

## Policy as Data

`app/policies.py` hält die gesamte Lizenz-/Gruppenstrategie als Daten:
Rolle → Lizenz-SKU, Rolle → rollenweite Gruppen, Klassenname → Gruppen-Nickname.
Eine Änderung der Lizenzstrategie ist damit eine Datenänderung, kein Eingriff in die Engine.
Der Lizenzkatalog verwendet reale `skuPartNumber`s (`STANDARDWOFFPACK_STUDENT`,
`ENTERPRISEPACKPLUS_FACULTY`, …) samt Referenzpreisen für die Kostenrechnung.

## Sicherheit gegen ungewollte Änderungen

- **Verwaltete Konten** werden über einen Herkunftsschlüssel (`employeeId` = Quell-ID)
  erkannt. Nur solche Konten kommen als Leaver in Betracht — Dienst- oder Admin-Konten
  ohne Herkunft werden nie automatisch deaktiviert.
- **Verwaltete Gruppen** sind auf Klassen-Gruppen (`klasse-*`) und definierte Rollengruppen
  beschränkt. EntraFlow entfernt niemanden aus fremden Gruppen.
- **Trennung Plan/Apply** + **Dry-Run** verhindern Überraschungen; jede angewandte Aktion
  ist im Audit-Log nachvollziehbar (Rechenschaftspflicht, Art. 5 (2) DSGVO).

## Determinismus

Planung und Optimierung hängen vom Datum ab (Fristen, Inaktivität). Ein fixer `REFERENCE_DATE`
macht Demo und Tests reproduzierbar; in Produktion wird er auf das aktuelle Datum gesetzt.

## Warum diese Trennung von Optimizer und Planner?

Der Planner setzt harte, sichere JML-Regeln um. Der Optimizer liefert **Empfehlungen** mit
Kostenwirkung, die menschlich geprüft werden sollen — etwa eine seit Monaten inaktive
Lehrkraft. Dieses „Human Oversight"-Prinzip ist Absicht: EntraFlow entzieht Lizenzen aktiver
Personen nicht automatisch, sondern macht sie sichtbar und rechenbar.

## Teststrategie

| Testdatei | Fokus |
|---|---|
| `test_planner.py` | JML-Regeln, Klassenwechsel, Idempotenz, Leaver-Fristen |
| `test_executor.py` | Apply vs. Dry-Run, Seat-Rotation, Kontingent-Durchsetzung, Audit |
| `test_optimizer.py` | Inaktivität, deaktiviert-lizenziert, Kostensumme, Fehlalarm-Vermeidung |
| `test_dsgvo.py` | Befunde, Löschkonzept, Zugriffsübersicht, verarbeitete Datensätze |
| `test_api.py` | REST-Vertrag Ende-zu-Ende inkl. CSV-Override |
