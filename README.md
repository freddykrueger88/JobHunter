# 🎯 JobHunter

> **Local, AI-powered job application manager** – Self-hosted, GDPR-compliant, no cloud required.

🇩🇪 [Deutsche Version](README.de.md)

[![Version](https://img.shields.io/badge/Version-1.9.0-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](backend/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](frontend/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1%20AA-blueviolet)](docs/accessibility.md)
[![GDPR](https://img.shields.io/badge/Privacy-GDPR%20compliant-green)](docs/dsgvo.md)

---

## What is JobHunter?

JobHunter is a fully local job application tracker with AI assistance. All data stays on your machine – no accounts, no subscriptions, no cloud. AI runs locally via [Ollama](https://ollama.com) inside Docker.

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
- **AI Application Coach** – contextual chat assistant per application (#62) 🆕
- Multilingual prompts (DE / EN auto-detected)

### ✉️ Cover Letter Template *(planned – #89)*
- Upload your own DOCX template once
- AI fills it with job-specific content (company address from job data, current date auto-set)
- Download ready-to-send DOCX

### 📊 Dashboard & Analytics
- Kanban board (Drag & Drop)
- Live statistics: pie chart, bar chart, funnel chart
- Weekly goal & streak tracking
- Gamification badges (10 achievements)
- PDF overview export

### 📧 Communication & Workflow
- E-mail templates (6 templates with placeholders)
- **E-mail parsing via IMAP** – auto-detects rejections, invitations & follow-ups (#68) 🆕
- Calendar export (`.ics` + subscribable feed) (#77) 🆕
- Contacts manager (recruiters, contact persons)
- Gross/net salary calculator (tax classes 1–6, 2025 social contributions)
- Automated local backup (daily, 7-day rotation)

### 🏢 Company Research
- **Company dossier** – Wikipedia-powered info panel (description, founded, employees, HQ, logo) per application (#71) 🆕

### 📤 Import / Export
- **JSON / CSV / XLSX export & import** of all applications (#65) 🆕
- PDF overview export

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

**Prerequisites:** Docker, Docker Compose, Python 3 (for key generation)

```bash
# 1. Clone repository
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter

# 2. Create .env file
cp .env.example .env
```

Now edit `.env` and fill in the three required values:

```bash
# Generate DB_PASSWORD:
python3 -c "import secrets; print(secrets.token_hex(16))"

# Generate SECRET_KEY:
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate ENCRYPTION_KEY (must be a Fernet key):
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

```bash
# 3. Start all services
docker compose up -d

# 4. Pull an AI model (Mistral recommended)
docker exec jobhunter-ollama ollama pull mistral
```

🌍 Open **http://localhost:3000**

> **GPU support (NVIDIA):** Uncomment the `deploy` section in `docker-compose.yml` under the `ollama` service.

---

> ### 📋 Detailed Installation Guide
> New here or running into problems? The **[INSTALL.md](INSTALL.md)** covers everything step by step:
> - ✅ All prerequisites with version check commands
> - ✅ Generating secure keys for `.env`
> - ✅ Docker setup & manual setup (without Docker)
> - ✅ Installing & verifying the Mistral AI model
> - ✅ First-start checklist
> - ✅ Updating the app
> - ✅ Troubleshooting (8 common issues with solutions)
>
> **→ [Open full installation guide](INSTALL.md)**

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

- [📋 Installation Guide](INSTALL.md)
- [🛠️ Setup Guide](docs/setup.md)
- [♿ Accessibility](docs/accessibility.md)
- [🔒 Privacy & GDPR](docs/dsgvo.md)
- [📍 Roadmap](docs/roadmap.md)
- [📝 Changelog](CHANGELOG.md)
- [📚 Wiki](wiki/Home.md)

---

## 🗺️ Roadmap

| Version | Theme | Status |
|---|---|---|
| v1.0 – v1.8 | Core, AI, Accessibility, Analytics, ATS | ✅ Done |
| v1.9 | Coach, IMAP, Calendar, Dossier, Import/Export (#62 #65 #68 #71 #77) | ✅ Done |
| v1.9.x | Cover letter template upload & AI fill (#89), Auto-Apply (#63) | 🚧 In Progress |
| v2.0+ | EU portals, browser extension, multi-user | 💡 Backlog |

→ Full roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## 📄 License

MIT – see [LICENSE](LICENSE)
