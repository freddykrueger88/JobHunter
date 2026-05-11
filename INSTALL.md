# 🛠️ JobHunter – Installationsanleitung

> **Vollständige, kleinschrittige Anleitung** für die lokale Installation auf Linux, macOS und Windows (WSL2).

---

## Inhaltsverzeichnis

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
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Voraussetzungen prüfen

### Weg A – Docker (empfohlen)

| Software | Mindestversion | Prüfbefehl |
|---|---|---|
| Docker Engine | 24.x | `docker --version` |
| Docker Compose | 2.x (Plugin) | `docker compose version` |
| Git | beliebig | `git --version` |

> **Windows-Nutzer:** Docker Desktop installieren und WSL2-Integration aktivieren.  
> **Linux-Nutzer:** Docker ohne `sudo` ausführen – eigenen User zur `docker`-Gruppe hinzufügen:
> ```bash
> sudo usermod -aG docker $USER
> newgrp docker
> ```

### Weg B – Manuell

| Software | Mindestversion | Prüfbefehl |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |
| PostgreSQL | 15+ | `psql --version` |
| Git | beliebig | `git --version` |
| Ollama | aktuell | `ollama --version` |

---

## 2. Repository klonen

```bash
# In das gewünschte Verzeichnis wechseln
cd ~

# Repository klonen
git clone https://github.com/freddykrueger88/JobHunter.git

# In das Projektverzeichnis wechseln
cd JobHunter
```

---

## 3. Umgebungsvariablen einrichten

Die App benötigt eine `.env`-Datei im Stammverzeichnis. Eine Vorlage liegt bereits bei.

### Schritt 1 – Vorlage kopieren

```bash
cp .env.example .env
```

### Schritt 2 – `.env` öffnen und befüllen

```bash
nano .env
# oder: code .env / vim .env
```

Die Datei sieht so aus:

```env
# ─── Datenbank ────────────────────────────────────────────────
DB_PASSWORD=changeme_secure_password

# ─── Backend ────────────────────────────────────────────────
SECRET_KEY=changeme_very_long_random_secret_key_here
ENCRYPTION_KEY=changeme_fernet_key_here

# ─── Ollama ─────────────────────────────────────────────────
OLLAMA_BASE_URL=http://ollama:11434
```

### Schritt 3 – Sichere Schlüssel generieren

**SECRET\_KEY** – zufälliger 64-Zeichen-String:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Den ausgegebenen Wert als `SECRET_KEY=...` in die `.env` einsetzen.

**ENCRYPTION\_KEY** – Fernet-Schlüssel für API-Key-Verschlüsselung:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
> Wenn `cryptography` noch nicht installiert ist: `pip install cryptography`

Den ausgegebenen Wert als `ENCRYPTION_KEY=...` einsetzen.

**DB\_PASSWORD** – beliebig sicheres Passwort wählen, z.B.:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

> ⚠️ **Wichtig:** Die `.env`-Datei niemals ins Git committen. Sie ist bereits in `.gitignore` eingetragen.

---

## 4. Installation – Weg A: Docker (empfohlen)

Dieser Weg startet alle Dienste (Backend, Frontend, Datenbank, Ollama) automatisch.

### Schritt 1 – Alle Container bauen und starten

```bash
docker compose up --build -d
```

> Beim ersten Start werden alle Docker-Images heruntergeladen und gebaut. Das dauert je nach Internetleitung **5–15 Minuten**.

### Schritt 2 – Fortschritt beobachten

```bash
docker compose logs -f
```

Mit `Strg + C` kannst du die Log-Ansicht jederzeit verlassen, ohne die Container zu stoppen.

### Schritt 3 – Status prüfen

```bash
docker compose ps
```

Alle 4 Dienste müssen `running` zeigen:

```
NAME                    STATUS
jobhunter-backend       running
jobhunter-frontend      running
jobhunter-db            running (healthy)
jobhunter-ollama        running
```

### Dienste & Ports

