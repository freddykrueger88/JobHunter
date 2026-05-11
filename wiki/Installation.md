# Installation

Diese Anleitung beschreibt die lokale Einrichtung von JobHunter mit Docker.

## Voraussetzungen

- Docker
- Docker Compose
- Optional: Ollama lokal installiert, wenn KI-Funktionen genutzt werden sollen

## Repository klonen

```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
```

## Umgebungsdatei anlegen

Falls noch nicht vorhanden:

```bash
cp .env.example .env
```

Typische Variablen:

```env
DATABASE_URL=sqlite+aiosqlite:///./jobhunter.db
AUTH_ENABLED=false
JWT_SECRET=change-me
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Start mit Docker

```bash
docker compose up --build
```

Danach erreichbar:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API-Doku: `http://localhost:8000/docs`

## OpenDyslexic Font

Für das Legasthenie-Theme müssen die Font-Dateien lokal im Frontend liegen.

Pfad:

```bash
frontend/public/fonts/OpenDyslexic/
```

Beispiel-Dateien:

- `OpenDyslexic-Regular.woff2`
- `OpenDyslexic-Bold.woff2`
- `OpenDyslexic-Italic.woff2`

## Migrationen

Alembic wird beim Start automatisch ausgeführt:

```bash
alembic upgrade head
```

## Erster Test

1. App öffnen
2. Einstellungen prüfen
3. Test-Stellensuche starten
4. Bewerbung ins Kanban übernehmen
5. Anschreiben generieren
