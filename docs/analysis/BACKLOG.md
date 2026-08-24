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
- [!] 0.2 GitHub-Auth klären — blockiert: kein Token/SSH-Key vorhanden. Wird erst bei
      Phase 5 (Wiki-Veröffentlichung) aktiv beim Nutzer angefragt, nicht vorher.
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
- [ ] 3.1 Entscheidung ableiten (Refactor / Restrukturierung / Teil-Neuaufbau) mit Begründung
- [ ] 3.2 docs/analysis/REWORK_PLAN_DE.md (5 Teilphasen wie vorgegeben)
- [ ] 3.3 docs/analysis/REWORK_PLAN_EN.md
- [ ] 3.4 docs/architecture/ (Diagramme + 1-3 ADRs für die wichtigsten Entscheidungen)
- [ ] >>> CHECKPOINT: Nutzer prüft Audit + Rework-Plan, bevor Code/i18n/Wiki angefasst wird <<<

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
