# ADR-0001: Gezielte Reparatur + Restrukturierung statt Neuaufbau

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

**Status:** Vorgeschlagen (Entscheidung getroffen, Umsetzung ausstehend –
siehe `docs/analysis/REWORK_PLAN_DE.md`)
**Datum:** 2026-08-24

---

## Deutsch

### Kontext

Ein umfassendes Audit (`docs/analysis/REPOSITORY_AUDIT_DE.md`, Kapitel 1–2)
sollte klären, ob JobHunter gezielt refaktoriert, modular restrukturiert
oder in wesentlichen Teilen neu aufgebaut werden soll. Das Audit hat drei
verifiziert kaputte Pipelines (Backend-Tests, Frontend-Lint, Frontend-Build),
einen kritischen Sicherheitsfund (Path Traversal beim CV-Upload), mehrere
tote Code-Pfade und eine i18n-Infrastruktur gefunden, die zu 89 % ungenutzt
bleibt.

### Entscheidung

JobHunter wird **gezielt repariert und modular restrukturiert**, nicht neu
aufgebaut. Kein Element des bestehenden Stacks (FastAPI, SQLAlchemy/
Postgres, React/Vite/TypeScript, TailwindCSS, i18next, Ollama) wird
gewechselt.

### Begründung

- Alle gefundenen Probleme sind Fertigstellungs-, Konfigurations- und
  Nutzungslücken, keine Architekturfehler (Audit 2.1).
- Der Stack ist für Größe, Zielgruppe (Solo-Maintainer, self-hosted,
  DSGVO-sensibel) und Funktionsumfang durchweg passend (Audit 2.2).
- Das Produkt ist funktional bereits sehr weit entwickelt (v1.9.0, 30
  Backend-Services, umfangreiche KI-Feature-Palette) – ein Neuaufbau würde
  das ohne belegbaren Zusatznutzen riskieren.

### Konsequenzen

- Die Umsetzung folgt der Fünf-Phasen-Roadmap in
  `docs/analysis/REWORK_PLAN_DE.md` (Stabilisierung → Struktur →
  Internationalisierung → Produktqualität → Engineering).
- Restrukturierung (nicht nur Bugfixing) bleibt nötig, da mehrere
  Strukturentscheidungen (gespaltene Endpunkt-Schicht, fehlender zentraler
  API-Client, offenes Auth-Fragment) vor der i18n-Migration bereinigt
  werden müssen.

---

## English

### Context

A comprehensive audit (`docs/analysis/REPOSITORY_AUDIT_EN.md`, chapters
1–2) was meant to determine whether JobHunter should be targeted for
refactoring, modular restructuring, or a substantial rebuild. The audit
found three verified-broken pipelines (backend tests, frontend lint,
frontend build), one critical security finding (path traversal on CV
upload), several dead code paths, and an i18n infrastructure that remains
89% unused.

### Decision

JobHunter will be **targeted for repair and modular restructuring**, not
rebuilt. No element of the existing stack (FastAPI, SQLAlchemy/Postgres,
React/Vite/TypeScript, TailwindCSS, i18next, Ollama) will be switched.

### Rationale

- Every problem found is a completion, configuration, or usage gap, not an
  architecture flaw (Audit 2.1).
- The stack consistently fits the product's size, target audience (solo
  maintainer, self-hosted, GDPR-sensitive), and feature scope (Audit 2.2).
- The product is already functionally very far along (v1.9.0, 30 backend
  services, an extensive AI feature set) – a rebuild would risk that
  without demonstrable added value.

### Consequences

- Implementation follows the five-phase roadmap in
  `docs/analysis/REWORK_PLAN_EN.md` (Stabilization → Structure →
  Internationalization → Product Quality → Engineering).
- Restructuring (not just bug fixing) remains necessary, since several
  structural decisions (split endpoint layer, missing central API client,
  open auth fragment) must be cleaned up before the i18n migration.
