# JobHunter – Repository Audit (English)

> **Status of this document:** Phase 1 (repository inventory) complete.
> Phase 2 (quality/architecture assessment with prioritized recommendations)
> follows in a separate work step and will be added as its own section
> "## 2. Quality and Architecture Assessment" (see `docs/analysis/BACKLOG.md`
> for progress). German version: `docs/analysis/REPOSITORY_AUDIT_DE.md`
> (equivalent content).
>
> As of: 2026-08-24. All statements are based on actual inspection of the
> checkout in LXC 142 (`/root/JobHunter`, branch `main`,
> remote `https://github.com/freddykrueger88/JobHunter.git`).

## 1. Project Inventory

### 1.1 Project Structure & Module Boundaries

JobHunter is a monorepo with a clear split into four Docker services
(see `docker-compose.yml`):

| Directory | Role | Technology (current state) |
|---|---|---|
| `backend/` | REST API, business logic, DB access | Python 3.11, FastAPI 0.111.0, SQLAlchemy 2.0.30 (async, via `asyncpg`), Alembic 1.13.1 |
| `frontend/` | Single-page application | React 18.3.1, Vite 5.2.13, TypeScript 5.4.5, TailwindCSS 3.4.4, i18next 23.11.5 / react-i18next 14.1.2 |
| `db` (compose service) | Persistence | PostgreSQL (image from `docker-compose.yml`, see database section) |
| `ollama` (compose service) | Local AI inference | Ollama, models pulled at runtime (currently includes `mistral`) |

Other top-level areas:

- `docs/` – 11 topic documents (incl. `architecture.md`, `dsgvo.md`,
  `PRIVACY.md`, `accessibility.md`, `roadmap.md`, `faq.md`,
  `backup-restore.md`, `ai-models.md`, `api-keys.md`, `portals.md`,
  `setup.md`). Several files are already structured as a single-page DE/EN
  mix (sections "## Deutsch" / "## English" in the same file), e.g.
  `architecture.md`, `CHANGELOG.md` – a different pattern from the
  separate-page-per-language scheme requested in the brief.
- `wiki/` – 6 Markdown files (`Home.md`, `Installation.md`,
  `Konfiguration.md`, `Entwicklung.md`, `Barrierefreiheit.md`,
  `Changelog.md`), **German only**, tracked directly in the main repo (not
  the separate `JobHunter.wiki.git` tree that GitHub uses for actual wikis –
  see the CI/CD & Publishing section).
- `alembic/` (top-level) **and** `backend/alembic/` – two Alembic trees
  exist simultaneously (`alembic.ini` + `backend/alembic.ini`). **Open
  question / risk:** unclear whether the top-level tree is still actively
  used or a leftover from an earlier structure – must be clarified before
  any migration change (potential source of inconsistent schema history).
- `.github/` – issue templates only (`bug.md`, `feature.md`,
  `accessibility.md`, `docs.md`, `config.yml`) and
  `PULL_REQUEST_TEMPLATE.md`. **No `.github/workflows/` directory – no
  CI/CD automation currently in the repo.**
- Root documents: `README.md` (English, leading in the repo root),
  `README.de.md` (German, linked from README.md), `CHANGELOG.md`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`,
  `LICENSE` (MIT per README badge), `CITATION.cff`, `HUMANS.md`,
  `INSTALL.md`.
- `scripts/setup.sh` – the only top-level helper script.

### Observation on Language Handling (project-wide)

The current state is inconsistent across three patterns:

1. **Per-language file duplicate**: `README.md` (EN) / `README.de.md` (DE).
2. **One file, two sections**: `docs/architecture.md`,
   `docs/CHANGELOG.md` – DE/EN via anchors (`#deutsch` / `#english`) in the
   same file.
3. **Single language only**: `wiki/*.md` (German only), most other
   `docs/*.md` files (not examined in detail yet, follows in 1.2 ff.).

The scheme requested in the brief (separate pages `Page` / `Page-English`)
**does not** exist in the current state – that is a deliberate architecture
decision for Phase 5, not a bug.

### Open Questions from this Section

