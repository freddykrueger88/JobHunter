# 🚀 Installation

JobHunter wird per Docker Compose gestartet. Alle Dienste (Backend, Frontend, Datenbank, Ollama) laufen in Containern.

## Voraussetzungen

| Tool | Mindestversion | Prüfen mit |
|---|---|---|
| Docker | 24.x | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |
| Python 3 | 3.10+ | `python3 --version` |
| Git | beliebig | `git --version` |

> **GPU-Beschleunigung (NVIDIA):** Im `docker-compose.yml` den `deploy`-Block unter dem `ollama`-Service auskommentieren.

## Schritt-für-Schritt

### 1. Repository klonen

```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
```

### 2. `.env`-Datei erstellen

```bash
cp .env.example .env
```

Die drei Pflichtfelder mit eigenen sicheren Werten befüllen:

```bash
# DB_PASSWORD – beliebiger sicherer String:
python3 -c "import secrets; print(secrets.token_hex(16))"

# SECRET_KEY – für JWT-Signaturen:
python3 -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY – muss ein gültiger Fernet-Key sein:
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Die generierten Werte in der `.env` eintragen:

```env
DB_PASSWORD=<generierter Wert>
SECRET_KEY=<generierter Wert>
ENCRYPTION_KEY=<generierter Fernet-Key>

# Optional:
AUTH_ENABLED=false
OLLAMA_BASE_URL=http://ollama:11434
```

### 3. Container starten

```bash
docker compose up -d
```

Beim ersten Start werden alle Images gebaut und die Datenbank migriert (Alembic läuft automatisch).

### 4. KI-Modell laden

```bash
# Mistral (empfohlen, ~4 GB):
docker exec jobhunter-ollama ollama pull mistral

# Alternativen:
docker exec jobhunter-ollama ollama pull llama3
docker exec jobhunter-ollama ollama pull phi3
```

### 5. App öffnen

| Dienst | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API-Docs (Swagger) | http://localhost:8000/docs |

## Erster Start – Checkliste

- [ ] App öffnt sich unter `http://localhost:3000`
- [ ] Einstellungen → KI-Modell auswählen
- [ ] Test-Stellensuche starten
- [ ] Bewerbung ins Kanban übernehmen
- [ ] Anschreiben generieren

## Legasthenie-Theme (OpenDyslexic)

Die Font-Dateien müssen manuell abgelegt werden:

```
frontend/public/fonts/OpenDyslexic/
├── OpenDyslexic-Regular.woff2
├── OpenDyslexic-Bold.woff2
└── OpenDyslexic-Italic.woff2
```

## Update

```bash
git pull
docker compose up -d --build
```

Alembic-Migrationen laufen beim Start automatisch.

## Häufige Probleme

| Problem | Lösung |
|---|---|
| Port 3000 / 8000 belegt | Ports in `docker-compose.yml` anpassen |
| Ollama antwortet nicht | `docker exec jobhunter-ollama ollama list` prüfen |
| `ENCRYPTION_KEY` ungültig | Muss ein Fernet-Key sein (44 Zeichen, Base64) |
| Datenbank-Fehler beim Start | `docker compose down -v` → neu starten (löscht alle Daten!) |
| Anschreiben-Generierung schlägt fehl | KI-Modell in den Einstellungen auswählen |

> Ausführliche Anleitung: [INSTALL.md](https://github.com/freddykrueger88/JobHunter/blob/main/INSTALL.md)
