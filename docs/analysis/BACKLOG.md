# JobHunter Rework-Backlog

Dieses Dokument ist die zentrale Steuerungsdatei für das Audit-, Rework- und i18n-Programm.
Vor jedem weiteren Arbeitsschritt wird zuerst hier nachgesehen, welche Punkte offen sind.
Ausschließlich neue Analyse-/Doku-Dateien werden hier vorbereitet – bestehender App-Code
wird erst ab Phase 4 angefasst, nach Freigabe durch den Nutzer (Checkpoint nach Phase 3).

Der vollständige Auftrag stammt aus der Nutzeranfrage vom 2026-08-24 (Rolle: Senior
Full-Stack-Architekt/Audit von github.com/freddykrueger88/JobHunter). Der ausführliche
Plan liegt unter `/root/.claude/plans/shiny-stargazing-matsumoto.md` auf dem Proxmox-Host
(LXC 142 = "JobHunter"-Container).

Status-Legende: `[ ]` offen · `[~]` in Arbeit · `[x]` erledigt · `[!]` blockiert (siehe Notiz)

## Wichtige Leitplanken (nicht wiederholt in jedem Item)

- Laufende uncommittete Änderungen des Nutzers (Stand 2026-08-24: `backend/alembic/env.py`,
  `backend/api/calendar.py`, `backend/entrypoint.sh`, `backend/main.py`,
  `backend/models/__init__.py`, `backend/models/application.py`,
  `backend/routers/blocklist.py`, `backend/routers/followups.py`,
  `backend/routers/jobs_image.py`, `docker-compose.yml` sowie neue Dateien
  `backend/alembic/versions/0004_add_blocklist_badges_backup_templates.py`,
  `backend/models/{backup_log,blocklist,cover_letter_template,followup,user_badge}.py`)
  werden **nicht angefasst und nicht mitcommittet**. Immer gezielt einzelne Dateien stagen.
- Kein `git push` nach `origin`, keine GitHub-Wiki-Veröffentlichung ohne erneute
  ausdrückliche Bestätigung des Nutzers.
- Jedes erledigte Item = ein eigener, thematisch sauberer lokaler Commit.
- Befunde nur auf Basis tatsächlich gelesenen Codes; Annahmen/offene Fragen explizit markieren.

## Phase 0 – Vorbereitung
- [x] 0.1 gh CLI installieren (`apt-get install gh`) im LXC 142 — erledigt 2026-08-24 (v2.4.0)
- [x] 0.2 GitHub-Auth geklärt (2026-08-24, nachträglich): `gh` ist auf dem
      Proxmox-Host (nicht in LXC 142) als freddykrueger88 authentifiziert
      (Token-Scope `repo`, u.a.). Wiki-Operationen (Phase 5) erfolgen darüber,
      z. B. Klonen von `JobHunter.wiki.git` in ein Host-Scratchpad-Verzeichnis.
- [x] 0.3 BACKLOG.md angelegt — erledigt 2026-08-24

## Phase 1 – Repository-Inventur (Audit)
- [x] 1.1 Projektstruktur & Modulgrenzen dokumentieren
- [x] 1.2 Frontend-Bestandsaufnahme (Komponenten, Routing, State, i18n-Abdeckung gezaehlt)
- [x] 1.3 Backend-Bestandsaufnahme (Router, Models, Services, Auth/Secrets)
- [x] 1.4 Datenbank/Migrationen (Alembic-Historie, Schema)
- [x] 1.5 Tests/CI/Linting/Build-Bestandsaufnahme (verifiziert per echter Befehlsausfuehrung)
- [x] 1.6 Security/OWASP/Datenschutz-Sichtung
- [x] 1.7 Architekturdiagramm (Mermaid) auf Basis realer Struktur
- [x] 1.8 docs/analysis/REPOSITORY_AUDIT_DE.md fertiggestellt (Phase 1)
- [x] 1.9 docs/analysis/REPOSITORY_AUDIT_EN.md geschrieben (inhaltsgleich)

