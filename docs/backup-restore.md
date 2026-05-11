# 💾 Backup & Restore

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter stores all data locally. Regular backups protect against accidental data loss.

## What Is Stored Where

| Data | Storage location | Docker Volume |
|---|---|---|
| Applications, jobs, settings | PostgreSQL | `pgdata` |
| Uploaded CVs, photos | File system | `uploads` |
| AI models (Mistral, etc.) | Ollama | `ollama-data` |
| Themes, language settings | Browser localStorage | – (per browser) |

> AI models do **not** need to be backed up – they can be re-downloaded at any time.

---

## Automatic Backup (built-in)

JobHunter creates a compressed backup automatically every day:

```bash
# View backup logs:
docker logs jobhunter-backend | grep backup

# Backup files location (in container):
docker exec jobhunter-backend ls -lh /app/backups/

# Copy backup to host:
docker cp jobhunter-backend:/app/backups/ ./jobhunter-backups/
```

Backups are kept for **7 days**, then automatically deleted.

> ⚠️ API keys are **not** included in automatic backups for security reasons.

---

## Manual Backup

### Option A – Full backup via app
```bash
docker exec jobhunter-backend python -c \
  "from services.backup import run_backup; import asyncio; asyncio.run(run_backup())"
```

### Option B – PostgreSQL dump
```bash
docker compose exec db pg_dump -U jobhunter jobhunter > backup_$(date +%Y%m%d).sql
```

### Option C – Complete Docker volumes
```bash
# Stop containers first:
docker compose down

# Copy volumes:
docker run --rm -v jobhunter_pgdata:/data -v $(pwd):/backup alpine \
  tar czf /backup/pgdata_$(date +%Y%m%d).tar.gz /data

docker run --rm -v jobhunter_uploads:/data -v $(pwd):/backup alpine \
  tar czf /backup/uploads_$(date +%Y%m%d).tar.gz /data

# Restart:
docker compose up -d
```

---

## Restore

### Restore from PostgreSQL dump
```bash
# Start only the database:
docker compose up -d db

# Import dump:
docker compose exec -T db psql -U jobhunter jobhunter < backup_20260511.sql

# Start all services:
docker compose up -d
```

### Restore from volume archive
```bash
# Stop containers:
docker compose down

# Delete old volume:
docker volume rm jobhunter_pgdata

# Create new volume and restore:
docker run --rm -v jobhunter_pgdata:/data -v $(pwd):/backup alpine \
  tar xzf /backup/pgdata_20260511.tar.gz -C /

# Start:
docker compose up -d
```

---

## Backup Strategy (recommendation)

| Frequency | Method | Storage location |
|---|---|---|
| Daily | Automatic backup (built-in) | Local in container |
| Weekly | Manual SQL dump | External hard drive / NAS |
| Before updates | Manual SQL dump | Local + external |
| Before full resets | Complete volume archive | External hard drive |

---

## Migrate to New Machine

```bash
# On old machine:
docker compose down
docker run --rm -v jobhunter_pgdata:/data -v $(pwd):/backup alpine \
  tar czf /backup/pgdata_migration.tar.gz /data
docker run --rm -v jobhunter_uploads:/data -v $(pwd):/backup alpine \
  tar czf /backup/uploads_migration.tar.gz /data

# Transfer pgdata_migration.tar.gz and uploads_migration.tar.gz to new machine

# On new machine (after fresh installation):
docker compose down
docker volume rm jobhunter_pgdata jobhunter_uploads
docker run --rm -v jobhunter_pgdata:/data -v $(pwd):/backup alpine \
  tar xzf /backup/pgdata_migration.tar.gz -C /
docker run --rm -v jobhunter_uploads:/data -v $(pwd):/backup alpine \
  tar xzf /backup/uploads_migration.tar.gz -C /
docker compose up -d
```

---
---

## Deutsch

JobHunter speichert alle Daten lokal. Regelmäßige Backups schützen vor versehentlichem Datenverlust.

## Was wo gespeichert wird

| Daten | Speicherort | Docker-Volume |
|---|---|---|
| Bewerbungen, Jobs, Einstellungen | PostgreSQL | `pgdata` |
| Hochgeladene Lebenslaeufe, Fotos | Dateisystem | `uploads` |
| KI-Modelle (Mistral etc.) | Ollama | `ollama-data` |
| Theme, Spracheinstellungen | Browser-localStorage | – (pro Browser) |

> KI-Modelle müssen **nicht** gesichert werden – sie können jederzeit neu heruntergeladen werden.

---

## Automatisches Backup (eingebaut)

JobHunter erstellt täglich automatisch ein komprimiertes Backup:

```bash
# Backup-Logs ansehen:
docker logs jobhunter-backend | grep backup

# Backup-Dateien im Container:
docker exec jobhunter-backend ls -lh /app/backups/

# Backup auf den Host kopieren:
docker cp jobhunter-backend:/app/backups/ ./jobhunter-backups/
```

Backups werden **7 Tage** aufbewahrt, dann automatisch gelöscht.

> ⚠️ API-Keys werden aus Sicherheitsgründen **nicht** in automatischen Backups gesichert.

---

## Manuelles Backup

### Option A – Vollbackup über die App
```bash
docker exec jobhunter-backend python -c \
  "from services.backup import run_backup; import asyncio; asyncio.run(run_backup())"
```

### Option B – PostgreSQL-Dump
```bash
docker compose exec db pg_dump -U jobhunter jobhunter > backup_$(date +%Y%m%d).sql
```

### Option C – Komplette Docker-Volumes
```bash
docker compose down
docker run --rm -v jobhunter_pgdata:/data -v $(pwd):/backup alpine \
  tar czf /backup/pgdata_$(date +%Y%m%d).tar.gz /data
docker run --rm -v jobhunter_uploads:/data -v $(pwd):/backup alpine \
  tar czf /backup/uploads_$(date +%Y%m%d).tar.gz /data
docker compose up -d
```

---

## Wiederherstellen

### Aus PostgreSQL-Dump
```bash
docker compose up -d db
docker compose exec -T db psql -U jobhunter jobhunter < backup_20260511.sql
docker compose up -d
```

### Aus Volume-Archiv
```bash
docker compose down
docker volume rm jobhunter_pgdata
docker run --rm -v jobhunter_pgdata:/data -v $(pwd):/backup alpine \
  tar xzf /backup/pgdata_20260511.tar.gz -C /
docker compose up -d
```

---

## Auf neuen Rechner umziehen

```bash
# Auf altem Rechner: Volumes sichern (s.o. Option C)
# Dateien übertragen
# Auf neuem Rechner: Docker-Installation + Volumes einspielen (s.o. aus Volume-Archiv)
```
