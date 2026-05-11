# ❓ FAQ & Schnellhilfe

Häufige Probleme und Lösungen beim Einrichten und Betreiben von JobHunter.

---

## 🚀 Installation & Start

### `ModuleNotFoundError: No module named 'cryptography'`

Das Python-Paket `cryptography` ist nicht system-weit installiert. Lösung: Den ENCRYPTION_KEY direkt aus dem Backend-Container generieren:

```bash
docker compose run --rm backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Alternativ systemweit installieren:

```bash
pip3 install cryptography
```

---

### `Bind for 0.0.0.0:3000 failed: port is already allocated`

Ein anderer Container oder Prozess belegt Port 3000. Prüfen:

```bash
docker ps
ss -tlnp | grep :3000
```

**Option A** – anderen Container stoppen:
```bash
docker stop <container-name>
docker compose up -d
```

**Option B** – JobHunter auf anderem Port starten, in `docker-compose.yml`:
```yaml
# frontend:
#   ports:
#     - "3001:3000"   ← statt 3000:3000
```
→ Dann erreichbar unter **http://localhost:3001**

---

### Frontend startet nicht / `Restarting`-Schleife

Prüfe die Logs:
```bash
docker logs jobhunter-frontend --tail 50
```

**Häufigste Ursache: fehlendes npm-Paket** (z.B. `Cannot find module 'vite-plugin-pwa'`)

Das passiert wenn das `node_modules`-Volume-Mount den Container-Inhalt überschreibt. Lösung: Image neu bauen:

```bash
docker compose down
docker compose build --no-cache frontend
docker compose up -d
```

---

### Alle Container stoppen und sauber neu starten

```bash
docker compose down
docker compose up -d
```

Mit komplettem Rebuild (z.B. nach Code-Änderungen):
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 🤖 Ollama / KI

### KI-Modell laden (nach dem ersten Start)

Ollama läuft als Docker-Container. Das Modell muss **in den Container** geladen werden:

```bash
docker exec jobhunter-ollama ollama pull mistral
```

Andere empfohlene Modelle:
```bash
docker exec jobhunter-ollama ollama pull llama3
docker exec jobhunter-ollama ollama pull phi3
```

### KI antwortet nicht / Timeout

1. Prüfen ob Ollama läuft: `docker ps | grep ollama`
2. Modell geladen? `docker exec jobhunter-ollama ollama list`
3. Logs prüfen: `docker logs jobhunter-ollama --tail 30`
4. Ollama neu starten: `docker restart jobhunter-ollama`

### GPU-Unterstützung aktivieren (NVIDIA)

In `docker-compose.yml` den `deploy`-Block unter `ollama` auskommentieren:

```yaml
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1
#           capabilities: [gpu]
```

→ Dann `docker compose up -d` erneut ausführen.

---

## 🔒 Konfiguration

### Welche Werte müssen in `.env` gesetzt werden?

| Variable | Beschreibung | Generieren mit |
|---|---|---|
| `DB_PASSWORD` | PostgreSQL-Passwort | `python3 -c "import secrets; print(secrets.token_hex(16))"` |
| `SECRET_KEY` | JWT-Signing-Key | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | Fernet-Key für API-Keys | `docker compose run --rm backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `OLLAMA_BASE_URL` | Ollama-Adresse | Standard: `http://ollama:11434` (nicht ändern bei Docker) |

### Backend startet nicht wegen Datenbankfehler

Die Datenbank braucht beim ersten Start etwas länger. Der Backend-Container wartet automatisch bis PostgreSQL `healthy` ist. Falls trotzdem Fehler:

```bash
docker logs jobhunter-backend --tail 30
docker logs jobhunter-db --tail 20
```

---

## 📊 Daten & Backup

### Wo werden die Daten gespeichert?

Alle Daten liegen in Docker-Volumes auf deinem Rechner:
- `pgdata` – PostgreSQL-Datenbank
- `ollama-data` – KI-Modelle
- `uploads` – hochgeladene Dateien (Lebensläufe, Fotos)

### Datenbank-Volumes löschen (kompletter Reset)

```bash
docker compose down -v
```
⚠️ **Achtung:** Löscht alle gespeicherten Bewerbungen und Einstellungen.

### Backup erstellen

JobHunter sichert täglich automatisch alle Daten als `.json.gz` im Container. Manuelles Backup auslösen:

```bash
docker exec jobhunter-backend python -c "from services.backup import run_backup; import asyncio; asyncio.run(run_backup())"
```

---

## 🔄 Updates

### JobHunter auf neue Version aktualisieren

```bash
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

*Weiteres Problem nicht dabei? → [Issue erstellen](https://github.com/freddykrueger88/JobHunter/issues/new)*
