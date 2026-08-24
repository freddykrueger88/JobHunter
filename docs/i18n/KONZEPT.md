# i18n-Konzept / i18n Concept

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## Deutsch

> Rework-Plan Phase C, Aufgabe 1 (`docs/analysis/REWORK_PLAN_DE.md`).
> Grundlage: ADR-0003 (`docs/architecture/adr/0003-i18n-namespace-struktur.md`).

### Grundsätze

1. **Deutsch ist Standard- und Fallback-Sprache.** `fallbackLng: 'de'` bleibt
   gesetzt. Englisch ist gleichwertig gepflegt, nie eine Notlösung.
2. **Keine Browser-Locale-Übernahme.** Die Sprache wird explizit gewählt
   (Einstellungen) und in `localStorage` persistiert, nicht automatisch aus
   `navigator.language` übernommen — verhindert, dass deutschsprachige
   Nutzer:innen mit englischem Browser ungefragt Englisch sehen.
3. **Kein sichtbarer Übersetzungsschlüssel im Produkt.** Fehlt ein Schlüssel,
   greift `fallbackLng` (Deutsch) statt den rohen Key anzuzeigen.
4. **Jeder neue Schlüssel gleichzeitig in `de/*.json` UND `en/*.json`.**
   Durchgesetzt durch den CI-Check (Rework-Plan Phase C, Aufgabe 6), nicht
   nur durch Konvention.

### Namespace-Struktur

Ablösung des bisherigen Inline-Objekts in `frontend/src/i18n.ts` durch
`frontend/src/locales/{de,en}/<namespace>.json` — ein Namespace pro
Seite/Feature-Bereich statt einer wachsenden Monolith-Datei:

```
frontend/src/locales/
├── de/
│   ├── common.json        # Speichern, Abbrechen, Löschen, Lädt, Fehler, ...
│   ├── nav.json
│   ├── dashboard.json
│   ├── jobs.json
│   ├── kanban.json
│   ├── history.json
│   ├── reminders.json
│   ├── settings.json
│   ├── searchProfiles.json
│   ├── interviewSimulator.json
│   ├── companyDossier.json
│   ├── coverLetter.json
│   ├── onboarding.json
│   └── components.json    # geteilte Kleinkomponenten (Badges, Dialoge, ...)
└── en/
    └── (identische Struktur)
```

Jede neue Seite/größere Komponente bekommt bei Bedarf einen eigenen
Namespace; kleine, wiederverwendete UI-Fragmente (Bestätigungsdialoge,
Badges, Overlays) teilen sich `components.json`.

### Schlüsselkonvention

**Semantisch, nicht Satz-als-Schlüssel.** Schlüssel beschreiben die Rolle
des Texts, nicht seinen Inhalt:

```json
// Richtig:
{ "search": { "placeholder": "Nach Jobtitel oder Firma suchen..." } }

// Falsch (Satz als Schlüssel):
{ "Nach Jobtitel oder Firma suchen...": "Nach Jobtitel oder Firma suchen..." }
```

Verschachtelung nach UI-Struktur (z. B. `form.fields.email.label`,
`form.fields.email.error.required`), maximal 3-4 Ebenen tief, danach lieber
ein neuer Namespace.

### Persistenzstrategie

- Weiterhin `localStorage` (`i18next`-Standard via
  `i18next-browser-languagedetector` oder der bestehende manuelle
  `localStorage.getItem('lang')`-Mechanismus, s. `i18n.ts`) — für
  nicht angemeldete Nutzer:innen ausreichend, da JobHunter aktuell
  Single-User/lokal ist (Rework-Plan Phase B.3: Auth-Feature entfernt).
- Sollte künftig Mehrbenutzerfähigkeit eingeführt werden, wäre ein
  `UserSettings.language`-Feld die naheliegende Erweiterung — aktuell
  nicht umgesetzt, da kein Nutzerkonto-Konzept mehr existiert.

### Datums-/Zahlenformatierung

`Intl.DateTimeFormat` / `Intl.NumberFormat` mit der aktiven i18next-Locale
statt manueller `strftime`-artiger Formatierung (aktuell teils
`toLocaleDateString('de-DE', ...)` hart codiert, z. B. in
`backend/api/export.py` CSV/XLSX-Export — dort serverseitig, bleibt
vorerst Deutsch-only, da Export-Dateien nicht Teil der UI-i18n sind,
siehe offene Frage unten).

### Backend-Fehlertexte

