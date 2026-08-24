# JobHunter – Repository-Audit (Deutsch)

> **Status dieses Dokuments:** Phase 1 (Repository-Inventur) abgeschlossen.
> Phase 2 (Qualitäts-/Architekturbewertung mit priorisierten Empfehlungen)
> folgt in einem separaten Arbeitsschritt und wird als eigener Abschnitt
> „## 2. Qualitäts- und Architekturbewertung" ergänzt (siehe
> `docs/analysis/BACKLOG.md` für den Fortschritt). Englische Fassung:
> `docs/analysis/REPOSITORY_AUDIT_EN.md` (inhaltsgleich).
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

### 1.3 Backend-Bestandsaufnahme

**Struktur** (`backend/`, Python 3.11 + FastAPI, alle Pfade unter `backend.*` importiert):

| Verzeichnis | Dateien | Rolle |
|---|---|---|
| `api/` | 18 Module | Haupt-Endpunkt-Schicht (jobs, applications, settings, cv, ai, dashboard, history, reminders, export, interview, company, eures, calendar, company_dossier, email_parsing, auth, cover_letter_pdf) |
| `routers/` | 3 Module | Neuere Endpunkte (`blocklist.py`, `followups.py`, `jobs_image.py`) – **zweiter, paralleler Ordner für dasselbe Konzept (Endpunkte)** neben `api/` |
| `models/` | 12 Module + `__init__.py` | SQLAlchemy-ORM-Modelle (application, job, user, cv, reminder, settings, history, search_profile, cover_letter, cover_letter_template, blocklist, followup, backup_log, user_badge, application_status_log) |
| `services/` | 30 Module + `job_search/`-Unterpaket | Business-Logik/Integrationen (KI-Prompts, ATS-Scorer, Auto-Apply, Backup, Kalender-Export, CV-Parser/-Optimizer, E-Mail-Parser/-Templates, Ghost-Job-Detector, Gehaltsrechner, Scheduler, Skill-Gap u. v. m.) |
| `schemas/` | 3 Module | Pydantic-Schemas (nur `application`, `job`, `settings` – s. Befund unten) |
| `core/` | 4 Module | `config.py` (Settings), `database.py`, `security.py` (JWT, optional), `crypto.py` (Fernet-Verschlüsselung) |
| `alembic/` | – | Migrationen (siehe Abschnitt 1.4) |
| `tests/` | 3 Dateien | s. Abschnitt 1.5 |

**Befund – Endpunkt-Schicht gespalten (`api/` vs. `routers/`):**
Es gibt keinen erkennbaren fachlichen Grund für die Trennung – `routers/`
enthält lediglich die zuletzt hinzugefügten Endpunkte
(`blocklist`, `followups`, `jobs_image`), während alle älteren Endpunkte in
`api/` liegen. `main.py` importiert aus beiden Ordnern parallel. Für die
Zielstruktur (Phase 3) empfiehlt sich eine Vereinheitlichung auf einen
Ordnernamen.

**Befund – `models.py` ist toter Code:**
Neben dem Package `models/` existiert weiterhin die alte Einzeldatei
`backend/models.py` (6,9 KB). Kein aktives Modul importiert daraus mehr
(`grep` über alle `.py`-Dateien liefert keine echten Importe von
`backend.models` als Einzeldatei). **Bestätigt durch den Code selbst**: Ein
Kommentar in der neuen, aktuell in Arbeit befindlichen Migration
(`backend/alembic/versions/0004_add_blocklist_badges_backup_templates.py`)
hält ausdrücklich fest, dass `backend/models.py` „vom
`backend/models/`-Package überschattet" wurde. `models.py` sollte in Phase 3
als Altlast entfernt werden (Aufwand S, Risiko niedrig – es wird
nachweislich nicht mehr importiert).

**Befund – zwei nicht registrierte API-Module:**
`main.py` bindet 16 Router ein; `api/auth.py` und `api/cover_letter_pdf.py`
existieren, werden aber **nicht** in `main.py` eingebunden.
- `cover_letter_pdf.py` passt zum in `README.md` als „planned – #89"
  markierten Feature „Cover Letter Template" – nachvollziehbar unfertig,
  kein Bug.
- `auth.py` implementiert `/auth/token` und `/auth/register` passend zum
  optionalen JWT-Mechanismus in `core/security.py`. Da der Router nicht
  eingebunden ist, gibt es aktuell **keinen erreichbaren Weg, ein Token zu
  erhalten**, selbst wenn `AUTH_ENABLED=true` gesetzt würde – der
  Auth-Mechanismus ist im Ist-Zustand nicht nutzbar. Offen, ob das
  Absicht ist (App laut README bewusst ohne Accounts/lokal-only) oder ein
  Fragment einer geplanten Mehrbenutzer-Funktion.

