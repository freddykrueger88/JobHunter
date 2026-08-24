# Abschlussbericht – JobHunter Audit & Rework (Phasen 0–E)

Stand: 2026-08-24. Zusammenfassung des gesamten Audit-, Rework- und
i18n-Programms gemäß `docs/analysis/BACKLOG.md`. Details und Belege stehen
in den referenzierten Einzeldokumenten – dieser Bericht fasst zusammen,
dupliziert aber nicht.

## Ist-Zustand (vorher → nachher)

| Bereich | Vorher (Audit, 2026-08-24) | Nachher |
|---|---|---|
| Backend-Tests | Komplett kaputt (Import-Fehler in `conftest.py`), effektiv 0% Abdeckung | 26/26 grün, inkl. 4 neuen Tests für den Security-Fix (Path Traversal) |
| Frontend-Tests | Kein Test-Framework vorhanden | Vitest + Testing Library neu eingerichtet, 8/8 grün |
| Lint | Frontend: keine ESLint-Config, Befehl nicht ausführbar. Backend: kein Linter | Frontend: 0 Errors (11 behoben), 10 Alt-Warnings dokumentiert. Backend: bewusst nicht eingeführt (kein Auftrag dafür) |
| Build | Keine `tsconfig.json`, `npm run build` faktisch nie lauffähig | Grün, Bundle-Größe durch Code-Splitting von 470KB auf 393KB (Hauptchunk) reduziert |
| CI/CD | Kein `.github/workflows/` | 3-Job-Pipeline (Backend/Frontend/i18n-Check), Dependabot, Pre-Commit-Hooks |
| Sicherheit | Path Traversal beim CV-Upload, schwache Default-Secrets | Beide behoben + Regressionstest für den Upload-Fix |
| i18n | ~6 von 45 Dateien mit sichtbarem UI-Text übersetzt (~13%) | Alle gerouteten Seiten + alle Kernkomponenten übersetzt (34 Namespaces, DE/EN-Parität CI-geprüft), Backend-Fehlercodes für 5 Domänen |
| Produkt-Container | Frontend-Container startete Vite-Dev-Server statt Build | Mehrstufiges Dockerfile (nginx-Produktion), Dev-Workflow über `docker-compose.override.yml` erhalten |

## Entscheidung (Kapitel 3, `REWORK_PLAN_DE.md`)

**Gezielte Reparatur + modulare Restrukturierung. Kein Neuaufbau.**
Begründung in Kürze: kein Stack-Element (FastAPI, SQLAlchemy/Postgres,
React/Vite/TS, i18next, Ollama) rechtfertigt einen Wechsel; alle Befunde
waren Fertigstellungs-/Konfigurationslücken, keine Architekturfehler. Eine
Restrukturierung (statt reinem Refactor) war trotzdem nötig wegen der
gespaltenen Endpunkt-Schicht (`api/`/`routers/`) und der fehlenden
zentralen Frontend-Struktur. Vollständige Begründung inkl. verworfener
Alternativen: `REWORK_PLAN_DE.md` Abschnitt 3.1.

## Top-10-Befunde – Status

Aus `REPOSITORY_AUDIT_DE.md` Abschnitt 2.1 (dort priorisiert nach Impact):

| # | Befund | Priorität | Status |
|---|---|---|---|
| 1 | Backend-Tests kaputt (`Base`-Import) | Kritisch | ✅ Behoben (Phase A) |
| 2 | Kein ESLint-Config | Kritisch | ✅ Behoben (Phase A), alle Errors beseitigt (Phase E) |
| 3 | Keine `tsconfig.json` | Kritisch | ✅ Behoben (Phase A) |
| 4 | Prod-Container startet Dev-Server | Hoch | ✅ Behoben (Phase A) |
| 5 | Path Traversal beim CV-Upload | Kritisch | ✅ Behoben (Phase A) + Regressionstest (Phase E) |
| 6 | Schwache Default-Secrets | Hoch | ✅ Behoben (Phase A, hartes Fail statt Fallback) |
| 7 | Tote Code-Pfade (`models.py`, Top-Level-`alembic/`) | Niedrig | ✅ Behoben (Phase B) |
| 8 | Gespaltene Endpunkt-Schicht `api/`/`routers/` | Mittel | ⏸️ Zurückgestellt – hängt an `main.py`, das der Nutzer selbst fertigstellt |
| 9 | `User`-Modell ohne Registrierung (Produktentscheidung) | Mittel | ✅ Gelöst (Nutzerentscheidung: entfernt, Phase B) |
| 10 | Kein zentraler Frontend-API-Client | Mittel | ✅ Behoben (Phase B, erweitert um Error-Toast in Phase D) |

