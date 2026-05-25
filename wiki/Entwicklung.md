# 🛠️ Entwicklung

Diese Seite beschreibt Architektur, Tech-Stack, Projektstruktur und den Workflow für Beitragende.

## Architektur-Überblick

```
┌─────────────────────────────────────────┐
│           Browser (React 18)            │
│  TypeScript · TailwindCSS · TanStack Q  │
└──────────────┬──────────────────────────┘
               │ HTTP / REST
┌──────────────▼──────────────────────────┐
│         FastAPI Backend (Python)        │
│  SQLAlchemy async · Alembic · Pydantic  │
└──────┬───────────────┬──────────────────┘
       │               │
┌──────▼──────┐  ┌──────▼──────┐
│ PostgreSQL  │  │   Ollama    │
│    16       │  │  (lokal)    │
└─────────────┘  └─────────────┘
```

Alle Dienste laufen in Docker-Containern und kommunizieren über ein internes Docker-Netzwerk.

## Tech-Stack

| Schicht | Technologie |
|---|---|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), Alembic, Pydantic v2 |
| Datenbank | PostgreSQL 16 |
| KI | Ollama (Mistral, LLaMA3, Phi-3) |
| Deployment | Docker Compose |
| Formatierung | Ruff (Python), ESLint + Prettier (TS) |

## Projektstruktur

```
JobHunter/
├── backend/
│   ├── api/          # FastAPI-Router (jobs, applications, settings …)
│   ├── services/     # Business-Logik (AI, IMAP, OCR, Cover Letter …)
│   ├── models.py     # SQLAlchemy-Modelle
│   ├── schemas.py    # Pydantic-Schemas
│   └── main.py       # App-Einstiegspunkt
├── frontend/
│   ├── src/
│   │   ├── components/   # Wiederverwendbare UI-Komponenten
│   │   ├── pages/        # Seiten (Dashboard, Kanban, Settings …)
│   │   ├── contexts/     # Theme, Accessibility, Auth
│   │   └── hooks/        # Custom React Hooks
│   └── public/
├── alembic/          # Datenbankmigrationen
├── docs/             # Technische Dokumentation
├── wiki/             # Dieses Wiki
├── .env.example      # Vorlage für Umgebungsvariablen
└── docker-compose.yml
```

## Entwicklungsprinzipien

- **Privacy first** – keine externen Datenübertragungen
- **Lokal vor Cloud** – KI läuft vollständig auf dem eigenen Rechner
- **Barrierefreiheit von Anfang an** – kein nachträgliches Patching
- **Modulare Erweiterbarkeit** – neue Features als eigenständige Services/Router
- **Issue-getriebene Entwicklung** – jedes Feature hat ein zugehöriges GitHub Issue

## Lokale Entwicklungsumgebung

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Datenbank starten (oder via Docker):
docker compose up db -d

# Migrationen anwenden:
alembic upgrade head

# Backend starten:
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend läuft auf `http://localhost:5173`, Backend auf `http://localhost:8000`.

## Beitragen (Contributing)

1. Repository forken
2. Feature-Branch erstellen: `git checkout -b feature/mein-feature`
3. Änderung umsetzen & lokal testen
4. Pull Request gegen `main` öffnen
5. Review abwarten → Merge

Ausführliche Hinweise: [CONTRIBUTING.md](https://github.com/freddykrueger88/JobHunter/blob/main/CONTRIBUTING.md)

## Datenbankmigrationen

Neue Migration erstellen:

```bash
alembic revision --autogenerate -m "Beschreibung der Änderung"
alembic upgrade head
```

Migrationen laufen beim Docker-Start automatisch.
