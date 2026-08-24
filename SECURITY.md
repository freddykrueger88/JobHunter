# 🔒 Security Policy / Sicherheitsrichtlinie

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

### Supported Versions

Security updates are only provided for the current version.

| Version | Supported |
|---|---|
| current (`main`) | ✅ Yes |
| older versions | ❌ No |

---

### 🐛 Reporting a Vulnerability

> ⚠️ **Please do NOT report security vulnerabilities as a public issue.**

If you have discovered a security vulnerability, please report it **confidentially** via GitHub:

**→ [Report a vulnerability](https://github.com/freddykrueger88/JobHunter/security/advisories/new)**

Alternatively, open an issue with the label `security` (without sensitive details).

---

### 💬 What makes a good report

Please include as many details as possible:

- **Type of vulnerability** (e.g. SQL injection, XSS, CSRF, insecure deserialization, ...)
- **Affected component** (Frontend, Backend, Docker configuration, ...)
- **Steps to reproduce** – as concrete as possible
- **Impact** – what can an attacker achieve with this?
- **Suggested fix** (optional, but very welcome)

---

### ⏱️ Response Times

| Step | Timeframe |
|---|---|
| Confirmation of receipt | within 48 hours |
| Initial assessment | within 7 days |
| Fix & release | depending on complexity |

---

### 🛡️ Security Architecture (for reference)

JobHunter is a **fully local** tool. By default there are no external connections except:
- Optional job portals (Adzuna, Bundesagentur, LinkedIn) – only when API keys are set
- Ollama runs locally in the Docker container

#### Implemented protections
- **AES-256 encryption** for all stored API keys (Fernet)
- **No telemetry**, no external tracking services
- **Alembic migrations** for safe database schema changes
- **GDPR-compliant** – all data stays local

---

### 🏆 Responsible Disclosure

We ask for **responsible disclosure**: Please no public disclosure before the vulnerability is fixed. We strive for a quick response and will credit finders in the release notes (if desired).

---
---

## Deutsch

### Unterstützte Versionen

Sicherheits-Updates werden nur für die jeweils aktuelle Version bereitgestellt.

| Version | Unterstützt |
|---|---|
| aktuell (`main`) | ✅ Ja |
| ältere Versionen | ❌ Nein |

---

### 🐛 Sicherheitslücke melden

> ⚠️ **Bitte Sicherheitslücken NICHT als öffentliches Issue melden.**

Wenn du eine Sicherheitslücke entdeckt hast, melde sie **vertraulich** über GitHub:

**→ [Sicherheitslücke melden](https://github.com/freddykrueger88/JobHunter/security/advisories/new)**

Alternativ reicht eine Beschreibung per Issue mit dem Label `security` (ohne sensible Details).

---

### 💬 Was eine gute Meldung enthält

Bitte so viele Details wie möglich mitgeben:

- **Typ der Lücke** (z.B. SQL-Injection, XSS, CSRF, unsichere Deserialisierung, ...)
- **Betroffene Komponente** (Frontend, Backend, Docker-Konfiguration, ...)
- **Schritte zur Reproduktion** – so konkret wie möglich
- **Auswirkung** – was kann ein Angreifer damit erreichen?
- **Vorschlag zur Behebung** (optional, aber sehr willkommen)

---

### ⏱️ Reaktionszeit

| Schritt | Zeitrahmen |
|---|---|
| Bestätigung des Eingangs | innerhalb 48 Stunden |
| Erste Einschätzung | innerhalb 7 Tage |
| Behebung & Release | abhängig von Komplexität |

---

### 🛡️ Sicherheitsarchitektur (zur Information)

JobHunter ist ein **vollständig lokales** Tool. Es gibt standardmäßig keine externen Verbindungen außer:
- Optionale Job-Portale (Adzuna, Bundesagentur, LinkedIn) – nur wenn API-Keys gesetzt sind
- Ollama läuft lokal im Docker-Container

#### Implementierte Schutzmaßnahmen
- **AES-256-Verschlüsselung** für alle gespeicherten API-Keys (Fernet)
- **Keine Telemetrie**, keine externen Tracking-Dienste
- **Alembic-Migrationen** für sichere Datenbank-Schemaänderungen
- **DSGVO-konform** – alle Daten verbleiben lokal

---

### 🏆 Responsible Disclosure

Wir bitten um **Responsible Disclosure**: Bitte keine öffentliche Veröffentlichung, bevor die Lücke behoben ist. Wir bemühen uns um schnelle Reaktion und nennen Finder in der Release-Note (sofern gewünscht).