- Purpose of the duplicate Alembic tree (`/alembic` vs. `/backend/alembic`)
  unresolved – examined further in the "Database/Migrations" section
  (backlog item 1.4).
- Whether `docs/` and `wiki/` are deliberately kept redundant (e.g. `docs/`
  for developers, `wiki/` for end users) or grew historically cannot be
  answered from the code alone – flagged as an assumption, not a fact.

### 1.2 Frontend Inventory

**Scope:** 45 TypeScript/TSX files under `frontend/src/`.

| Area | Files | Examples |
|---|---|---|
| `pages/` (route level) | 11 | `Dashboard.tsx`, `Jobs.tsx`, `Kanban.tsx`, `History.tsx`, `Settings.tsx`, `Reminders.tsx`, `SearchProfiles.tsx`, `InterviewSimulator.tsx`, `CompanyDossier.tsx`, `CoverLetter.tsx`, `Onboarding.tsx` |
| `components/` | 21 | incl. `AtsScorePanel`, `AutoApplyButton`, `BadgesPanel`, `CoachChatDrawer`, `CompanyDossier`, `EmailParsingSetup`, `ExportImportPanel`, `MarketAnalyzerPanel`, `SalaryNegotiationModal`, `TopNav` |
| `context/` | 2 | `ThemeContext.tsx`, `AccessibilityContext.tsx` |
| `hooks/` | 5 | `useAnnounce`, `useConfirm`, `useFocusTrap`, `useKeyboardShortcuts`, `useUndoToast` |
| Entry/config | `App.tsx`, `main.tsx`, `i18n.ts` | – |

**Routing** (`App.tsx`, `react-router-dom` v6, `BrowserRouter` in
`main.tsx`): 9 top-level routes (`/`, `/jobs`, `/kanban`, `/history`,
`/settings`, `/reminders`, `/search-profiles`, `/interview-simulator`,
`/company-dossier`). `pages/CoverLetter.tsx` has **no route of its own** –
reference search shows it is used from `Kanban.tsx` and
`components/AutoApplyButton.tsx`, presumably as a modal/sub-component in
the application workflow rather than a standalone page. The exact call
path was not conclusively verified – flagged as an open question.

**Naming collision:** Both `pages/CompanyDossier.tsx` and
`components/CompanyDossier.tsx` exist. Without a deeper look into both
files it is unclear whether this is a page+sub-component pair (analogous
to the CoverLetter pattern) or unintentional duplication – flagged as an
open question for Phase 2.

**State management:**
- Server state: TanStack React Query (`@tanstack/react-query`, one global
  `QueryClient` in `main.tsx`), used directly in 9 of 45 files
  (`useQuery`/`useMutation`).
- No global client-state store (no Redux/Zustand/Jotai) – local `useState`
  plus two React context providers (`Theme`, `Accessibility`) for
  app-wide cross-cutting concerns. Appropriate for the project size, see
  assessment in Phase 2.
- **No central API client**: `axios` is imported directly in 22 of 45
  files; there is no `api.ts`/`client.ts`/`services/` file and no match for
  `axios.create(...)` or a central `baseURL` configuration. Every
  component apparently builds its own requests. **Risk:** duplicated
  base-URL/header/error-handling logic across many files – relevant both
  for maintainability (Phase 2) and for consistent i18n of API error
  messages (Phase 4).

**i18n coverage (key finding for Phase 4):**
- `useTranslation` is used in **5 of 45 files**: `TopNav.tsx`,
  `Dashboard.tsx`, `Jobs.tsx`, `Onboarding.tsx`, `Settings.tsx`. That is
  **roughly 11% of frontend files** – the remaining 40 files presumably
  contain predominantly hardcoded German UI text.
- Translation resources live **inline in `i18n.ts`** as a JS object (no
  separate `locales/` directory, no per-language/namespace JSON files), and
  cover only a small slice: `nav`, `dashboard` (title/status labels),
  `jobs` (title/search/hide), `settings` (title/theme/language/AI),
  `common` (save/cancel/delete/loading). Module namespaces for the
  remaining ~20 pages/components (Kanban, Reminders, SearchProfiles,
  InterviewSimulator, CompanyDossier, CoverLetter, all panels/modals) are
  completely missing.
