# ⚙️ JobHunter – Setup Guide / Einrichtung

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

### Prerequisites
- Docker & Docker Compose
- Ollama (for AI features): https://ollama.com

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter

# 2. Configure environment variables
cp .env.example .env
# Generate ENCRYPTION_KEY:
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# 3. Load Ollama model (once)
ollama pull mistral

# 4. Start
docker compose up -d

# 5. Open browser
open http://localhost:3000
```

### Environment Variables (`.env`)

| Variable | Description | Example |
|---|---|---|
| `ENCRYPTION_KEY` | AES key for API keys (required) | `base64-string` |
| `POSTGRES_PASSWORD` | Database password | `secure-password` |
| `OLLAMA_BASE_URL` | Ollama address | `http://ollama:11434` |
| `SECRET_KEY` | FastAPI JWT secret (optional) | `random-string` |

### Ports

| Port | Service |
|---|---|
| 3000 | Frontend (React) |
| 8000 | Backend API (FastAPI) |
| 11434 | Ollama |
| 5432 | PostgreSQL (internal) |

### Backup

```bash
# Database backup
docker compose exec db pg_dump -U jobhunter jobhunter > backup.sql

# Backup uploads
docker cp jobhunter_backend_1:/app/uploads ./uploads_backup
```

### Ollama Models

```bash
ollama pull mistral      # Fast, good for German
ollama pull llama3       # Very good, more RAM
ollama pull phi3         # Compact, for weaker hardware
```

---
---

## Deutsch

### Voraussetzungen
- Docker & Docker Compose
- Ollama (für KI-Funktionen): https://ollama.com

### Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter

# 2. Umgebungsvariablen konfigurieren
cp .env.example .env
# ENCRYPTION_KEY generieren:
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# 3. Ollama-Modell laden (einmalig)
ollama pull mistral

# 4. Starten
docker compose up -d

# 5. Browser öffnen
open http://localhost:3000
```

### Umgebungsvariablen (`.env`)

| Variable | Beschreibung | Beispiel |
|---|---|---|
| `ENCRYPTION_KEY` | AES-Schlüssel für API-Keys (Pflicht) | `base64-string` |
| `POSTGRES_PASSWORD` | Datenbankpasswort | `sicheres-passwort` |
| `OLLAMA_BASE_URL` | Ollama-Adresse | `http://ollama:11434` |
| `SECRET_KEY` | FastAPI JWT-Secret (optional) | `zufälliger-string` |

### Ports

| Port | Dienst |
|---|---|
| 3000 | Frontend (React) |
| 8000 | Backend API (FastAPI) |
| 11434 | Ollama |
| 5432 | PostgreSQL (intern) |

### Daten sichern

```bash
docker compose exec db pg_dump -U jobhunter jobhunter > backup.sql
docker cp jobhunter_backend_1:/app/uploads ./uploads_backup
```

### Ollama-Modelle

```bash
ollama pull mistral      # Schnell, gut für Deutsch
ollama pull llama3       # Sehr gut, mehr RAM
ollama pull phi3         # Kompakt, für schwächere Hardware
```
