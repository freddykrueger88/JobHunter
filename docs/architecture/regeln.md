# Architekturregeln / Architecture Rules

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## Deutsch

> Kurzregeln aus Rework-Plan Phase B (`docs/analysis/REWORK_PLAN_DE.md`).
> Gelten ab sofort fuer neuen Code; bestehender Code wird schrittweise
> gemaess Rework-Plan angepasst, nicht per Big Bang.

1. **Neue Backend-Endpunkte gehoeren nach `backend/routers/`, nicht nach
   `backend/api/`.** `api/` wird gemaess ADR-0002 aufgeloest, sobald
   Phase B.2 umgesetzt ist (aktuell zurueckgestellt, da `main.py` beim
   Anlegen dieser Regel Teil laufender, uncommitteter Arbeit war).
2. **Jede neue Response nutzt ein Pydantic-Schema** (`backend/schemas/`),
   keine direkte Ruecklieferung von ORM-Objekten oder Ad-hoc-Dicts fuer
   neue Endpunkte.
3. **Kein neuer direkter `axios`-Call.** Neue Frontend-API-Aufrufe nutzen
   den zentralen Client `frontend/src/lib/api.ts` (`baseURL: "/api"`,
   zentrales Error-Handling). Bestehende direkte `axios`-Aufrufe werden
   schrittweise migriert (Rework-Plan Phase C/D), nicht alle auf einmal.
4. **Backend-Router-Praefixe beginnen immer mit `/api`.** Alle
   Frontend-Aufrufe nutzen durchgaengig `/api/...` (verifiziert in
   REPOSITORY_AUDIT_DE.md 1.2) - ein Router ohne `/api`-Praefix ist vom
   Frontend aus nicht erreichbar (realer Bug, der in Rework-Plan Phase A
   an 12 Routern behoben wurde).
5. **Neue UI-Texte immer in `de/*.json` UND `en/*.json` gleichzeitig**,
   sobald die i18n-Namespace-Struktur aus ADR-0003 (Rework-Plan Phase C)
   steht - niemals nur eine Sprache.
6. **Vor jeder Aenderung an `docker-compose.yml`/den Dockerfiles**: pruefen,
   ob `docker-compose.override.yml` (lokaler Dev-Modus fuer das Frontend,
   siehe Rework-Plan Phase A.4) davon betroffen ist.

---

## English

> Short rules from Rework Plan Phase B (`docs/analysis/REWORK_PLAN_EN.md`).
> Apply to new code from now on; existing code is adapted incrementally
> per the rework plan, not as a big bang.

1. **New backend endpoints belong in `backend/routers/`, not
   `backend/api/`.** `api/` is dissolved per ADR-0002 once Phase B.2 is
   implemented (currently deferred, since `main.py` was part of active,
   uncommitted work when this rule was written).
2. **Every new response uses a Pydantic schema** (`backend/schemas/`), no
   direct return of ORM objects or ad-hoc dicts for new endpoints.
3. **No new direct `axios` call.** New frontend API calls use the central
   client `frontend/src/lib/api.ts` (`baseURL: "/api"`, central error
   handling). Existing direct `axios` calls are migrated incrementally
   (Rework Plan Phase C/D), not all at once.
4. **Backend router prefixes always start with `/api`.** All frontend
   calls consistently use `/api/...` (verified in
   `REPOSITORY_AUDIT_EN.md` 1.2) - a router without an `/api` prefix is
   unreachable from the frontend (a real bug fixed on 12 routers in
   Rework Plan Phase A).
5. **New UI text always goes into `de/*.json` AND `en/*.json`
   simultaneously**, once the i18n namespace structure from ADR-0003
   (Rework Plan Phase C) is in place - never just one language.
6. **Before changing `docker-compose.yml`/the Dockerfiles**: check whether
   `docker-compose.override.yml` (local dev mode for the frontend, see
   Rework Plan Phase A.4) is affected.
