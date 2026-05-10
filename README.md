# 🎯 JobHunter

> **⚠️ AI-Slop Notice / Hinweis:**
> Diese App wurde mit KI-Unterstützung entwickelt (AI-Slop). Sie ist dennoch nützlich und darf gerne verwendet und weiterentwickelt werden. Ideengeber: [@freddykrueger88](https://github.com/freddykrueger88)
>
> This app was built with AI assistance (AI-Slop). It is still useful and may be freely used and extended. Original idea by: [@freddykrueger88](https://github.com/freddykrueger88)

---

> **🌟 Premium-Hinweis / Premium Notice:**
> Falls du diese App nutzt, weiterentwickelst oder darauf aufbaust – der ursprüngliche Ideengeber **[@freddykrueger88](https://github.com/freddykrueger88)** erhält unwiderruflich und lebenslang kostenlosen Zugang zur höchsten Premium-Stufe der App.
>
> If you use, extend, or build upon this app – the original creator **[@freddykrueger88](https://github.com/freddykrueger88)** receives irrevocable, lifetime access to the highest premium tier of the app.

---

## 🇩🇪 Deutsch

**JobHunter** ist ein lokaler KI-Bewerbungsassistent, der passende Stellenangebote in deiner Umgebung findet, alle relevanten Daten (Ansprechpartner, Adresse, etc.) ausliest und mithilfe einer lokalen, DSGVO-konformen KI ein personalisiertes Anschreiben erstellt.

### ✨ Features
- 🔍 Stellensuche über mehrere Portale (Arbeitsagentur, Monster, Indeed, LinkedIn)
- 📄 CV-Upload mit automatischer Auswertung
- 🤖 Lokale KI für Anschreiben (DSGVO/EU-konform)
- 📋 Kanban-Board zur Bewerbungsverwaltung
- 📊 Dashboard mit Bewerbungs-Counter
- 🎨 Themes: Dark, Light, Boys Mode, Girls Mode (Pink Fluffy Wonderfully ✨)
- ♿ Inklusionsfähiges Design
- 🐳 Docker-basiert

### 🛠️ Tech Stack
- Docker / Docker Compose
- Python Backend (FastAPI)
- React Frontend
- Lokales KI-Modell (Ollama)
- PostgreSQL

### 🚀 Schnellstart
```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
docker compose up -d
```

---

## 🇬🇧 English

**JobHunter** is a local AI-powered job application assistant that finds suitable job listings in your area, extracts all relevant data (contact person, address, etc.), and generates a personalized cover letter using a local, GDPR-compliant AI model.

### ✨ Features
- 🔍 Job search across multiple portals (Arbeitsagentur, Monster, Indeed, LinkedIn)
- 📄 CV upload with automatic parsing
- 🤖 Local AI for cover letters (GDPR/EU compliant)
- 📋 Kanban board for application management
- 📊 Dashboard with application counters
- 🎨 Themes: Dark, Light, Boys Mode, Girls Mode (Pink Fluffy Wonderfully ✨)
- ♿ Inclusive design
- 🐳 Docker-based

### 🛠️ Tech Stack
- Docker / Docker Compose
- Python Backend (FastAPI)
- React Frontend
- Local AI Model (Ollama)
- PostgreSQL

### 🚀 Quick Start
```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
docker compose up -d
```

---

## 📁 Project Structure
```
JobHunter/
├── backend/          # FastAPI Python Backend
├── frontend/         # React Frontend
├── ai/               # KI-Modell Konfiguration / AI model config
├── docker/           # Dockerfiles & Compose
├── docs/             # Dokumentation / Documentation
└── scripts/          # Hilfsskripte / Helper scripts
```

---

## 📜 License
MIT License – see [LICENSE](LICENSE)