## Phase 2 – Qualitäts-/Architekturbewertung
- [x] 2.1 Codequalitaet bewertet (Befund/Prioritaet/Empfehlung/Aufwand/Risiko je Punkt)
- [x] 2.2 Stack-Eignung fuers Job-Tool bewertet (Ist vs. Ziel)
- [x] 2.3 Ergebnisse in REPOSITORY_AUDIT_{DE,EN}.md eingearbeitet (Kapitel 2 komplett, beide Sprachen)

## Phase 3 – Rework-Entscheidung & Roadmap
- [x] 3.1 Entscheidung abgeleitet (gezielte Reparatur + modulare Restrukturierung)
- [x] 3.2 docs/analysis/REWORK_PLAN_DE.md geschrieben (5 Phasen)
- [x] 3.3 docs/analysis/REWORK_PLAN_EN.md geschrieben (inhaltsgleich)
- [x] 3.4 docs/architecture/ (Diagramme + 3 ADRs) angelegt
- [x] >>> CHECKPOINT: Nutzer hat am 2026-08-24 explizit angewiesen, Phase 2+3 komplett durchzuarbeiten, ohne zwischendurch zu pruefen. Review von Audit+Rework-Plan steht inhaltlich aber noch aus, bevor Phase 4 (Code-Aenderungen) beginnt. <<<

## Phase 4 – Internationalisierung (Umsetzung)
- [ ] 4.1 docs/i18n/KONZEPT.md (Locale-Strategie, Schlüsselschema, Persistenz, Fallbacks)
- [ ] 4.2 i18n-Grundgerüst ausbauen (Namespaces statt einer Monolith-Datei)
- [ ] 4.3 Hardcodierte Strings modulweise migrieren (kleine Batches je Seite/Feature —
      konkrete Unterpunkte werden ergänzt, sobald 1.2 die vollständige Dateiliste liefert)
- [ ] 4.4 Backend: Fehlertexte/Validierungen/E-Mail-Templates i18n-fähig machen
- [ ] 4.5 CI-Check: fehlende/ungenutzte Übersetzungsschlüssel (Script + ggf. GH Action)
- [ ] 4.6 Tests für DE-Standard + EN-Alternative

## Phase 5 – Wiki (zweisprachig)
- [ ] 5.1 docs/wiki/ als Quelle/Fallback aufbauen (13 Themen × DE/EN)
- [ ] 5.2 Falls gh-Auth steht: echtes GitHub-Wiki klonen & Inhalte übertragen
- [ ] 5.3 README.md / README.de.md aktualisieren (Status, Wiki-Links, Quick Start)

## Abschlussbericht
- [x] Zusammenfassung nach Vorgabe (Ist-Zustand, Entscheidung, Top-10, i18n-Status,
      Wiki-Status, Validierung, offene Risiken) — erledigt 2026-08-24 als
      docs/analysis/ABSCHLUSSBERICHT_{DE,EN}.md, nach Abschluss der Phasen 0-E

## Änderungsprotokoll
- 2026-08-24: Backlog angelegt, gh installiert, Auth als blockiert markiert.
- 2026-08-24: Phase D (Produktqualitaet) umgesetzt - einheitliche Fehleranzeige,
  Code-Splitting, dsgvo.md-Sachfehler korrigiert. Naechster Schritt: Phase E.
- 2026-08-24 (Fortsetzung): Phase E (Engineering) umgesetzt - CI-Workflow,
  Testpyramide (26 Backend-/8 Frontend-Tests), Dependabot, Pre-Commit,
  Release-Prozess dokumentiert. Dabei 2 echte Bugs gefunden+gefixt
  (Dashboard-Counter-Labels, Dashboard-Stats "soon"-Bucket). Rework-Plan
  Phasen A-E damit vollstaendig durchlaufen.

