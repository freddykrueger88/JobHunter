# 🎯 JobHunter

> **Lokale, KI-gestützte Bewerbungsverwaltung** – Self-Hosted, DSGVO-konform, keine Cloud.

🇬🇧 [English version](README.md)

[![Version](https://img.shields.io/badge/Version-1.8.0-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](backend/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](frontend/)
[![WCAG](https://img.shields.io/badge/Barrierefreiheit-WCAG%202.1%20AA-blueviolet)](docs/accessibility.md)
[![DSGVO](https://img.shields.io/badge/Datenschutz-DSGVO%20konform-green)](docs/dsgvo.md)

---

## Was ist JobHunter?

JobHunter ist ein vollständig lokaler Bewerbungs-Tracker mit KI-Unterstützung. Alle Daten bleiben auf deinem Rechner – kein Account, kein Abo, keine Cloud. Die KI läuft lokal über [Ollama](https://ollama.com).

---

## ✨ Features

### 🔍 Stellensuche & Import
- Stellensuche über Bundesagentur für Arbeit, Adzuna, StepStone, LinkedIn
- Foto-Upload von Stellenanzeigen (OCR + KI-Extraktion)
- Duplikat-Erkennung (Fuzzy-Matching)
- Ghost-Job-Erkennung ⚠️
- Bewerbungsfristen-Tracker mit Ampel-Badges

### 🤖 KI-Features (100% lokal via Ollama)
- Anschreiben-Generator (4 Tone: formell / direkt / modern / kreativ)
- Lebenslauf-Optimierung & Anschreiben-Bewertung
- Skill-Gap-Analyse
- Interview-Vorbereitung (10 Fragen + Musterantworten)
- Absage-Analyse
- ATS-Score-Checker (Keyword-Abgleich CV ↔ Stellenbeschreibung, 0–100)
- Bewerbungs-Qualitätsscore
- Gehaltsnegotiations-Coach (3 Szenarien)
- Marktlage-Analyse pro Stelle (Wettbewerb, optimales Timing, Strategie)
- Mehrsprachige Prompts (DE / EN automatisch erkannt)

### 📊 Dashboard & Analyse
- Kanban-Board (Drag & Drop)
- Live-Statistiken: Pie-Chart, Bar-Chart, Funnel-Chart
- Wöchentliches Ziel & Streak-Tracking
- Gamification: 10 Abzeichen
- PDF-Druckansicht & Export

### 📧 Kommunikation & Workflow
- E-Mail-Vorlagen (6 Templates mit Platzhaltern)
- Kalender-Export (`.ics` + abonnierbarer Feed)
- Kontakte-Verwaltung (Recruiter, Ansprechpartner)
- Netto-Brutto-Gehaltsrechner (Steuerklassen 1–6, SV-Beiträge 2025)
- Automatisches lokales Backup (täglich, 7-Tage-Rotation)

### ♿ Barrierefreiheit (WCAG 2.1 AA)
- Legasthenie-Theme (OpenDyslexic)
- Farbenblindheits-Filter (4 Typen)
- ADHS-Modus (Fokus-Modus, reduzierte Informationsdichte)
- Tastaturkürzel-System
- Screenreader-optimiert (ARIA, Skip-Links, Live-Regionen)
- Undo-Toast & Bestätigungs-Dialog

### 🔒 Datenschutz & Sicherheit
- 100% lokal – keine externen Datenübertragungen
- DSGVO-konform (Art. 20 Datenexport)
- AES-256-verschlüsselte API-Key-Speicherung
- Optionale JWT-Authentifizierung (`AUTH_ENABLED=true`)
- Alembic-Datenbankmigrationen

---

## 🚀 Schnellstart

```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
cp .env.example .env

# Verschlüsselungsschlüssel generieren und in .env eintragen:
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# KI-Modell laden (Mistral empfohlen):
ollama pull mistral

# Starten:
docker compose up -d
```

🌍 **http://localhost:3000** öffnen

---

## 🛠️ Tech Stack

| Schicht | Technologie |
|---|---|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Datenbank | PostgreSQL 16 |
| KI | Ollama (Mistral, LLaMA3, Phi-3) |
| Deployment | Docker Compose |

---

## 📖 Dokumentation

- [🛠️ Einrichtung](docs/setup.md)
- [♿ Barrierefreiheit](docs/accessibility.md)
- [🔒 Datenschutz & DSGVO](docs/dsgvo.md)
- [📍 Roadmap](docs/roadmap.md)
- [📝 Changelog](CHANGELOG.md)

---

## 🗺️ Roadmap

| Version | Thema | Status |
|---|---|---|
| v1.0 – v1.8 | Kern, KI, Barrierefreiheit, Analyse, ATS | ✅ Fertig |
| v1.9 | Bewerbungscoach & Automatisierung (#62–#64) | 📌 Geplant |
| v2.0+ | EU-Portale, Browser-Extension, Multi-User | 💡 Backlog |

→ Vollständige Roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## 📄 Lizenz

MIT – siehe [LICENSE](LICENSE)
