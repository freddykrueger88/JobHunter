# ADR-0003: i18n-Namespace-Struktur statt Inline-Übersetzungsobjekt

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

**Status:** Vorgeschlagen (Teil von Rework-Phase C, noch nicht umgesetzt)
**Datum:** 2026-08-24

---

## Deutsch

### Kontext

`frontend/src/i18n.ts` enthält aktuell alle Übersetzungen als ein einziges
Inline-JS-Objekt für `nav`, `dashboard`, `jobs`, `settings`, `common` – nur
~11 % der Frontend-Dateien nutzen überhaupt `useTranslation` (Audit 1.2).
Für die geforderte vollständige Zweisprachigkeit (~40 weitere Dateien)
skaliert dieses Muster nicht: eine wachsende Monolith-Datei erschwert
Übersicht, Review und die im Auftrag geforderte automatisierte Prüfung auf
fehlende/verwaiste Schlüssel.

### Entscheidung

Umstellung auf eine **Namespace-Struktur mit einer JSON-Datei pro
Sprache und Feature**:
`frontend/src/locales/de/{nav,dashboard,jobs,kanban,reminders,settings,
common,...}.json` und äquivalente `en/`-Struktur. `i18n.ts` lädt die
Namespaces statt eines Inline-Objekts.

Schlüsselkonvention: **semantisch, nicht Satz-als-Schlüssel** – z. B.
`jobs.search.placeholder` statt `"Nach Jobtitel oder Firma suchen..."` als
Schlüssel. Details in `docs/i18n/KONZEPT.md` (Rework-Phase C, Aufgabe 1).

### Begründung

- i18next unterstützt Namespaces nativ – keine neue Bibliothek nötig
  (Audit 2.2 bestätigt: kein Bibliothekswechsel gerechtfertigt).
- Ermöglicht die im Auftrag geforderte CI-Prüfung auf Schlüssel-Parität
  zwischen `de/` und `en/` (Diff zweier Verzeichnisstrukturen statt Parsen
  eines TS-Objekts).
- Kleinere, feature-bezogene Dateien reduzieren Merge-Konflikte bei
  paralleler Arbeit an mehreren Batches (siehe Rework-Phase C,
  Batch-1-bis-5-Aufteilung).

### Konsequenzen

- Migration der 5 bereits übersetzten Bereiche als erster, risikoarmer
  Schritt (reine Umstrukturierung, keine neuen Inhalte).
- Jede neue UI-Text-Ergänzung erfordert künftig **immer** einen Eintrag in
  sowohl `de/*.json` als auch `en/*.json` – wird durch den CI-Check
  (Rework-Phase C, Aufgabe 6) erzwungen, nicht nur durch Konvention.

---

## English

### Context

`frontend/src/i18n.ts` currently holds all translations as a single inline
JS object for `nav`, `dashboard`, `jobs`, `settings`, `common` – only
~11% of frontend files use `useTranslation` at all (Audit 1.2). For the
required full bilingualism (~40 more files), this pattern does not scale:
a growing monolithic file makes overview, review, and the automated
missing/orphaned-key check required by the brief harder.

### Decision

Switch to a **namespace structure with one JSON file per language and
feature**: `frontend/src/locales/de/{nav,dashboard,jobs,kanban,reminders,
settings,common,...}.json` and an equivalent `en/` structure. `i18n.ts`
loads the namespaces instead of an inline object.

Key convention: **semantic, not sentence-as-key** – e.g.
`jobs.search.placeholder` instead of using
`"Search by job title or company..."` as the key itself. Details in
`docs/i18n/KONZEPT.md` (Rework Phase C, task 1).

### Rationale

- i18next supports namespaces natively – no new library needed (Audit 2.2
  confirms no library switch is justified).
- Enables the CI check for key parity between `de/` and `en/` required by
  the brief (diffing two directory structures instead of parsing a TS
  object).
- Smaller, feature-scoped files reduce merge conflicts when working on
  several batches in parallel (see Rework Phase C, batch 1–5 split).

### Consequences

- Migrating the 5 already-translated areas is the first, low-risk step
  (pure restructuring, no new content).
- Every new UI text addition will henceforth **always** require an entry
  in both `de/*.json` and `en/*.json` – enforced by the CI check (Rework
  Phase C, task 6), not just by convention.
