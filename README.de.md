# 🎯 JobHunter

> **Lokale, KI-gestützte Bewerbungsverwaltung** – Self-hosted, DSGVO-konform, keine Cloud erforderlich.

🇬🇧 [English Version](README.md)

[![Version](https://img.shields.io/badge/Version-1.9.0-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](backend/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](frontend/)
[![WCAG](https://img.shields.io/badge/Barrierefreiheit-WCAG%202.1%20AA-blueviolet)](docs/accessibility.md)
[![DSGVO](https://img.shields.io/badge/Datenschutz-DSGVO%20konform-green)](docs/dsgvo.md)

---

## Was ist JobHunter?

JobHunter ist ein vollständig lokaler Bewerbungs-Tracker mit KI-Unterstützung. Alle Daten bleiben auf deinem Rechner – kein Account, kein Abo, keine Cloud. Die KI läuft lokal via [Ollama](https://ollama.com) in Docker.

---

## ✨ Features

### 🔍 Stellensuche & Import
- Stellensuche via Bundesagentur für Arbeit, Adzuna, StepStone, LinkedIn
- Foto-Upload von Stellenanzeigen (OCR + KI-Extraktion)
- Duplikat-Erkennung (Fuzzy Matching)
- Ghost-Job-Erkennung ⚠️
- Deadline-Tracker mit Ampel-Badges

### 🤖 KI-Funktionen (100 % lokal via Ollama)
- Anschreiben-Generator (4 Töne: formal / direkt / modern / kreativ)
- CV-Optimierer & Anschreiben-Evaluator
- Skill-Gap-Analyse
- Interview-Vorbereitung (10 Fragen + Musterantworten)
- Absage-Analyse
- ATS-Score (Keyword-Abgleich CV ↔ Stellenbeschreibung, 0–100)
- Bewerbungsqualitäts-Score
- Gehaltsverhandlungs-Coach (3 Szenarien)
- Marktanalyse pro Stelle
- **AI Application Coach** – kontextueller Chat-Assistent pro Bewerbung (#62) 🆕
- Mehrsprachige Prompts (DE / EN automatisch erkannt)

### ✉️ Anschreiben-Vorlage *(geplant – #89)*
- Eigene DOCX-Vorlage einmalig hochladen
- KI füllt Vorlage stellenspezifisch aus (Firmenadresse aus Stellendaten, Datum automatisch)
- Fertiges DOCX herunterladen

### 📊 Dashboard & Auswertungen
- Kanban-Board (Drag & Drop)
- Live-Statistiken: Kreisdiagramm, Balkendiagramm, Funnel-Chart
- Wochenziel & Streak-Tracking
- Gamification-Badges (10 Achievements)
- PDF-Übersichtsexport

### 📧 Kommunikation & Workflow
- E-Mail-Vorlagen (6 Templates mit Platzhaltern)
- **E-Mail-Parser via IMAP** – erkennt automatisch Absagen, Einladungen & Follow-ups (#68) 🆕
- Kalender-Export (`.ics` + abonnierbarer Feed) (#77) 🆕
- Kontakte-Manager (Recruiter, Ansprechpartner)
- Brutto-/Netto-Rechner (Steuerklassen 1–6, Sozialabgaben 2025)
- Automatisches lokales Backup (täglich, 7-Tage-Rotation)

### 🏢 Firmenrecherche
- **Firmen-Dossier** – Wikipedia-basiertes Info-Panel (Beschreibung, Gründung, Mitarbeiter, HQ, Logo) pro Bewerbung (#71) 🆕

### 📤 Import / Export
- **JSON / CSV / XLSX Export & Import** aller Bewerbungen (#65) 🆕
- PDF-Übersichtsexport

### ♿ Barrierefreiheit (WCAG 2.1 AA)
- Legasthenie-Theme (OpenDyslexic)
- Farbenblindheits-Filter (4 Typen)
- ADHS-Modus (Fokus-Modus, reduzierte Informationsdichte)
- Tastaturkürzel-System
- Screenreader-optimiert (ARIA, Skip-Links, Live-Regions)
- Undo-Toast & Bestätigungsdialoge

### 🔒 Datenschutz & Sicherheit
- 100 % lokal – keine externe Datenübertragung
- DSGVO-konform (Art. 20 Datenexport)
- AES-256-verschlüsselte API-Key-Speicherung
- Optionale JWT-Authentifizierung (`AUTH_ENABLED=true`)
- Alembic-Datenbankmigrationen

---

## 🚀 Quickstart

**Voraussetzungen:** Docker, Docker Compose, Python 3

```bash
# 1. Repository klonen
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter

# 2. .env-Datei erstellen
cp .env.example .env
```

Die drei Pflichtfelder in der `.env` mit sicheren Werten befüllen:

```bash
# DB_PASSWORD generieren:
python3 -c "import secrets; print(secrets.token_hex(16))"

# SECRET_KEY generieren:
python3 -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY generieren (muss ein Fernet-Key sein):
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

```bash
# 3. Alle Dienste starten
docker compose up -d

# 4. KI-Modell laden (Mistral empfohlen)
docker exec jobhunter-ollama ollama pull mistral
```

🌍 App öffnen: **http://localhost:3000**

> **GPU-Unterstützung (NVIDIA):** Den `deploy`-Block im `docker-compose.yml` unter dem `ollama`-Service auskommentieren.

---

> ### 📋 Ausführliche Installationsanleitung
> Neu hier oder Probleme beim Start? **[INSTALL.md](INSTALL.md)** deckt alles ab:
> - ✅ Alle Voraussetzungen mit Prüfbefehlen
> - ✅ Sichere Schlüssel für `.env` generieren
> - ✅ Docker-Setup & manuelles Setup (ohne Docker)
> - ✅ Mistral-Modell installieren & prüfen
> - ✅ Erste-Schritte-Checkliste
> - ✅ App aktualisieren
> - ✅ Troubleshooting (8 häufige Probleme mit Lösungen)
>
> **→ [Zur vollständigen Installationsanleitung](INSTALL.md)**

---

## 🛠️ Tech-Stack

| Schicht | Technologie |
|---|---|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Datenbank | PostgreSQL 16 |
| KI | Ollama (Mistral, LLaMA3, Phi-3) |
| Deployment | Docker Compose |

---

## 📖 Dokumentation

- [📋 Installationsanleitung](INSTALL.md)
- [🛠️ Setup-Guide](docs/setup.md)
- [♿ Barrierefreiheit](docs/accessibility.md)
- [🔒 Datenschutz & DSGVO](docs/dsgvo.md)
- [📍 Roadmap](docs/roadmap.md)
- [📝 Changelog](CHANGELOG.md)
- [📚 Wiki](wiki/Home.md)

---

## 🗺️ Roadmap

| Version | Thema | Status |
|---|---|---|
| v1.0 – v1.8 | Grundgerüst, KI, Barrierefreiheit, Analytics, ATS | ✅ Fertig |
| v1.9 | Coach, IMAP, Kalender, Dossier, Import/Export (#62 #65 #68 #71 #77) | ✅ Fertig |
| v1.9.x | Anschreiben-Vorlage & KI-Befüllung (#89), Auto-Apply (#63) | 🚧 In Arbeit |
| v2.0+ | EU-Jobportale, Browser-Extension, Multi-User | 💡 Backlog |

→ Vollständige Roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## 📄 Lizenz

MIT – siehe [LICENSE](LICENSE)