**Auth/Secrets-Handling:**
- Authentifizierung ist **optional** über `AUTH_ENABLED`-Env-Variable
  (Default `false`) – passend zum Produktversprechen „kein Account nötig,
  lokal, self-hosted" aus dem README. Für Mehrbenutzerfähigkeit (im Auftrag
  als Anforderung genannt) wäre der JWT-Mechanismus die Grundlage, ist aber
  aktuell nicht verdrahtet (s. o.).
- `core/config.py` definiert **Python-seitige Default-Fallbacks** für
  `SECRET_KEY = "changeme"` und `DATABASE_URL` mit Passwort `changeme` –
  falls `.env` fehlt oder unvollständig ist, startet die App also mit
  schwachen Default-Secrets statt hart zu scheitern. `.env.example`
  selbst leitet dagegen korrekt zur Generierung sicherer Werte an
  (`secrets.token_hex(32)`, `Fernet.generate_key()`). **Sicherheitsrisiko,
  wird in Abschnitt 1.6 (Security/OWASP) vertieft.**
- `.env` ist korrekt in `.gitignore` gelistet und **nicht** im Git-Repo
  getrackt (`git ls-files .env` liefert keinen Treffer) – kein
  Secret-Leak im Repo festgestellt.
- API-Keys Dritter (z. B. für Adzuna/StepStone/Arbeitsagentur, laut
  `docs/api-keys.md`) werden laut `core/crypto.py` als Fernet-verschlüsselte
  Werte in der DB abgelegt (`encrypt`/`decrypt`-Helper) – solides Muster
  für „at rest"-Schutz sensibler Bewerbungs-/Zugangsdaten.
- SMTP-Zugangsdaten (`services/mail.py`) werden pro Aufruf als Parameter
  übergeben (`smtp_user`, `smtp_password`), nicht global gehalten – Herkunft
  dieser Werte (vermutlich verschlüsselt aus den Settings) wird in Abschnitt
  1.6 nachvollzogen.

**Schemas-Schicht dünn:**
Nur 3 Pydantic-Schema-Module (`application`, `job`, `settings`) stehen 18
`api/`- und 3 `routers/`-Modulen sowie 12 Model-Modulen gegenüber. Viele
Endpunkte validieren Requests vermutlich direkt über die SQLAlchemy-Modelle
oder Inline-Pydantic-Klassen statt über eine einheitliche Schema-Schicht –
wird in Phase 2 (Konsistenz der Datenverträge) vertieft, nicht hier im Detail
geprüft.

### Offene Fragen aus diesem Abschnitt

- Ist `api/auth.py` ein bewusst ruhendes Feature für künftige
  Mehrbenutzerfähigkeit, oder soll Auth dauerhaft ungenutzt bleiben? Diese
  Produktentscheidung kann nicht aus dem Code allein beantwortet werden –
  echte offene Frage für Phase 3.
- Herkunft/Verschlüsselungsstatus der SMTP-Zugangsdaten in der DB noch nicht
  verifiziert (folgt in 1.6).

### 1.4 Datenbank/Migrationen

**Doppelter Alembic-Baum – Frage aus 1.1 jetzt geklärt:**
Der Top-Level-Baum (`/alembic.ini`, `/alembic/versions/20260511_0001_initial.py`,
1 Migration) ist **nachweislich tot**:
- `backend/Dockerfile` setzt `WORKDIR /app/backend` und kopiert nur den
  Inhalt von `backend/` in das Image (`COPY . .` nach `WORKDIR /app/backend`).
- `docker-compose.yml` baut den Backend-Service mit `build.context: ./backend`
  – der Repo-Root-Ordner `/alembic/` gelangt **nie** ins Image.
- `backend/entrypoint.sh` ruft `alembic upgrade head` ohne `-c`-Flag im
  Arbeitsverzeichnis `/app/backend` auf → es wird ausschließlich
  `backend/alembic.ini` mit `script_location = alembic` (relativ, also
  `backend/alembic/`) verwendet.

→ Der Top-Level-Ordner `/alembic/` ist eine Altlast ohne Laufzeitwirkung und
sollte in Phase 3 entfernt werden (Aufwand S, Risiko niedrig – rein additive
Bereinigung, keine Laufzeitabhängigkeit).

**Aktiver Migrationsverlauf** (`backend/alembic/versions/`, 4 Revisionen,
linear, keine erkennbaren Branches):

| Revision | Zweck |
|---|---|
| `0001_initial_schema` | Ausgangsschema |
| `0002_add_followups_table` | Follow-up-Tracking |
| `0003_add_color_blind_mode` | Einzelnes Settings-Feld (Barrierefreiheit) |
| `0004_add_blocklist_badges_backup_templates` *(aktuell uncommitted, in Arbeit)* | Blocklist, Gamification-Badges, Backup-Log, Anschreiben-Vorlagen |

