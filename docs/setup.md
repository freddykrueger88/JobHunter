# JobHunter – Einrichtung

## Voraussetzungen
- Docker & Docker Compose
- Ollama (für KI-Funktionen): https://ollama.com

## Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter

# 2. Umgebungsvariablen konfigurieren
cp .env.example .env
# → .env öffnen und ENCRYPTION_KEY setzen (32 zufällige Bytes, base64)
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# 3. Ollama-Modell laden (einmalig)
ollama pull mistral

# 4. Starten
docker compose up -d

# 5. Browser öffnen
open http://localhost:3000
```

## Umgebungsvariablen (`.env`)

| Variable | Beschreibung | Beispiel |
|---|---|---|
| `ENCRYPTION_KEY` | AES-Schlüssel für API-Keys (Pflicht) | `base64-string` |
| `POSTGRES_PASSWORD` | Datenbankpasswort | `sicheres-passwort` |
| `OLLAMA_BASE_URL` | Ollama-Adresse | `http://ollama:11434` |
| `SECRET_KEY` | FastAPI JWT-Secret (optional) | `zufälliger-string` |

## Ports

| Port | Dienst |
|---|---|
| 3000 | Frontend (React) |
| 8000 | Backend API (FastAPI) |
| 11434 | Ollama |
| 5432 | PostgreSQL (intern) |

## Daten sichern

```bash
# Datenbank-Backup
docker compose exec db pg_dump -U jobhunter jobhunter > backup.sql

# Uploads sichern
docker cp jobhunter_backend_1:/app/uploads ./uploads_backup
```

## Ollama-Modelle

Empfohlen für Anschreiben-Generierung:
```bash
ollama pull mistral      # Schnell, gut für Deutsch
ollama pull llama3       # Sehr gut, mehr RAM
ollama pull phi3         # Kompakt, für schwächere Hardware
```
