# 🗺️ JobHunter Roadmap

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

### Status

| Version | Theme | Status |
|---------|-------|--------|
| v1.0 | Core features (Backend, Frontend, AI, GDPR, WCAG) | ✅ Done |
| v1.1 | Export, PDF, Cron, Portals, JWT, Alembic | ✅ Done |
| v1.2 | Inclusion & Accessibility | ✅ Done |
| v1.3 | Mobile & Basic Productivity | ✅ Done |
| v1.4 | Smart Search & Data Analysis | ✅ Done |
| v1.5 | AI Depth | ✅ Done |
| v1.6 | Communication & Workflow | ✅ Done |
| v1.7 | Statistics & Motivation | ✅ Done |
| v1.8 | ATS Optimization & Application Quality | 🚧 In Progress |
| v1.9 | Application Coach & Automation | 📌 Planned |
| v2.0 | EU-wide Job Portals (see below) | 🚧 In Progress |

---

### v1.8 – ATS Optimization & Application Quality

> Background: 75% of all applications are filtered by ATS systems before a human reads them. JobHunter helps overcome exactly that – locally, without a cloud service.

- **#57** – ATS Score Checker: AI compares CV vs. job description for keyword match, score 0–100 with traffic light display
- **#58** – Ghost Job Detection: Analyzes behavioral signals, badge ⚠️ "Possibly Ghost Job"
- **#59** – Application Quality Score: Checklist per application, overall score 0–100
- **#60** – Salary Negotiation Coach: AI generates negotiation strategy, 3 scenarios (conservative / realistic / optimistic)
- **#61** – Market Analysis per Job: AI analyzes competition, optimal timing, application strategy

---

### v1.9 – Application Coach & Automation

- **#62** – Application Coach Chat: AI chatbot directly in the app, context-aware (knows current application)
- **#63** – Auto-Apply Preparation (1-Click Package): Export cover letter (PDF) + CV (PDF) + metadata as ZIP
- **#64** – Follow-Up System with Reminders: "Follow up in X days" per application, dashboard shows due items

---

### v2.0 – EU-wide Job Portals

> Vision: connect European job boards from national down to municipal level (see [docs/portals.md](portals.md) for the full list and technical notes).

- EURES – the EU's own pan-European job board, all 31 member countries, country picker in the Jobs page
- Karriere.NRW – Open Data API for North Rhine-Westphalia (state + municipalities)
- service.bund.de – German public-sector postings, federal + all 16 states + municipalities
- France Travail – France's national employment agency (requires free registration, see [docs/api-keys.md](api-keys.md))
- Arbetsförmedlingen – Sweden's national employment agency (JobTech open-data platform)
- More EU countries: researched and parked for now (see `docs/analysis/BACKLOG.md`, Phase M) – several require manual approval from the national agency or deeper reverse-engineering rather than a clean self-service API

### Future (v2.0+)

| Feature | Description |
|---------|-------------|
| Browser Extension | Import job listing directly from browser into JobHunter |
| Multi-User Support | Manage multiple profiles locally |
| Mobile App (React Native) | Native app for Android/iOS |

---

### Principles

- Local before cloud-based
- Privacy first
- Accessibility in every version
- No external dependencies without opt-in

---
---

## Deutsch

### Status

| Version | Thema | Status |
|---------|-------|--------|
| v1.0 | Kern-Features (Backend, Frontend, KI, DSGVO, WCAG) | ✅ Fertig |
| v1.1 | Export, PDF, Cron, Portale, JWT, Alembic | ✅ Fertig |
| v1.2 | Inklusion & Barrierefreiheit | ✅ Fertig |
| v1.3 | Mobil & Basis-Produktivität | ✅ Fertig |
| v1.4 | Smarte Suche & Datenanalyse | ✅ Fertig |
| v1.5 | KI-Tiefe | ✅ Fertig |
| v1.6 | Kommunikation & Workflow | ✅ Fertig |
| v1.7 | Statistiken & Motivation | ✅ Fertig |
| v1.8 | ATS-Optimierung & Bewerbungsqualität | 🚧 In Arbeit |
| v1.9 | Bewerbungscoach & Automatisierung | 📌 Geplant |
| v2.0 | EU-weite Jobportale (siehe unten) | 🚧 In Arbeit |

---

### v1.8 – ATS-Optimierung & Bewerbungsqualität

- **#57** – ATS-Score-Checker: KI vergleicht CV vs. Stellenbeschreibung, Score 0–100 mit Ampel
- **#58** – Ghost-Job-Erkennung: Analyse von Verhaltenssignalen, Badge ⚠️
- **#59** – Bewerbungs-Qualitätsscore: Checkliste pro Bewerbung, Gesamt-Score 0–100
- **#60** – Gehaltsnegotiations-Coach: KI-Strategie, 3 Szenarien
- **#61** – Marktlage-Analyse: Wettbewerb, optimales Timing, Bewerbungsstrategie

---

### v1.9 – Bewerbungscoach & Automatisierung

- **#62** – Bewerbungscoach-Chat: KI-Chatbot, kontextbewusst
- **#63** – Auto-Apply-Vorbereitung: 1-Klick-Export als ZIP
- **#64** – Wiedervorlagen-System: Nachfassen-Erinnerungen mit Ampel

---

### v2.0 – EU-weite Jobportale

> Vision: europaeische Jobboersen anbinden, von national bis zur kleinsten Kommune (vollstaendige Liste + technische Details siehe [docs/portals.md](portals.md)).

- EURES – das offizielle EU-weite Jobportal, alle 31 Mitgliedslaender, Laenderauswahl auf der Jobs-Seite
- Karriere.NRW – Open-Data-API des Landes NRW (Land + Kommunen)
- service.bund.de – deutsche oeffentliche Stellen, Bund + alle 16 Laender + Kommunen
- France Travail – franzoesische nationale Arbeitsagentur (braucht kostenlose Registrierung, siehe [docs/api-keys.md](api-keys.md))
- Arbetsförmedlingen – schwedische nationale Arbeitsagentur (offene "JobTech"-Plattform)
- Weitere EU-Laender: recherchiert und vorerst zurueckgestellt (siehe `docs/analysis/BACKLOG.md`, Phase M) - mehrere brauchen eine manuelle Freigabe der jeweiligen Behoerde oder tieferes Reverse-Engineering statt einer sauberen Self-Service-API

### Zukunft (v2.0+)

| Feature | Beschreibung |
|---------|-------------|
| Browser-Extension | Stellenanzeige per Klick aus Browser importieren |
| Multi-User-Support | Mehrere Profile lokal verwalten |
| Mobile App (React Native) | Native App für Android/iOS |

---

### Prinzipien

- Lokal vor cloudbasiert
- Datenschutz zuerst
- Barrierefreiheit in jeder Version
- Keine externen Abhängigkeiten ohne Opt-in