- Rough sample estimate (regex search for capitalized JSX text nodes with
  typically German word patterns, **not an exact measure**, does not
  capture e.g. `placeholder`/`aria-label` attributes or multi-line text):
  at least 36 hits for probably hardcoded German UI text with this crude
  method alone – the actual number is likely much higher. A reliable,
  complete count requires manual review per file; that work is deferred to
  the migration batches in Phase 4 (backlog item 4.3) rather than done here.
- Language-selection mechanics in `i18n.ts`:
  `lng: localStorage.getItem('lang') || 'de'`, `fallbackLng: 'de'` –
  **German is already correctly anchored as the default and fallback**, but
  there is no browser-locale detection (deliberately so, which prevents
  exactly the "browser locale must not override German" requirement from
  the brief – so this point is already compliant, not something to "fix").

### Open Questions from this Section

- Exact integration path of `pages/CoverLetter.tsx` (modal? own sub-route
  via state instead of the router?) – needs clarifying before this page's
  i18n migration.
- Purpose/relationship of `pages/CompanyDossier.tsx` to
  `components/CompanyDossier.tsx`.
- Whether the missing browser-locale detection is a deliberate decision or
  simply not yet implemented – flagged as an assumption (currently treated
  as "already brief-compliant", see above).

### 1.3 Backend Inventory

**Structure** (`backend/`, Python 3.11 + FastAPI, all paths imported under
`backend.*`):

| Directory | Files | Role |
|---|---|---|
| `api/` | 18 modules | Main endpoint layer (jobs, applications, settings, cv, ai, dashboard, history, reminders, export, interview, company, eures, calendar, company_dossier, email_parsing, auth, cover_letter_pdf) |
| `routers/` | 3 modules | Newer endpoints (`blocklist.py`, `followups.py`, `jobs_image.py`) – **a second, parallel directory for the same concept (endpoints)** alongside `api/` |
| `models/` | 12 modules + `__init__.py` | SQLAlchemy ORM models (application, job, user, cv, reminder, settings, history, search_profile, cover_letter, cover_letter_template, blocklist, followup, backup_log, user_badge, application_status_log) |
| `services/` | 30 modules + `job_search/` sub-package | Business logic/integrations (AI prompts, ATS scorer, auto-apply, backup, calendar export, CV parser/optimizer, e-mail parser/templates, ghost-job detector, salary calculator, scheduler, skill gap, and more) |
| `schemas/` | 3 modules | Pydantic schemas (only `application`, `job`, `settings` – see finding below) |
| `core/` | 4 modules | `config.py` (settings), `database.py`, `security.py` (JWT, optional), `crypto.py` (Fernet encryption) |
| `alembic/` | – | Migrations (see section 1.4) |
| `tests/` | 3 files | see section 1.5 |

**Finding – endpoint layer split (`api/` vs. `routers/`):**
No discernible technical reason for the split – `routers/` contains only
the most recently added endpoints (`blocklist`, `followups`, `jobs_image`),
while all older endpoints live in `api/`. `main.py` imports from both
directories in parallel. For the target structure (Phase 3), unifying on
one directory name is recommended.

**Finding – `models.py` is dead code:**
Alongside the `models/` package, the old single file `backend/models.py`
(6.9 KB) still exists. No active module imports from it anymore (`grep`
across all `.py` files returns no genuine imports of `backend.models` as a
single file). **Confirmed by the code itself**: a comment in the new,
currently in-progress migration
(`backend/alembic/versions/0004_add_blocklist_badges_backup_templates.py`)
explicitly states that `backend/models.py` was "shadowed by the
`backend/models/` package". `models.py` should be removed as legacy in
Phase 3 (effort S, risk low – demonstrably no longer imported).

**Finding – two unregistered API modules:**
`main.py` includes 16 routers; `api/auth.py` and `api/cover_letter_pdf.py`
exist but are **not** included in `main.py`.
- `cover_letter_pdf.py` matches the "Cover Letter Template" feature marked
  as "planned – #89" in `README.md` – understandably unfinished, not a bug.
