# 🎯 JobHunter

> **Lokale, KI-gestützte Bewerbungsverwaltung** – Self-Hosted, DSGVO-konform, keine Cloud.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](backend/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](frontend/)

---

## Features

| Feature | Status |
|---|---|
| 🔍 Stellensuche (Bundesagentur für Arbeit, Adzuna) | ✅ |
| 💼 Kanban-Board (Drag & Drop) | ✅ |
| ✍️ Anschreiben-Generator (Ollama KI, 4 Tone) | ✅ |
| 📄 CV-Upload & Parsing (PDF/DOCX) | ✅ |
| 🔔 Erinnerungen | ✅ |
| 📊 Dashboard mit Live-Statistiken | ✅ |
| 🔒 Verschlüsselte API-Key-Speicherung (AES-256) | ✅ |
| 🌙/☀️/💙/🌸 4 Themes | ✅ |
| 🇩🇪/🇬🇧 DE/EN Lokalisierung | ✅ |
| ♿ WCAG 2.1 AA Barrierefreiheit | ✅ |
| 🔒 DSGVO-konform (vollständig lokal) | ✅ |

## Schnellstart

```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
cp .env.example .env
# ENCRYPTION_KEY in .env setzen:
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
ollama pull mistral
docker compose up -d
```

🌍 **http://localhost:3000**

## Dokumentation

- [🛠️ Einrichtung](docs/setup.md)
- [♿ Barrierefreiheit](docs/accessibility.md)
- [🔒 Datenschutz & DSGVO](docs/dsgvo.md)

## Tech Stack

| Schicht | Technologie |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Datenbank | PostgreSQL 16 |
| KI | Ollama (Mistral, LLaMA3, Phi-3) |
| Deployment | Docker Compose |

## Lizenz

MIT – siehe [LICENSE](LICENSE)
