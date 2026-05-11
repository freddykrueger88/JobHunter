# Changelog

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

All notable changes to JobHunter are documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

### [Unreleased]

> Planned for v1.9: Application Coach Chat (#62), Auto-Apply Package (#63), Follow-Up System (#64)

---

### [1.8.0] – 2026-05-11

#### ATS Optimization & Application Quality

- **ATS Score Checker** – `ats_scorer.py`: tokenizer with stop-word filter (DE+EN), top-30 keyword frequency analysis, weighted match score 0–100, traffic light system (🔴 < 50 / 🟡 50–70 / 🟢 ≥ 70), format check (tables, SVG icons, multi-column); `AtsScorePanel.tsx` with expandable keyword list + AI suggestions (#57)
- **Ghost Job Detection** – `ghost_job_detector.py`: 5 weighted heuristics (age 35% · no contact person 20% · no salary 15% · boilerplate 20% · short description 10%); `GhostJobBadge.tsx` with ⚠️ badge and tooltip of reasons (#58)
- **Application Quality Score** – `application_quality.py`: weighted total score from cover letter (20%) + cover letter score (25%) + CV (15%) + ATS score (25%) + skill gap (15%); `QualityScoreCard.tsx` with SVG progress ring, checklist and "Next Step" banner with quick link (#59)
- **Salary Negotiation Coach** – `salary_negotiation.py`: AI generates 3 scenarios (conservative / realistic / optimistic) with concrete amounts; `SalaryNegotiationModal.tsx` with tab switcher Email ↔ Phone, 1-click copy, realistic scenario highlighted; builds on `salary_calculator.py` (v1.6) (#60)
- **Market Analysis** – `market_analyzer.py`: pre-heuristic (urgency / growth / turnover) + AI analysis: competition level (low/medium/high), optimal application timing, company type (startup/SME/corporation/authority), strategy recommendation; `MarketAnalyzerPanel.tsx` with competition traffic light, 2-column grid, heuristic badges (⚡ Urgent / 📈 Growth / 🔄 Replacement) (#61)

---

### [1.7.0] – 2026-05-11

#### Statistics & Motivation

- **Extended Dashboard Statistics** – `StatsChart.tsx` with Pie chart (status distribution), Bar chart (applications per week), Funnel chart (Applied → Invited → Interview → Offer) via Recharts (#36)
- **Browser Push Notifications** – `goals.py` with `get_streak()`, `get_weekly_progress()`, `get_stats()` (#37)
- **Application Goals + Streak Tracking** – `WeeklyGoalWidget.tsx`: configurable weekly goal, progress bar, 🔥 streak display, ARIA-accessible (#51)
- **Gamification – Badges** – `badges.py`: 10 badges (First Application, 10/50 Applications, First Invitation, First Offer, 3/7-day streak, AI Cover Letter, CV, Photo Upload); `BadgesPanel.tsx` (#52)
- **Print View as PDF** – `pdf_overview.py`: HTML→PDF via weasyprint, filterable by period and status (#53)

---

### [1.6.0] – 2026-05-11

#### Communication & Workflow

- **Calendar Export** – `calendar_export.py`: `.ics` export per interview + subscribable calendar feed `GET /api/calendar/feed.ics` (#47)
- **Email Templates** – `email_templates.py`: 6 templates (follow-up, inquiry, rejection reply, offer confirm, appointment confirm/cancel) with placeholders (#48)
- **Contacts Management** – `Contact` model: recruiters and contact persons with company, role, email, phone, LinkedIn URL, notes, next contact date (#49)
- **Net-Gross Salary Calculator** – `salary_calculator.py`: tax classes 1–6, social security contributions 2025, BBG-compliant calculation, 100% local (#43)

---

### [1.5.0] – 2026-05-11

#### AI Depth

- **Rejection Analysis via AI** – `rejection_analyzer.py`: rejection + cover letter + job description → strengths, weaknesses, 3 improvement suggestions (#40)
- **Interview Preparation via AI** – `interview_prep.py`: 10 questions (5 technical, 3 personal, 2 salary) with model answers (#41)
- **Skill Gap Analysis** – `skill_gap.py`: match score 0–100, existing/missing skills, learning recommendations; result cached in DB (#42)
- **CV Optimization via AI** – `cv_optimizer.py`: score + strengths/weaknesses + section-by-section suggestions (#55)
- **Cover Letter Rating via AI** – `cover_letter_evaluator.py`: relevance/tone/structure score (0–100), saves `cover_letter_score` in DB (#56)

---

### [1.4.0] – 2026-05-11

#### Smart Search & Data Analysis

- **Job Listing Photo Upload** – `ocr.py` + `jobs_image.py`: `POST /api/jobs/from-image`; easyocr preferred (fallback: pytesseract), AI extracts title/company/location/deadline/tags (#38)
- **Duplicate Detection** – `duplicate_detection.py`: fuzzy matching via rapidfuzz, weighting title 50% + company 35% + location 15%, threshold 75%, warning before saving (#39)
- **Application Deadline Tracker** – `DeadlineBadge.tsx`: traffic light badge 🟢 >7d · 🟡 3–7d · 🔴 <3d · ⚫ expired, fully ARIA-labeled (#44)
- **Job Description Analysis** – `job_analyzer.py`: AI extracts must-haves, nice-to-haves, salary, remote/hybrid, tags; writes results back to DB (#45)
- **Company Blocklist** – `blocklist.py`: `GET/POST/DELETE /api/blocklist/`, `is_blocked()` helper function for all search endpoints (#46)

---

### [1.3.0] – 2026-05-11

#### Mobile & Basic Productivity

- **PWA Install Support** – `vite.config.ts` with `vite-plugin-pwa`: autoUpdate, Workbox offline cache, `manifest.webmanifest` with icons; `PwaInstallBanner.tsx` via `beforeinstallprompt`, 7-day snooze (#33)
- **Application Templates** – `CoverLetterTemplate` model + `default_templates.py`: 5 default templates (IT general, IT Support, Office, Logistics, IT EN) (#34)
- **Multilingual AI Prompts** – `ai_prompts.py`: complete DE/EN prompt library, `detect_language()` via frequency words (#35)
- **Onboarding Flow** – `Onboarding.tsx`: 5-step wizard (Language → Location → Ollama check → Theme → Done), live connection test (#50)
- **Automatic Backup** – `backup.py`: compressed `.json.gz` backup daily, 7-day rotation, API keys not backed up (#54)

---

### [1.2.0] – 2026-05-11

#### Inclusion & Accessibility

- **Dyslexia Theme** – OpenDyslexic font (SIL OFL, locally hosted), line spacing 1.8, letter spacing +0.05em, cream white background (#fffef5), max. 65ch line width (#27)
- **Color Blindness Filters** – 4 SVG `feColorMatrix` filters (Deuteranopia, Protanopia, Tritanopia, Achromatopsia), combinable with all themes (#28)
- **Screen Reader Improvements** – skip link, `aria-live="polite"` + `role="alert"` regions, `useAnnounce()` hook, `useFocusTrap()` hook (#29)
- **ADHD Mode** – focus mode, disable animations, information density (normal/compact/minimal), `AccessibilityContext` with localStorage persistence (#30)
- **Keyboard Shortcut System** – `useKeyboardShortcuts()` hook, G-sequence navigation, `ShortcutOverlay` modal via `?` key (#31)
- **Undo Toast** – 5s countdown bar, undo button; **ConfirmDialog** – Promise-based, `Enter`/`Escape` keyboard control (#32)

---

### [1.1.0] – 2026-05-11

#### New

- **Inline Notes in Kanban** – double-click on note field opens `<textarea>`, save via `Enter`, cancel via `Escape` (#22)
- **Status Timeline** – `ApplicationStatusLog` model, `GET /api/applications/{id}/timeline`, vertical timeline in detail modal (#23)
- **Email Notifications** – `aiosmtplib` service, HTML + plaintext, cron every 15 minutes, SMTP fields in settings (#24)
- **JWT Authentication** – optional via `AUTH_ENABLED=true`; `/auth/token`, `/auth/register`, `/auth/change-password`; bcrypt passwords (#25)
- **Alembic Migrations** – `alembic.ini` + async `env.py`, initial migration `0001`, automatic `alembic upgrade head` on startup (#26)

#### Portal Integration

- **StepStone Scraper** – robots.txt-compliant HTTP scraper with rate limiting (#20)
- **LinkedIn Job Search Adapter** – official API adapter (#21)

#### Data & Export

- **JSON Export/Import** – GDPR Art. 20, complete backup of all tables (#17)
- **PDF Export** – cover letter as PDF via `weasyprint` (#18)
- **Auto-Search Cron** – APScheduler-based job for search profiles (#19)

---

### [1.0.0] – 2026-05-11

#### Core Features

- **Data Models** – `Job`, `Application`, `Reminder`, `SearchProfile`, `UserSettings`, `ApplicationHistory` (#02)
- **FastAPI Backend** – complete REST API with Pydantic schemas and async SQLAlchemy (#03)
- **React Frontend** – Vite + TypeScript + TailwindCSS, React Router, i18n (DE/EN), 4 themes (#04)
- **CV Parsing** – PDF and DOCX resume parsing, automatic field extraction (#05)
- **Job Search** – Adzuna API + Arbeitsagentur API, search duplicate detection (#06)
- **Search Profiles** – saved searches with filters and auto-search (#07)
- **Kanban Board** – drag & drop, status columns, keyboard alternative (#08)
- **Dashboard** – live statistics, daily progress, application overview (#09)
- **Ollama AI** – local LLM integration, cover letter generator with tone selection (#10)
- **Cover Letter Generator** – AI-powered, tone selection (formal/direct/modern/creative) (#11)
- **Reminders** – CRUD, due date, repetitions (#12)
- **Settings** – complete settings page with API key management (AES-256) (#13)
- **History** – application history page with timeline (#14)
- **WCAG 2.1 AA Audit** – contrast check, focus states, touch targets, ARIA labels (#15)
- **GDPR Documentation** – privacy policy, data protection docs, deletion concept (#16)

#### Infrastructure

- Docker + Docker Compose (#01)
- Project structure and crypto module (AES-256) (#01)
- README (DE + EN) with complete project description

---

### [0.1.0] – 2026-05-10

#### Initial

- Repository created
- README added

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

---
---

## Deutsch

Alle wesentlichen Änderungen an JobHunter werden in dieser Datei dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

---

### [Unreleased]

> Geplant für v1.9: Bewerbungscoach-Chat (#62), Auto-Apply-Paket (#63), Wiedervorlagen-System (#64)

---

### [1.8.0] – 2026-05-11

#### ATS-Optimierung & Bewerbungsqualität

- **ATS-Score-Checker** – `ats_scorer.py`: Tokenizer mit Stop-Wörter-Filter (DE+EN), Top-30-Keyword-Frequenzanalyse, gewichteter Match-Score 0–100, Ampel-System (🔴 < 50 / 🟡 50–70 / 🟢 ≥ 70), Formatierungs-Check; `AtsScorePanel.tsx` mit aufklappbarer Keyword-Liste + KI-Vorschlägen (#57)
- **Ghost-Job-Erkennung** – `ghost_job_detector.py`: 5 gewichtete Heuristiken; `GhostJobBadge.tsx` mit ⚠️-Badge und Tooltip (#58)
- **Bewerbungs-Qualitätsscore** – `application_quality.py`: gewichteter Gesamt-Score; `QualityScoreCard.tsx` mit SVG-Fortschrittsring, Checkliste und „Nächster Schritt“-Banner (#59)
- **Gehaltsnegotiations-Coach** – `salary_negotiation.py`: KI generiert 3 Szenarien; `SalaryNegotiationModal.tsx` mit Tab-Umschalter E-Mail ↔ Telefonat (#60)
- **Marktlage-Analyse** – `market_analyzer.py`: Vorab-Heuristik + KI-Analyse: Wettbewerb-Level, optimaler Zeitpunkt, Unternehmenstyp, Strategie-Empfehlung (#61)

---

### [1.7.0] – 2026-05-11

#### Statistiken & Motivation

- **Erweiterte Dashboard-Statistiken** – Pie-Chart, Bar-Chart, Funnel-Chart via Recharts (#36)
- **Browser-Push-Benachrichtigungen** – `goals.py` (#37)
- **Bewerbungs-Ziele + Streak-Tracking** – `WeeklyGoalWidget.tsx`: konfigurierbares Wochenziel, 🔥 Streak-Anzeige (#51)
- **Gamification – Abzeichen** – 10 Abzeichen; `BadgesPanel.tsx` (#52)
- **Druckansicht als PDF** – `pdf_overview.py` via weasyprint (#53)

---

### [1.6.0] – 2026-05-11

#### Kommunikation & Workflow

- **Kalender-Export** – `.ics`-Export + abonnierbarer Kalender-Feed (#47)
- **E-Mail-Vorlagen** – 6 Templates mit Platzhaltern (#48)
- **Kontakte-Verwaltung** – Recruiter und Ansprechpartner (#49)
- **Netto-Brutto-Gehaltsrechner** – Steuerklassen 1–6, 100% lokal (#43)

---

### [1.5.0] – 2026-05-11

#### KI-Tiefe

- **Absage-Analyse per KI** – Stärken, Schwächen, 3 Verbesserungsvorschläge (#40)
- **Interview-Vorbereitung per KI** – 10 Fragen mit Musterantworten (#41)
- **Skill-Gap-Analyse** – Match-Score 0–100, Lernempfehlungen (#42)
- **Lebenslauf-Optimierung per KI** (#55)
- **Anschreiben-Bewertung per KI** – Relevanz/Ton/Struktur-Score (#56)

---

### [1.4.0] – 2026-05-11

#### Smarte Suche & Datenanalyse

- **Foto-Upload von Stellenanzeigen** – easyocr + KI-Extraktion (#38)
- **Duplikat-Erkennung** – rapidfuzz, Schwellenwert 75% (#39)
- **Bewerbungsfristen-Tracker** – Ampel-Badge (#44)
- **Stellenbeschreibung-Analyse** – KI extrahiert Must-haves, Nice-to-haves, Gehalt (#45)
- **Firmen-Schwarze-Liste** (#46)

---

### [1.3.0] – 2026-05-11

#### Mobil & Basis-Produktivität

- **PWA Install-Support** – Offline-Cache, Install-Banner (#33)
- **Bewerbungs-Templates** – 5 vorgefertigte Templates (#34)
- **Mehrsprachige KI-Prompts** – DE/EN-Prompt-Bibliothek (#35)
- **Onboarding-Flow** – 5-Schritt-Wizard (#50)
- **Automatisches Backup** – täglich, 7-Tage-Rotation (#54)

---

### [1.2.0] – 2026-05-11

#### Inklusion & Barrierefreiheit

- **Legasthenie-Theme** – OpenDyslexic, Cremeweiß-Hintergrund (#27)
- **Farbenblindheits-Filter** – 4 SVG-Filter kombinierbar mit allen Themes (#28)
- **Screenreader-Verbesserungen** – Skip-Link, aria-live, useFocusTrap (#29)
- **ADHS-Modus** – Fokus-Modus, Animationen deaktivieren (#30)
- **Tastaturkürzel-System** – `useKeyboardShortcuts()`, ShortcutOverlay via `?` (#31)
- **Undo-Toast + ConfirmDialog** (#32)

---

### [1.1.0] – 2026-05-11

#### Neu

- **Inline-Notizen im Kanban** (#22)
- **Status-Zeitstrahl** (#23)
- **E-Mail-Benachrichtigungen** (#24)
- **JWT-Authentifizierung** – optional via `AUTH_ENABLED=true` (#25)
- **Alembic-Migrationen** (#26)
- **StepStone-Scraper** (#20) · **LinkedIn-Adapter** (#21)
- **JSON-Export/Import** (#17) · **PDF-Export** (#18) · **Auto-Search-Cron** (#19)

---

### [1.0.0] – 2026-05-11

#### Kern-Features

- Datenmodelle, FastAPI-Backend, React-Frontend, CV-Parsing, Job-Suche, Suchprofile, Kanban-Board, Dashboard, Ollama KI, Anschreiben-Generator, Erinnerungen, Einstellungen, Verlauf, WCAG 2.1 AA, DSGVO-Dokumentation, Docker + Docker Compose

---

### [0.1.0] – 2026-05-10

- Repository erstellt, README angelegt