- `auth.py` implements `/auth/token` and `/auth/register` matching the
  optional JWT mechanism in `core/security.py`. Since the router is not
  included, there is currently **no reachable way to obtain a token**, even
  if `AUTH_ENABLED=true` were set – the auth mechanism is unusable in the
  current state. Open question whether this is intentional (app deliberately
  account-free/local-only per README) or a fragment of a planned
  multi-user feature.

**Auth/Secrets handling:**
- Authentication is **optional** via the `AUTH_ENABLED` env variable
  (default `false`) – matching the product promise "no account needed,
  local, self-hosted" from the README. For multi-user capability (a
  requirement named in the brief), the JWT mechanism would be the
  foundation, but it is currently not wired up (see above).
- `core/config.py` defines **Python-side default fallbacks** for
  `SECRET_KEY = "changeme"` and a `DATABASE_URL` with password `changeme` –
  if `.env` is missing or incomplete, the app starts with weak default
  secrets instead of failing hard. `.env.example` itself, by contrast,
  correctly guides toward generating secure values
  (`secrets.token_hex(32)`, `Fernet.generate_key()`). **Security risk,
  examined further in section 1.6 (Security/OWASP).**
- `.env` is correctly listed in `.gitignore` and **not** tracked in the git
  repo (`git ls-files .env` returns no match) – no secret leak found in the
  repo.
- Third-party API keys (e.g. for Adzuna/StepStone/Bundesagentur, per
  `docs/api-keys.md`) are, per `core/crypto.py`, stored as Fernet-encrypted
  values in the DB (`encrypt`/`decrypt` helpers) – a solid pattern for
  "at rest" protection of sensitive application/access data.
- SMTP credentials (`services/mail.py`) are passed as parameters per call
  (`smtp_user`, `smtp_password`), not held globally – the origin of these
  values (presumably decrypted from settings) is traced in section 1.6.

**Thin schema layer:**
Only 3 Pydantic schema modules (`application`, `job`, `settings`) face 18
`api/` and 3 `routers/` modules as well as 12 model modules. Many endpoints
presumably validate requests directly via the SQLAlchemy models or inline
Pydantic classes instead of through a unified schema layer – examined
further in Phase 2 (consistency of data contracts), not investigated in
detail here.

### Open Questions from this Section

- Is `api/auth.py` a deliberately dormant feature for future multi-user
  capability, or should auth remain permanently unused? This product
  decision cannot be answered from the code alone – a genuine open
  question for Phase 3.
- Origin/encryption status of SMTP credentials in the DB not yet verified
  (follows in 1.6).

### 1.4 Database/Migrations

**Duplicate Alembic tree – question from 1.1 now resolved:**
The top-level tree (`/alembic.ini`,
`/alembic/versions/20260511_0001_initial.py`, 1 migration) is
**demonstrably dead**:
- `backend/Dockerfile` sets `WORKDIR /app/backend` and copies only the
  contents of `backend/` into the image (`COPY . .` after
  `WORKDIR /app/backend`).
- `docker-compose.yml` builds the backend service with
  `build.context: ./backend` – the repo-root `/alembic/` folder **never**
  makes it into the image.
- `backend/entrypoint.sh` calls `alembic upgrade head` without a `-c` flag
  in the working directory `/app/backend` → only `backend/alembic.ini` with
  `script_location = alembic` (relative, i.e. `backend/alembic/`) is ever
  used.

→ The top-level `/alembic/` directory is legacy with no runtime effect and
should be removed in Phase 3 (effort S, risk low – purely additive
cleanup, no runtime dependency).

**Active migration history** (`backend/alembic/versions/`, 4 revisions,
linear, no discernible branches):

| Revision | Purpose |
|---|---|
| `0001_initial_schema` | Baseline schema |
| `0002_add_followups_table` | Follow-up tracking |
| `0003_add_color_blind_mode` | Single settings field (accessibility) |
| `0004_add_blocklist_badges_backup_templates` *(currently uncommitted, in progress)* | Blocklist, gamification badges, backup log, cover-letter templates |

