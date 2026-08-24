# 🤝 Contributing to JobHunter / Mitmachen bei JobHunter

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

Thank you for contributing to JobHunter! All help is welcome – whether it's a bugfix, new feature, translation, or documentation improvement.

### 📋 Table of Contents

1. [Code of Conduct](#1-code-of-conduct)
2. [How can I help?](#2-how-can-i-help)
3. [Setting up the development environment](#3-setting-up-the-development-environment)
4. [Git Workflow](#4-git-workflow)
5. [Commit Conventions](#5-commit-conventions)
6. [Creating a Pull Request](#6-creating-a-pull-request)
7. [Code Style](#7-code-style)
8. [Release Process](#8-release-process)
9. [Questions & Help](#9-questions--help)

---

### 1. Code of Conduct

Please be respectful and constructive. Discrimination, insults or personal attacks will not be tolerated.

---

### 2. How can I help?

#### 🐛 Report Bugs
Open an [Issue](https://github.com/freddykrueger88/JobHunter/issues/new) with:
- Brief description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- OS, browser, Docker version

#### 💡 Suggest a Feature
Also as an [Issue](https://github.com/freddykrueger88/JobHunter/issues/new) with the label `enhancement`. Please check if a similar suggestion already exists.

#### 🔧 Contribute Code
- Bugfixes, new features, performance improvements
- Please always open an issue first and briefly align before starting large changes

#### 📖 Improve Documentation
- Typos, unclear sections, missing explanations
- Translations (DE ↔ EN)

---

### 3. Setting up the Development Environment

See [INSTALL.md](INSTALL.md) for the full installation guide.

Quick start:
```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
cp .env.example .env
# Fill .env with your own values
docker compose up --build -d
docker exec -it jobhunter-ollama ollama pull mistral
```

---

### 4. Git Workflow

```bash
# 1. Create a fork (top right on GitHub: "Fork")

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/JobHunter.git
cd JobHunter

# 3. Add upstream
git remote add upstream https://github.com/freddykrueger88/JobHunter.git

# 4. Create a new branch
git checkout -b fix/descriptive-name
# or
git checkout -b feat/new-feature

# 5. Make changes & commit
git add .
git commit -m "fix(kanban): fix drag-and-drop on mobile devices"

# 6. Push to your fork
git push origin fix/descriptive-name

# 7. Open a Pull Request – a banner will appear automatically on GitHub
```

> Keep your branch up to date:
> ```bash
> git fetch upstream
> git rebase upstream/main
> ```

---

### 5. Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description
```

| Type | When |
|---|---|
| `feat` | New feature |
| `fix` | Bugfix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Restructure without new feature/fix |
| `perf` | Performance improvement |
| `test` | Add/change tests |
| `chore` | Build, dependencies, CI |

**Examples:**
```
feat(ai): add salary negotiation coach
fix(kanban): fix drag-drop bug on iOS
docs(install): add troubleshooting for Windows WSL2
chore(deps): update FastAPI to 0.115
```

---

### 6. Creating a Pull Request

Please fill in the PR description:

- **What** was changed?
- **Why** (link to issue if applicable)
- **How** to test?
- Screenshots if UI changes

PRs are only merged if:
- [ ] No existing tests are broken
- [ ] Code style is maintained
- [ ] Commits are clean (no WIP commits)
- [ ] Description is filled in

---

### 7. Code Style

#### Frontend (TypeScript / React)
- Functional components, no classes
- Tailwind CSS for styling
- `clsx` for conditional classes
- No `any` types if avoidable
- Consider accessibility: `aria-*`, `role`, keyboard navigation

#### Backend (Python / FastAPI)
- Follow PEP 8
- Async functions for all DB operations
- Pydantic schemas for all request/response types
- New endpoints with OpenAPI description (`summary`, `description`)

#### General
- No commented-out code in PRs
- German or English comments and variable names are both fine (project language is DE/EN)

---

### 8. Release Process

*(Made explicit in Rework-Plan Phase E.5 – previously informal/undocumented, see `docs/analysis/REPOSITORY_AUDIT_EN.md`.)*

JobHunter follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

| Bump | When |
|---|---|
| `MAJOR` | Breaking changes (incompatible API/DB migration, removed feature) |
| `MINOR` | New features, backward-compatible (the common case – see `CHANGELOG.md` history) |
| `PATCH` | Bugfixes only, no new features |

**Steps to cut a release:**

1. Make sure CI (`.github/workflows/ci.yml`) is green on `main` – releases are only cut from a green commit.
2. Move the relevant `[Unreleased]` entries in `CHANGELOG.md` into a new `[X.Y.Z] – YYYY-MM-DD` section, **both** in the English and German half of the file (single-file DE/EN scheme, see file header).
3. Update the version badge in `README.md` and `README.de.md`.
4. Commit: `git commit -m "chore(release): vX.Y.Z"`.
5. Tag and push: `git tag -a vX.Y.Z -m "vX.Y.Z"` then `git push origin main --tags`.
6. Optionally create a GitHub Release from the tag, using the matching `CHANGELOG.md` section as the description.

> **Known gap (as of this writing):** `frontend/package.json`'s `"version"` field is not currently kept in sync with the README/CHANGELOG version (README shows v1.9.0, `package.json` shows 0.4.0). Keep it in sync going forward when cutting a release; retroactively fixing the existing drift is a separate decision, not assumed here.

---

### 9. Questions & Help

Simply open an [Issue](https://github.com/freddykrueger88/JobHunter/issues) with the label `question`. No question is too simple!

---

> Thank you for your contribution! 🎯

---
---

## Deutsch

Danke, dass du zu JobHunter beitragen möchtest! Jede Hilfe ist willkommen – egal ob Bugfix, neue Funktion, Übersetzung oder Dokumentation.

### 📋 Inhaltsverzeichnis

1. [Verhaltenskodex](#1-verhaltenskodex)
2. [Wie kann ich helfen?](#2-wie-kann-ich-helfen)
3. [Entwicklungsumgebung einrichten](#3-entwicklungsumgebung-einrichten)
4. [Arbeitsablauf (Git)](#4-arbeitsablauf-git)
5. [Commit-Konventionen](#5-commit-konventionen)
6. [Pull Request erstellen](#6-pull-request-erstellen)
7. [Code-Stil](#7-code-stil)
8. [Release-Prozess](#8-release-prozess)
9. [Fragen & Hilfe](#9-fragen--hilfe)

---

### 1. Verhaltenskodex

Bitte respektvoll und konstruktiv miteinander umgehen. Diskriminierung, Beleidigungen oder persönliche Angriffe werden nicht toleriert.

---

### 2. Wie kann ich helfen?

#### 🐛 Bugs melden
Einen [Issue](https://github.com/freddykrueger88/JobHunter/issues/new) öffnen mit:
- Kurze Beschreibung des Problems
- Schritte zur Reproduktion
- Erwartetes vs. tatsächliches Verhalten
- Betriebssystem, Browser, Docker-Version

#### 💡 Feature vorschlagen
Ebenfalls als [Issue](https://github.com/freddykrueger88/JobHunter/issues/new) mit dem Label `enhancement`. Bitte zuerst prüfen ob ein ähnlicher Vorschlag bereits existiert.

#### 🔧 Code beitragen
- Bugfixes, neue Features, Performance-Verbesserungen
- Bitte immer zuerst ein Issue öffnen und kurz abstimmen, bevor du große Änderungen anfängst

#### 📖 Dokumentation verbessern
- Tippfehler, unklare Stellen, fehlende Erklärungen
- Übersetzungen (DE ↔ EN)

---

### 3. Entwicklungsumgebung einrichten

Siehe [INSTALL.md](INSTALL.md) für die vollständige Installationsanleitung.

Kurzversion:
```bash
git clone https://github.com/freddykrueger88/JobHunter.git
cd JobHunter
cp .env.example .env
# .env mit eigenen Werten befüllen
docker compose up --build -d
docker exec -it jobhunter-ollama ollama pull mistral
```

---

### 4. Arbeitsablauf (Git)

```bash
# 1. Fork erstellen (auf GitHub oben rechts "Fork")

# 2. Fork klonen
git clone https://github.com/DEIN-USERNAME/JobHunter.git
cd JobHunter

# 3. Upstream hinzufügen
git remote add upstream https://github.com/freddykrueger88/JobHunter.git

# 4. Neuen Branch erstellen
git checkout -b fix/beschreibender-name
# oder
git checkout -b feat/neue-funktion

# 5. Änderungen machen & committen
git add .
git commit -m "fix(kanban): korrigiere Drag-and-Drop auf mobilen Geräten"

# 6. Auf deinen Fork pushen
git push origin fix/beschreibender-name

# 7. Pull Request öffnen – auf GitHub erscheint automatisch ein Banner
```

> Halte deinen Branch aktuell:
> ```bash
> git fetch upstream
> git rebase upstream/main
> ```

---

### 5. Commit-Konventionen

Wir nutzen [Conventional Commits](https://www.conventionalcommits.org/):

```
typ(bereich): kurze Beschreibung
```

| Typ | Wann |
|---|---|
| `feat` | Neue Funktion |
| `fix` | Bugfix |
| `docs` | Nur Dokumentation |
| `style` | Formatierung, kein Logikänderung |
| `refactor` | Umbau ohne neue Funktion/Fix |
| `perf` | Performance-Verbesserung |
| `test` | Tests hinzufügen/ändern |
| `chore` | Build, Abhängigkeiten, CI |

**Beispiele:**
```
feat(ai): füge Gehaltsverhandlungs-Coach hinzu
fix(kanban): behebe Drag-Drop-Fehler auf iOS
docs(install): ergänze Troubleshooting für Windows WSL2
chore(deps): aktualisiere FastAPI auf 0.115
```

---

### 6. Pull Request erstellen

Bitte im PR-Beschreibungsfeld ausfüllen:

- **Was** wurde geändert?
- **Warum** (Link zum Issue falls vorhanden)
- **Wie** testen?
- Screenshots falls UI-Änderungen

PRs werden nur gemergt wenn:
- [ ] Kein bestehender Test bricht
- [ ] Code-Stil eingehalten
- [ ] Commits sauber (keine WIP-Commits)
- [ ] Beschreibung ausgefüllt

---

### 7. Code-Stil

#### Frontend (TypeScript / React)
- Funktionale Komponenten, keine Klassen
- Tailwind CSS für Styling
- `clsx` für bedingte Klassen
- Keine `any`-Types wenn vermeidbar
- Barrierefreiheit beachten: `aria-*`, `role`, Tastaturnavigation

#### Backend (Python / FastAPI)
- PEP 8 einhalten
- Async-Funktionen für alle DB-Operationen
- Pydantic-Schemas für alle Request/Response-Typen
- Neue Endpunkte mit OpenAPI-Beschreibung (`summary`, `description`)

#### Allgemein
- Kein auskommentierter Code in PRs
- Deutsche und englische Kommentare und Variablennamen sind beide OK (Projektsprache ist DE/EN)

---

### 8. Release-Prozess

*(Explizit gemacht in Rework-Plan Phase E.5 – zuvor informell/undokumentiert, siehe `docs/analysis/REPOSITORY_AUDIT_DE.md`.)*

JobHunter folgt [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

| Erhöhung | Wann |
|---|---|
| `MAJOR` | Breaking Changes (inkompatible API-/DB-Migration, entferntes Feature) |
| `MINOR` | Neue Features, abwärtskompatibel (der Regelfall – siehe `CHANGELOG.md`-Historie) |
| `PATCH` | Nur Bugfixes, keine neuen Features |

**Schritte für einen Release:**

1. Sicherstellen, dass CI (`.github/workflows/ci.yml`) auf `main` grün ist – Releases werden nur von einem grünen Commit aus geschnitten.
2. Die relevanten `[Unreleased]`-Einträge in `CHANGELOG.md` in einen neuen Abschnitt `[X.Y.Z] – YYYY-MM-DD` verschieben, **sowohl** im englischen als auch im deutschen Teil der Datei (Ein-Datei-DE/EN-Schema, siehe Dateikopf).
3. Das Versions-Badge in `README.md` und `README.de.md` aktualisieren.
4. Committen: `git commit -m "chore(release): vX.Y.Z"`.
5. Taggen und pushen: `git tag -a vX.Y.Z -m "vX.Y.Z"`, dann `git push origin main --tags`.
6. Optional einen GitHub Release aus dem Tag erstellen, mit dem passenden `CHANGELOG.md`-Abschnitt als Beschreibung.

> **Bekannte Lücke (Stand jetzt):** Das `"version"`-Feld in `frontend/package.json` wird aktuell nicht mit der README-/CHANGELOG-Version synchron gehalten (README zeigt v1.9.0, `package.json` zeigt 0.4.0). Ab jetzt bei jedem Release synchron halten; die bestehende Abweichung rückwirkend zu korrigieren ist eine eigene Entscheidung, die hier nicht vorausgesetzt wird.

---

### 9. Fragen & Hilfe

Einfach ein [Issue](https://github.com/freddykrueger88/JobHunter/issues) mit dem Label `question` öffnen. Keine Frage ist zu simpel!

---

> Danke für deinen Beitrag! 🎯