`HTTPException(detail="...")` liefert aktuell durchgängig deutschen
Klartext. Zielbild: Fehlercode statt Klartext
(`{"error_code": "invalid_credentials"}`), Übersetzung erfolgt im Frontend
über dieselbe Namespace-Struktur (`common.errors.<code>`). Migration
schrittweise, Klartext bleibt als `detail` zusätzlich erhalten, bis das
Frontend vollständig umgestellt ist (Rework-Plan Phase C, Aufgabe 4).

### Wie neue Texte/Übersetzungen hinzufügen

1. Schlüssel in `frontend/src/locales/de/<namespace>.json` ergänzen.
2. **Im selben Commit** denselben Schlüssel in
   `frontend/src/locales/en/<namespace>.json` ergänzen (auch als
   vorläufige, später verbesserte Übersetzung — nie leer lassen).
3. `useTranslation('<namespace>')` in der Komponente verwenden,
   `t('schluessel.pfad')`.
4. Vor dem Commit: `npm run i18n:check` (Rework-Plan Phase C, Aufgabe 6)
   lokal laufen lassen, um fehlende/verwaiste Schlüssel zu finden.

### Offene Fragen

- Ob Export-Dateien (CSV/XLSX-Spaltenüberschriften) Teil der
  i18n-Migration werden sollen, ist eine Produktentscheidung — aktuell
  nicht im Scope, da sie serverseitig generiert werden und die
  Locale des Nutzers dem Backend nicht mitgeteilt wird.

---

## English

> Rework Plan Phase C, task 1 (`docs/analysis/REWORK_PLAN_EN.md`).
> Basis: ADR-0003 (`docs/architecture/adr/0003-i18n-namespace-struktur.md`).

### Principles

1. **German is the default and fallback language.** `fallbackLng: 'de'`
   stays set. English is maintained to the same standard, never a
   stopgap.
2. **No browser-locale takeover.** The language is chosen explicitly
   (Settings) and persisted in `localStorage`, never inferred
   automatically from `navigator.language` — prevents German-speaking
   users with an English browser from seeing English unasked.
3. **No visible translation key in the product.** If a key is missing,
   `fallbackLng` (German) applies instead of showing the raw key.
4. **Every new key goes into `de/*.json` AND `en/*.json`
   simultaneously.** Enforced by the CI check (Rework Plan Phase C, task
   6), not just by convention.

### Namespace Structure

Replaces the previous inline object in `frontend/src/i18n.ts` with
`frontend/src/locales/{de,en}/<namespace>.json` — one namespace per
page/feature area instead of a growing monolithic file (see the file tree
in the German section above; identical on the English side).

### Key Convention

**Semantic, not sentence-as-key.** Keys describe the text's role, not its
content (see German section for the code example). Nest by UI structure,
max 3-4 levels deep, then prefer a new namespace.

### Persistence Strategy

- Continues to use `localStorage` — sufficient for JobHunter's current
  single-user/local design (Rework Plan Phase B.3: auth feature removed).
- If multi-user capability is introduced later, a `UserSettings.language`
  field would be the natural extension — not implemented now, since no
  user-account concept exists anymore.

### Date/Number Formatting

`Intl.DateTimeFormat` / `Intl.NumberFormat` with the active i18next locale
instead of manual `strftime`-style formatting (currently partly hardcoded,
e.g. in `backend/api/export.py` CSV/XLSX export — that stays server-side
and German-only for now, since export files are not part of the UI i18n,
see open question below).

### Backend Error Messages

`HTTPException(detail="...")` currently consistently returns German plain
text. Target: an error code instead of plain text
(`{"error_code": "invalid_credentials"}`), translated in the frontend via
the same namespace structure (`common.errors.<code>`). Migrated
incrementally; plain text stays as `detail` in addition until the frontend
is fully switched over (Rework Plan Phase C, task 4).

### How to Add New Text/Translations

1. Add the key to `frontend/src/locales/de/<namespace>.json`.
2. **In the same commit**, add the same key to
   `frontend/src/locales/en/<namespace>.json` (even as a provisional,
   later-refined translation — never leave it empty).
3. Use `useTranslation('<namespace>')` in the component,
   `t('key.path')`.
4. Before committing: run `npm run i18n:check` locally (Rework Plan Phase
   C, task 6) to find missing/orphaned keys.

### Open Questions

- Whether export files (CSV/XLSX column headers) should become part of
  the i18n migration is a product decision — currently out of scope,
  since they are generated server-side and the user's locale is not
  communicated to the backend.