`backend/alembic/env.py` correctly sets `sqlalchemy.url` at runtime from
`settings.DATABASE_URL` (from `.env`) – the placeholder value in
`backend/alembic.ini` (`driver://user:pass@localhost/dbname`) is thus never
actually used, but is potentially confusing as file content for new
contributors.

**Important finding – `User` model without migration/table:**
`backend/models/user.py` exists and is imported by `core/security.py` and
`api/auth.py`, but is **not** registered in `backend/models/__init__.py`
(unlike all 14 other models). Consistent with that: none of the four
migrations creates a `users` table. Since `backend/alembic/env.py`
registers all models for autogenerate exclusively via
`import backend.models` (the package, not the single file), `User` is
missing from `target_metadata` – a future
`alembic revision --autogenerate` would therefore not automatically add
the (non-existent) users table, but simply ignore it. **Practical
consequence:** the optional auth mechanism from section 1.3 (`api/auth.py`,
`core/security.py`) is thus not only unregistered in the router, but in
all likelihood **also has no database table** – even with
`AUTH_ENABLED=true` and the router included, `/auth/register` would
presumably fail with a DB error. This confirms the question left open in
1.3: auth looks like an incomplete, dormant feature fragment, not an
actively maintained function.

**DB service (`docker-compose.yml`):** `postgres:16-alpine`, **no host
port mapping** (reachable only internally on the Docker network – good
practice for a self-hosted tool with sensitive application data), health
check via `pg_isready` present, data in the named volume `pgdata`
(persistent across container restarts).

### Open Questions from this Section

- Product decision on whether the `User` model/auth feature should be
  pursued further (including adding the missing migration) or removed
  entirely – see also the open question from 1.3.

### 1.5 Tests/CI/Linting/Build

**These findings were not just read, but verified through actual command
execution in the running Docker containers**
(`docker exec jobhunter-backend`/`jobhunter-frontend`, see commands below).

**Backend tests – currently completely broken (verified):**
```
docker exec jobhunter-backend sh -c "cd /app/backend && python -m pytest -q"
→ ImportError while loading conftest '/app/backend/tests/conftest.py'.
  tests/conftest.py:14: in <module>
      from backend.models import Base
  ImportError: cannot import name 'Base' from 'backend.models'
```
Cause: `Base` is defined in `backend/core/database.py`, but is not
re-exported by `backend/models/__init__.py`. `conftest.py` (used by all 3
test files via `testpaths = tests` in `pytest.ini`) incorrectly imports
`Base` from `backend.models` instead of `backend.core.database`.
**Consequence: not a single one of the 3 test files can currently run –
test coverage is effectively 0%, regardless of the tests' actual content.**
The error affects only `tests/`, not the application itself (runtime code
correctly imports `Base` from `core.database`).
*Note on verification method: `pytest`/`pytest-asyncio`/`aiosqlite` from
`requirements-dev.txt` were installed temporarily and exclusively inside
the running container for this test (not in the image, not in the git
repo) – purely for verification, with no lasting change.*