- 2026-08-24 (Fortsetzung): Phase 1 (Audit DE+EN), Phase 2 (Codequalitaet + Stack-Eignung DE+EN)
  und Phase 3 (Rework-Entscheidung, REWORK_PLAN_DE/EN.md, docs/architecture/ mit 3 ADRs) auf
  ausdruecklichen Nutzerwunsch komplett und ohne Zwischen-Nachfragen abgearbeitet. Naechster
  Schritt: inhaltliches Review durch den Nutzer, danach Start Phase 4 (i18n-Umsetzung) gemaess
  REWORK_PLAN_DE.md Phase A-E. Laufende uncommittete Arbeitsdateien des Nutzers weiterhin
  unveraendert (verifiziert: git status zeigt dieselben 10 Dateien wie bei Sessionbeginn).

## Phase A - Umsetzung (2026-08-24, waehrend Nutzer abwesend, auf expliziten Wunsch)
- [x] A.1 conftest.py Base-Import gefixt (0 -> 15 gruene Tests, 7 separate Bugs sichtbar geworden)
- [x] A.2 ESLint-Config ergaenzt (.eslintrc.cjs) - 26 echte Lint-Findings jetzt sichtbar
- [x] A.3 tsconfig.json ergaenzt - deckte 2 echte Bugs auf (fehlende recharts/date-fns
      Dependencies, totes focusMode-Prop, JSX-Syntaxfehler in CoverLetter.tsx) - alle gefixt,
      npm run build laeuft jetzt komplett durch
- [x] A.5 Path-Traversal-Luecke in api/cv.py geschlossen (os.path.basename), per echtem
      Angriffsversuch verifiziert
- [x] A.6 Harte Secret-Validierung in core/config.py (kein "changeme"-Fallback mehr),
      positiv+negativ verifiziert
- [x] NEU ENTDECKT waehrend Verifikation: 14 von 21 Backend-Routern hatten kein /api-Praefix,
      obwohl ALLE Frontend-Calls durchgaengig /api/... nutzen -> Grossteil der App war ueber
      den Browser/Dev-Proxy nicht erreichbar (404). 12 Router gefixt und verifiziert.
      - api/company.py vs api/company_dossier.py: GELOEST (2026-08-24, Nutzerentscheidung,
        s. Entscheidungsblock unten) - company_dossier.py behalten, company.py entfernt.
      - api/jobs.py vs routers/jobs_image.py: weiterhin offen, main.py-abhaengig (s. B.2).
      - api/search_profiles.py: Praefix gefixt, aber Router weiterhin nicht in main.py
        eingebunden (separater Bug) - SearchProfiles-Seite im Frontend weiterhin tot,
        haengt an B.2 (main.py-Konsolidierung).
