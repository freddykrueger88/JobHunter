# 🔒 Sicherheitsrichtlinie

## Unterstützte Versionen

Sicherheits-Updates werden nur für die jeweils aktuelle Version bereitgestellt.

| Version | Unterstützt |
|---|---|
| aktuell (`main`) | ✅ Ja |
| ältere Versionen | ❌ Nein |

---

## 🐛 Sicherheitslücke melden

> ⚠️ **Bitte Sicherheitslücken NICHT als öffentliches Issue melden.**

Wenn du eine Sicherheitslücke entdeckt hast, melde sie **vertraulich** über GitHub:

**→ [Sicherheitslücke melden](https://github.com/freddykrueger88/JobHunter/security/advisories/new)**

Alternativ reicht eine Beschreibung per Issue mit dem Label `security` (ohne sensible Details).

---

## 💬 Was eine gute Meldung enthält

Bitte so viele Details wie möglich mitgeben:

- **Typ der Lücke** (z.B. SQL-Injection, XSS, CSRF, unsichere Deserialisierung, ...)
- **Betroffene Komponente** (Frontend, Backend, Docker-Konfiguration, ...)
- **Schritte zur Reproduktion** – so konkret wie möglich
- **Auswirkung** – was kann ein Angreifer damit erreichen?
- **Vorschlag zur Behebung** (optional, aber sehr willkommen)

---

## ⏱️ Reaktionszeit

| Schritt | Zeitrahmen |
|---|---|
| Bestätigung des Eingangs | innerhalb 48 Stunden |
| Erste Einschätzung | innerhalb 7 Tage |
| Behebung & Release | abhängig von Komplexität |

---

## 🛡️ Sicherheitsarchitektur (zur Information)

JobHunter ist ein **vollständig lokales** Tool. Es gibt standardmäßig keine externen Verbindungen außer:
- Optionale Job-Portale (Adzuna, Bundesagentur, LinkedIn) – nur wenn API-Keys gesetzt sind
- Ollama läuft lokal im Docker-Container

### Implementierte Schutzmaßnahmen
- **AES-256-Verschlüsselung** für alle gespeicherten API-Keys (Fernet)
- **Optionale JWT-Authentifizierung** (`AUTH_ENABLED=true` in `.env`)
- **Keine Telemetrie**, keine externen Tracking-Dienste
- **Alembic-Migrationen** für sichere Datenbank-Schemaänderungen
- **DSGVO-konform** – alle Daten verbleiben lokal

---

## 🏆 Responsible Disclosure

Wir bitten um **Responsible Disclosure**: Bitte keine öffentliche Veröffentlichung, bevor die Lücke behoben ist. Wir bemühen uns um schnelle Reaktion und nennen Finder in der Release-Note (sofern gewünscht).
