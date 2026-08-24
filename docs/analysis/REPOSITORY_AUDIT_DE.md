# JobHunter – Repository-Audit (Deutsch)

> **Status dieses Dokuments:** Entwurf, wird abschnittsweise befüllt (siehe
> `docs/analysis/BACKLOG.md` für den Fortschritt). Englische Fassung:
> `docs/analysis/REPOSITORY_AUDIT_EN.md` (wird parallel gepflegt, sobald ein
> Abschnitt hier final ist).
>
> Stand: 2026-08-24. Alle Aussagen beruhen auf tatsächlicher Sichtung des
> Checkouts in LXC 142 (`/root/JobHunter`, Branch `main`,
> Remote `https://github.com/freddykrueger88/JobHunter.git`).

## 1. Projektinventur

### 1.1 Projektstruktur & Modulgrenzen

JobHunter ist ein Monorepo mit klarer Trennung in vier Docker-Services
(siehe `docker-compose.yml`):

| Verzeichnis | Rolle | Technologie (Ist-Stand) |
|---|---|---|
| `backend/` | REST-API, Business-Logik, DB-Zugriff | Python 3.11, FastAPI 0.111.0, SQLAlchemy 2.0.30 (async, via `asyncpg`), Alembic 1.13.1 |
| `frontend/` | Single-Page-Application | React 18.3.1, Vite 5.2.13, TypeScript 5.4.5, TailwindCSS 3.4.4, i18next 23.11.5 / react-i18next 14.1.2 |
| `db` (Compose-Service) | Persistenz | PostgreSQL (Image aus `docker-compose.yml`, siehe Abschnitt Datenbank) |
| `ollama` (Compose-Service) | Lokale KI-Inferenz | Ollama, Modelle werden zur Laufzeit gezogen (aktuell u. a. `mistral`) |

Weitere Top-Level-Bereiche:

