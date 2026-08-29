# Evidence Guide

Dieses Verzeichnis beschreibt, **wie praktische Erfahrung belegt wird**, ohne Secrets oder personenbezogene Echtdaten öffentlich zu machen.

## Grundregel

Ein Szenario ist erst abgeschlossen, wenn der Nachweis zeigt:

1. **Ausgangslage** – Was sollte administriert oder gelöst werden?
2. **Aktion** – Welche Policy, welches Script oder welcher Admin-Schritt wurde verwendet?
3. **Ergebnis** – Was hat sich technisch verändert?
4. **Kontrolle** – Wie wurde das Ergebnis verifiziert?
5. **Security** – Welche Sicherheits-/Least-Privilege-Überlegung wurde berücksichtigt?

## LAB-01

Für LAB-01 gelten:

- [Technische Bewertung](LAB-01-baseline.md)
- [Evidence-Manifest](LAB-01-evidence-manifest.md)
- [RBAC-Matrix](LAB-01-RBAC-MATRIX.md)
- [Break-Glass-Konzept](LAB-01-BREAK-GLASS.md)
- [Sicheres Capture-Runbook](../docs/LAB-01-EVIDENCE-CAPTURE.md)

Die fünf PNG-Dateien müssen aus der echten Testtenant-Ausführung stammen. Platzhalter und nachgestellte Resultate gelten nicht als Evidence.

## Empfohlene Dateinamen

```text
LAB-02-01-whatif.png
LAB-02-02-users-after.png
LAB-02-result-redacted.csv
LAB-02-summary.md
```

## Template für `LAB-XX-summary.md`

```markdown
# LAB-XX – Titel

**Datum:** YYYY-MM-DD
**Ziel:**

## Ausgangslage
...

## Umsetzung
- ...

## Verifikation
- ...

## Ergebnis
- ...

## Security / Lessons Learned
- ...
```

## Niemals öffentlich committen

- Passwörter
- Client Secrets
- private Schlüssel / Zertifikatsdateien
- BitLocker Recovery Keys
- Access-/Refresh-Tokens
- echte Mitarbeiter-/Schülerdaten
- Tenant-, Client-, Benutzer- oder Objekt-IDs
- E-Mail-Adressen und User Principal Names
- Screenshots mit sensitiven personenbezogenen Daten

## Recruiter-Ansicht

Für das öffentliche Portfolio genügen redigierte Screenshots und technische Kurzberichte. Entscheidend ist, dass aus den Artefakten ersichtlich wird, dass die Konfiguration **selbst geplant, ausgeführt, kontrolliert und dokumentiert** wurde.
