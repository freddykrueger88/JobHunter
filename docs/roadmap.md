# JobHunter Roadmap

## Status

| Version | Thema | Status |
|---------|-------|--------|
| v1.0 | Kern-Features (Backend, Frontend, KI, DSGVO, WCAG) | ✅ Fertig |
| v1.1 | Export, PDF, Cron, Portale, JWT, Alembic | ✅ Fertig |
| v1.2 | Inklusion & Barrierefreiheit | ✅ Fertig |
| v1.3 | Mobil & Basis-Produktivität | ✅ Fertig |
| v1.4 | Smarte Suche & Datenanalyse | ✅ Fertig |
| v1.5 | KI-Tiefe | ✅ Fertig |
| v1.6 | Kommunikation & Workflow | ✅ Fertig |
| v1.7 | Statistiken & Motivation | ✅ Fertig |
| v1.8 | ATS-Optimierung & Bewerbungsqualität | 🚧 In Arbeit |
| v1.9 | Bewerbungscoach & Automatisierung | 📌 Geplant |

---

## v1.8 – ATS-Optimierung & Bewerbungsqualität

> Hintergrund: 75% aller Bewerbungen werden von ATS-Systemen gefiltert, bevor ein Mensch sie liest.
> JobHunter hilft, genau das zu überwinden – lokal, ohne Cloud-Dienst.

### #57 – ATS-Score-Checker

**Problem:** Bewerber wissen nicht, ob ihr Lebenslauf ein ATS-System passiert.

**Lösung:**
- KI vergleicht CV vs. Stellenbeschreibung auf Keyword-Übereinstimmung
- Score 0–100 mit Ampel-Anzeige (< 50 🔴, 50–70 🟡, > 70 🟢)
- Listet fehlende Keywords mit Kontext: _"Erwähne Linux in deinem Erfahrungsabschnitt"
- ATS-Parser-Check: Erkennt problematische Formatierungen (Tabellen, SVG-Icons, Mehrspalter)
- Dateien: `backend/services/ats_scorer.py`, `frontend/src/components/AtsScorePanel.tsx`

### #58 – Ghost-Job-Erkennung

**Problem:** Viele Stellenanzeigen sind veraltet ("Ghost Jobs") – Zeitverschwendung.

**Lösung:**
- Analysiert Verhaltenssignale: Veraltetes Datum, generische Beschreibung, fehlende Ansprechperson
- Heuristik-Score: Datum (>30 Tage), kein konkreter Name, keine Gehaltsspanne, Boilerplate-Text
- Badge ⚠️ "Möglicherweise Ghost Job" in der Stellenliste
- Dateien: `backend/services/ghost_job_detector.py`, `frontend/src/components/GhostJobBadge.tsx`

### #59 – Bewerbungs-Qualitätsscore

**Problem:** Nutzer wissen nicht, wie vollständig ihre Bewerbungsunterlagen sind.

**Lösung:**
- Checkliste pro Bewerbung: Anschreiben, CV, Anschreiben-Score, Skill-Gap, ATS-Check
- Gesamt-Score 0–100 aus gewichteten Einzelscores
- "Verbessern"-Schnelllink direkt zum fehlenden Element
- Dateien: `backend/services/application_quality.py`, `frontend/src/components/QualityScoreCard.tsx`

### #60 – Gehaltsnegotiations-Coach

**Problem:** Die meisten Bewerber kennen ihren Marktwert nicht und verhandeln nicht.

**Lösung:**
- KI generiert Verhandlungsstrategie basierend auf: Stelle, Region, eigene Erfahrung, Gehaltsband der Anzeige
- 3 Szenarien: konservativ / realistisch / optimistisch
- Konkrete Formulierungen für E-Mail und Telefonat
- Kombination mit dem vorhandenen Gehaltsrechner (v1.6)
- Dateien: `backend/services/salary_negotiation.py`, `frontend/src/components/SalaryNegotiationModal.tsx`

### #61 – Marktlage-Analyse pro Stelle

**Problem:** Wie umkämpft ist eine Stelle wirklich? Wann sollte man sich bewerben?

**Lösung:**
- KI analysiert Beschreibung auf Signale: Dringlichkeit, Team-Wachstum, Fluktuation, Startup vs. Konzern
- Gibt Einschätzung: Wettbewerb (niedrig/mittel/hoch), optimaler Zeitpunkt (sofort vs. 1 Woche warten)
- Bewerbungsstrategie-Empfehlung ("Direkt bewerben" vs. "Erst LinkedIn-Kontakt suchen")
- Dateien: `backend/services/market_analyzer.py`

---

## v1.9 – Bewerbungscoach & Automatisierung

> Fokus: Den Bewerber aktiv begleiten – nicht nur tracken, sondern coachen und automatisieren.

### #62 – Bewerbungscoach-Chat

**Problem:** Bewerber wissen oft nicht wie sie bestimmte Situationen formulieren sollen.

**Lösung:**
- KI-Chatbot direkt in der App (lokal via Ollama)
- Kontextbewusst: Kennt die aktuelle Bewerbung (Stelle, Status, Dokumente)
- Beispiel-Fragen: "Wie formuliere ich eine Absage höflich?", "Wann sollte ich nachfassen?", "Wie erkläre ich meine Karrierelücke?"
- Chat-Verlauf wird gespeichert (pro Bewerbung)
- Dateien: `backend/services/coach_chat.py`, `frontend/src/components/CoachChatDrawer.tsx`

### #63 – Auto-Apply-Vorbereitung (1-Klick-Paket)

**Problem:** Bewerber müssen Anschreiben, CV und Formulardaten jedes Mal manuell zusammensuchen.

**Lösung:**
- 1-Klick-Export: Anschreiben (PDF) + CV (PDF) + Metadaten (JSON) als ZIP
- Dateiname automatisch generiert: `Bewerbung_Firma_Stelle_Datum.zip`
- Vorschau-Modal zeigt Dateiliste vor Download
- Dateien: `backend/services/auto_apply.py`, `frontend/src/components/AutoApplyButton.tsx`

### #64 – Wiedervorlagen-System mit Erinnerungen

**Problem:** Bewerber vergessen nachzufassen – eine der häufigsten Ursachen für verpasste Chancen.

**Lösung:**
- "Nachfassen in X Tagen" direkt bei jeder Bewerbung setzbar (1 / 3 / 7 / 14 Tage)
- Dashboard zeigt fällige Wiedervorlagen mit Ampel-Farbe (heute 🔴, morgen 🟡, später 🟢)
- Vorgefertigte E-Mail-Vorlage für Nachfass-Mail (per Klick in Clipboard kopieren)
- Dateien: `backend/services/followup_scheduler.py`, `frontend/src/components/FollowUpWidget.tsx`

---

## Zukunft (v2.0+)

| Feature | Beschreibung |
|---------|-------------|
| Browser-Extension | Stellenanzeige per Klick direkt aus Browser in JobHunter importieren |
| Multi-User-Support | Mehrere Profile lokal verwalten |
| Mobile App (React Native) | Native App für Android/iOS |

---

## Prinzipien

- Lokal vor cloudbasiert
- Datenschutz zuerst
- Barrierefreiheit in jeder Version
- Keine externen Abhängigkeiten ohne Opt-in