- `docs/` – 11 Themen-Dokumente (u. a. `architecture.md`, `dsgvo.md`,
  `PRIVACY.md`, `accessibility.md`, `roadmap.md`, `faq.md`,
  `backup-restore.md`, `ai-models.md`, `api-keys.md`, `portals.md`,
  `setup.md`). Mehrere Dateien sind bereits als Ein-Seiten-DE/EN-Mix
  aufgebaut (Abschnitt „## Deutsch" / „## English" in derselben Datei),
  z. B. `architecture.md`, `CHANGELOG.md` – ein anderes Muster als das vom
  Auftrag geforderte Schema mit getrennten Seiten pro Sprache.
- `wiki/` – 6 Markdown-Dateien (`Home.md`, `Installation.md`,
  `Konfiguration.md`, `Entwicklung.md`, `Barrierefreiheit.md`,
  `Changelog.md`), **nur Deutsch**, direkt im Hauptrepo getrackt (nicht der
  separate `JobHunter.wiki.git`-Git-Baum, den GitHub für echte Wikis
  verwendet – siehe Abschnitt CI/CD & Publishing).
- `alembic/` (Top-Level) **und** `backend/alembic/` – zwei Alembic-Bäume
  gleichzeitig vorhanden (`alembic.ini` + `backend/alembic.ini`). **Offene
  Frage / Risiko:** unklar, ob der Top-Level-Baum noch aktiv genutzt wird
  oder ein Überbleibsel einer früheren Struktur ist – muss vor jeder
  Migrations-Änderung geklärt werden (potenzielle Quelle für inkonsistente
  Schema-Historie).
- `.github/` – ausschließlich Issue-Templates (`bug.md`, `feature.md`,
  `accessibility.md`, `docs.md`, `config.yml`) und `PULL_REQUEST_TEMPLATE.md`.
  **Kein `.github/workflows/`-Ordner vorhanden – keinerlei CI/CD-Automatisierung
  aktuell im Repo.**
- Root-Dokumente: `README.md` (Englisch, führend im Repo-Root),
  `README.de.md` (Deutsch, aus README.md heraus verlinkt), `CHANGELOG.md`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`,
  `LICENSE` (MIT laut README-Badge), `CITATION.cff`, `HUMANS.md`,
  `INSTALL.md`.
- `scripts/setup.sh` – einziges Hilfsskript auf Top-Level.

### Beobachtung zur Sprachführung (projektübergreifend)

Der Ist-Zustand ist uneinheitlich zwischen drei Mustern:

1. **Datei-Duplikat pro Sprache**: `README.md` (EN) / `README.de.md` (DE).
2. **Eine Datei, zwei Abschnitte**: `docs/architecture.md`,
   `docs/CHANGELOG.md` – DE/EN über Anker (`#deutsch` / `#english`) in
   derselben Datei.
3. **Nur eine Sprache**: `wiki/*.md` (nur Deutsch), die meisten übrigen
   `docs/*.md` (bisher nicht im Detail geprüft, folgt in 1.2 ff.).

Das im Auftrag geforderte Schema (getrennte Seiten `Seite` / `Seite-English`)
existiert im Ist-Zustand **nicht** – das ist eine bewusste
Architekturentscheidung für Phase 5, kein Bug.

### Offene Fragen aus diesem Abschnitt

- Zweck des doppelten Alembic-Baums (`/alembic` vs. `/backend/alembic`)
  ungeklärt – wird in Abschnitt „Datenbank/Migrationen" (Backlog-Item 1.4)
  vertieft.
- Ob `docs/` und `wiki/` bewusst redundant geführt werden (z. B. `docs/`
  für Entwickler, `wiki/` für Endnutzer) oder historisch gewachsen sind,
  ist aus dem Code allein nicht zweifelsfrei zu beantworten – als Annahme
  markiert, nicht als Fakt.

### 1.2 Frontend-Bestandsaufnahme

**Umfang:** 45 TypeScript/TSX-Dateien unter `frontend/src/`.

| Bereich | Dateien | Beispiele |
|---|---|---|
| `pages/` (Routen-Ebene) | 11 | `Dashboard.tsx`, `Jobs.tsx`, `Kanban.tsx`, `History.tsx`, `Settings.tsx`, `Reminders.tsx`, `SearchProfiles.tsx`, `InterviewSimulator.tsx`, `CompanyDossier.tsx`, `CoverLetter.tsx`, `Onboarding.tsx` |
| `components/` | 21 | u. a. `AtsScorePanel`, `AutoApplyButton`, `BadgesPanel`, `CoachChatDrawer`, `CompanyDossier`, `EmailParsingSetup`, `ExportImportPanel`, `MarketAnalyzerPanel`, `SalaryNegotiationModal`, `TopNav` |
| `context/` | 2 | `ThemeContext.tsx`, `AccessibilityContext.tsx` |
| `hooks/` | 5 | `useAnnounce`, `useConfirm`, `useFocusTrap`, `useKeyboardShortcuts`, `useUndoToast` |
| Einstieg/Config | `App.tsx`, `main.tsx`, `i18n.ts` | – |

**Routing** (`App.tsx`, `react-router-dom` v6, `BrowserRouter` in `main.tsx`):
9 Top-Level-Routen (`/`, `/jobs`, `/kanban`, `/history`, `/settings`,
`/reminders`, `/search-profiles`, `/interview-simulator`,
`/company-dossier`). `pages/CoverLetter.tsx` besitzt **keine eigene Route**
– es wird laut Referenzsuche aus `Kanban.tsx` und
`components/AutoApplyButton.tsx` heraus verwendet, vermutlich als
Modal/Unterkomponente im Bewerbungs-Workflow statt als eigene Seite. Nicht
abschließend verifiziert, welchen genauen Aufruf-Pfad das hat – als offene
Frage markiert.

**Namenskollision:** Es existieren sowohl `pages/CompanyDossier.tsx` als
auch `components/CompanyDossier.tsx`. Ohne tieferen Blick in beide Dateien
unklar, ob das Seite+Unterkomponente ist (analog zum CoverLetter-Muster)
oder eine unbeabsichtigte Doppelung – als offene Frage für Phase 2 markiert.

**State-Management:**
- Server-State: TanStack React Query (`@tanstack/react-query`, ein
  `QueryClient` global in `main.tsx`), in 9 von 45 Dateien direkt verwendet
  (`useQuery`/`useMutation`).
- Kein globaler Client-State-Store (kein Redux/Zustand/Jotai) – lokaler
  `useState` plus zwei React-Context-Provider (`Theme`, `Accessibility`)
  für App-weite Querschnittsthemen. Für die Projektgröße angemessen, siehe
  Bewertung in Phase 2.
- **Kein zentraler API-Client**: `axios` wird in 22 von 45 Dateien direkt
  importiert; es gibt keine `api.ts`/`client.ts`/`services/`-Datei und keine
  Fundstelle für `axios.create(...)` oder eine zentrale `baseURL`-Konfiguration.
  Jede Komponente baut ihre Requests offenbar einzeln auf. **Risiko:**
  duplizierte Basis-URL-/Header-/Fehlerbehandlungs-Logik über viele Dateien
  hinweg – relevant sowohl für Wartbarkeit (Phase 2) als auch für
  einheitliche i18n von API-Fehlermeldungen (Phase 4).

**i18n-Abdeckung (Kernbefund für Phase 4):**
- `useTranslation` wird in **5 von 45 Dateien** verwendet:
  `TopNav.tsx`, `Dashboard.tsx`, `Jobs.tsx`, `Onboarding.tsx`, `Settings.tsx`.
  Das entspricht **rund 11 % der Frontend-Dateien** – die übrigen 40 Dateien
  enthalten voraussichtlich überwiegend hartcodierte deutsche UI-Texte.
- Übersetzungsressourcen liegen **inline in `i18n.ts`** als JS-Objekt (kein
  separates `locales/`-Verzeichnis, keine JSON-Dateien pro Sprache/Namespace),
  und decken nur einen kleinen Ausschnitt ab: `nav`, `dashboard`
  (Titel/Status-Labels), `jobs` (Titel/Suche/Ausblenden), `settings`
  (Titel/Theme/Sprache/KI), `common` (Speichern/Abbrechen/Löschen/Lädt).
  Modul-Namensräume für die übrigen ~20 Seiten/Komponenten (Kanban,
  Reminders, SearchProfiles, InterviewSimulator, CompanyDossier,
  CoverLetter, alle Panels/Modals) fehlen vollständig.
- Grobe Stichproben-Schätzung (Regex-Suche nach großgeschriebenen
  JSX-Textknoten mit typisch deutschen Wortmustern, **kein exaktes Maß**,
  erfasst z. B. keine `placeholder`-/`aria-label`-Attribute oder
  mehrzeiligen Text): mindestens 36 Treffer für wahrscheinlich hartcodierten
  deutschen UI-Text allein bei dieser groben Methode – die tatsächliche
  Zahl dürfte deutlich höher liegen. Eine belastbare, vollständige Zählung
  erfordert manuelle Sichtung pro Datei; das wird nicht hier, sondern als
  Arbeitsgrundlage für die Migrations-Batches in Phase 4 (Backlog-Item 4.3)
  gemacht.
- Sprachauswahl-Mechanik in `i18n.ts`: `lng: localStorage.getItem('lang') || 'de'`,
  `fallbackLng: 'de'` – **Deutsch ist bereits korrekt als Standard und
  Fallback verankert**, es gibt aber keine Browser-Locale-Erkennung
  (bewusst so, verhindert genau das im Auftrag geforderte "Browser-Locale
  darf Deutsch nicht verdrängen" – ist also schon konform, nicht zu
  "reparieren").

### Offene Fragen aus diesem Abschnitt

- Exakter Einbindungspfad von `pages/CoverLetter.tsx` (Modal? eigene
  Sub-Route via State statt Router?) – zu klären vor i18n-Migration dieser
  Seite.
- Zweck/Verhältnis von `pages/CompanyDossier.tsx` zu
  `components/CompanyDossier.tsx`.
- Ob die fehlende Browser-Locale-Erkennung bewusste Entscheidung oder
  schlicht noch nicht umgesetzt ist – als Annahme markiert (aktuell als
  „bereits auftragskonform" gewertet, siehe oben).

---

*Fortsetzung folgt (1.3 Backend-Bestandsaufnahme, …) gemäß `docs/analysis/BACKLOG.md`.*
