# JobHunter – Repository-Audit (Deutsch)

> **Status dieses Dokuments:** Entwurf, wird abschnittsweise befüllt (siehe
> `docs/analysis/BACKLOG.md` für den Fortschritt). Englische Fassung:
> `docs/analysis/REPOSITORY_AUDIT_EN.md` (wird parallel gepflegt, sobald ein
> Abschnitt hier final ist).
>
> Stand: 2026-08-24. Alle Aussagen beruhen auf tatsächlicher Sichtung des
> Checkouts in LXC 142 (`/root/JobHunter`, Branch `main`,
> Remote `https://github.com/freddykrueger88/JobHunter.git`).

## 1. Projektinventur

### 1.1 Projektstruktur & Modulgrenzen

JobHunter ist ein Monorepo mit klarer Trennung in vier Docker-Services
(siehe `docker-compose.yml`):

| Verzeichnis | Rolle | Technologie (Ist-Stand) |
|---|---|---|
| `backend/` | REST-API, Business-Logik, DB-Zugriff | Python 3.11, FastAPI 0.111.0, SQLAlchemy 2.0.30 (async, via `asyncpg`), Alembic 1.13.1 |
| `frontend/` | Single-Page-Application | React 18.3.1, Vite 5.2.13, TypeScript 5.4.5, TailwindCSS 3.4.4, i18next 23.11.5 / react-i18next 14.1.2 |
| `db` (Compose-Service) | Persistenz | PostgreSQL (Image aus `docker-compose.yml`, siehe Abschnitt Datenbank) |
| `ollama` (Compose-Service) | Lokale KI-Inferenz | Ollama, Modelle werden zur Laufzeit gezogen (aktuell u. a. `mistral`) |

Weitere Top-Level-Bereiche:

- `docs/` – 11 Themen-Dokumente (u. a. `architecture.md`, `dsgvo.md`,
  `PRIVACY.md`, `accessibility.md`, `roadmap.md`, `faq.md`,
  `backup-restore.md`, `ai-models.md`, `api-keys.md`, `portals.md`,
  `setup.md`). Mehrere Dateien sind bereits als Ein-Seiten-DE/EN-Mix
  aufgebaut (Abschnitt „## Deutsch" / „## English" in derselben Datei),
  z. B. `architecture.md`, `CHANGELOG.md` – ein anderes Muster als das vom
  Auftrag geforderte Schema mit getrennten Seiten pro Sprache.
- `wiki/` – 6 Markdown-Dateien (`Home.md`, `Installation.md`,
  `Konfiguration.md`, `Entwicklung.md`, `Barrierefreiheit.md`,
  `Changelog.md`), **nur Deutsch**, direkt im Hauptrepo getrackt (nicht der
  separate `JobHunter.wiki.git`-Git-Baum, den GitHub für echte Wikis
  verwendet – siehe Abschnitt CI/CD & Publishing).
- `alembic/` (Top-Level) **und** `backend/alembic/` – zwei Alembic-Bäume
  gleichzeitig vorhanden (`alembic.ini` + `backend/alembic.ini`). **Offene
  Frage / Risiko:** unklar, ob der Top-Level-Baum noch aktiv genutzt wird
  oder ein Überbleibsel einer früheren Struktur ist – muss vor jeder
  Migrations-Änderung geklärt werden (potenzielle Quelle für inkonsistente
  Schema-Historie).
- `.github/` – ausschließlich Issue-Templates (`bug.md`, `feature.md`,
  `accessibility.md`, `docs.md`, `config.yml`) und `PULL_REQUEST_TEMPLATE.md`.
  **Kein `.github/workflows/`-Ordner vorhanden – keinerlei CI/CD-Automatisierung
  aktuell im Repo.**
- Root-Dokumente: `README.md` (Englisch, führend im Repo-Root),
  `README.de.md` (Deutsch, aus README.md heraus verlinkt), `CHANGELOG.md`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`,
  `LICENSE` (MIT laut README-Badge), `CITATION.cff`, `HUMANS.md`,
  `INSTALL.md`.
- `scripts/setup.sh` – einziges Hilfsskript auf Top-Level.

### Beobachtung zur Sprachführung (projektübergreifend)

Der Ist-Zustand ist uneinheitlich zwischen drei Mustern:

1. **Datei-Duplikat pro Sprache**: `README.md` (EN) / `README.de.md` (DE).
2. **Eine Datei, zwei Abschnitte**: `docs/architecture.md`,
   `docs/CHANGELOG.md` – DE/EN über Anker (`#deutsch` / `#english`) in
   derselben Datei.
3. **Nur eine Sprache**: `wiki/*.md` (nur Deutsch), die meisten übrigen
   `docs/*.md` (bisher nicht im Detail geprüft, folgt in 1.2 ff.).

Das im Auftrag geforderte Schema (getrennte Seiten `Seite` / `Seite-English`)
existiert im Ist-Zustand **nicht** – das ist eine bewusste
Architekturentscheidung für Phase 5, kein Bug.

### Offene Fragen aus diesem Abschnitt

- Zweck des doppelten Alembic-Baums (`/alembic` vs. `/backend/alembic`)
  ungeklärt – wird in Abschnitt „Datenbank/Migrationen" (Backlog-Item 1.4)
  vertieft.
- Ob `docs/` und `wiki/` bewusst redundant geführt werden (z. B. `docs/`
  für Entwickler, `wiki/` für Endnutzer) oder historisch gewachsen sind,
  ist aus dem Code allein nicht zweifelsfrei zu beantworten – als Annahme
  markiert, nicht als Fakt.

---

*Fortsetzung folgt (1.2 Frontend-Bestandsaufnahme, 1.3 Backend-Bestandsaufnahme, …) gemäß `docs/analysis/BACKLOG.md`.*
