# 🎯 JobHunter

> **Local, AI-powered job application manager** – Self-hosted, GDPR-compliant, no cloud required.

🇩🇪 [Deutsche Version](README.de.md)

[![Version](https://img.shields.io/badge/Version-1.8.0-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](backend/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](frontend/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1%20AA-blueviolet)](docs/accessibility.md)
[![GDPR](https://img.shields.io/badge/Privacy-GDPR%20compliant-green)](docs/dsgvo.md)

---

## What is JobHunter?

JobHunter is a fully local job application tracker with AI assistance. All data stays on your machine – no accounts, no subscriptions, no cloud. Powered by [Ollama](https://ollama.com) for local LLM inference.

---

## ✨ Features

### 🔍 Job Search & Import
- Job search via Bundesagentur für Arbeit, Adzuna, StepStone, LinkedIn
- Photo upload of job ads (OCR + AI extraction)
- Duplicate detection (fuzzy matching)
- Ghost job detection ⚠️
- Deadline tracker with traffic-light badges

### 🤖 AI Features (100% local via Ollama)
- Cover letter generator (4 tones: formal / direct / modern / creative)
- CV optimizer & cover letter evaluator
- Skill gap analysis
- Interview preparation (10 questions + sample answers)
- Rejection analysis
- ATS score checker (keyword match CV ↔ job description, 0–100)
- Application quality score
- Salary negotiation coach (3 scenarios)
- Market analysis per job (competition, optimal timing, strategy)
- Multilingual prompts (DE / EN auto-detected)

### 📊 Dashboard & Analytics
- Kanban board (Drag & Drop)
- Live statistics: pie chart, bar chart, funnel chart
- Weekly goal & streak tracking
- Gamification badges (10 achievements)
- PDF overview export

### 📧 Communication & Workflow
- E-mail templates (6 templates with placeholders)
- Calendar export (`.ics` + subscribable feed)
- Contacts manager (recruiters, contact persons)
- Gross/net salary calculator (tax classes 1–6, 2025 social contributions)
- Automated local backup (daily, 7-day rotation)

### ♿ Accessibility (WCAG 2.1 AA)
- Dyslexia theme (OpenDyslexic)
- Color blindness filters (4 types)
- ADHD mode (focus mode, reduced information density)
- Keyboard shortcut system
- Screenreader optimized (ARIA, skip links, live regions)
- Undo toast & confirm dialog

### 🔒 Privacy & Security
- 100% local – no external data transfer
- GDPR-compliant (Art. 20 data export)
- AES-256 encrypted API key storage
- Optional JWT authentication (`AUTH_ENABLED=true`)
- Alembic database migrations

---

## 🚀 Quickstart

```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
cp .env.example .env

# Generate encryption key and add to .env:
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# Pull an AI model (Mistral recommended):
ollama pull mistral

# Start:
docker compose up -d
```

🌍 Open **http://localhost:3000**

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL 16 |
| AI | Ollama (Mistral, LLaMA3, Phi-3) |
| Deployment | Docker Compose |

---

## 📖 Documentation

- [🛠️ Setup Guide](docs/setup.md)
- [♿ Accessibility](docs/accessibility.md)
- [🔒 Privacy & GDPR](docs/dsgvo.md)
- [📍 Roadmap](docs/roadmap.md)
- [📝 Changelog](CHANGELOG.md)

---

## 🗺️ Roadmap

| Version | Theme | Status |
|---|---|---|
| v1.0 – v1.8 | Core, AI, Accessibility, Analytics, ATS | ✅ Done |
| v1.9 | Application coach & automation (#62–#64) | 📌 Planned |
| v2.0+ | EU portals, browser extension, multi-user | 💡 Backlog |

→ Full roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## 📄 License

MIT – see [LICENSE](LICENSE)
