# Konfiguration

Hier sind die wichtigsten Konfigurationsoptionen von JobHunter zusammengefasst.

## Einstellungen in der App

### Erscheinungsbild

Verfügbare Themes:

- Dark Mode
- Light Mode
- Boys Mode
- Girls Mode
- Legasthenie-Modus

### Farbenblindheits-Filter

Zusätzliche Darstellungsfilter:

- Kein Filter
- Deuteranopie
- Protanopie
- Tritanopie
- Achromatopsie

### ADHS & Kognition

- ADHS-Modus
- Fokus-Modus
- Animationen deaktivieren
- Informationsdichte: normal / kompakt / minimal

### Sprache

- Deutsch
- Englisch

### KI

- Modell-Auswahl
- Schreibstil / Ton

### Stellensuche

- Standard-Ort
- Suchradius
- Ausbildungsstellen ausblenden

### Erinnerungen

- Standard-Vorlaufzeit in Tagen
- E-Mail-Versand bei Fälligkeit

## API-Keys

Unterstützte Integrationen:

- Adzuna
- Arbeitsagentur
- LinkedIn

API-Keys werden verschlüsselt gespeichert.

## Authentifizierung

Optional aktivierbar über `.env`:

```env
AUTH_ENABLED=true
```

Dann stehen JWT-Endpunkte zur Verfügung:

- `/auth/register`
- `/auth/token`
- `/auth/change-password`

## Mail-Versand

SMTP-Felder in den Einstellungen:

- Host
- Port
- Benutzer
- Passwort
- Empfängeradresse

Der Reminder-Cron prüft standardmäßig alle 15 Minuten fällige Einträge.