`backend/alembic/env.py` setzt `sqlalchemy.url` korrekt zur Laufzeit aus
`settings.DATABASE_URL` (aus `.env`) – der Platzhalter-Wert in
`backend/alembic.ini` (`driver://user:pass@localhost/dbname`) wird dadurch
nie tatsächlich verwendet, ist aber als Datei-Inhalt potenziell verwirrend
für neue Mitwirkende.

**Wichtiger Befund – `User`-Modell ohne Migration/Tabelle:**
`backend/models/user.py` existiert und wird von `core/security.py` sowie
`api/auth.py` importiert, ist aber **nicht** in `backend/models/__init__.py`
registriert (im Gegensatz zu allen 14 anderen Modellen). Passend dazu: In
keiner der vier Migrationen wird eine `users`-Tabelle angelegt. Da
`backend/alembic/env.py` alle Modelle für Autogenerate ausschließlich über
`import backend.models` (das Package, nicht die Einzeldatei) registriert,
fehlt `User` in `target_metadata` – ein künftiger
`alembic revision --autogenerate` würde die (nicht existierende)
Users-Tabelle also nicht automatisch nachziehen, sondern schlicht ignorieren.
**Praktische Konsequenz:** Der optionale Auth-Mechanismus aus Abschnitt 1.3
(`api/auth.py`, `core/security.py`) ist damit nicht nur unregistriert im
Router, sondern hat aller Voraussicht nach **auch keine Datenbanktabelle** –
selbst mit `AUTH_ENABLED=true` und eingebundenem Router würde
`/auth/register` vermutlich mit einem DB-Fehler scheitern. Dies bestätigt die
in 1.3 offen gelassene Frage: Auth wirkt wie ein unvollständiges,
ruhendes Feature-Fragment, nicht wie eine aktiv gepflegte Funktion.

**DB-Service (`docker-compose.yml`):** `postgres:16-alpine`, **kein
Host-Port-Mapping** (nur intern im Docker-Netz erreichbar – gute Praxis für
ein self-hosted Tool mit sensiblen Bewerbungsdaten), Healthcheck via
`pg_isready` vorhanden, Daten in benanntem Volume `pgdata` (persistent über
Container-Neustarts hinweg).

### Offene Fragen aus diesem Abschnitt

- Produktentscheidung, ob das `User`-Modell/Auth-Feature weiterverfolgt
  (inkl. fehlender Migration nachgezogen) oder vollständig entfernt werden
  soll – siehe auch offene Frage aus 1.3.

### 1.5 Tests/CI/Linting/Build

**Diese Befunde wurden nicht nur gelesen, sondern durch tatsächliche
Befehlsausführung in den laufenden Docker-Containern verifiziert**
(`docker exec jobhunter-backend`/`jobhunter-frontend`, s. Kommandos unten).

**Backend-Tests – aktuell komplett kaputt (verifiziert):**
```
docker exec jobhunter-backend sh -c "cd /app/backend && python -m pytest -q"
→ ImportError while loading conftest '/app/backend/tests/conftest.py'.
  tests/conftest.py:14: in <module>
      from backend.models import Base
  ImportError: cannot import name 'Base' from 'backend.models'
```
Ursache: `Base` ist in `backend/core/database.py` definiert, wird aber von
`backend/models/__init__.py` nicht re-exportiert. `conftest.py` (genutzt von
allen 3 Testdateien über `testpaths = tests` in `pytest.ini`) importiert
`Base` fälschlich aus `backend.models` statt aus `backend.core.database`.
**Konsequenz: Keine einzige der 3 Testdateien kann aktuell laufen –
Testabdeckung ist faktisch 0 %, unabhängig vom Inhalt der Tests selbst.**
Der Fehler betrifft ausschließlich `tests/`, nicht die Anwendung selbst
(Laufzeitcode importiert `Base` korrekt aus `core.database`).
*Hinweis zur Prüfmethode: `pytest`/`pytest-asyncio`/`aiosqlite` aus
`requirements-dev.txt` wurden für diesen Test temporär und ausschließlich
im laufenden Container installiert (nicht im Image, nicht im Git-Repo) –
rein zur Verifikation, ohne bleibende Änderung.*

