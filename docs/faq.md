# ❓ FAQ & Quick Help / Schnellhilfe

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

Common problems and solutions when setting up and running JobHunter.

---

### 🚀 Installation & Start

#### `ModuleNotFoundError: No module named 'cryptography'`

```bash
docker compose run --rm backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# or install globally:
pip3 install cryptography
```

---

#### `Bind for 0.0.0.0:3000 failed: port is already allocated`

```bash
docker ps
ss -tlnp | grep :3000
```

**Option A** – Stop other container:
```bash
docker stop <container-name>
docker compose up -d
```

**Option B** – Use different port in `docker-compose.yml`:
```yaml
# ports:
#   - "3001:3000"
```
→ Then available at **http://localhost:3001**

---

#### Frontend not starting / `Restarting` loop

```bash
docker logs jobhunter-frontend --tail 50
```

Most common cause: missing npm package. Fix:
```bash
docker compose down
docker compose build --no-cache frontend
docker compose up -d
```

---

#### Stop all containers and restart cleanly

```bash
docker compose down
docker compose up -d
# With full rebuild:
docker compose down && docker compose build --no-cache && docker compose up -d
```

---

### 🤖 Ollama / AI

#### Load AI model (after first start)

```bash
docker exec jobhunter-ollama ollama pull mistral
# Other recommended models:
docker exec jobhunter-ollama ollama pull llama3
docker exec jobhunter-ollama ollama pull phi3
```

#### AI not responding / Timeout

1. Check if Ollama is running: `docker ps | grep ollama`
2. Model loaded? `docker exec jobhunter-ollama ollama list`
3. Check logs: `docker logs jobhunter-ollama --tail 30`
4. Restart: `docker restart jobhunter-ollama`

#### Enable GPU support (NVIDIA)

Uncomment `deploy` block under `ollama` in `docker-compose.yml`, then `docker compose up -d`.

---

### 🔒 Configuration

#### Which values must be set in `.env`?

| Variable | Description | Generate with |
|---|---|---|
| `DB_PASSWORD` | PostgreSQL password | `python3 -c "import secrets; print(secrets.token_hex(16))"` |
| `SECRET_KEY` | JWT signing key | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | Fernet key for API keys | `docker compose run --rm backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `OLLAMA_BASE_URL` | Ollama address | Default: `http://ollama:11434` (don't change with Docker) |

---

### 📊 Data & Backup

#### Where is data stored?

All data lives in Docker volumes on your machine:
- `pgdata` – PostgreSQL database
- `ollama-data` – AI models
- `uploads` – uploaded files (CVs, photos)

#### Delete database volumes (full reset)

```bash
docker compose down -v
```
⚠️ **Warning:** Deletes all saved applications and settings.

#### Create backup

```bash
docker exec jobhunter-backend python -c "from services.backup import run_backup; import asyncio; asyncio.run(run_backup())"
```

---

### 🔄 Updates

```bash
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

*Problem not listed? → [Create an Issue](https://github.com/freddykrueger88/JobHunter/issues/new)*

---
---

## Deutsch

Häufige Probleme und Lösungen beim Einrichten und Betreiben von JobHunter.

---

### 🚀 Installation & Start

#### `ModuleNotFoundError: No module named 'cryptography'`

```bash
docker compose run --rm backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# oder systemweit:
pip3 install cryptography
```

---

#### `Bind for 0.0.0.0:3000 failed: port is already allocated`

```bash
docker ps
ss -tlnp | grep :3000
```

**Option A** – anderen Container stoppen:
```bash
docker stop <container-name> && docker compose up -d
```

**Option B** – anderen Port in `docker-compose.yml` setzen:
```yaml
# ports:
#   - "3001:3000"
```

---

#### Frontend startet nicht / `Restarting`-Schleife

```bash
docker logs jobhunter-frontend --tail 50
docker compose down && docker compose build --no-cache frontend && docker compose up -d
```

---

### 🤖 Ollama / KI

#### KI-Modell laden

```bash
docker exec jobhunter-ollama ollama pull mistral
docker exec jobhunter-ollama ollama pull llama3
docker exec jobhunter-ollama ollama pull phi3
```

#### KI antwortet nicht

1. `docker ps | grep ollama`
2. `docker exec jobhunter-ollama ollama list`
3. `docker logs jobhunter-ollama --tail 30`
4. `docker restart jobhunter-ollama`

---

### 🔒 Konfiguration

| Variable | Beschreibung | Generieren mit |
|---|---|---|
| `DB_PASSWORD` | PostgreSQL-Passwort | `python3 -c "import secrets; print(secrets.token_hex(16))"` |
| `SECRET_KEY` | JWT-Signing-Key | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | Fernet-Key | `docker compose run --rm backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `OLLAMA_BASE_URL` | Ollama-Adresse | Standard: `http://ollama:11434` |

---

### 📊 Daten & Backup

- Daten in Docker-Volumes: `pgdata`, `ollama-data`, `uploads`
- Manuelles Backup: `docker exec jobhunter-backend python -c "from services.backup import run_backup; import asyncio; asyncio.run(run_backup())"`
- Alles zurücksetzen: `docker compose down -v` ⚠️

---

### 🔄 Updates

```bash
git pull origin main && docker compose down && docker compose build --no-cache && docker compose up -d
```

---

*Weiteres Problem nicht dabei? → [Issue erstellen](https://github.com/freddykrueger88/JobHunter/issues/new)*
