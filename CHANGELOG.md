# Changelog

Alle wesentlichen Änderungen an JobHunter werden in dieser Datei dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

---

## [Unreleased]

> Ideen für v1.9: Multi-User-Support, Mobile-App (React Native), Bewerbungscoach-Chat, Browser-Extension

---

## [1.8.0] – 2026-05-11

### ATS-Optimierung & Bewerbungsqualität

- **ATS-Score-Checker** – `ats_scorer.py`: Tokenizer mit Stop-Wörter-Filter (DE+EN), Top-30-Keyword-Frequenzanalyse, gewichteter Match-Score 0–100, Ampel-System (🔴 < 50 / 🟡 50–70 / 🟢 ≥ 70), Formatierungs-Check (Tabellen, SVG-Icons, Mehrspalter); `AtsScorePanel.tsx` mit aufklappbarer Keyword-Liste + KI-Vorschlägen (#57)
- **Ghost-Job-Erkennung** – `ghost_job_detector.py`: 5 gewichtete Heuristiken (Alter 35% · kein Ansprechpartner 20% · kein Gehalt 15% · Boilerplate 20% · kurze Beschreibung 10%); `GhostJobBadge.tsx` mit ⚠️-Badge und Tooltip der Gründe (#58)
- **Bewerbungs-Qualitätsscore** – `application_quality.py`: gewichteter Gesamt-Score aus Anschreiben (20%) + Anschreiben-Score (25%) + CV (15%) + ATS-Score (25%) + Skill-Gap (15%); `QualityScoreCard.tsx` mit SVG-Fortschrittsring, Checkliste und „Nächster Schritt“-Banner mit Schnelllink (#59)
- **Gehaltsnegotiations-Coach** – `salary_negotiation.py`: KI generiert 3 Szenarien (konservativ / realistisch / optimistisch) mit konkreten Beträgen; `SalaryNegotiationModal.tsx` mit Tab-Umschalter E-Mail ↔ Telefonat, 1-Klick-Kopieren, realistisches Szenario hervorgehoben; baut auf `salary_calculator.py` (v1.6) auf (#60)
- **Marktlage-Analyse** – `market_analyzer.py`: Vorab-Heuristik (Dringlichkeit / Wachstum / Fluktuation) + KI-Analyse: Wettbewerb-Level (niedrig/mittel/hoch), optimaler Bewerbungszeitpunkt, Unternehmenstyp (Startup/KMU/Konzern/Behörde), Strategie-Empfehlung mit Begründung (#61)

---

## [1.7.0] – 2026-05-11

### Statistiken & Motivation

- **Erweiterte Dashboard-Statistiken** – `StatsChart.tsx` mit Pie-Chart (Status-Verteilung), Bar-Chart (Bewerbungen pro Woche), Funnel-Chart (Beworben → Eingeladen → Gespräch → Zusage) via Recharts (#36)
- **Browser-Push-Benachrichtigungen** – `goals.py` mit `get_streak()`, `get_weekly_progress()`, `get_stats()` – alle Stats-Endpoints fertig (#37)
- **Bewerbungs-Ziele + Streak-Tracking** – `WeeklyGoalWidget.tsx`: konfigurierbares Wochenziel, Fortschrittsbalken, 🔥 Streak-Anzeige, ARIA-accessible (#51)
- **Gamification – Abzeichen** – `badges.py`: 10 Abzeichen (Erste Bewerbung, 10/50 Bewerbungen, Erste Einladung, Erste Zusage, 3/7-Tage-Streak, KI-Anschreiben, Lebenslauf, Foto-Upload); `BadgesPanel.tsx` mit gesperrten/freigeschalteten Abzeichen (#52)
- **Druckansicht als PDF** – `pdf_overview.py`: HTML→PDF via weasyprint, filterbar nach Zeitraum und Status, Tabelle mit allen Bewerbungen (#53)

---

## [1.6.0] – 2026-05-11

### Kommunikation & Workflow

- **Kalender-Export** – `calendar_export.py`: `.ics`-Export pro Vorstellungsgespräch + abonnierbarer Kalender-Feed `GET /api/calendar/feed.ics` für alle Termine (#47)
- **E-Mail-Vorlagen** – `email_templates.py`: 6 Templates (Follow-up, Nachfrage, Absage-Antwort, Zusage bestätigen, Termin bestätigen/absagen) mit Platzhaltern `{anrede}`, `{stelle}`, `{firma}`, `{datum}` (#48)
- **Kontakte-Verwaltung** – `Contact`-Modell: Recruiter und Ansprechpartner mit Firma, Rolle, E-Mail, Telefon, LinkedIn-URL, Notizen, nächstem Kontaktdatum (#49)
- **Netto-Brutto-Gehaltsrechner** – `salary_calculator.py`: Steuerklassen 1–6, SV-Beiträge 2025 (KV/PV/RV/AV), BBG-konforme Berechnung, 100% lokal (#43)

---

## [1.5.0] – 2026-05-11

### KI-Tiefe

- **Absage-Analyse per KI** – `rejection_analyzer.py`: Absage + Anschreiben + Stellenbeschreibung → Stärken, Schwächen, 3 Verbesserungsvorschläge, Zusammenfassung (#40)
- **Interview-Vorbereitung per KI** – `interview_prep.py`: 10 Fragen (5 fachlich, 3 persönlich, 2 Gehalt) mit Musterantworten, passend zu CV + Stelle (#41)
- **Skill-Gap-Analyse** – `skill_gap.py`: Match-Score 0–100, vorhandene/fehlende Skills, Lernempfehlungen; Ergebnis wird in DB gecacht (#42)
- **Lebenslauf-Optimierung per KI** – `cv_optimizer.py`: Score + Stärken/Schwächen + Abschnitt-für-Abschnitt-Vorschläge, optional mit Zielstelle (#55)
- **Anschreiben-Bewertung per KI** – `cover_letter_evaluator.py`: Relevanz/Ton/Struktur-Score (0–100), speichert `anschreiben_score` in DB (#56)

---

## [1.4.0] – 2026-05-11

### Smarte Suche & Datenanalyse

- **Foto-Upload von Stellenanzeigen** – `ocr.py` + `jobs_image.py`: `POST /api/jobs/from-image`; easyocr bevorzugt (Fallback: pytesseract), KI extrahiert Titel/Firma/Ort/Frist/Tags; `ImageJobUpload.tsx` mit Drag & Drop + Kamera-Button (#38)
- **Duplikat-Erkennung** – `duplicate_detection.py`: Fuzzy-Matching via rapidfuzz, Gewichtung Titel 50% + Firma 35% + Ort 15%, Schwellenwert 75%, Warnung vor dem Speichern (#39)
- **Bewerbungsfristen-Tracker** – `DeadlineBadge.tsx`: Ampel-Badge 🟢 >7T · 🟡 3–7T · 🔴 <3T · ⚫ abgelaufen, vollständig ARIA-beschriftet (#44)
- **Stellenbeschreibung-Analyse** – `job_analyzer.py`: KI extrahiert Must-haves, Nice-to-haves, Gehalt, Remote/Hybrid, Tags; schreibt Ergebnisse zurück in DB (#45)
- **Firmen-Schwarze-Liste** – `blocklist.py`: `GET/POST/DELETE /api/blocklist/`, `is_blocked()`-Hilfsfunktion für alle Such-Endpoints (#46)

---

## [1.3.0] – 2026-05-11

### Mobil & Basis-Produktivität

- **PWA Install-Support** – `vite.config.ts` mit `vite-plugin-pwa`: autoUpdate, Workbox Offline-Cache (NetworkFirst für `/api/`), `manifest.webmanifest` mit Icons; `PwaInstallBanner.tsx` via `beforeinstallprompt`, 7-Tage-Snooze (#33)
- **Bewerbungs-Templates** – `CoverLetterTemplate`-Modell + `default_templates.py`: 5 vorgefertigte Templates (IT allgemein, IT-Support, Büro, Logistik, IT EN), Platzhalter `{stelle}`, `{firma}`, `{ort}`, `{datum}`, `{anrede}` (#34)
- **Mehrsprachige KI-Prompts** – `ai_prompts.py`: vollständige DE/EN-Prompt-Bibliothek (Anschreiben, Job-Analyse, Skill-Gap, Interview-Prep, Absage-Analyse), `detect_language()` via Häufigkeitswörter (#35)
- **Onboarding-Flow** – `Onboarding.tsx`: 5-Schritt-Wizard (Sprache → Ort → Ollama-Check → Theme → Fertig), Fortschrittsbalken, Live-Verbindungstest (#50)
- **Automatisches Backup** – `backup.py`: komprimiertes `.json.gz`-Backup täglich, 7-Tage-Rotation, API-Keys werden nicht gesichert, `BackupLog`-Modell (#54)

---

## [1.2.0] – 2026-05-11

### Inklusion & Barrierefreiheit

- **Legasthenie-Theme** – OpenDyslexic-Font (SIL OFL, lokal gehostet), Zeilenabstand 1.8, Buchstabenabstand +0.05em, Cremeweißer Hintergrund (#fffef5), max. 65ch Zeilenbreite (#27)
- **Farbenblindheits-Filter** – 4 SVG `feColorMatrix`-Filter (Deuteranopie, Protanopie, Tritanopie, Achromatopsie), kombinierbar mit allen Themes (#28)
- **Screenreader-Verbesserungen** – Skip-Link, `aria-live="polite"` + `role="alert"` Regionen, `useAnnounce()`-Hook, `useFocusTrap()`-Hook, `<main id="main-content">` (#29)
- **ADHS-Modus** – Fokus-Modus, Animationen deaktivieren, Informationsdichte (normal/kompakt/minimal), `AccessibilityContext` mit localStorage-Persistenz (#30)
- **Tastaturkürzel-System** – `useKeyboardShortcuts()`-Hook, G-Sequenz-Navigation, `ShortcutOverlay`-Modal via `?`-Taste (#31)
- **Undo-Toast** – 5s Countdown-Balken, Rückgängig-Button; **ConfirmDialog** – Promise-basiert, `Enter`/`Escape` Tastatursteuerung (#32)

---

## [1.1.0] – 2026-05-11

### Neu

- **Inline-Notizen im Kanban** – Doppelklick auf Notizfeld öffnet `<textarea>`, Speichern via `Enter`, Abbrechen via `Escape` (#22)
- **Status-Zeitstrahl** – `ApplicationStatusLog`-Modell, `GET /api/applications/{id}/timeline`, vertikaler Zeitstrahl im Detail-Modal (#23)
- **E-Mail-Benachrichtigungen** – `aiosmtplib`-Service, HTML + Plaintext, Cron alle 15 Minuten, SMTP-Felder in Settings (#24)
- **JWT-Authentifizierung** – optional via `AUTH_ENABLED=true`; `/auth/token`, `/auth/register`, `/auth/change-password`; bcrypt-Passwörter (#25)
- **Alembic-Migrationen** – `alembic.ini` + async `env.py`, initiale Migration `0001`, automatischer `alembic upgrade head` beim Start (#26)

### Portal-Integration

- **StepStone-Scraper** – robots.txt-konformer HTTP-Scraper mit Rate-Limiting (#20)
- **LinkedIn Job Search Adapter** – offizieller API-Adapter (#21)

### Daten & Export

- **JSON Export/Import** – DSGVO Art. 20, vollständiges Backup aller Tabellen (#17)
- **PDF-Export** – Anschreiben als PDF via `weasyprint` (#18)
- **Auto-Search-Cron** – APScheduler-basierter Job für Suchprofile (#19)

---

## [1.0.0] – 2026-05-11

### Kern-Features

- **Datenmodelle** – `Job`, `Application`, `Reminder`, `SearchProfile`, `UserSettings`, `ApplicationHistory` (#02)
- **FastAPI-Backend** – vollständige REST-API mit Pydantic-Schemas und async SQLAlchemy (#03)
- **React-Frontend** – Vite + TypeScript + TailwindCSS, React Router, i18n (DE/EN), 4 Themes (#04)
- **CV-Parsing** – PDF- und DOCX-Lebenslauf-Parsing, automatische Feldextraktion (#05)
- **Job-Suche** – Adzuna API + Arbeitsagentur API, Suchduplikat-Erkennung (#06)
- **Suchprofile** – gespeicherte Suchen mit Filtern und Auto-Search (#07)
- **Kanban-Board** – Drag & Drop, Status-Spalten, Tastaturalternative (#08)
- **Dashboard** – Live-Statistiken, Tagesfortschritt, Bewerbungs-Übersicht (#09)
- **Ollama KI** – lokale LLM-Integration, Anschreiben-Generator mit Tonauswahl (#10)
- **Anschreiben-Generator** – KI-gestützt, Tonauswahl (formell/direkt/modern/kreativ) (#11)
- **Erinnerungen** – CRUD, Fälligkeitsdatum, Wiederholungen (#12)
- **Einstellungen** – vollständige Settings-Seite mit API-Key-Verwaltung (AES-256) (#13)
- **Verlauf** – Bewerbungs-Verlaufsseite mit Timeline (#14)
- **WCAG 2.1 AA Audit** – Kontrastprüfung, Fokuszustände, Touch-Targets, ARIA-Labels (#15)
- **DSGVO-Dokumentation** – Privacy Policy, Datenschutzdoku, Löschkonzept (#16)

### Infrastruktur

- Docker + Docker Compose (#01)
- Projektstruktur und Krypto-Modul (AES-256) (#01)
- README (DE + EN) mit vollständiger Projektbeschreibung

---

## [0.1.0] – 2026-05-10

### Initial

- Repository erstellt
- README angelegt

---

[Unreleased]: https://github.com/freddykrueger88/JobHunter/compare/v1.8.0...HEAD
[1.8.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/freddykrueger88/JobHunter/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/freddykrueger88/JobHunter/releases/tag/v0.1.0
