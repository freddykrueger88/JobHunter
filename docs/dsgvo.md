# Datenschutz & DSGVO-Konformität

JobHunter ist eine **lokal betriebene** Anwendung (Self-Hosted via Docker).
Es werden **keine Daten an externe Server übertragen**, außer an die
explizit vom Nutzer konfigurierten Dienste.

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

### Bundesagentur für Arbeit (Jobsuche API)
- **Übertragene Daten**: Suchbegriff, Ort, Radius
- **Keine personenbezogenen Daten** werden übertragen
- Datenschutzerklärung: https://www.arbeitsagentur.de/datenschutz

### Adzuna
- **Übertragene Daten**: Suchbegriff, Ort, Radius, App-ID, API-Key
- Wird nur aktiv wenn API-Key in den Einstellungen gesetzt
- Datenschutzerklärung: https://www.adzuna.de/privacy

### Ollama (KI)
- Läuft **vollständig lokal** im Docker-Container
- Keine Datenübertragung ins Internet
- Modelle: Mistral, LLaMA3, Phi-3 (lokal gespeichert)

## Datensicherheit

### API-Key-Verschlüsselung
Alle API-Keys werden mit **AES-256-GCM** verschlüsselt gespeichert:
```python
# backend/core/crypto.py
from cryptography.fernet import Fernet
# Schlüssel aus Umgebungsvariable ENCRYPTION_KEY
# Keys werden nie im Klartext geloggt oder angezeigt
```

### Datenbankzugang
- PostgreSQL läuft im Docker-Netzwerk (nicht öffentlich erreichbar)
- Passwort über Umgebungsvariable `POSTGRES_PASSWORD`
- Kein direkter Internetzugang der Datenbank

### Uploads
- Dateien werden in `/app/uploads/` gespeichert (Docker Volume)
- Nur unterstützte Formate: `.pdf`, `.docx`, `.doc`
- Dateiname wird nicht verändert – keine Ausführung möglich

## Betroffenenrechte (DSGVO Art. 15–22)

Da JobHunter **lokal** betrieben wird, liegt die volle Datenkontrolle
beim Nutzer selbst:

| Recht | Umsetzung |
|---|---|
| Auskunft (Art. 15) | Alle Daten direkt in der App einsehbar |
| Berichtigung (Art. 16) | Bewerbungen, CV, Einstellungen editierbar |
| Löschung (Art. 17) | CV löschen entfernt auch die Datei; DB-Daten löschbar |
| Portabilität (Art. 20) | Verlauf & Bewerbungen als JSON-Export (v1.1 geplant) |
| Widerspruch (Art. 21) | Einzelne API-Dienste jederzeit abschaltbar |

## Aufbewahrungsfristen
- Verlaufseinträge: unbegrenzt (manuell löschbar)
- Hochgeladene CVs: unbegrenzt (manuell löschbar)
- Keine automatische Datenlöschung (Nutzer entscheidet selbst)

## Kontakt / Verantwortlicher
Da JobHunter ein privates Self-Hosted-Tool ist, ist der jeweilige
Betreiber der Instanz für die Datenverarbeitung verantwortlich (Art. 4 Nr. 7 DSGVO).
