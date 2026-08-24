# ⚙️ Konfiguration

JobHunter wird über zwei Wege konfiguriert: die `.env`-Datei für systemweite Einstellungen und die In-App-Einstellungen für nutzerspezifische Optionen.

## `.env`-Variablen (systemweit)

| Variable | Pflicht | Beschreibung |
|---|---|---|
| `DB_PASSWORD` | ✅ | PostgreSQL-Passwort |
| `SECRET_KEY` | ✅ | JWT-Signaturschlüssel (token_hex 32) |
| `ENCRYPTION_KEY` | ✅ | Fernet-Key für API-Key-Verschlüsselung |
| `OLLAMA_BASE_URL` | – | Ollama-Endpunkt (Standard: `http://ollama:11434`) |
| `SMTP_HOST` | – | SMTP-Server für E-Mail-Erinnerungen |
| `SMTP_PORT` | – | SMTP-Port (Standard: `587`) |
| `SMTP_USER` | – | SMTP-Benutzername |
| `SMTP_PASSWORD` | – | SMTP-Passwort |

## In-App-Einstellungen

### 🎨 Erscheinungsbild

- **Theme:** Dark Mode · Light Mode · Boys Mode · Girls Mode
- **Legasthenie-Modus:** OpenDyslexic-Font, erhöhter Zeilen- & Buchstabenabstand, cremefarbener Hintergrund
- **Farbenblindheits-Filter:** Deuteranopie · Protanopie · Tritanopie · Achromatopsie
- **Sprache:** Deutsch / Englisch

### 🧠 ADHS & Kognition

- **ADHS-Modus:** reduzierte visuelle Ablenkung
- **Fokus-Modus:** blendet Nebenspalten aus
- **Animationen deaktivieren:** für `prefers-reduced-motion`-Präferenz
- **Informationsdichte:** normal · kompakt · minimal

### 🤖 KI (Ollama)

- **Modell-Auswahl:** Mistral (empfohlen) · LLaMA 3 · Phi-3
- **Schreibstil:** formal · direkt · modern · kreativ
- **Sprache:** automatisch erkannt (DE / EN)

### 🔍 Stellensuche

- **Standard-Ort:** wird für alle Suchanfragen vorbelegt
- **Suchradius:** in km
- **Ausbildungsstellen ausblenden:** filtert Ausbildungsangebote heraus

### 🔔 Erinnerungen

- **Standard-Vorlaufzeit:** Tage vor Deadline für automatische Erinnerung
- **E-Mail-Versand bei Fälligkeit:** benötigt SMTP-Konfiguration
- **Cron-Intervall:** prüft alle 15 Minuten auf fällige Einträge

### 📧 IMAP (E-Mail-Parser)

Automatische Erkennung von Absagen, Einladungen und Follow-ups aus dem Postfach:

- **IMAP-Host / Port**
- **Benutzername / Passwort**
- **Zu überwachender Ordner** (Standard: `INBOX`)
- **Intervall** (Standard: alle 10 Minuten)

### 🔑 API-Keys

Alle API-Keys werden AES-256-verschlüsselt in der Datenbank gespeichert:

| Integration | Verwendung |
|---|---|
| Adzuna | Stellensuche (internationale Jobs) |
| Bundesagentur für Arbeit | Stellensuche (DE) |
| LinkedIn | Stellensuche |
