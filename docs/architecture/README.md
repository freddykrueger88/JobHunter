# Architektur / Architecture

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## Deutsch

Dieser Ordner enthält die maßgeblichen Architekturdiagramme und
Architekturentscheidungen (ADRs) für JobHunter, entstanden aus dem
Audit-/Rework-Programm (siehe `docs/analysis/`).

- **[diagrams.md](diagrams.md)** – System-/Deployment-Sicht und
  Backend-Modulsicht (Mermaid), identisch zu den Diagrammen in
  `docs/analysis/REPOSITORY_AUDIT_DE.md` Abschnitt 1.7, hier als
  eigenständige, langfristig aktuell zu haltende Referenz geführt.
- **[adr/0001-gezielte-reparatur-statt-neuaufbau.md](adr/0001-gezielte-reparatur-statt-neuaufbau.md)**
  – Warum kein Rebuild, sondern gezielte Reparatur + Restrukturierung.
- **[adr/0002-endpunkt-schicht-vereinheitlichen.md](adr/0002-endpunkt-schicht-vereinheitlichen.md)**
  – Zusammenführung von `api/` und `routers/`.
- **[adr/0003-i18n-namespace-struktur.md](adr/0003-i18n-namespace-struktur.md)**
  – Übersetzungsstruktur für Phase C (Internationalisierung).

**Hinweis zum Pflegezustand:** Diese ADRs sind schriftlich fixierte
Entscheidungen aus dem Rework-Plan (`docs/analysis/REWORK_PLAN_DE.md`).
Sie werden verbindlich, sobald die zugehörige Rework-Phase umgesetzt wird –
bis dahin gelten sie als **vorgeschlagen**, nicht als bereits im Code
umgesetzt (siehe jeweiliger Status-Hinweis im ADR).

---

## English

This directory contains the authoritative architecture diagrams and
architecture decision records (ADRs) for JobHunter, produced by the
audit/rework program (see `docs/analysis/`).

- **[diagrams.md](diagrams.md)** – system/deployment view and backend
  module view (Mermaid), identical to the diagrams in
  `docs/analysis/REPOSITORY_AUDIT_EN.md` section 1.7, kept here as a
  standalone reference to be maintained long-term.
- **[adr/0001-gezielte-reparatur-statt-neuaufbau.md](adr/0001-gezielte-reparatur-statt-neuaufbau.md)**
  – Why no rebuild, but targeted repair + restructuring.
- **[adr/0002-endpunkt-schicht-vereinheitlichen.md](adr/0002-endpunkt-schicht-vereinheitlichen.md)**
  – Merging `api/` and `routers/`.
- **[adr/0003-i18n-namespace-struktur.md](adr/0003-i18n-namespace-struktur.md)**
  – Translation structure for Phase C (internationalization).

**Maintenance note:** These ADRs are decisions fixed in writing from the
rework plan (`docs/analysis/REWORK_PLAN_EN.md`). They become binding once
the corresponding rework phase is implemented – until then they are
**proposed**, not yet implemented in code (see the status note in each
ADR).