| Dienst | Adresse | Beschreibung |
|---|---|---|
| Frontend | http://localhost:3000 | Haupt-Oberfläche |
| Backend API | http://localhost:8000 | REST-API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Ollama | http://localhost:11434 | KI-Endpunkt |

---

## 5. Installation – Weg B: Manuell ohne Docker

### 5a – PostgreSQL-Datenbank anlegen

```bash
# PostgreSQL-Shell öffnen
sudo -u postgres psql
```

In der PostgreSQL-Shell:
```sql
CREATE USER jobhunter WITH PASSWORD 'dein_passwort_aus_env';
CREATE DATABASE jobhunter OWNER jobhunter;
GRANT ALL PRIVILEGES ON DATABASE jobhunter TO jobhunter;
\q
```

### 5b – Backend einrichten

```bash
# In den Backend-Ordner wechseln
cd backend

# Virtuelle Python-Umgebung erstellen
python3 -m venv .venv

# Virtuelle Umgebung aktivieren
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Abhängigkeiten installieren
pip install -r requirements.txt

# Zurück ins Stammverzeichnis
cd ..
```

Die `DATABASE_URL` in der `.env` anpassen (direkte Verbindung statt Docker-intern):
```env
DATABASE_URL=postgresql+asyncpg://jobhunter:dein_passwort@localhost:5432/jobhunter
OLLAMA_BASE_URL=http://localhost:11434
```

### 5c – Frontend einrichten

```bash
# In den Frontend-Ordner wechseln
cd frontend

# Node-Abhängigkeiten installieren
npm install

# Zurück ins Stammverzeichnis
cd ..
```

### 5d – Manuell starten

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

## 6. KI-Modell (Mistral) installieren

Das KI-Modell muss einmalig heruntergeladen werden. Es ist ca. **4,1 GB** groß.

### Weg A – Mit Docker

```bash
# Mistral in den Ollama-Container laden
docker exec -it jobhunter-ollama ollama pull mistral
```

Der Download-Fortschritt wird direkt im Terminal angezeigt. Das dauert je nach Leitung **2–10 Minuten**.

### Weg B – Manuell (Ollama lokal installiert)

```bash
ollama pull mistral
```

### Installation prüfen

```bash
# Alle installierten Modelle anzeigen
curl http://localhost:11434/api/tags
```

Erwartete Ausgabe (gekürzt):
```json
{"models":[{"name":"mistral:latest", ...}]}
```

### Kurztest – Modell antwortet?

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Sag kurz Hallo",
  "stream": false
}'
```

Wenn `"response":"..."` zurückkommt – alles in Ordnung. ✅

### Alternatives Modell: llama3

Falls Mistral zu groß ist (wenig RAM), kann auch ein kleineres Modell genutzt werden:

```bash
# Docker:
docker exec -it jobhunter-ollama ollama pull llama3

# Manuell:
ollama pull llama3
```

In den Einstellungen der App unter **🤖 KI → KI-Modell** dann `llama3` auswählen.

---

## 7. Datenbank initialisieren

Die Tabellen werden beim ersten Start des Backends **automatisch** angelegt (Alembic-Migrationen).

Bei Bedarf manuell ausführen:

### Weg A – Docker

```bash
docker exec -it jobhunter-backend alembic upgrade head
```

### Weg B – Manuell

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

---

## 8. Erster Start & Prüfung

### Checkliste

```
☐  http://localhost:3000  →  JobHunter-Oberfläche lädt
☐  http://localhost:8000/docs  →  Swagger API-Docs zeigen alle Routen
☐  http://localhost:11434/api/tags  →  mistral:latest in der Liste
☐  Einstellungen → 🤖 KI → Modell auf "mistral" gesetzt & gespeichert
☐  Dashboard → kein Fehler-Banner
```

### Ersten API-Key prüfen (optional)

```bash
curl http://localhost:8000/api/settings/
```

Erwartete Antwort: JSON-Objekt mit den Standard-Einstellungen.

---

## 9. Optionale API-Keys einrichten

Die App funktioniert ohne externe Keys. Folgende Portale ermöglichen erweiterte Jobsuche:

| Portal | Key holen | Funktion |
|---|---|---|
| **Adzuna** | https://developer.adzuna.com/ | Millionen Stellenanzeigen weltweit |
| **Bundesagentur für Arbeit** | https://jobsuche.api.bund.dev/ | Deutsche Stellenanzeigen |
| **LinkedIn** | https://developer.linkedin.com/ | LinkedIn-Jobs |

Keys in der App eintragen: **Einstellungen → 🔑 API Keys**

Alle Keys werden **AES-256 verschlüsselt** in der Datenbank gespeichert.

---

## 10. Updates einspielen

### Weg A – Docker

```bash
# Neuesten Stand holen
git pull origin main