Inhaltlich vorhanden ist nur `test_followup_scheduler.py` (Unit- + In-Memory-
Integrationstests für `services/followup_scheduler.py`, Issue #64) – für ein
Projekt mit 30 Service-Modulen, 18+3 API-Modulen und 15 Models ist das eine
sehr dünne Abdeckung, sobald der Import-Fehler behoben ist.

**Frontend-Tests – nicht vorhanden:**
Kein Testframework in `frontend/package.json` (weder Vitest noch Jest o. ä.),
keine `*.test.ts(x)`/`*.spec.ts(x)`-Dateien im gesamten `frontend/src`.
0 % Testabdeckung, keine Teststrategie erkennbar.

**Linting – Frontend verifiziert kaputt, Backend nicht vorhanden:**
```
docker exec jobhunter-frontend sh -c "cd /app && npm run lint"
→ ESLint couldn't find a configuration file.
```
Es existiert **keine** `.eslintrc*`- oder `eslint.config.*`-Datei im
gesamten `frontend/`-Verzeichnis, obwohl `eslint` als Dependency und
`"lint": "eslint src --ext ts,tsx"` als Skript in `package.json` deklariert
sind. Der Lint-Befehl aus dem README/package.json ist **im Ist-Zustand
nicht ausführbar**.
Für das Backend ist in `requirements-dev.txt` kein Linter/Formatter
(z. B. `ruff`, `black`, `flake8`) deklariert; entsprechend gibt es keinen
Lint-Befehl und keine Konfiguration dafür.

**Build – Frontend-Produktionsbuild verifiziert kaputt:**
```
docker exec jobhunter-frontend sh -c "cd /app && npm run build"   # = tsc && vite build
→ tsc gibt nur die eigene Hilfe/Versionsausgabe aus (Version 5.9.3),
  kein Kompilierlauf.
```
Ursache: **Es existiert kein `tsconfig.json`** in `frontend/` – weder aktuell
noch, laut `git log --all -- frontend/tsconfig.json`, jemals in der
gesamten Repo-Historie. `tsc` findet ohne Konfigurationsdatei und ohne
Datei-Argumente nichts zu kompilieren und bricht praktisch wirkungslos ab,
`vite build` wird dadurch nie erreicht.

**Erklärung, warum das bisher nicht aufgefallen ist:** `frontend/Dockerfile`
startet den „Produktions"-Container mit
`CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]` –
**der tatsächlich laufende Frontend-Container ist der Vite-Dev-Server**, nicht
ein gebauter Produktions-Bundle. Der (kaputte) `npm run build`-Pfad wird im
gesamten aktuellen Betrieb nie durchlaufen. Das erklärt, warum die App
trotz fehlender `tsconfig.json` sichtbar funktioniert, aber auch, dass ein
echter Produktionsbuild derzeit gar nicht möglich ist. **Hohe Priorität für
Phase 3/4** – betrifft sowohl Performance/Ressourcenverbrauch im
Dauerbetrieb (Dev-Server statt optimiertem Static-Build) als auch die reine
Möglichkeit, überhaupt jemals `npm run build` erfolgreich auszuführen.

**CI/CD:** Bestätigung des Befunds aus 1.1 – kein `.github/workflows/`,
keine automatisierte Ausführung von Tests/Lint/Build bei Pull Requests.
Mit den drei oben genannten kaputten Befehlen wäre eine naiv eingerichtete
CI ohnehin sofort rot; eine CI-Einführung (Phase-Empfehlung „Engineering")
sollte daher zeitlich nach der Behebung dieser drei Fehler erfolgen, nicht
davor.

**Pre-Commit/Sonstige Qualitäts-Gates:** Keine `.pre-commit-config.yaml`
oder vergleichbare Konfiguration im Repo gefunden.

### Offene Fragen aus diesem Abschnitt

Keine – alle drei Kernbefunde (Test-Import-Fehler, fehlende ESLint-Config,
fehlende tsconfig.json) sind durch tatsächliche Befehlsausführung
zweifelsfrei bestätigt, nicht nur vermutet.

### 1.6 Security/OWASP/Datenschutz-Sichtung

**🔴 Kritischer Fund – Path Traversal / Arbitrary File Write beim CV-Upload:**
`backend/api/cv.py`, Endpunkt `POST /cv/upload`:
```python
ext = os.path.splitext(file.filename)[1].lower()
if ext not in allowed:                       # nur Endungspruefung
    raise HTTPException(...)
dest = os.path.join(UPLOAD_DIR, file.filename)  # <-- Dateiname UNGEPRUEFT
with open(dest, "wb") as f:
    shutil.copyfileobj(file.file, f)
```
`file.filename` stammt direkt aus dem vom Client gesendeten
Multipart-Header und wird **ohne Sanitisierung** in `os.path.join`
verwendet. Die Endungsprüfung schützt nicht davor, weil sie nur das Suffix
prüft, nicht die Pfadstruktur davor – ein Dateiname wie
`../../../app/irgendwas.pdf` erfüllt die Endungsprüfung trotzdem und
würde außerhalb von `UPLOAD_DIR` schreiben (klassisches **OWASP
A03:2021 – Injection / Path Traversal**, praktisch ein potenzieller
Arbitrary-File-Write). Derselbe ungeprüfte Dateiname wird beim späteren
Lesezugriff wiederverwendet (`api/cv.py:92`,
`os.path.join(UPLOAD_DIR, cv.filename)`), das Problem pflanzt sich also
fort. **Empfehlung (Phase 3/4, Aufwand S):** Dateinamen serverseitig neu
generieren (z. B. UUID + geprüfte Endung) statt Client-Input zu
übernehmen – Standardmuster, keine Architekturänderung nötig.
Weitere Upload-Endpunkte (`routers/jobs_image.py` für Foto-Upload) nutzen
kein vergleichbares Dateisystem-Pattern (Bilder werden direkt aus dem
Request-Body verarbeitet, nicht dateibasiert gespeichert) – dort kein
gleichartiges Risiko gefunden.

**Bereits in 1.3/1.4 dokumentierte, hier eingeordnete Sicherheitsbefunde**
(nicht wiederholt, nur klassifiziert):
- **OWASP A02 (Cryptographic Failures) / A05 (Security Misconfiguration):**
  Schwache Default-Secrets (`SECRET_KEY="changeme"`) als Python-Fallback in
  `core/config.py`, falls `.env` fehlt.
- **OWASP A01 (Broken Access Control):** Der optionale JWT-Auth-Mechanismus
  ist nicht erreichbar (Router nicht eingebunden, vermutlich keine
  DB-Tabelle) – für den aktuellen Einsatzzweck (rein lokal, kein
  Netzwerk-Exposure vorgesehen) kein akutes Risiko, wird aber **kritisch**,
  falls die App jemals über `localhost` hinaus exponiert wird (z. B. Reverse
  Proxy, Zugriff aus dem Heimnetz), ohne dass vorher ein funktionierender
  Auth-Layer nachgerüstet wird.

**Positiv verifizierte Punkte:**
- Kein Treffer für rohe SQL-String-Interpolation (`text(f"..."`,
  `.format()` in Queries) – SQLAlchemy-ORM wird durchgängig parametrisiert
  genutzt, kein erkennbares SQL-Injection-Risiko.
- Kein `dangerouslySetInnerHTML` im gesamten Frontend – kein
  offensichtliches XSS-Einfallstor über React-Rendering.
- Kein `eval`/`exec`/`os.system`/`subprocess` im Backend – kein
  Command-Injection-Risiko durch dynamische Codeausführung gefunden.
- CORS (`main.py`) ist auf `http://localhost:3000` fest eingestellt, kein
  Wildcard (`*`) – korrekt restriktiv für den self-hosted Einsatzzweck.
- `.env` nicht im Git getrackt (s. 1.3); API-Keys Dritter werden
  Fernet-verschlüsselt in der DB abgelegt (s. 1.3).
- DB-Service ohne Host-Port-Exposure (s. 1.4).

**Fehlendes Rate-Limiting:** Keine Rate-Limiting-Bibliothek (z. B. `slowapi`)
oder eigene Implementierung im Backend gefunden. Für ein rein lokal
laufendes Tool aktuell geringes Risiko, sollte aber spätestens beim
Nachrüsten von Auth/Netzwerk-Exposure (s. o.) mitgedacht werden – insbesondere
für KI-Endpunkte (`api/ai.py`), die Rechenzeit/Ollama-Ressourcen kosten.

**Dependency-Risiken:** Kein `dependabot.yml` oder vergleichbare
automatisierte Abhängigkeits-Überwachung im Repo (`.github/` enthält nur
Templates, s. 1.1/1.5). Backend- und Frontend-Abhängigkeiten sind zwar exakt
gepinnt (gut für Reproduzierbarkeit), aber ohne automatisierte
Sicherheits-Scans (`pip-audit`, `npm audit`, Dependabot/Renovate) bleiben
bekanntwerdende CVEs in den gepinnten Versionen unbemerkt. Dies wurde hier
nicht durch einen tatsächlichen Scan verifiziert (kein Internetzugriff aus
dem Audit-Kontext angenommen/nicht geprüft) – als Empfehlung für die
Engineering-Phase markiert, nicht als bestätigter Fund einzelner CVEs.

**Datenschutz/DSGVO:** `docs/dsgvo.md` und `docs/PRIVACY.md` existieren
bereits und sind inhaltlich substanziell (Datenkategorien, Speicherort,
Zweck, Rechtsgrundlage tabellarisch aufgeführt; lokal-only-Architektur
als zentrales Datenschutzversprechen). Deckt die vom Auftrag geforderten
Datenschutz-Aspekte für sensible Bewerbungsdaten bereits gut ab – wird in
Phase 4/5 lediglich um die fehlende englische Vollständigkeit geprüft
(beide Dateien sind laut Kopfzeile bereits zweisprachig
angelegt, Detailprüfung der EN-Vollständigkeit folgt bei Bedarf in Phase 4).

### Offene Fragen aus diesem Abschnitt

- Keine offenen Fragen – der Path-Traversal-Fund ist eindeutig im Code
  nachvollziehbar, keine Annahme nötig.

### 1.7 Architekturdiagramm

Beide Diagramme bilden ausschließlich tatsächlich im Code vorgefundene
Komponenten ab (`docker-compose.yml`, `main.py`-Router-Registrierung,
`services/job_search/`, `services/{mail,email_parser,company_research}.py`).
Keine geplanten/erfundenen Komponenten enthalten.

**System-/Deployment-Sicht:**

```mermaid
flowchart LR
    Browser["Browser (Nutzer)"]

    subgraph Docker["Docker Compose (jobhunter-net)"]
        FE["frontend\nVite **Dev-Server** in \"Produktion\"\n:3000"]
        BE["backend\nFastAPI + SQLAlchemy async\n:8000"]
        DB[("db\nPostgreSQL 16-alpine\nnur intern, kein Host-Port")]
        OL["ollama\nLokale KI-Inferenz\n:11434 (Modelle z.B. mistral)"]
    end

    Ext1["Jobbörsen-APIs/-Scraper\nBundesagentur, Adzuna,\nStepStone, LinkedIn, EURES"]
    Ext2["Wikipedia API\n(Firmen-Dossier)"]
    Ext3["IMAP-Server\n(E-Mail-Parsing, Nutzer-Konto)"]
    Ext4["SMTP-Server\n(Erinnerungs-/Vorlagen-Mails)"]

    Browser -- "HTTP :3000" --> FE
    FE -- "REST/JSON :8000" --> BE
    BE -- "SQL (asyncpg) :5432 intern" --> DB
    BE -- "HTTP :11434 intern" --> OL
    BE -- "HTTPS" --> Ext1
    BE -- "HTTPS" --> Ext2
    BE -- "IMAP" --> Ext3
    BE -- "SMTP" --> Ext4
```

**Backend-Modulsicht** (durchgezogen = aktiv genutzt, gestrichelt = toter Code
laut Abschnitt 1.3/1.4):

```mermaid
flowchart TD
    Main["main.py"]
    ApiPkg["api/ (18 Module)"]
    RoutersPkg["routers/ (3 Module:\nblocklist, followups, jobs_image)"]
    Services["services/ (30 Module +\njob_search/-Unterpaket)"]
    Schemas["schemas/ (3 Module:\napplication, job, settings)"]
    ModelsPkg["models/ (Package, 14 registrierte\nModelle inkl. Base aus core.database)"]
    Core["core/ (config, database,\nsecurity, crypto)"]
    AlembicActive["backend/alembic/\n(0001-0004, AKTIV)"]
    DBNode[("PostgreSQL")]

    ModelsOld["backend/models.py\n(TOTER CODE, vom Package ueberschattet)"]
    AlembicOld["/alembic/ (Top-Level)\n(TOTER CODE, nie im Docker-Build-Context)"]
    AuthApi["api/auth.py\n(nicht in main.py eingebunden)"]
    CLPdfApi["api/cover_letter_pdf.py\n(nicht eingebunden, Feature #89 geplant)"]

    Main -->|"app.include_router()\nfuer 16 von 18 Modulen"| ApiPkg
    Main -->|"app.include_router()"| RoutersPkg
    ApiPkg --> Services
    RoutersPkg --> Services
    ApiPkg -.->|"nicht registriert"| AuthApi
    ApiPkg -.->|"nicht registriert"| CLPdfApi
    ApiPkg --> Schemas
    Services --> ModelsPkg
    ModelsPkg --> Core
    Core --> DBNode
    AlembicActive --> DBNode

    ModelsOld -.->|"kein Import mehr"| ModelsPkg
    AlembicOld -.->|"kein Build-Context-Bezug"| DBNode
```

### Offene Fragen aus diesem Abschnitt

Keine – Diagramme fassen ausschließlich bereits verifizierte Befunde aus
1.1–1.6 zusammen.

## Zusammenfassung Phase 1

Kurzer, sortierter Überblick über die Kernbefunde aus 1.1–1.7 – Details
und Begründungen jeweils im referenzierten Abschnitt. Bewertung/Priorisierung
(kritisch/hoch/mittel/niedrig, Aufwand, Empfehlung) folgt in Phase 2, hier nur
Bestandsaufnahme.

**Verifiziert kaputt (durch tatsächliche Befehlsausführung, nicht nur gelesen):**
- Backend-Testsuite: `ImportError` beim Sammeln, 0 % lauffähig (1.5).
- Frontend-Lint: keine ESLint-Konfiguration vorhanden, Befehl bricht ab (1.5).
- Frontend-Produktionsbuild: keine `tsconfig.json` im gesamten Repo, `tsc`
  läuft ins Leere (1.5). Bleibt unbemerkt, weil der „Produktions"-Container
  tatsächlich den Vite-Dev-Server startet (1.5).

**Sicherheitsrelevant (1.6):**
- 🔴 Path-Traversal-Risiko beim CV-Upload (`api/cv.py`, ungeprüfter
  Client-Dateiname).
- Schwache Default-Secrets als Fallback ohne `.env` (1.3/1.6).
- Kein funktionierender Auth-Pfad trotz vorhandenem JWT-Code (1.3/1.4/1.6).
- Kein Rate-Limiting, kein automatisiertes Dependency-Scanning (1.6).
- Positiv: keine SQLi-/XSS-/Command-Injection-Muster gefunden, CORS
  restriktiv, `.env` nicht getrackt, API-Keys verschlüsselt, DB ohne
  Host-Port-Exposure, DSGVO-/Privacy-Dokumentation bereits vorhanden (1.6).

**Struktur/Altlasten (1.1/1.3/1.4):**
- Zwei parallele Endpunkt-Ordner (`api/` vs. `routers/`) ohne fachlichen Grund.
- Toter Code: `backend/models.py`, Top-Level-`/alembic/`-Baum – beide vom
  Projekt selbst (Migrations-Kommentar) bzw. durch Docker-Build-Context
  nachweislich unbenutzt.
- `User`-Modell ohne Registrierung, ohne Migration, ohne erreichbaren Router
  – Auth wirkt wie ein unvollständiges Feature-Fragment.
- Uneinheitliche Sprachführung über drei verschiedene Muster
  (Datei-Duplikat, Ein-Datei-DE/EN-Mix, nur-Deutsch) in `docs/`/`wiki/`/README.

**Internationalisierung (1.2, zentral für den Auftrag):**
- i18n-Infrastruktur (i18next/react-i18next) vorhanden, aber nur in **5 von
  45** Frontend-Dateien genutzt (~11 %).
- Übersetzungen inline in einer Datei statt als Namespace-/JSON-Struktur,
  decken nur Nav/Dashboard/Jobs/Settings/Common ab.
- Positiv: Deutsch ist bereits korrekt als Standard+Fallback verankert,
  keine Browser-Locale-Verdrängung.

**Nicht kritisch, aber wartungsrelevant (1.2/1.3):**
- Kein zentraler Frontend-API-Client (`axios` in 22 Dateien direkt genutzt).
- Dünne Pydantic-Schema-Schicht (3 Module) im Verhältnis zu 18+3
  API-Modulen.
- Namenskollision `pages/CompanyDossier.tsx` / `components/CompanyDossier.tsx`.
- `pages/CoverLetter.tsx` ohne eigene Route, Einbindungspfad nicht
  abschließend verifiziert.

Diese Zusammenfassung ist bewusst noch **unbewertet** (keine Priorisierung,
keine Aufwandsschätzung) – das ist Gegenstand von Kapitel 2
(„Qualitäts- und Architekturbewertung"), das als eigener Arbeitsschritt
folgt.

## 2. Qualitäts- und Architekturbewertung

Bewertet die Befunde aus Kapitel 1 systematisch nach Priorität, Aufwand und
Risiko. Format je Empfehlung: Beobachtung → Problem/Chance →
Priorität → Empfehlung → Aufwand (S/M/L/XL) → Risiko der Umsetzung.
Priorität bezieht sich auf die Dringlichkeit *vor* Beginn der
i18n-Umsetzung (Phase 4) bzw. eines echten Produktionsbetriebs – nicht
zwingend auf die Reihenfolge in der Roadmap (die folgt in Kapitel 3).

### 2.1 Codequalität

| # | Beobachtung (Ref.) | Priorität | Empfehlung | Aufwand | Risiko der Umsetzung |
|---|---|---|---|---|---|
| 1 | Backend-Tests kaputt: `Base`-Import in `conftest.py` falsch (1.5) | **Kritisch** | Import auf `from backend.core.database import Base` korrigieren | S | Sehr gering – Ein-Zeilen-Fix, durch grünen Testlauf sofort verifizierbar |
| 2 | Kein ESLint-Config im Frontend (1.5) | **Kritisch** | `eslint.config.js` (Flat Config, passend zu ESLint 8.57) mit TypeScript+React-Regeln anlegen | S | Gering – Config-Erstellung, ggf. viele Erstbefunde beim ersten Lauf abzuarbeiten (separater Folgeaufwand) |
| 3 | Keine `tsconfig.json`, `npm run build` faktisch nie lauffähig (1.5) | **Kritisch** | `tsconfig.json` passend zu Vite/React/TS 5.4 anlegen (`tsc --init` + Vite-Preset als Basis), danach `npm run build` verifizieren | S–M | Mittel – TypeScript-Strict-Modus kann bestehende, bisher nie typgeprüfte Fehler aufdecken; iteratives Vorgehen empfohlen |
| 4 | „Produktions"-Container startet Vite-Dev-Server statt Build (1.5) | **Hoch** | Mehrstufiges `frontend/Dockerfile` (Build-Stage mit `npm run build`, Serve-Stage z. B. `nginx`/`vite preview`) | M | Mittel – Deployment-Verhalten ändert sich sichtbar, vor Umstellung lokal gegentesten |
| 5 | Path Traversal beim CV-Upload (1.6) | **Kritisch** | Serverseitige UUID-Dateinamen statt Client-`filename` übernehmen | S | Gering – lokal isolierter Fix in `api/cv.py`, keine Schema-Änderung |
| 6 | Schwache Default-Secrets in `core/config.py` (1.3/1.6) | **Hoch** | Bei fehlendem `SECRET_KEY`/`ENCRYPTION_KEY` **hart fehlschlagen** (`raise` statt stillem Fallback) statt unsicherer Defaults | S | Gering – reine Absicherung, betrifft nur den Fehlerfall bei fehlkonfiguriertem `.env` |
| 7 | Zwei tote Code-Pfade: `backend/models.py`, Top-Level-`/alembic/` (1.1/1.3/1.4) | **Niedrig** | Beide Pfade entfernen (nachweislich unbenutzt) | S | Sehr gering – reine Löschung, durch Tests/Build-Lauf danach absicherbar |
| 8 | Gespaltene Endpunkt-Schicht `api/` vs. `routers/` (1.3) | **Mittel** | Auf einen Ordnernamen vereinheitlichen (z. B. alles nach `routers/` verschieben, `api/` auflösen) | M | Mittel – reine Verschiebung, aber viele Importpfade betroffen; am besten in Phase 3 zusammen mit anderer Strukturbereinigung |
| 9 | `User`-Modell ohne Registrierung/Migration/Router (1.3/1.4) | **Mittel** *(Produktentscheidung nötig)* | Erst entscheiden: Auth-Feature vervollständigen (Migration nachziehen, Router einbinden) **oder** vollständig entfernen (Modell, `core/security.py`-Teile, `api/auth.py`) | M–L je nach Entscheidung | Mittel – Entscheidung hat Domänenauswirkung (Mehrbenutzerfähigkeit lt. Auftrag gewünscht) |
| 10 | Kein zentraler Frontend-API-Client, `axios` 22× direkt genutzt (1.2) | **Mittel** | Zentralen `frontend/src/lib/api.ts` mit `axios.create({baseURL})` + Interceptor für Fehlerbehandlung einführen, Aufrufe schrittweise migrieren | M | Gering – additiv einführbar, alte Aufrufe funktionieren parallel weiter während der Migration |
| 11 | Dünne Schema-Schicht (3 Pydantic-Module ggü. 18+3 API-Modulen) (1.3) | **Mittel** | Pro Domäne (z. B. `reminders`, `cv`, `interview`) eigenes Schema-Modul ergänzen, wo aktuell inline/ORM-direkt validiert wird | L | Gering – additiv, schrittweise pro Endpunkt möglich |
| 12 | Kein Rate-Limiting (1.6) | **Niedrig** *(steigt bei Netzwerk-Exposure)* | `slowapi` oder einfache Middleware ergänzen, sobald Auth/Exposure angegangen wird | S | Gering |
| 13 | Kein Dependency-Scanning (1.6) | **Mittel** | `dependabot.yml` (oder Renovate) für `pip`/`npm` einrichten; einmalig `pip-audit`/`npm audit` laufen lassen | S | Sehr gering – reine Automatisierung |
| 14 | Namenskollision `pages/CompanyDossier.tsx` / `components/CompanyDossier.tsx` (1.2) | **Niedrig** | Eine der beiden Dateien umbenennen (z. B. `CompanyDossierPage.tsx`) nach Klärung der Rollen | S | Sehr gering |
| 15 | `pages/CoverLetter.tsx` ohne eigene Route (1.2) | **Niedrig** | Einbindungspfad dokumentieren (Kommentar/ADR), keine Code-Änderung zwingend nötig | S | Keines – informativ |

**Übergreifende Beobachtung:** Die drei kritischen Kaputt-Befunde (#1, #2,
#3) sind bewusst **vor** jede weitere Empfehlung zu stellen – ohne
lauffähige Tests/Lint/Build kann keine der übrigen Maßnahmen (erst recht
nicht die groß angelegte i18n-Migration in Phase 4) verlässlich verifiziert
werden. Dies bestimmt maßgeblich die Reihenfolge der Roadmap in Kapitel 3.

### Offene Fragen aus diesem Abschnitt

- Produktentscheidung zu Punkt 9 (`User`-Modell/Auth) steht weiterhin aus
  – siehe bereits in 1.3/1.4 vermerkt, hier nur in die Priorisierung
  eingeordnet.

---

*Fortsetzung folgt (2.2 Stack-Eignung, …) gemäß `docs/analysis/BACKLOG.md`.*
