# Entwicklung

Diese Seite beschreibt Architektur, Technologien und den Entwicklungsansatz von JobHunter.

## Architektur

JobHunter besteht aus zwei Hauptteilen:

- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Frontend:** React + TypeScript + TailwindCSS

## Backend

Wichtige Bereiche:

- REST-API für Jobs, Bewerbungen, Einstellungen, Erinnerungen, Verlauf
- Datenbankmodelle für Bewerbungsverwaltung
- JWT-Authentifizierung optional
- Reminder-/Cron-Logik
- E-Mail-Service
- CV-Parsing und KI-Integration

## Frontend

Wichtige Bereiche:

- React Router Navigation
- Theme- und Accessibility-Kontexte
- Kanban-Board
- Dashboard
- Suchprofile
- Settings mit Integrationen

## Infrastruktur

- Docker / Docker Compose
- Alembic-Migrationen
- SQLite als Standard-DB
- lokale KI via Ollama

## Entwicklungsprinzipien

- Datenschutz zuerst
- lokal vor cloudbasiert
- barrierearme Bedienung
- klare, pragmatische UX
- modulare Erweiterbarkeit

## Issue-Workflow

Die Entwicklung wurde issue-basiert umgesetzt.

Abgedeckte Themen:

- Grundgerüst und Datenmodelle
- FastAPI-Backend
- React-Frontend
- Suche und CV-Parsing
- Kanban, Dashboard, Erinnerungen
- DSGVO, Accessibility und Inklusion
- Authentifizierung und Migrationen

## Mitwirken

Empfohlener Ablauf:

1. Branch erstellen
2. Änderung umsetzen
3. lokal testen
4. Pull Request erstellen
5. Review und Merge
