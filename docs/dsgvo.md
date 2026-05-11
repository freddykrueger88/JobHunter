# 🔒 Privacy & GDPR / Datenschutz & DSGVO

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter is a **locally operated** application (self-hosted via Docker).
**No data is transferred to external servers**, except to services explicitly configured by the user.

## Data Processed

| Data Category | Where Stored | Purpose | Legal Basis |
|---|---|---|---|
| CV (PDF/DOCX) | Local `/app/uploads/` | CV parsing | Art. 6(1)(b) GDPR |
| Extracted CV data | PostgreSQL (local) | Cover letter generation | Art. 6(1)(b) GDPR |
| Application data | PostgreSQL (local) | Application management | Art. 6(1)(b) GDPR |
| API keys | PostgreSQL (encrypted, AES-256) | Job search | Art. 6(1)(a) GDPR |
| Settings | PostgreSQL + localStorage | Personalization | Art. 6(1)(a) GDPR |
| Theme / Language | localStorage (browser) | UI personalization | Art. 6(1)(a) GDPR |

## External Services (opt-in)

### Bundesagentur für Arbeit (Job Search API)
- **Data transmitted**: search term, location, radius
- **No personal data** is transmitted
- Privacy policy: https://www.arbeitsagentur.de/datenschutz

### Adzuna
- **Data transmitted**: search term, location, radius, app ID, API key
- Only active when API key is set in settings
- Privacy policy: https://www.adzuna.de/privacy

### Ollama (AI)
- Runs **entirely locally** in the Docker container
- No data transfer to the internet
- Models: Mistral, LLaMA3, Phi-3 (stored locally)

## Data Security

- **AES-256 encryption** for all stored API keys (Fernet)
- PostgreSQL runs in Docker network (not publicly accessible)
- Uploads stored in `/app/uploads/` (Docker volume), supported formats only

## Data Subject Rights (GDPR Art. 15–22)

Since JobHunter is **locally operated**, full data control rests with the user:

| Right | Implementation |
|---|---|
| Access (Art. 15) | All data viewable directly in the app |
| Rectification (Art. 16) | Applications, CV, settings editable |
| Erasure (Art. 17) | Delete CV removes file; DB data deletable |
| Portability (Art. 20) | History & applications as JSON export |
| Objection (Art. 21) | Individual API services can be disabled at any time |

## Controller
Since JobHunter is a private self-hosted tool, the operator of each instance is responsible for data processing (Art. 4(7) GDPR).

---
---

## Deutsch

JobHunter ist eine **lokal betriebene** Anwendung (Self-Hosted via Docker).
Es werden **keine Daten an externe Server übertragen**, außer an die explizit vom Nutzer konfigurierten Dienste.

## Verarbeitete Daten

| Datenkategorie | Wo gespeichert | Zweck | Rechtsgrundlage |
|---|---|---|---|
| Lebenslauf (PDF/DOCX) | Lokal `/app/uploads/` | CV-Parsing | Art. 6 Abs. 1 lit. b DSGVO |
| Extrahierte CV-Daten | PostgreSQL (lokal) | Anschreiben-Generierung | Art. 6 Abs. 1 lit. b DSGVO |
| Bewerbungsdaten | PostgreSQL (lokal) | Bewerbungsverwaltung | Art. 6 Abs. 1 lit. b DSGVO |
| API-Keys | PostgreSQL (verschlüsselt, AES-256) | Stellensuche | Art. 6 Abs. 1 lit. a DSGVO |
| Einstellungen | PostgreSQL + localStorage | Personalisierung | Art. 6 Abs. 1 lit. a DSGVO |
| Theme / Sprache | localStorage (Browser) | UI-Personalisierung | Art. 6 Abs. 1 lit. a DSGVO |

## Externe Dienste (opt-in)

### Bundesagentur für Arbeit
- Übertragene Daten: Suchbegriff, Ort, Radius – keine personenbezogenen Daten
- Datenschutz: https://www.arbeitsagentur.de/datenschutz

### Adzuna
- Nur aktiv wenn API-Key gesetzt – Datenschutz: https://www.adzuna.de/privacy

### Ollama (KI)
- Läuft vollständig lokal – keine Datenübertragung

## Betroffenenrechte (DSGVO Art. 15–22)

| Recht | Umsetzung |
|---|---|
| Auskunft (Art. 15) | Alle Daten direkt in der App einsehbar |
| Berichtigung (Art. 16) | Bewerbungen, CV, Einstellungen editierbar |
| Löschung (Art. 17) | CV löschen entfernt auch die Datei |
| Portabilität (Art. 20) | JSON-Export |
| Widerspruch (Art. 21) | API-Dienste jederzeit abschaltbar |

## Verantwortlicher
Da JobHunter ein privates Self-Hosted-Tool ist, ist der jeweilige Betreiber verantwortlich (Art. 4 Nr. 7 DSGVO).
