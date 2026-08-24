# ADR-0002: Endpunkt-Schicht vereinheitlichen (`api/` + `routers/` → `routers/`)

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

**Status:** Vorgeschlagen (Teil von Rework-Phase B, noch nicht umgesetzt)
**Datum:** 2026-08-24

---

## Deutsch

### Kontext

Das Backend besitzt zwei parallele Ordner für FastAPI-Endpunkte: `api/`
(18 Module, älterer Code) und `routers/` (3 Module: `blocklist`,
`followups`, `jobs_image` – die zuletzt hinzugefügten Endpunkte). `main.py`
importiert aus beiden. Es gibt keinen erkennbaren fachlichen Grund für die
Trennung (Audit 1.3) – sie ist historisch entstanden, nicht bewusst
architektonisch begründet.

### Entscheidung

Beide Ordner werden auf **einen** Ordnernamen vereinheitlicht:
Empfehlung `routers/`, da der Name die tatsächliche FastAPI-Rolle
(`APIRouter`-Module) klarer beschreibt als das generische `api/`. Alle 18
Module aus `api/` wandern nach `routers/`, `api/` wird aufgelöst.

### Begründung

- Reduziert kognitive Last für neue Mitwirkende („wo lege ich einen neuen
  Endpunkt an?").
- Voraussetzung für die in `docs/architecture/` festgehaltene
  Architekturregel „Endpunkte immer in `routers/`".
- Geringes Risiko: reine Verschiebung, keine Verhaltensänderung, durch
  Test-/Build-Lauf nach der Verschiebung vollständig verifizierbar.

### Konsequenzen

- Alle Importe in `main.py` und ggf. Tests müssen angepasst werden.
- Sollte gemeinsam mit anderen Strukturbereinigungen aus Rework-Phase B
  durchgeführt werden (siehe `docs/analysis/REWORK_PLAN_DE.md`, Phase B,
  Aufgabe 2), nicht isoliert.
- Nach Abschluss: vollständige Textsuche nach alten Importpfaden als
  Verifikationsschritt (nicht nur `main.py` prüfen).

---

## English

### Context

The backend has two parallel directories for FastAPI endpoints: `api/`
(18 modules, older code) and `routers/` (3 modules: `blocklist`,
`followups`, `jobs_image` – the most recently added endpoints). `main.py`
imports from both. There is no discernible technical reason for the split
(Audit 1.3) – it arose historically, not from a deliberate architectural
choice.

### Decision

Both directories are unified into **one** directory name: recommended
`routers/`, since that name more clearly describes the actual FastAPI role
(`APIRouter` modules) than the generic `api/`. All 18 modules from `api/`
move into `routers/`, and `api/` is dissolved.

### Rationale

- Reduces cognitive load for new contributors ("where do I add a new
  endpoint?").
- A prerequisite for the architecture rule "endpoints always live in
  `routers/`" recorded in `docs/architecture/`.
- Low risk: a pure move, no behavior change, fully verifiable via a
  test/build run after the move.

### Consequences

- All imports in `main.py` and any tests must be updated.
- Should be carried out together with the other structural cleanup in
  Rework Phase B (see `docs/analysis/REWORK_PLAN_EN.md`, Phase B, task 2),
  not in isolation.
- After completion: a full text search for old import paths as a
  verification step (not just checking `main.py`).
