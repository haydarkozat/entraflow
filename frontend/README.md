# EntraFlow – Frontend

Dashboard-Oberfläche für **EntraFlow**, die Automatisierung des
Microsoft-365-/Entra-ID-Lebenszyklus für Schulen. Gebaut mit **Next.js 15**
(App Router) und **TypeScript** – ganz ohne UI-Framework oder CSS-Bibliothek,
mit einem einzigen handgeschriebenen Stylesheet (`app/globals.css`).

## Funktionen

- **Übersicht** – Kennzahlen des Mandanten, Lizenzauslastung, DSGVO-Score und Einsparpotenzial.
- **Lebenszyklus (JML)** – Joiner-/Mover-/Leaver-Pläne erstellen, simulieren (Dry-Run) und anwenden.
- **Lizenz-Governance** – Auslastung, Kosten und Rückgewinnungs-Empfehlungen.
- **DSGVO-Compliance** – Score-Anzeige, Feststellungen, fällige Löschungen und Zugriffsübersicht.
- **Audit-Log** – revisionssichere Protokollierung aller Änderungen.

## Voraussetzungen

- Node.js 18.18+ (empfohlen: 20 LTS)
- Das EntraFlow-Backend (FastAPI) muss erreichbar sein – standardmäßig unter `http://localhost:8000`.

## Installation

```bash
npm install
```

## Entwicklung

Das Backend muss auf Port **8000** laufen. Dann:

```bash
npm run dev
```

Die Oberfläche ist anschließend unter `http://localhost:3000` verfügbar.

## Produktions-Build

```bash
npm run build
npm run start
```

## Konfiguration

Die API-Basis-URL wird über die Umgebungsvariable `NEXT_PUBLIC_API_BASE`
gesteuert (Standard: `http://localhost:8000`). Beispiel:

```bash
NEXT_PUBLIC_API_BASE=https://entraflow.example.org npm run build
```

Ist das Backend nicht erreichbar, zeigt die Oberfläche einen freundlichen
Hinweis („Backend nicht erreichbar“) an, statt abzustürzen.
