# 🤝 Mitmachen bei JobHunter

Danke, dass du zu JobHunter beitragen möchtest! Jede Hilfe ist willkommen – egal ob Bugfix, neue Funktion, Übersetzung oder Dokumentation.

---

## 📋 Inhaltsverzeichnis

1. [Verhaltenskodex](#1-verhaltenskodex)
2. [Wie kann ich helfen?](#2-wie-kann-ich-helfen)
3. [Entwicklungsumgebung einrichten](#3-entwicklungsumgebung-einrichten)
4. [Arbeitsablauf (Git)](#4-arbeitsablauf-git)
5. [Commit-Konventionen](#5-commit-konventionen)
6. [Pull Request erstellen](#6-pull-request-erstellen)
7. [Code-Stil](#7-code-stil)
8. [Fragen & Hilfe](#8-fragen--hilfe)

---

## 1. Verhaltenskodex

Bitte respektvoll und konstruktiv miteinander umgehen. Diskriminierung, Beleidigungen oder persönliche Angriffe werden nicht toleriert.

---

## 2. Wie kann ich helfen?

### 🐛 Bugs melden
Einen [Issue](https://github.com/freddykrueger88/JobHunter/issues/new) öffnen mit:
- Kurze Beschreibung des Problems
- Schritte zur Reproduktion
- Erwartetes vs. tatsächliches Verhalten
- Betriebssystem, Browser, Docker-Version

### 💡 Feature vorschlagen
Ebenfalls als [Issue](https://github.com/freddykrueger88/JobHunter/issues/new) mit dem Label `enhancement`. Bitte zuerst prüfen ob ein ähnlicher Vorschlag bereits existiert.

### 🔧 Code beitragen
- Bugfixes, neue Features, Performance-Verbesserungen
- Bitte immer zuerst ein Issue öffnen und kurz abstimmen, bevor du große Änderungen anfängst

### 📖 Dokumentation verbessern
- Tippfehler, unkläre Stellen, fehlende Erklärungen
- Übersetzungen (DE ↔ EN)

---

## 3. Entwicklungsumgebung einrichten

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

## 4. Arbeitsablauf (Git)

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

## 5. Commit-Konventionen

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

## 6. Pull Request erstellen

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

## 7. Code-Stil

### Frontend (TypeScript / React)
- Funktionale Komponenten, keine Klassen
- Tailwind CSS für Styling
- `clsx` für bedingte Klassen
- Keine `any`-Types wenn vermeidbar
- Barrierefreiheit beachten: `aria-*`, `role`, Tastaturnavigation

### Backend (Python / FastAPI)
- PEP 8 einhalten
- Async-Funktionen für alle DB-Operationen
- Pydantic-Schemas für alle Request/Response-Typen
- Neue Endpunkte mit OpenAPI-Beschreibung (`summary`, `description`)

### Allgemein
- Kein auskommentierter Code in PRs
- Deutsche Kommentare und Variablennamen sind OK (Projektsprache ist DE/EN)

---

## 8. Fragen & Hilfe

Einfach ein [Issue](https://github.com/freddykrueger88/JobHunter/issues) mit dem Label `question` öffnen. Keine Frage ist zu simpel!

---

> Danke für deinen Beitrag! 🎯
