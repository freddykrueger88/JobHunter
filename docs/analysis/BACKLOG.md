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
- [ ] Zusammenfassung nach Vorgabe (Ist-Zustand, Entscheidung, Top-10, i18n-Status,
      Wiki-Status, Validierung, offene Risiken)

## Änderungsprotokoll
- 2026-08-24: Backlog angelegt, gh installiert, Auth als blockiert markiert.

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
- [!] NEU ENTDECKT waehrend Verifikation: 14 von 21 Backend-Routern hatten kein /api-Praefix,
      obwohl ALLE Frontend-Calls durchgaengig /api/... nutzen -> Grossteil der App war ueber
      den Browser/Dev-Proxy nicht erreichbar (404). 12 Router gefixt und verifiziert.
      OFFEN (Produktentscheidung/main.py-Konflikt, absichtlich nicht angefasst):
      - api/company.py vs api/company_dossier.py: /dossier-Route wuerde kollidieren
      - api/jobs.py vs routers/jobs_image.py: potenzielle Pfad-Kollision, main.py-abhaengig
      - api/search_profiles.py: Praefix gefixt, aber Router war schon vorher nicht in main.py
        eingebunden (separater Bug) - SearchProfiles-Seite im Frontend aktuell tot
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
- [!] B.3 Produktentscheidung User/Auth (vervollstaendigen vs. entfernen) - ZURUECKGESTELLT:
      echte Produktentscheidung, kann nicht autonom getroffen werden.
- [x] B.4 Zentraler Frontend-API-Client frontend/src/lib/api.ts eingefuehrt,
      Dashboard.tsx als erste Datei migriert (Proof of Concept), verifiziert per
      npm run build + echtem HTTP-Request
- [x] B.5 Namenskollision CompanyDossier aufgeloest (pages/CompanyDossier.tsx ->
      CompanyDossierPage.tsx). Nebenbefund: components/CompanyDossier.tsx wird
      nirgends importiert - totes, unverdrahtetes Fragment, aehnlich Auth-Muster,
      absichtlich nicht geloescht (Produktentscheidung)
- [~] B.6 Backend-Schema-Schicht ausbauen - 6 Domaenen erledigt, jede einzeln per
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
      reminders.py und jobs.py hatten bereits gute Inline-Schemas (kein Handlungsbedarf).

      BEWUSST NICHT angefasst, mit Grund:
      - applications.py: haengt an models/application.py, Nutzer-eigene uncommittete
        Datei - nicht ohne Ruecksprache aendern.
      - ai.py, interview.py: geben teils direkt geparste LLM-Rohausgaben zurueck
        (services/interview_simulator.py parst z.B. json.loads() auf KI-Freitext ohne
        Formatgarantie) - eine strikte Schema-Erzwingung koennte bei abweichender
        KI-Antwort einen neuen 500er erzeugen, wo heute durchgereicht wird. Echte
        Designfrage (wie streng KI-Output validiert werden soll), keine reine
        Bugfix-Aufgabe - zurueckgestellt.
      - cover_letter_pdf.py, search_profiles.py: beide nicht in main.py eingebunden
        (bereits als Fund aus Phase A dokumentiert) - nicht per echtem HTTP-Request
        verifizierbar, daher zurueckgestellt bis die Registrierung geklaert ist.

      Damit sind praktisch alle ohne main.py-Aenderung oder KI-Design-Entscheidung
      sicher bearbeitbaren Domaenen abgedeckt.
- [x] B.7 Architekturregeln dokumentiert (docs/architecture/regeln.md)

Phase B Status: 4 von 7 abgeschlossen, B.6 so weit wie ohne main.py-Aenderungen bzw.
Produktentscheidungen moeglich (6 Domaenen).

Naechster Schritt: Review durch den Nutzer, insbesondere zu den zurueckgestellten
Punkten B.2/B.3 sowie den main.py-abhaengigen Themen (company.py/jobs.py/
search_profiles.py/cover_letter_pdf.py Registrierung) und der KI-Schema-Designfrage.
Danach Phase C (Internationalisierung) gemaess REWORK_PLAN_DE.md.
