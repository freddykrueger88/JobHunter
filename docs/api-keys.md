# 🔑 API Keys Setup / API-Keys einrichten

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter works **without any API keys** out of the box. Keys are optional and unlock additional job portals.
All keys are stored **AES-256 encrypted** in the local database – never in plain text.

## Overview

| Portal | Required? | Cost | What it unlocks |
|---|---|---|---|
| Bundesagentur für Arbeit | ❌ No | Free | Works without key (higher rate limit with key) |
| StepStone | ❌ No | Free | Works via scraping |
| **Adzuna** | Optional | Free | Millions of jobs worldwide (Indeed, Monster, etc.) |
| **LinkedIn** | Optional | Free* | LinkedIn jobs directly |

*LinkedIn API access requires approval and can take several days.

## Adzuna (recommended)

Adzuna aggregates millions of job listings from Indeed, Monster, Totaljobs and many more.

### Step 1 – Register
1. Go to https://developer.adzuna.com/
2. Click **"Sign Up"**
3. Confirm email

### Step 2 – Create App
1. Log in → **"My Apps"** → **"Create App"**
2. Name: `JobHunter` (or anything)
3. You will receive:
   - `App ID` (e.g. `a1b2c3d4`)
   - `App Key` (e.g. `e5f6g7h8i9j0...`)

### Step 3 – Enter in JobHunter
1. Open http://localhost:3000
2. **Settings** → **🔑 API Keys**
3. Enter `App ID` and `App Key`
4. Click **Save** → green checkmark = connected ✅

### Limits
- 1,000 requests/day (free tier)
- Resets daily at midnight UTC
- For personal use: more than enough

---

## LinkedIn

> ⚠️ LinkedIn API access is **restrictive** and requires manual approval. This can take days to weeks.
> **Alternative**: Adzuna already aggregates many LinkedIn jobs.

### Step 1 – Create Developer App
1. Go to https://developer.linkedin.com/
2. Log in with your LinkedIn account
3. **"Create App"**
4. Fill in: App name (`JobHunter`), LinkedIn Page (your profile), App logo

### Step 2 – Request Products
1. In the app → **"Products"** tab
2. Request **"Job Search"** or **"Sign In with LinkedIn"**
3. Wait for approval (1–7 days)

### Step 3 – Get Credentials
1. **"Auth"** tab → copy `Client ID` and `Client Secret`
2. Add Redirect URL: `http://localhost:8000/auth/linkedin/callback`

### Step 4 – Enter in JobHunter
1. **Settings** → **🔑 API Keys**
2. Enter `Client ID` and `Client Secret`
3. Click **Connect LinkedIn** → OAuth2 flow opens

---

## Bundesagentur für Arbeit (optional)

Works without a key. With a registered Client ID you get a higher rate limit.

1. Go to https://jobsuche.api.bund.dev/
2. Register → receive `Client ID`
3. **Settings** → **🔑 API Keys** → enter `BA Client ID`

---

## Security

- All keys are encrypted with **Fernet AES-128** before being stored in the database
- Keys are never written to logs or `.env` files
- To rotate: delete old key in settings, enter new one
- Full reset: `docker compose down -v` (deletes all data including keys)

---
---

## Deutsch

JobHunter funktioniert **ohne API-Keys** direkt nach der Installation. Keys sind optional und schalten weitere Jobportale frei.
Alle Keys werden **AES-256-verschlüsselt** in der lokalen Datenbank gespeichert – nie im Klartext.

## Übersicht

| Portal | Pflicht? | Kosten | Was es freischaltet |
|---|---|---|---|
| Bundesagentur für Arbeit | ❌ Nein | Kostenlos | Funktioniert ohne Key (höheres Rate-Limit mit Key) |
| StepStone | ❌ Nein | Kostenlos | Funktioniert via Scraping |
| **Adzuna** | Optional | Kostenlos | Millionen Jobs weltweit |
| **LinkedIn** | Optional | Kostenlos* | LinkedIn-Jobs direkt |

## Adzuna (empfohlen)

### Schritt 1 – Registrieren
1. https://developer.adzuna.com/ aufrufen
2. **"Sign Up"** klicken → E-Mail bestätigen

### Schritt 2 – App erstellen
1. Einloggen → **"My Apps"** → **"Create App"**
2. Du erhältst `App ID` und `App Key`

### Schritt 3 – In JobHunter eintragen
1. http://localhost:3000 öffnen
2. **Einstellungen** → **🔑 API Keys**
3. `App ID` und `App Key` eintragen → **Speichern** → grüner Haken = verbunden ✅

### Limits
- 1.000 Anfragen/Tag (kostenloses Kontingent)
- Für privaten Gebrauch mehr als ausreichend

---

## LinkedIn

> ⚠️ LinkedIn-API-Zugang ist **restriktiv** und erfordert manuelle Genehmigung (kann Tage bis Wochen dauern).
> **Alternative**: Adzuna aggregiert bereits viele LinkedIn-Jobs.

### Schritte
1. https://developer.linkedin.com/ aufrufen → einloggen
2. **"Create App"** → App-Name, LinkedIn-Seite, Logo angeben
3. Tab **"Products"** → **"Job Search"** beantragen
4. Nach Genehmigung: `Client ID` und `Client Secret` aus Tab **"Auth"** kopieren
5. Redirect-URL hinzufügen: `http://localhost:8000/auth/linkedin/callback`
6. In JobHunter: **Einstellungen** → **🔑 API Keys** → eintragen → **LinkedIn verbinden**

---

## Bundesagentur für Arbeit (optional)

1. https://jobsuche.api.bund.dev/ aufrufen → registrieren → `Client ID` erhalten
2. **Einstellungen** → **🔑 API Keys** → `BA Client ID` eintragen

---

## Sicherheit

- Alle Keys werden mit **Fernet AES-128** verschlüsselt vor dem Speichern
- Keys werden nie in Logs oder `.env`-Dateien geschrieben
- Rotieren: alten Key in Einstellungen löschen, neuen eintragen
- Komplett-Reset: `docker compose down -v` (löscht alle Daten inkl. Keys)