Weitere Befunde aus derselben Tabelle: #13 (kein Dependency-Scanning) ist
mit Dependabot (Phase E) gelöst; #14 (Namenskollision CompanyDossier)
gelöst (Phase B); #11 (dünne Schema-Schicht) teilweise (8 von mehreren
Domänen, Rest hängt ebenfalls an `main.py`); #12 (kein Rate-Limiting) und
#15 (`CoverLetter.tsx` ohne Route) bewusst nicht angegangen – beide waren
im Audit als niedrige Priorität eingestuft und nicht Teil des
Rework-Plans.

## i18n-Status

- 34 i18next-Namespaces (automatisch geladen über `import.meta.glob`),
  DE als Default/Fallback, EN gleichwertig gepflegt.
- Alle gerouteten Seiten und alle wiederverwendeten Komponenten
  übersetzt, inkl. der zwei nachträglich gefundenen Lücken
  `Dashboard.tsx` (dabei ein echter Anzeige-Bug behoben, siehe
  `BACKLOG.md` Phase E) und `Settings.tsx`.
- CI-Check (`npm run i18n:check`) erzwingt Schlüssel-Parität DE/EN bei
  jedem PR.
- Backend-Fehlercodes über `X-Error-Code`-Header für 5 Domänen
  (cv, reminders, export, company_dossier, interview) – Frontend
  übersetzt sie automatisch, mit Klartext-Fallback für noch nicht
  migrierte Endpunkte.
- Bekannte Lücke: `pages/Onboarding.tsx` ist toter, ungerouteter Code und
  wurde nicht auditiert (Löschen/Behalten-Entscheidung steht beim
  Nutzer aus).

## Wiki-Status

**Nicht umgesetzt.** `gh` CLI ist im LXC installiert, aber ohne
GitHub-Auth (kein Token hinterlegt). `docs/wiki/`-Vereinheitlichung wurde
bewusst mit der eigentlichen Wiki-Veröffentlichung zusammengelegt
(`BACKLOG.md` C.7), um Doppelarbeit zu vermeiden. Voraussetzung für den
nächsten Schritt: ein GitHub Personal Access Token vom Nutzer.

## Validierung

Durchgängiges Prinzip über alle Phasen: **kein Commit ohne echten
Nachweis.** Konkret bei jedem Batch:
- `npm run build` / `npm run lint` / `npm run test` / `npm run i18n:check`
  im laufenden `jobhunter-frontend`-Container
- `pytest tests/ -v` im laufenden `jobhunter-backend`-Container
- Echte HTTP-Requests (`httpx`/`curl`) gegen laufende Endpunkte statt
  angenommenem Verhalten – u. a. wie der SQLite-spezifische Bug im
  Dashboard-"soon"-Bucket (Phase E) und der `dashboard.${tKey}`-
  Übersetzungsfehler (Phase E) dabei entdeckt wurden.
- Manuelle Browser-Bestätigung nach dem größten Vorfall der laufenden
  Arbeit: ein durch parallele `npm install`-Läufe korrumpierter
  Vite-Dependency-Cache, der die App im Browser leer erscheinen ließ –
  durch Container-Neustart behoben, vom Nutzer bestätigt.

Gesamtergebnis: Backend 26/26, Frontend 8/8, Build/Lint/i18n-Check
durchgängig grün (Stand des letzten Laufs, siehe Commit-Historie).

## Offene Risiken

1. **`main.py`-Konsolidierung (B.2)** – blockiert mehrere Folgepunkte
   (Endpunkt-Vereinheitlichung, restliche Schema-Module,
   `cover_letter_pdf.py`/`search_profiles.py`-Einbindung). Der Nutzer
   arbeitet an dieser Datei selbst; keine Fremdänderung ohne Rücksprache.
2. **GitHub-Wiki (Phase 5)** – benötigt ein Personal Access Token vom
   Nutzer, dann `gh auth login` + Inhalte übertragen.
3. **`pages/Onboarding.tsx`** – toter Code, Entscheidung steht aus.
4. **Versions-Drift** – `frontend/package.json` (0.4.0) vs.
   README-Badge (v1.9.0), dokumentiert in `CONTRIBUTING.md` Abschnitt 8,
   nicht rückwirkend korrigiert.
5. **Accessibility-Audit (D.3)** – laut Rework-Plan explizit außerhalb
   dieses Programms, als eigener Folge-Auftrag empfohlen.
6. **Kein Rate-Limiting** – Audit-Befund #12, niedrige Priorität, nicht
   angegangen (relevant erst bei echter Netzwerk-Exposure über das
   Self-Hosted-Setup hinaus).

---

*Vollständige Historie: `git log` im Repository, jede Phase als Serie
kleiner, einzeln verifizierter Commits. Laufende Steuerungsdatei:
`docs/analysis/BACKLOG.md`.*
