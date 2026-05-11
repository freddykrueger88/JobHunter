# 🛠️ JobHunter – Installation Guide / Installationsanleitung

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

> **Complete, step-by-step guide** for local installation on Linux, macOS and Windows (WSL2).

### Table of Contents

1. [Check Prerequisites](#1-check-prerequisites)
2. [Clone Repository](#2-clone-repository)
3. [Set Up Environment Variables](#3-set-up-environment-variables)
4. [Installation – Option A: Docker (recommended)](#4-installation--option-a-docker-recommended)
5. [Installation – Option B: Manual without Docker](#5-installation--option-b-manual-without-docker)
6. [Install AI Model (Mistral)](#6-install-ai-model-mistral)
7. [Initialize Database](#7-initialize-database)
8. [First Start & Verification](#8-first-start--verification)
9. [Set Up Optional API Keys](#9-set-up-optional-api-keys)
10. [Apply Updates](#10-apply-updates)
11. [Troubleshooting](#11-troubleshooting)

---

### 1. Check Prerequisites

#### Option A – Docker (recommended)

| Software | Min. Version | Check Command |
|---|---|---|
| Docker Engine | 24.x | `docker --version` |
| Docker Compose | 2.x (Plugin) | `docker compose version` |
| Git | any | `git --version` |

> **Windows users:** Install Docker Desktop and enable WSL2 integration.
> **Linux users:** Run Docker without `sudo` – add your user to the `docker` group:
> ```bash
> sudo usermod -aG docker $USER
> newgrp docker
> ```

#### Option B – Manual

| Software | Min. Version | Check Command |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |
| PostgreSQL | 15+ | `psql --version` |
| Git | any | `git --version` |
| Ollama | current | `ollama --version` |

---

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
```

---

### 3. Set Up Environment Variables

#### Step 1 – Copy template

```bash
cp .env.example .env
```

#### Step 2 – Open and fill `.env`

```bash
nano .env
# or: code .env / vim .env
```

#### Step 3 – Generate secure keys

**SECRET_KEY** – random 64-character string:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**ENCRYPTION_KEY** – Fernet key for API key encryption:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
> If `cryptography` is not installed: `pip install cryptography`

**DB_PASSWORD** – any secure password, e.g.:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

> ⚠️ **Important:** Never commit the `.env` file to Git. It is already listed in `.gitignore`.

---

### 4. Installation – Option A: Docker (recommended)

#### Step 1 – Build and start all containers

```bash
docker compose up --build -d
```

> On first run, all Docker images will be downloaded and built. This takes **5–15 minutes** depending on your connection.

#### Step 2 – Watch progress

```bash
docker compose logs -f
```

Press `Ctrl + C` to exit the log view without stopping the containers.

#### Step 3 – Check status

```bash
docker compose ps
```

All 4 services must show `running`:

```
NAME                    STATUS
jobhunter-backend       running
jobhunter-frontend      running
jobhunter-db            running (healthy)
jobhunter-ollama        running
```

#### Services & Ports

| Service | Address | Description |
|---|---|---|
| Frontend | http://localhost:3000 | Main UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Ollama | http://localhost:11434 | AI endpoint |

---

### 5. Installation – Option B: Manual without Docker

#### 5a – Create PostgreSQL database

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:
```sql
CREATE USER jobhunter WITH PASSWORD 'your_password_from_env';
CREATE DATABASE jobhunter OWNER jobhunter;
GRANT ALL PRIVILEGES ON DATABASE jobhunter TO jobhunter;
\q
```

#### 5b – Set up backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
cd ..
```

Update `DATABASE_URL` in `.env` for direct connection:
```env
DATABASE_URL=postgresql+asyncpg://jobhunter:your_password@localhost:5432/jobhunter
OLLAMA_BASE_URL=http://localhost:11434
```

#### 5c – Set up frontend

```bash
cd frontend
npm install
cd ..
```

#### 5d – Start manually

**Terminal 1 – Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 – Frontend:**
```bash
cd frontend
npm run dev
```

---

### 6. Install AI Model (Mistral)

The AI model needs to be downloaded once. It is approx. **4.1 GB**.

#### Option A – With Docker

```bash
docker exec -it jobhunter-ollama ollama pull mistral
```

#### Option B – Manual

```bash
ollama pull mistral
```

#### Verify installation

```bash
curl http://localhost:11434/api/tags
```

Expected output (shortened):
```json
{"models":[{"name":"mistral:latest", ...}]}
```

#### Quick test

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Say hello briefly",
  "stream": false
}'
```

If `"response":"..."` is returned – everything is working. ✅

#### Alternative model: llama3

```bash
# Docker:
docker exec -it jobhunter-ollama ollama pull llama3
# Manual:
ollama pull llama3
```

---

### 7. Initialize Database

Tables are created **automatically** on first backend start (Alembic migrations).

Manually if needed:

```bash
# Docker:
docker exec -it jobhunter-backend alembic upgrade head
# Manual:
cd backend && source .venv/bin/activate && alembic upgrade head
```

---

### 8. First Start & Verification

```
☐  http://localhost:3000        →  JobHunter UI loads
☐  http://localhost:8000/docs   →  Swagger API docs show all routes
☐  http://localhost:11434/api/tags  →  mistral:latest in list
☐  Settings → 🤖 AI → Model set to "mistral" & saved
☐  Dashboard → no error banner
```

---

### 9. Set Up Optional API Keys

The app works without external keys. The following portals enable extended job search:

| Portal | Get Key | Function |
|---|---|---|
| **Adzuna** | https://developer.adzuna.com/ | Millions of job listings worldwide |
| **Bundesagentur für Arbeit** | https://jobsuche.api.bund.dev/ | German job listings |
| **LinkedIn** | https://developer.linkedin.com/ | LinkedIn jobs |

Enter keys in the app: **Settings → 🔑 API Keys**

All keys are stored **AES-256 encrypted** in the database.

---

### 10. Apply Updates

#### Docker

```bash
git pull origin main
docker compose up --build -d
docker exec -it jobhunter-backend alembic upgrade head
```

#### Manual

```bash
git pull origin main
cd backend && source .venv/bin/activate && pip install -r requirements.txt && alembic upgrade head && cd ..
cd frontend && npm install && cd ..
# Restart services
```

---

### 11. Troubleshooting

#### ❌ Port already in use

```bash
sudo lsof -i :3000
sudo lsof -i :8000
sudo kill -9 <PID>
```

#### ❌ Frontend loads but API errors (CORS / 502)

```bash
docker compose logs backend
curl http://localhost:8000/
```

#### ❌ Ollama not responding (`connection refused`)

```bash
docker compose ps
docker compose logs ollama
docker compose restart ollama
```

#### ❌ Mistral model missing (`model not found`)

```bash
docker exec -it jobhunter-ollama ollama pull mistral
```

#### ❌ Database error on startup

```bash
docker compose logs db
docker compose restart db
docker compose restart backend
```

#### ❌ `.env` changes not taking effect

```bash
docker compose up --build -d
```

#### ❌ Full reset (⚠️ deletes all data)

```bash
docker compose down -v
docker compose up --build -d
```

#### ❌ Not enough RAM for Mistral (needs 8 GB+)

```bash
docker exec -it jobhunter-ollama ollama pull phi3       # 3.8 GB
docker exec -it jobhunter-ollama ollama pull tinyllama  # 1.1 GB
```

#### System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Disk | 10 GB free | 20 GB free |
| GPU | not required | NVIDIA (CUDA) for fast AI |
| OS | Linux / macOS / Windows WSL2 | Linux |

> Questions or problems? Open a [GitHub Issue](https://github.com/freddykrueger88/JobHunter/issues).

---
---

## Deutsch

> **Vollständige, kleinschrittige Anleitung** für die lokale Installation auf Linux, macOS und Windows (WSL2).

### Inhaltsverzeichnis

1. [Voraussetzungen prüfen](#1-voraussetzungen-prüfen)
2. [Repository klonen](#2-repository-klonen)
3. [Umgebungsvariablen einrichten](#3-umgebungsvariablen-einrichten)
4. [Installation – Weg A: Docker (empfohlen)](#4-installation--weg-a-docker-empfohlen)
5. [Installation – Weg B: Manuell ohne Docker](#5-installation--weg-b-manuell-ohne-docker)
6. [KI-Modell (Mistral) installieren](#6-ki-modell-mistral-installieren)
7. [Datenbank initialisieren](#7-datenbank-initialisieren)
8. [Erster Start & Prüfung](#8-erster-start--prüfung)
9. [Optionale API-Keys einrichten](#9-optionale-api-keys-einrichten)
10. [Updates einspielen](#10-updates-einspielen)
11. [Troubleshooting](#11-troubleshooting-1)

---

### 1. Voraussetzungen prüfen

#### Weg A – Docker (empfohlen)

| Software | Mindestversion | Prüfbefehl |
|---|---|---|
| Docker Engine | 24.x | `docker --version` |
| Docker Compose | 2.x (Plugin) | `docker compose version` |
| Git | beliebig | `git --version` |

> **Windows-Nutzer:** Docker Desktop installieren und WSL2-Integration aktivieren.
> **Linux-Nutzer:** Docker ohne `sudo` ausführen:
> ```bash
> sudo usermod -aG docker $USER
> newgrp docker
> ```

#### Weg B – Manuell

| Software | Mindestversion | Prüfbefehl |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |
| PostgreSQL | 15+ | `psql --version` |
| Git | beliebig | `git --version` |
| Ollama | aktuell | `ollama --version` |

---

### 2. Repository klonen

```bash
cd ~
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
```

---

### 3. Umgebungsvariablen einrichten

#### Schritt 1 – Vorlage kopieren

```bash
cp .env.example .env
```

#### Schritt 2 – `.env` öffnen und befüllen

```bash
nano .env
```

#### Schritt 3 – Sichere Schlüssel generieren

```bash
# SECRET_KEY:
python3 -c "import secrets; print(secrets.token_hex(32))"
# ENCRYPTION_KEY:
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# DB_PASSWORD:
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

> ⚠️ Die `.env`-Datei niemals ins Git committen. Sie ist bereits in `.gitignore`.

---

### 4. Installation – Weg A: Docker (empfohlen)

```bash
docker compose up --build -d
docker compose logs -f
docker compose ps
```

#### Dienste & Ports

| Dienst | Adresse | Beschreibung |
|---|---|---|
| Frontend | http://localhost:3000 | Haupt-Oberfläche |
| Backend API | http://localhost:8000 | REST-API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Ollama | http://localhost:11434 | KI-Endpunkt |

---

### 5. Installation – Weg B: Manuell ohne Docker

```bash
# PostgreSQL-Shell:
sudo -u postgres psql
```
```sql
CREATE USER jobhunter WITH PASSWORD 'dein_passwort';
CREATE DATABASE jobhunter OWNER jobhunter;
GRANT ALL PRIVILEGES ON DATABASE jobhunter TO jobhunter;
\q
```
```bash
# Backend:
cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cd ..
# Frontend:
cd frontend && npm install && cd ..
```

---

### 6. KI-Modell (Mistral) installieren

```bash
# Docker:
docker exec -it jobhunter-ollama ollama pull mistral
# Manuell:
ollama pull mistral
```

---

### 7. Datenbank initialisieren

```bash
# Docker:
docker exec -it jobhunter-backend alembic upgrade head
# Manuell:
cd backend && source .venv/bin/activate && alembic upgrade head
```

---

### 8. Erster Start & Prüfung

```
☐  http://localhost:3000        →  JobHunter-Oberfläche lädt
☐  http://localhost:8000/docs   →  Swagger API-Docs zeigen alle Routen
☐  http://localhost:11434/api/tags  →  mistral:latest in der Liste
☐  Einstellungen → 🤖 KI → Modell auf "mistral" gesetzt & gespeichert
☐  Dashboard → kein Fehler-Banner
```

---

### 9. Optionale API-Keys einrichten

| Portal | Key holen | Funktion |
|---|---|---|
| **Adzuna** | https://developer.adzuna.com/ | Millionen Stellenanzeigen |
| **Bundesagentur für Arbeit** | https://jobsuche.api.bund.dev/ | Deutsche Stellen |
| **LinkedIn** | https://developer.linkedin.com/ | LinkedIn-Jobs |

Eintragen unter: **Einstellungen → 🔑 API Keys**

---

### 10. Updates einspielen

```bash
git pull origin main
docker compose up --build -d
docker exec -it jobhunter-backend alembic upgrade head
```

---

### 11. Troubleshooting

#### ❌ Port bereits belegt
```bash
sudo lsof -i :3000 && sudo kill -9 <PID>
```

#### ❌ Ollama antwortet nicht
```bash
docker compose restart ollama
```

#### ❌ Mistral fehlt
```bash
docker exec -it jobhunter-ollama ollama pull mistral
```

#### ❌ Alles zurücksetzen (⚠️ löscht alle Daten)
```bash
docker compose down -v && docker compose up --build -d
```

#### Systemanforderungen

| Komponente | Minimum | Empfohlen |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 Kerne | 8 Kerne |
| Festplatte | 10 GB frei | 20 GB frei |
| GPU | nicht nötig | NVIDIA (CUDA) |
| OS | Linux / macOS / Windows WSL2 | Linux |

> Fragen oder Probleme? [GitHub Issue erstellen](https://github.com/freddykrueger88/JobHunter/issues)