The only test content that exists is `test_followup_scheduler.py`
(unit + in-memory integration tests for `services/followup_scheduler.py`,
issue #64) – for a project with 30 service modules, 18+3 API modules, and
15 models, that is very thin coverage once the import error is fixed.

**Frontend tests – none exist:**
No test framework in `frontend/package.json` (neither Vitest nor Jest or
similar), no `*.test.ts(x)`/`*.spec.ts(x)` files anywhere in
`frontend/src`. 0% test coverage, no discernible test strategy.

**Linting – frontend verified broken, backend not present:**
```
docker exec jobhunter-frontend sh -c "cd /app && npm run lint"
→ ESLint couldn't find a configuration file.
```
**No** `.eslintrc*` or `eslint.config.*` file exists anywhere in
`frontend/`, even though `eslint` is declared as a dependency and
`"lint": "eslint src --ext ts,tsx"` as a script in `package.json`. The lint
command from the README/package.json **cannot currently be executed**.
For the backend, `requirements-dev.txt` declares no linter/formatter (e.g.
`ruff`, `black`, `flake8`); accordingly there is no lint command and no
configuration for one.

**Build – frontend production build verified broken:**
```
docker exec jobhunter-frontend sh -c "cd /app && npm run build"   # = tsc && vite build
→ tsc only prints its own help/version output (version 5.9.3),
  no compilation run.
```
Cause: **no `tsconfig.json` exists** in `frontend/` – neither currently nor,
per `git log --all -- frontend/tsconfig.json`, ever in the repo's entire
history. With no config file and no file arguments, `tsc` finds nothing to
compile and effectively no-ops, so `vite build` is never reached.

**Explanation of why this has gone unnoticed:** `frontend/Dockerfile`
starts the "production" container with
`CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]` –
**the frontend container that actually runs is the Vite dev server**, not a
built production bundle. The (broken) `npm run build` path is never
exercised during current operation at all. That explains why the app
visibly works despite the missing `tsconfig.json`, but also that a real
production build is currently simply not possible. **High priority for
Phase 3/4** – affects both performance/resource usage in ongoing operation
(dev server instead of an optimized static build) and the sheer
possibility of ever successfully running `npm run build`.

**CI/CD:** Confirms the finding from 1.1 – no `.github/workflows/`, no
automated execution of tests/lint/build on pull requests. With the three
broken commands named above, a naively set-up CI would be red immediately
anyway; introducing CI (the "Engineering" phase recommendation) should
therefore happen after fixing these three issues, not before.

**Pre-commit/other quality gates:** No `.pre-commit-config.yaml` or
comparable configuration found in the repo.

### Open Questions from this Section

None – all three core findings (test import error, missing ESLint config,
missing tsconfig.json) are unambiguously confirmed through actual command
execution, not merely suspected.

### 1.6 Security/OWASP/Privacy Review

**🔴 Critical finding – path traversal / arbitrary file write on CV
upload:**
`backend/api/cv.py`, endpoint `POST /cv/upload`:
```python
ext = os.path.splitext(file.filename)[1].lower()
if ext not in allowed:                       # extension check only
    raise HTTPException(...)
dest = os.path.join(UPLOAD_DIR, file.filename)  # <-- filename UNCHECKED
with open(dest, "wb") as f:
    shutil.copyfileobj(file.file, f)
```
`file.filename` comes directly from the client-supplied multipart header
and is used in `os.path.join` **without sanitization**. The extension
check does not protect against this, because it only checks the suffix,
not the path structure before it – a filename like
`../../../app/something.pdf` still satisfies the extension check and would
write outside `UPLOAD_DIR` (classic **OWASP A03:2021 – Injection / Path
Traversal**, practically a potential arbitrary file write). The same
unchecked filename is reused on later read access (`api/cv.py:92`,
`os.path.join(UPLOAD_DIR, cv.filename)`), so the problem propagates.
**Recommendation (Phase 3/4, effort S):** regenerate filenames
server-side (e.g. UUID + verified extension) instead of taking client
input – a standard pattern, no architecture change needed. Other upload
endpoints (`routers/jobs_image.py` for photo upload) do not use a
comparable filesystem pattern (images are processed directly from the
request body, not stored file-based) – no similar risk found there.

**Security findings already documented in 1.3/1.4, classified here** (not
repeated, only categorized):
- **OWASP A02 (Cryptographic Failures) / A05 (Security
  Misconfiguration):** Weak default secrets (`SECRET_KEY="changeme"`) as a
  Python fallback in `core/config.py` if `.env` is missing.
- **OWASP A01 (Broken Access Control):** The optional JWT auth mechanism is
  unreachable (router not included, presumably no DB table) – no acute
  risk for the current use case (purely local, no network exposure
  intended), but becomes **critical** if the app is ever exposed beyond
  `localhost` (e.g. reverse proxy, access from the home network) without a
  working auth layer being retrofitted first.

**Positively verified points:**
- No match for raw SQL string interpolation (`text(f"..."`, `.format()` in
  queries) – the SQLAlchemy ORM is used with parameterization throughout,
  no discernible SQL injection risk.
- No `dangerouslySetInnerHTML` anywhere in the frontend – no obvious XSS
  entry point via React rendering.
- No `eval`/`exec`/`os.system`/`subprocess` in the backend – no command
  injection risk found through dynamic code execution.
- CORS (`main.py`) is fixed to `http://localhost:3000`, no wildcard (`*`)
  – correctly restrictive for the self-hosted use case.
- `.env` not tracked in git (see 1.3); third-party API keys are stored
  Fernet-encrypted in the DB (see 1.3).
- DB service with no host port exposure (see 1.4).

**Missing rate limiting:** No rate-limiting library (e.g. `slowapi`) or
custom implementation found in the backend. Currently low risk for a
purely locally run tool, but should be considered at the latest when auth/
network exposure is retrofitted (see above) – particularly for the AI
endpoints (`api/ai.py`), which cost compute time/Ollama resources.

**Dependency risks:** No `dependabot.yml` or comparable automated
dependency monitoring in the repo (`.github/` contains only templates, see
1.1/1.5). Backend and frontend dependencies are pinned exactly (good for
reproducibility), but without automated security scans (`pip-audit`,
`npm audit`, Dependabot/Renovate), CVEs that become known in the pinned
versions go unnoticed. This was not verified here through an actual scan
(no internet access assumed/checked from the audit context) – flagged as a
recommendation for the Engineering phase, not as a confirmed finding of
individual CVEs.

**Privacy/GDPR:** `docs/dsgvo.md` and `docs/PRIVACY.md` already exist and
are substantively solid (data categories, storage location, purpose, legal
basis listed in tables; local-only architecture as the central privacy
promise). Already covers the privacy aspects required by the brief for
sensitive application data well – in Phase 4/5 only the completeness of
the English version needs checking (both files are already set up as
bilingual per their headers; detailed verification of EN completeness
follows in Phase 4 if needed).

### Open Questions from this Section

None – the path traversal finding is unambiguously traceable in the code,
no assumption needed.

### 1.7 Architecture Diagram

Both diagrams depict exclusively components actually found in the code
(`docker-compose.yml`, `main.py` router registration, `services/job_search/`,
`services/{mail,email_parser,company_research}.py`). No planned/invented
components included.

**System/Deployment view:**

```mermaid
flowchart LR
    Browser["Browser (User)"]

    subgraph Docker["Docker Compose (jobhunter-net)"]
        FE["frontend\nVite **dev server** in \"production\"\n:3000"]
        BE["backend\nFastAPI + SQLAlchemy async\n:8000"]
        DB[("db\nPostgreSQL 16-alpine\ninternal only, no host port")]
        OL["ollama\nLocal AI inference\n:11434 (models e.g. mistral)"]
    end

    Ext1["Job board APIs/scrapers\nBundesagentur, Adzuna,\nStepStone, LinkedIn, EURES"]
    Ext2["Wikipedia API\n(company dossier)"]
    Ext3["IMAP server\n(e-mail parsing, user account)"]
    Ext4["SMTP server\n(reminder/template e-mails)"]

    Browser -- "HTTP :3000" --> FE
    FE -- "REST/JSON :8000" --> BE
    BE -- "SQL (asyncpg) :5432 internal" --> DB
    BE -- "HTTP :11434 internal" --> OL
    BE -- "HTTPS" --> Ext1
    BE -- "HTTPS" --> Ext2
    BE -- "IMAP" --> Ext3
    BE -- "SMTP" --> Ext4
```

**Backend module view** (solid = actively used, dashed = dead code per
sections 1.3/1.4):

```mermaid
flowchart TD
    Main["main.py"]
    ApiPkg["api/ (18 modules)"]
    RoutersPkg["routers/ (3 modules:\nblocklist, followups, jobs_image)"]
    Services["services/ (30 modules +\njob_search/ sub-package)"]
    Schemas["schemas/ (3 modules:\napplication, job, settings)"]
    ModelsPkg["models/ (package, 14 registered\nmodels incl. Base from core.database)"]
    Core["core/ (config, database,\nsecurity, crypto)"]
    AlembicActive["backend/alembic/\n(0001-0004, ACTIVE)"]
    DBNode[("PostgreSQL")]

    ModelsOld["backend/models.py\n(DEAD CODE, shadowed by the package)"]
    AlembicOld["/alembic/ (top-level)\n(DEAD CODE, never in Docker build context)"]
    AuthApi["api/auth.py\n(not included in main.py)"]
    CLPdfApi["api/cover_letter_pdf.py\n(not included, feature #89 planned)"]

    Main -->|"app.include_router()\nfor 16 of 18 modules"| ApiPkg
    Main -->|"app.include_router()"| RoutersPkg
    ApiPkg --> Services
    RoutersPkg --> Services
    ApiPkg -.->|"not registered"| AuthApi
    ApiPkg -.->|"not registered"| CLPdfApi
    ApiPkg --> Schemas
    Services --> ModelsPkg
    ModelsPkg --> Core
    Core --> DBNode
    AlembicActive --> DBNode

    ModelsOld -.->|"no longer imported"| ModelsPkg
    AlembicOld -.->|"no build-context reference"| DBNode
```

### Open Questions from this Section

None – the diagrams only summarize findings already verified in 1.1–1.6.

## Phase 1 Summary

Short, sorted overview of the core findings from 1.1–1.7 – details and
rationale in the respective referenced section. Assessment/prioritization
(critical/high/medium/low, effort, recommendation) follows in Phase 2; this
is inventory only.

**Verified broken (through actual command execution, not just reading):**
- Backend test suite: `ImportError` on collection, 0% runnable (1.5).
- Frontend lint: no ESLint configuration exists, command aborts (1.5).
- Frontend production build: no `tsconfig.json` in the whole repo, `tsc`
  runs into nothing (1.5). Goes unnoticed because the "production"
  container actually starts the Vite dev server (1.5).

**Security-relevant (1.6):**
- 🔴 Path traversal risk on CV upload (`api/cv.py`, unchecked client
  filename).
- Weak default secrets as a fallback without `.env` (1.3/1.6).
- No working auth path despite existing JWT code (1.3/1.4/1.6).
- No rate limiting, no automated dependency scanning (1.6).
- Positive: no SQLi/XSS/command-injection patterns found, CORS restrictive,
  `.env` not tracked, API keys encrypted, DB with no host port exposure,
  GDPR/privacy documentation already present (1.6).

**Structure/legacy debt (1.1/1.3/1.4):**
- Two parallel endpoint directories (`api/` vs. `routers/`) with no
  technical reason.
- Dead code: `backend/models.py`, top-level `/alembic/` tree – both
  demonstrably unused, per the project's own comment (migration) and per
  the Docker build context respectively.
- `User` model without registration, without migration, without a
  reachable router – auth looks like an incomplete feature fragment.
- Inconsistent language handling across three different patterns
  (per-file duplicate, single-file DE/EN mix, German-only) in
  `docs/`/`wiki/`/README.

**Internationalization (1.2, central to the brief):**
- i18n infrastructure (i18next/react-i18next) present, but used in only
  **5 of 45** frontend files (~11%).
- Translations inline in a single file instead of a namespace/JSON
  structure, covering only Nav/Dashboard/Jobs/Settings/Common.
- Positive: German is already correctly anchored as default+fallback, no
  browser-locale override.

**Not critical, but maintenance-relevant (1.2/1.3):**
- No central frontend API client (`axios` used directly in 22 files).
- Thin Pydantic schema layer (3 modules) relative to 18+3 API modules.
- Naming collision `pages/CompanyDossier.tsx` /
  `components/CompanyDossier.tsx`.
- `pages/CoverLetter.tsx` without its own route, integration path not
  conclusively verified.

This summary is deliberately still **unassessed** (no prioritization, no
effort estimate) – that is the subject of Chapter 2 ("Quality and
Architecture Assessment"), which follows as its own work step.

---

*Phase 1 complete. Continued with Chapter 2 (Quality/Architecture Assessment) per `docs/analysis/BACKLOG.md`.*
