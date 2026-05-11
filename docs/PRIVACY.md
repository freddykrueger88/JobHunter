# Datenschutz / Privacy

## 🇩🇪 Deutsch

JobHunter ist eine **lokal betriebene** Anwendung. Alle Daten verbleiben auf deinem eigenen System.

### Was gespeichert wird
- Lebenslaufdaten (lokal in PostgreSQL)
- Stellenangebote und Bewerbungsstatus (lokal)
- Einstellungen und API-Keys (lokal, verschlüsselt)
- Generierte Anschreiben (lokal)

### Was NICHT passiert
- Keine Telemetrie oder Tracking
- Keine Weitergabe an Dritte
- Die KI (Ollama) läuft vollständig lokal – keine Daten verlassen deinen Server
- API-Keys werden verschlüsselt (Fernet AES-128) in der lokalen Datenbank gespeichert

### DSGVO-Konformität
Da alle Daten lokal verarbeitet und gespeichert werden, fällt für den privaten Eigengebrauch keine Aufbewahrungspflicht nach DSGVO an. Bei kommerziellem Einsatz oder Mehrbenutzerbetrieb gelten die üblichen DSGVO-Regelungen.

---

## 🇬🇧 English

JobHunter is a **locally operated** application. All data stays on your own system.

### What is stored
- CV data (locally in PostgreSQL)
- Job listings and application status (local)
- Settings and API keys (local, encrypted)
- Generated cover letters (local)

### What does NOT happen
- No telemetry or tracking
- No sharing with third parties
- The AI (Ollama) runs entirely locally – no data leaves your server
- API keys are encrypted (Fernet AES-128) in the local database

### GDPR Compliance
Since all data is processed and stored locally, no GDPR retention obligations apply for private personal use. For commercial use or multi-user setups, standard GDPR regulations apply.