- [x] A.4 Frontend-Dockerfile auf Mehrstufen-Build umgestellt (nginx statt Dev-Server), verifiziert per isoliertem docker build+run, Dev-Workflow via docker-compose.override.yml erhalten
- [ ] A.7 Punktuelle docs/*.md Korrekturen - zurueckgestellt (niedrige Prioritaet, kein Blocker)

Phase A Status: 6 von 7 Aufgaben erledigt und einzeln verifiziert (A.7 zurueckgestellt,
niedrige Prioritaet).

## Phase B - Umsetzung (2026-08-24, Fortsetzung)
- [x] B.1 Toten Code entfernt (backend/models.py, Top-Level-/alembic/), verifiziert
      per pytest + alembic current
- [!] B.2 Endpunkt-Schicht vereinheitlichen (api/ -> routers/) - ZURUECKGESTELLT:
      betrifft main.py, das Nutzer-eigene, uncommittete Arbeit enthaelt. Nicht ohne
      Ruecksprache angefasst.
- [x] B.3 Produktentscheidung User/Auth: ENTFERNEN (Nutzerentscheidung 2026-08-24).
      backend/models/user.py, backend/api/auth.py, backend/core/security.py komplett
      geloescht (nur von auth.py importiert - keine Teilausduennung noetig).
      python-jose/passlib aus requirements.txt entfernt. AUTH_ENABLED-Erwaehnungen aus
      laufend gepflegter Doku entfernt (README×2, SECURITY.md, docs/architecture.md,
      wiki/Installation.md, wiki/Konfiguration.md) - CHANGELOG.md/wiki/Changelog.md
      bewusst unangetastet (historische Aufzeichnung). Verifiziert: Backend startet
      sauber, Health-Check OK, pytest unveraendert 15/22.
      Nebenbefund: SECRET_KEY in core/config.py wird jetzt von keinem Code mehr
      gelesen (war nur fuer JWT). Bewusst nicht entfernt (schadet nicht).
- [x] B.4 Zentraler Frontend-API-Client frontend/src/lib/api.ts eingefuehrt,
      Dashboard.tsx als erste Datei migriert (Proof of Concept), verifiziert per
      npm run build + echtem HTTP-Request
- [x] B.5 Namenskollision CompanyDossier aufgeloest (pages/CompanyDossier.tsx ->
      CompanyDossierPage.tsx). components/CompanyDossier.tsx (totes, unverdrahtetes
      Fragment) am 2026-08-24 per Nutzerentscheidung geloescht (statt behalten/einbauen),
      verifiziert per npm run build.
- [x] Company-Dossier-Konsolidierung (2026-08-24, Nutzerentscheidung, main.py-Aenderung):
      company_dossier.py behalten (hatte bereits /api-Praefix), Job-ID-Variante
      (GET /dossier/{job_id}) aus company.py dorthin uebernommen, company.py geloescht.
      main.py chirurgisch angepasst (nur company-Importzeile + include_router-Zeile
      entfernt, sonst unveraendert - main.py enthaelt weiterhin Nutzer-eigene
      uncommittete Aenderungen an anderer Stelle). Verifiziert: beide Varianten
      funktionieren unter /api/company/dossier[...], pytest unveraendert.
- [x] B.6 Backend-Schema-Schicht ausbauen - 8 Domaenen erledigt, jede einzeln per
      echtem HTTP-Request gegen die laufende API verifiziert:
      - backend/schemas/cv.py (CVUploadResponse/CVListItem/CVDetail) -> api/cv.py
      - backend/schemas/history.py (HistoryEntryRead) -> api/history.py
      - backend/schemas/dashboard.py (DashboardStats/DueReminder) -> api/dashboard.py
      - backend/schemas/eures.py (EuresSearchResult/EuresJob, deckt Erfolgs- UND
        Fehlerfall des Scrapers ab) -> api/eures.py
      - backend/schemas/company.py (CompanyDossier) -> api/company.py UND
        api/company_dossier.py (beide liefern nachweislich identisches Format -
        bestaetigt die bereits dokumentierte Ueberschneidung)
      - backend/schemas/export.py (ImportStats/ImportResult) -> POST /api/export/import
        (die drei GET-Export-Endpunkte liefern StreamingResponse/Datei-Downloads,
        dort greift response_model nicht). Nebenbefund: import_data() verarbeitet
        "applications" aus dem JSON gar nicht (nur jobs/reminders/history) - separater
        Bug, nicht gefixt (waere Verhaltensaenderung, kein reiner Schema-Fix).
      - backend/schemas/interview.py (InterviewQuestionsResponse/AnswerEvaluationResponse)
        -> api/interview.py. Nutzerentscheidung KI-Schema-Strenge: STRIKT MIT FALLBACK.
        services/interview_simulator.py validiert die von der KI geparste JSON-Antwort
        jetzt gegen die erwartete Form, bevor sie zurueckgegeben wird - bei Abweichung
        greift der vorhandene Text-Fallback statt eines falsch geformten Objekts.
        Verifiziert per echtem End-to-End-Test (Job anlegen -> Fragen generieren);
        sogar im echten Ollama-Fehlerfall kam eine schema-konforme 200-Antwort zurueck.
      - backend/schemas/ai.py (ModelsResponse/ChatResponse/CoverLetterResponse) ->
        api/ai.py. Diese Endpunkte geben einfache Strings/Listen zurueck (kein
        json.loads() auf LLM-Freitext) - ohne zusaetzliche Fallback-Logik sicher
        schembar. Verifiziert per echtem Request inkl. echter Ollama-Antwort.
      reminders.py und jobs.py hatten bereits gute Inline-Schemas (kein Handlungsbedarf).

      BEWUSST NICHT angefasst, mit Grund:
      - applications.py: haengt an models/application.py, Nutzer-eigene uncommittete
        Datei - nicht ohne Ruecksprache aendern.
      - cover_letter_pdf.py, search_profiles.py: beide weiterhin nicht in main.py
        eingebunden (haengt an B.2) - nicht per echtem HTTP-Request verifizierbar.
- [x] B.7 Architekturregeln dokumentiert (docs/architecture/regeln.md)

Phase B Status: 6 von 7 abgeschlossen (B.3 GELOEST: Auth entfernt; B.6 fuer alle
erreichbaren Domaenen abgeschlossen). Nur B.2 (main.py-Konsolidierung api/->routers/)
bleibt zurueckgestellt - main.py enthaelt weiterhin Nutzer-eigene, uncommittete Arbeit;
davon haengen auch cover_letter_pdf.py/search_profiles.py-Registrierung und die
jobs.py/jobs_image.py-Pfadkollision ab.

Naechster Schritt (Nutzerentscheidung 2026-08-24: "nach dem Plan weiter"): Phase C
(Internationalisierung) gemaess REWORK_PLAN_DE.md. B.2 bleibt als offener Punkt
stehen, bis main.py fertig/committet ist.

## Phase C - Internationalisierung (2026-08-24, Umsetzung)
- [x] C.1 docs/i18n/KONZEPT.md geschrieben (Namespace-Struktur, Schluesselkonvention,
      Persistenz, Datumsformatierung, Backend-Fehlertexte-Zielbild, CI-Check-Plan)
- [x] C.2 i18n.ts auf automatisches Namespace-Laden umgestellt (import.meta.glob
      statt manueller Imports - verhindert Pflegefehler bei jeder neuen Batch-Datei).
      5 bereits uebersetzte Bereiche (nav/dashboard/jobs/settings/common) migriert.
- [x] C.3 ALLE 38 Frontend-Dateien mit sichtbarem UI-Text uebersetzt (DE+EN), jede
      einzeln per npm run build + ESLint verifiziert:
      Batch 1: Kanban, CoverLetter
      Batch 2: Reminders, History, SearchProfiles
      Batch 3: InterviewSimulator, CompanyDossierPage
      Batch 4: DeadlineBadge, GhostJobBadge, BadgesPanel, CalendarExportButton,
        WeeklyGoalWidget, UndoToast, PwaInstallBanner, ShortcutOverlay,
        ConfirmDialog, StatsChart, QualityScoreCard, AtsScorePanel,
        AutoApplyButton, SalaryNegotiationModal, ExportImportPanel,
        ImageJobUpload, EmailParsingSetup, JobSearchDropdown,
        MarketAnalyzerPanel, CoachChatDrawer, FollowUpWidget
      SakuraPetals.tsx brauchte kein i18n (rein dekorativ, aria-hidden, kein Text).

      Nebenbei gefundene und behobene Bugs waehrend der Migration:
      - lib/formatDate.ts (formatDate/formatDateTime/formatNumber/formatCurrencyEur)
        neu eingefuehrt - ersetzt hartcodierte de-DE-Locale in Kanban, Reminders,
        History, SearchProfiles, DeadlineBadge, SalaryNegotiationModal.
      - KRITISCH: ExportImportPanel.tsx rief /export/... statt /api/export/...
        auf (fehlendes Praefix aus Phase A hier uebersehen) - Nutzer haetten eine
        kaputte "Export"-Datei heruntergeladen (Content-Type text/html statt json/
        Datei). Gefixt und verifiziert.
      - Mehrere neu durch t()-Nutzung entstandene Findings sofort behoben
        (useCallback-deps in ImageJobUpload, Variablen-Shadowing von t() in
        SalaryNegotiationModal/TopNav-Batches).
      - Mehrere VORBESTEHENDE Lint-Findings nebenbei mitgeloest (unused clsx-Import
        BadgesPanel, unescaped-entities InterviewSimulator).

      Ergebnis: npm run lint gesamt zeigt 22 Findings (11 Fehler, 11 Warnungen) -
      WENIGER als die urspruenglichen 26 aus Phase A, keine neuen Regressionen.
- [x] C.4 Backend-Fehlercodes: backend/core/errors.py (api_error()-Helfer, sendet
      Fehlercode ueber X-Error-Code-Header statt detail von String auf Objekt
      umzustellen - keine Breaking Changes, main.py nicht angefasst). 5 repraesentative
      Endpunkte umgestellt (cv, reminders, export, company_dossier, interview -
      bewusst ausserhalb main.py/applications.py/calendar.py). Frontend:
      lib/api.ts::getApiErrorMessage() uebersetzt per Code, faellt sonst auf
      deutschen Klartext zurueck. Verifiziert per echtem curl gegen alle 5 Codes
      + Build/Lint/i18n-Check.
- [x] C.5 Locale-Umschaltung: bereits vorhanden, verifiziert (Settings.tsx,
      sichtbare Flaggen-Buttons 🇩🇪/🇬🇧, i18n.changeLanguage + localStorage).
- [x] C.6 CI-Schluessel-Check: frontend/scripts/check-i18n.js (npm run i18n:check) -
      prueft Namespace-Existenz + verschachtelte Schluessel-Paritaet de/en +
      Best-Effort-Warnung fuer unreferenzierte Namespaces. Aktueller Stand: 33
      Namespaces, volle Paritaet.
- [~] C.7 docs/, wiki/, README auf einheitliches Zweisprachigkeits-Schema bringen -
      BEWUSST NICHT hier separat umgesetzt: ueberschneidet sich vollstaendig mit
      Phase 5 (echtes GitHub-Wiki), die exakt dasselbe zweisprachige Schema fuer
      wiki/ zum Ziel hat (13 Themenseiten x DE/EN). Doppelte Bearbeitung waere
      Verschwendung. C.7 wird als Teilaufgabe in Phase 5 erledigt, wenn diese
      angegangen wird. docs/-Ordner (architecture.md, CHANGELOG.md mit Ein-Datei-
      DE/EN-Mix) bleibt vorerst wie er ist - kein Blocker fuer den Release.

Phase C Status: ABGESCHLOSSEN (C.1-C.6 erledigt, C.7 bewusst nach Phase 5
verschoben statt doppelt gemacht).

## Phase D - Produktqualitaet (2026-08-24, Umsetzung)
- [x] D.1 Einheitliche Fehleranzeige: lib/errorToast.ts (window-CustomEvent-Kanal)
      + components/ErrorToastContainer.tsx (Toast im UndoToast-Stil, Auto-Dismiss
      6s, in App.tsx eingehaengt) + lib/api.ts-Interceptor nutzt jetzt
      getApiErrorMessage() statt nur console.error. Neuer Namespace
      errorToastContainer (DE/EN). Verifiziert: Build/Lint/i18n-Check + echter
      Request gegen GET /api/cv/999999 liefert x-error-code: cv.not_found,
      der Interceptor uebersetzt und zeigt ihn an.
- [x] D.2 Ladezustaende: Spot-Check aller 9 gerouteten Seiten - 8/9 haben bereits
      isLoading/Loader2-Muster (grossteils waehrend Phase-C-Batches miterledigt,
      wie im Rework-Plan D.2 vorgesehen). Einzige Ausnahme: pages/Onboarding.tsx
      hat keinerlei Ladezustand UND ist nirgends in App.tsx/anderswo referenziert
      bzw. geroutet (toter Code, bisher nicht entdeckt) - deshalb bewusst NICHT
      angefasst/geloescht in diesem Schritt: anders als das kleine tote Fragment
      aus B.5 ist das eine vollstaendige, potenziell unfertige Onboarding-Seite;
      Loeschen ohne Rueckfrage waere eine Annahme ueber Nutzerabsicht. Als offener
      Punkt vermerkt, nicht stillschweigend geloest.
- [!] D.3 Accessibility: laut Rework-Plan explizit NICHT Teil dieses Plans
      (eigener dedizierter Accessibility-Audit-Pass empfohlen). Bleibt offen,
      bewusst nicht in diesem Release-Zyklus behandelt.
- [x] D.4 Performance/Bundle-Groesse: vite build zeigte vor der Aenderung einen
      einzigen 470.78KB/143.97KB-gzip-Hauptchunk. Alle Routen ausser Dashboard
      (bleibt eager wg. Suspense-Flackern) per React.lazy() umgestellt -
      einheitlich fuer alle 8 Nicht-Startseiten statt nur der zwei im Plan
      genannten Beispiele (InterviewSimulator/CompanyDossierPage sind darunter).
      Ergebnis: Hauptchunk 393.23KB/126.90KB gzip (-17%/-12%), Rest als
      eigene 3-24KB-Chunks. RouteFallback-Spinner nutzt vorhandenen
      common:loading-Key. Verifiziert: Build/Lint/i18n-Check.
- [x] D.5 Datenschutz-Dokumente geprueft: docs/dsgvo.md UND docs/PRIVACY.md sind
      beide bereits vollstaendig zweisprachig (Ein-Datei-Schema mit Sprunganker,
      strukturell symmetrisch DE/EN). Dabei Sachfehler gefunden: dsgvo.md nannte
      an 3 Stellen AES-256, tatsaechlich genutzt wird cryptography.fernet.Fernet
      (backend/core/crypto.py) = spezifiziert als AES-128-CBC+HMAC-SHA256;
      PRIVACY.md hatte bereits korrekt AES-128 (Fernet) stehen. dsgvo.md korrigiert
      und an PRIVACY.md angeglichen.

Phase D Status: D.1/D.2/D.4/D.5 abgeschlossen (D.2 mit offenem Fund, nicht
geloest). D.3 bleibt wie im Rework-Plan vorgesehen ausserhalb des Scopes.

## Phase E - Engineering (2026-08-24, Umsetzung)
- [x] Vorbedingung fuer E.1: alle 11 ESLint-Errors behoben (waren
      @typescript-eslint/no-explicit-any), sonst waere der neue CI-Lint-Job
      sofort dauerhaft rot gewesen. Dabei Nebenbefund in Dashboard.tsx
      gefixt: t(`dashboard.${tKey}`) suchte einen verschachtelten Schluessel
      der so nicht existiert - die 5 Counter-Kachel-Labels auf der
      Startseite zeigten vermutlich den rohen i18next-Fallback statt Text.
      Dashboard.tsx war nicht Teil der 38 in Phase C migrierten Dateien und
      dadurch uebersehen worden; dabei vollstaendig i18n-migriert.
      Settings.tsx hat denselben Luecken-Status (nur die Type-Error-Stelle
      gefixt, Rest bewusst offen) - siehe Fund unten.
- [x] E.2 Testpyramide: 4 neue Backend-Tests (backend/tests/test_cv_upload.py
      - Path-Traversal-Regressionsschutz fuer den Phase-A-Fix + X-Error-Code-
      Verifikation fuer cv.not_found/cv.invalid_file_type, ueber echten
      httpx.AsyncClient/ASGITransport gegen die echte FastAPI-App). Dabei
      einen ECHTEN Produktivbug gefunden und gefixt (siehe E.2b unten).
      4+4 neue Frontend-Tests (vitest + @testing-library/react neu
      eingerichtet): lib/api.test.ts (alle 4 Fallback-Pfade von
      getApiErrorMessage()), pages/CoverLetter.test.tsx (Rendering mit
      echten DE-Uebersetzungen, Ton-Auswahl, echter Generieren-Flow mit
      gemocktem axios.post, disabled-State). Ergebnis: Backend 26/26 gruen
      (vorher 22), Frontend 8/8 gruen (vorher 0).
- [x] E.2b (Nebenbefund waehrend E.2, nicht separat geplant): 7 von 22
      vorbestehenden Backend-Tests schlugen fehl (Job(titel=..., firma=...)
      - Modell nutzt aber title/company). Gefixt, wodurch ein bisher nie
      erreichter Assertion-Pfad zum ersten Mal lief und einen ECHTEN Bug in
      berechne_dashboard_stats() aufdeckte: der "soon"-Bucket (morgen
      faellig) nutzte func.current_date() + 1, was auf SQLite als schwach
      typisierte Zahlen-Arithmetik behandelt wird (kein gueltiges Datum) -
      der Bucket blieb dadurch immer leer. Gefixt auf Python-seitig
      berechnetes today/tomorrow als gebundene Parameter (dialektneutral).
- [x] E.1 CI-Workflow: .github/workflows/ci.yml, 3 Jobs (Backend-pytest,
      Frontend Lint+Test+Build, i18n-Check), laeuft auf jedem PR/Push gegen
      main. Lokal verifiziert (kein gh-Runner verfuegbar): alle Schritte
      einzeln mit Exit-Code 0 nachvollzogen.
- [x] E.3 Dependabot: .github/dependabot.yml, woechentlich, pip+npm+
      github-actions, kein Auto-Merge (Produktentscheidung bewusst offen
      gelassen).
- [x] E.4 Pre-Commit: .pre-commit-config.yaml, allgemeine Hygiene-Hooks +
      lokaler Frontend-ESLint-Hook (via "docker compose exec", da auf dem
      LXC-Host kein natives npm existiert - verifiziert). Echter Testlauf
      via "pre-commit run --all-files" durchgefuehrt, deckte 9 Dateien mit
      trailing whitespace/fehlendem Zeilenumbruch auf (rein kosmetisch
      gefixt).
- [x] E.5 Release-Prozess: CONTRIBUTING.md Abschnitt 8 (DE+EN) - SemVer-
      Regeln, Schritt-fuer-Schritt-Ablauf. Dabei Fund: frontend/package.json
      ("version": "0.4.0") laeuft der README-Badge-Version (v1.9.0)
      hinterher - als bekannte Luecke dokumentiert, nicht rueckwirkend
      korrigiert (eigene Produktentscheidung).

Offene Funde aus Phase E (nicht geloest, bewusst vermerkt):
- [x] Settings.tsx i18n-Luecke geschlossen (2026-08-24, Nutzerentscheidung
      "Settings.tsx i18n-Luecke schliessen"): komplette Seite uebersetzt
      (~60 neue Schluessel DE+EN, Trans-Komponente fuer den API-Keys-Intro-
      Text mit <strong>-Markup). Verifiziert: Build/Lint/i18n-Check/Tests
      gruen, echter curl-Abruf ueber den laufenden Dev-Server bestaetigt.
- frontend/package.json-Version nicht synchron zu README/CHANGELOG (siehe
  E.5).
- pages/Onboarding.tsx weiterhin toter, ungerouteter Code (aus D.2) -
  Entscheidung (loeschen/behalten) steht noch aus.

Phase E Status: ABGESCHLOSSEN (E.1-E.5 erledigt). Rework-Plan-Phasen A-E
damit vollstaendig durchlaufen. Offen bleiben: B.2 (main.py-Konsolidierung,
wartet auf den Nutzer), restliche B.6-Schemas (applications.py etc., haengen
ebenfalls an main.py), C.7/Phase 5 (echtes GitHub-Wiki), D.3 (Accessibility-
Audit, expliziter Nicht-Scope), die beiden i18n-Luecken oben.