# Container neu bauen und starten
docker compose up --build -d

# Datenbank-Migrationen ausführen (falls neue dabei)
docker exec -it jobhunter-backend alembic upgrade head
```

### Weg B – Manuell

```bash
# Neuesten Stand holen
git pull origin main

# Backend-Abhängigkeiten aktualisieren
cd backend
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
cd ..

# Frontend-Abhängigkeiten aktualisieren
cd frontend
npm install
cd ..

# Dienste neu starten
```

---

## 11. Troubleshooting

### ❌ `docker compose up` schlägt fehl – Port bereits belegt

```bash
# Welcher Prozess belegt Port 3000 oder 8000?
sudo lsof -i :3000
sudo lsof -i :8000

# Prozess beenden (PID aus obigem Befehl einsetzen)
sudo kill -9 <PID>
```

### ❌ Frontend lädt, aber API-Fehler (CORS / 502)

```bash
# Backend-Logs prüfen
docker compose logs backend

# Ist das Backend wirklich erreichbar?
curl http://localhost:8000/
```

### ❌ Ollama antwortet nicht (`connection refused`)

```bash
# Container-Status
docker compose ps

# Ollama-Logs
docker compose logs ollama

# Container neu starten
docker compose restart ollama
```

### ❌ Mistral-Modell fehlt (`model not found`)

```bash
docker exec -it jobhunter-ollama ollama pull mistral
```

### ❌ Datenbank-Fehler beim Start

```bash
# DB-Logs anschauen
docker compose logs db

# Prüfen ob Healthcheck besteht
docker inspect jobhunter-db | grep -A5 Health

# DB-Container neu starten
docker compose restart db

# Danach Backend neu starten
docker compose restart backend
```

### ❌ `.env`-Werte wurden geändert, Änderungen greifen nicht

Nach jeder Änderung an der `.env` müssen die Container neu erstellt werden:
```bash
docker compose up --build -d
```

### ❌ Alles zurücksetzen (kompletter Neustart)

> ⚠️ Hiermit werden **alle Daten gelöscht** (Datenbank, Uploads, Modell-Cache)!

```bash
# Alle Container, Netzwerke und Volumes löschen
docker compose down -v

# Dann neu starten
docker compose up --build -d
```

### ❌ Zu wenig RAM für Mistral

Mistral 7B benötigt mindestens **8 GB RAM**. Alternativen:

```bash
# Kleineres Modell (3.8 GB, 4 GB RAM ausreichend)
docker exec -it jobhunter-ollama ollama pull phi3

# Oder noch kleiner (1.1 GB)
docker exec -it jobhunter-ollama ollama pull tinyllama
```

In **Einstellungen → 🤖 KI → KI-Modell** das installierte Modell auswählen.

---

## Systemanforderungen (Empfehlung)

| Komponente | Minimum | Empfohlen |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 Kerne | 8 Kerne |
| Festplatte | 10 GB frei | 20 GB frei |
| GPU | nicht nötig | NVIDIA (CUDA) für schnelle KI |
| OS | Linux / macOS / Windows WSL2 | Linux |

---

> Bei Fragen oder Problemen: [GitHub Issues](https://github.com/freddykrueger88/JobHunter/issues) öffnen.
