# 🏗️ Architecture / Architektur

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter is a fully self-hosted application consisting of 4 Docker services that communicate exclusively within the local Docker network.

## System Overview

```
┌────────────────────────────────────────────────┐
│              Browser (User)                │
└───────┬─────────────────────────────────────┘
         │
    :3000 │            :8000
┌───────┴───────┐  REST API  ┌───────────────┐
│   Frontend     │➡️➡️➡️│    Backend     │
│  React + Vite  │⬅️⬅️⬅️│  FastAPI + SA  │
└───────────────┘          └─────┬─────────┘
                                    │
                        ┌───────┴───────┐
                        │           │
               ┌──────┴────┐  ┌────┴─────┐
               │ PostgreSQL │  │   Ollama   │
               │   :5432    │  │  :11434   │
               └────────────┘  └───────────┘
```

## Services

| Service | Technology | Port | Description |
|---|---|---|---|
| **frontend** | React 18 + Vite + TypeScript + TailwindCSS | 3000 | Single Page Application |
| **backend** | Python 3.11 + FastAPI + SQLAlchemy (async) | 8000 | REST API + business logic |
| **db** | PostgreSQL 15 | 5432 (internal) | Persistent data storage |
| **ollama** | Ollama + Mistral/LLaMA3/Phi-3 | 11434 (internal) | Local AI inference |

## Backend Structure

```
backend/
├── main.py                  # FastAPI app, router registration
├── models/                  # SQLAlchemy ORM models
├── schemas/                 # Pydantic schemas (request/response)
├── routers/                 # API route handlers
├── services/                # Business logic
│   ├── job_search/          # Job portal adapters
│   ├── ai/                  # Ollama integration, prompts
│   ├── ats_scorer.py        # ATS score checker
│   ├── backup.py            # Automatic backup
│   └── ...                  # More services
├── alembic/                 # Database migrations
└── requirements.txt
```

## Frontend Structure

```
frontend/src/
├── pages/                   # Page components (Dashboard, Kanban, etc.)
├── components/              # Reusable UI components
├── hooks/                   # Custom React hooks
├── context/                 # React Context (Theme, Language, Auth)
├── i18n/                    # Translations (DE + EN)
├── utils/                   # Helper functions
└── main.tsx                 # App entry point
```

## Data Flow: Cover Letter Generation

```
User clicks "Generate"
    ↓
Frontend POST /api/cover-letter/generate
    ↓
Backend loads: CV data + job description + template + tone
    ↓
Ollama API (local): POST http://ollama:11434/api/generate
    ↓
Mistral generates cover letter text
    ↓
Backend saves result in PostgreSQL
    ↓
Frontend displays cover letter
```

## Data Flow: Job Search

```
User enters search (keywords + location + radius)
    ↓
Frontend POST /api/jobs/search
    ↓
Backend: aggregator.py calls all active portal adapters in parallel
    ↓
Arbeitsagentur API + StepStone scraper + Adzuna API + LinkedIn API
    ↓
Duplicate detection (rapidfuzz)
    ↓
Results saved in PostgreSQL, returned to frontend
```

## Security Model

| Aspect | Implementation |
|---|---|
| API Key Storage | Fernet AES-128 encrypted in PostgreSQL |
| Network | All services in isolated Docker network |
| File Uploads | Type check + size limit, stored in volume |
| External Requests | Only from backend, never from frontend directly |

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Recharts |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| AI | Ollama, Mistral, LLaMA3, Phi-3 |
| Database | PostgreSQL 15 |
| Infrastructure | Docker, Docker Compose |
| PDF | WeasyPrint |
| OCR | easyocr, pytesseract |
| Fuzzy Matching | rapidfuzz |

---
---

## Deutsch

JobHunter ist eine vollständig selbst-gehostete Anwendung bestehend aus 4 Docker-Diensten, die ausschließlich innerhalb des lokalen Docker-Netzwerks kommunizieren.

## Dienste

| Dienst | Technologie | Port | Beschreibung |
|---|---|---|---|
| **frontend** | React 18 + Vite + TypeScript + TailwindCSS | 3000 | Single Page Application |
| **backend** | Python 3.11 + FastAPI + SQLAlchemy (async) | 8000 | REST-API + Geschäftslogik |
| **db** | PostgreSQL 15 | 5432 (intern) | Persistente Datenspeicherung |
| **ollama** | Ollama + Mistral/LLaMA3/Phi-3 | 11434 (intern) | Lokale KI-Inferenz |

## Backend-Struktur

```
backend/
├── main.py                  # FastAPI-App, Router-Registrierung
├── models/                  # SQLAlchemy ORM-Modelle
├── schemas/                 # Pydantic-Schemas
├── routers/                 # API-Route-Handler
├── services/                # Geschäftslogik
│   ├── job_search/          # Jobportal-Adapter
│   ├── ai/                  # Ollama-Integration
│   └── ...                  # Weitere Services
├── alembic/                 # Datenbankmigrationen
└── requirements.txt
```

## Sicherheitsmodell

| Aspekt | Umsetzung |
|---|---|
| API-Key-Speicherung | Fernet AES-128 verschlüsselt in PostgreSQL |
| Netzwerk | Alle Dienste im isolierten Docker-Netzwerk |
| Datei-Uploads | Typ-Prüfung + Größenlimit, gespeichert im Volume |

## Technologie-Stack

| Schicht | Technologie |
|---|---|
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Recharts |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| KI | Ollama, Mistral, LLaMA3, Phi-3 |
| Datenbank | PostgreSQL 15 |
| Infrastruktur | Docker, Docker Compose |
