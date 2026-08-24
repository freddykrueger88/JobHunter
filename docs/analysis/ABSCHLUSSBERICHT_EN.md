# Final Report – JobHunter Audit & Rework (Phases 0–E)

As of: 2026-08-24. Summary of the entire audit, rework, and i18n program
per `docs/analysis/BACKLOG.md`. Details and evidence live in the
referenced individual documents – this report summarizes without
duplicating them.

## Current State (before → after)

| Area | Before (Audit, 2026-08-24) | After |
|---|---|---|
| Backend tests | Completely broken (import error in `conftest.py`), effectively 0% coverage | 26/26 passing, incl. 4 new tests for the security fix (path traversal) |
| Frontend tests | No test framework at all | Vitest + Testing Library newly set up, 8/8 passing |
| Lint | Frontend: no ESLint config, command not runnable. Backend: no linter | Frontend: 0 errors (11 fixed), 10 pre-existing warnings documented. Backend: deliberately not introduced (out of scope) |
| Build | No `tsconfig.json`, `npm run build` effectively never worked | Green; bundle size reduced from 470KB to 393KB (main chunk) via code-splitting |
| CI/CD | No `.github/workflows/` | 3-job pipeline (backend/frontend/i18n-check), Dependabot, pre-commit hooks |
| Security | Path traversal on CV upload, weak default secrets | Both fixed + regression test for the upload fix |
| i18n | ~6 of 45 files with visible UI text translated (~13%) | All routed pages + all core components translated (34 namespaces, DE/EN parity CI-checked), backend error codes for 5 domains |
| Product container | Frontend container ran the Vite dev server instead of a build | Multi-stage Dockerfile (nginx production), dev workflow preserved via `docker-compose.override.yml` |

## Decision (Chapter 3, `REWORK_PLAN_EN.md`)

**Targeted repair + modular restructuring. No rebuild.**
Reasoning in short: no part of the stack (FastAPI, SQLAlchemy/Postgres,
React/Vite/TS, i18next, Ollama) justifies a switch; every finding was a
completion or configuration gap, not an architectural flaw. Restructuring
(rather than a plain refactor) was still needed because of the split
endpoint layer (`api/`/`routers/`) and the missing central frontend
structure. Full reasoning incl. rejected alternatives:
`REWORK_PLAN_EN.md` section 3.1.

## Top-10 Findings – Status

From `REPOSITORY_AUDIT_EN.md` section 2.1 (prioritized there by impact):

| # | Finding | Priority | Status |
|---|---|---|---|
| 1 | Backend tests broken (`Base` import) | Critical | ✅ Fixed (Phase A) |
| 2 | No ESLint config | Critical | ✅ Fixed (Phase A), all errors eliminated (Phase E) |
| 3 | No `tsconfig.json` | Critical | ✅ Fixed (Phase A) |
| 4 | Prod container runs dev server | High | ✅ Fixed (Phase A) |
| 5 | Path traversal on CV upload | Critical | ✅ Fixed (Phase A) + regression test (Phase E) |
| 6 | Weak default secrets | High | ✅ Fixed (Phase A, hard fail instead of fallback) |
| 7 | Dead code paths (`models.py`, top-level `alembic/`) | Low | ✅ Fixed (Phase B) |
| 8 | Split endpoint layer `api/`/`routers/` | Medium | ✅ Fixed (2026-08-25, 12 of 16 routers moved, user decision "handle main.py yourself"). Found a critical bug in the process: `jobs.py` had been mounted without the `/api` prefix since the very first commit – job search/listing had been dead on arrival since project inception. Fixed. |
| 9 | `User` model without registration (product decision) | Medium | ✅ Resolved (user decision: removed, Phase B) |
| 10 | No central frontend API client | Medium | ✅ Fixed (Phase B, extended with an error toast in Phase D) |

Further findings from the same table: #13 (no dependency scanning) is
resolved with Dependabot (Phase E); #14 (CompanyDossier naming collision)
resolved (Phase B); #11 (thin schema layer) partially (8 of several
domains, the rest also depends on `main.py`); #12 (no rate limiting) and
#15 (`CoverLetter.tsx` without a route) were deliberately not addressed –
both were rated low priority in the audit and were not part of the
rework plan.

## i18n Status

- 34 i18next namespaces (auto-loaded via `import.meta.glob`), DE as
  default/fallback, EN maintained equally.
- All routed pages and all reused components are translated, including
  two gaps found later: `Dashboard.tsx` (a real display bug was fixed
  along the way, see `BACKLOG.md` Phase E) and `Settings.tsx`.
- CI check (`npm run i18n:check`) enforces DE/EN key parity on every PR.
- Backend error codes via the `X-Error-Code` header for 5 domains
  (cv, reminders, export, company_dossier, interview) – the frontend
  translates them automatically, with a plain-text fallback for
  endpoints not yet migrated.
- Known gap: `pages/Onboarding.tsx` is documented as a "shipped" feature
  in `CHANGELOG.md` (v1.3, #50), but git history shows it was never
  wired into `App.tsx`/`main.tsx` – unreachable for any user since v1.3.
  Deleting it (no functional loss, since it never worked) vs. wiring it
  up (a real product decision about trigger logic) is pending with the
  user, so it was not audited further.

## Wiki Status

**Not implemented.** `gh` CLI is installed in the LXC but without GitHub
auth (no token stored). Unifying `docs/wiki/` was deliberately merged
with the actual wiki publication step (`BACKLOG.md` C.7) to avoid
duplicate work. Prerequisite for the next step: a GitHub Personal Access
Token from the user.

## Validation

Consistent principle across all phases: **no commit without real
evidence.** Concretely, for every batch:
- `npm run build` / `npm run lint` / `npm run test` / `npm run i18n:check`
  inside the running `jobhunter-frontend` container
- `pytest tests/ -v` inside the running `jobhunter-backend` container
- Real HTTP requests (`httpx`/`curl`) against live endpoints instead of
  assumed behavior – this is how the SQLite-specific bug in the
  dashboard "soon" bucket (Phase E) and the `dashboard.${tKey}`
  translation bug (Phase E) were found.
- Manual browser confirmation after the biggest incident during this
  work: a Vite dependency cache corrupted by concurrent `npm install`
  runs, which made the app appear blank in the browser – fixed via a
  container restart, confirmed by the user.

Overall result: Backend 26/26, Frontend 8/8, build/lint/i18n-check
consistently green (as of the last run, see commit history).

## Open Risks

1. **Remaining schema modules (B.6)** – `applications.py` still depends
   on `backend/models/application.py`, a file the user is actively
   editing; no third-party changes without coordination.
   `cover_letter_pdf.py`/`search_profiles.py` remain deliberately
   unregistered (README marks them as unfinished/planned).
2. **GitHub Wiki (Phase 5)** – needs a Personal Access Token from the
   user, then `gh auth login` + content migration.
3. **`pages/Onboarding.tsx`** – shipped per changelog, but never wired
   up; delete-or-rewire decision pending.
4. ~~Version drift~~ – **fixed** (2026-08-25): `frontend/package.json`
   synced to `1.9.0`.
5. **Accessibility audit (D.3)** – explicitly outside this program per
   the rework plan, recommended as a dedicated follow-up.
6. **No rate limiting** – audit finding #12, low priority, not addressed
   (only relevant once real network exposure goes beyond the
   self-hosted setup).

---

*Full history: `git log` in the repository, every phase as a series of
small, individually verified commits. Ongoing control file:
`docs/analysis/BACKLOG.md`.*
