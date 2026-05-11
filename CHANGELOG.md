# Changelog

Alle wesentlichen Änderungen an JobHunter werden in dieser Datei dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

---

## [Unreleased]

> Ideen für v1.3: Mehrsprachige KI-Prompts, Mobile-PWA, Bewerbungs-Templates

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

[Unreleased]: https://github.com/freddykrueger88/JobHunter/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/freddykrueger88/JobHunter/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/freddykrueger88/JobHunter/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/freddykrueger88/JobHunter/releases/tag/v0.1.0
