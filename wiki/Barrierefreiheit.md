# ♿ Barrierefreiheit

JobHunter erfüllt WCAG 2.1 AA und geht in mehreren Bereichen darüber hinaus – mit konkreten Inklusions-Features für Legasthenie, Farbenblindheit und ADHS.

## WCAG-Basis

- Sichtbarer Fokuszustand für alle interaktiven Elemente
- Vollständige Tastaturbedienbarkeit (Tab, Enter, Escape, Pfeiltasten)
- Kontrastoptimierung (≥ 4,5:1 für Fließtext, ≥ 3:1 für große Texte)
- Mindestgröße für Touch-Ziele (44 × 44 px)
- `prefers-reduced-motion` wird systemweit respektiert
- Semantisches HTML (`<main>`, `<nav>`, `<section>`, `<article>` etc.)
- Überschriftenhierarchie ohne Sprünge

## Screenreader

- **Skip-Link** zu `#main-content` als erstes fokussierbares Element
- **`aria-live="polite"`** für alle Statusmeldungen und asynchrone Updates
- **`role="alert"`** für kritische Fehlermeldungen
- **Fokus-Management** bei Modaldialogen (Fokus-Trap beim Öffnen, Rückgabe beim Schließen)
- **`aria-label`** auf allen Icon-only-Buttons
- **Live-Regions** für Kanban-Status-Updates

## 🔤 Legasthenie-Theme

Aktivierbar in den Einstellungen unter *Erscheinungsbild → Legasthenie-Modus*:

- **OpenDyslexic-Font** – speziell für Legasthenie entwickelte Schriftart
- **Erhöhter Zeilenabstand** (1,8 statt 1,5)
- **Größerer Buchstaben- und Wortabstand**
- **Cremefarbener Hintergrund** statt hartem Weiß (reduziert Flimmern)
- **Begrenzte Zeilenlänge** (max. 65 Zeichen)

> Die Font-Dateien müssen manuell unter `frontend/public/fonts/OpenDyslexic/` abgelegt werden (siehe [[Installation]]).

## 🎨 Farbenblindheits-Filter

SVG-basierte CSS-Filter – aktivierbar pro Typ:

| Filter | Beschreibung |
|---|---|
| Deuteranopie | Grünschwäche |
| Protanopie | Rotschwäche |
| Tritanopie | Blauschwäche |
| Achromatopsie | Vollständige Farbenblindheit |

## 🧠 ADHS & Kognition

- **ADHS-Modus:** reduzierte visuelle Ablenkung, weniger Animationen
- **Fokus-Modus** (`F`): blendet Sidebar und sekundäre Inhalte aus
- **Informationsdichte:** normal · kompakt · minimal
- **Animationen global deaktivierbar**
- **Undo-Toast** nach destruktiven Aktionen (Löschen, Archivieren)
- **Bestätigungsdialoge** vor nicht rückgängig machbaren Aktionen
- **Shortcut-Overlay** (`?`) für schnellen Überblick aller Tastaturkürzel

## ⌨️ Tastaturkürzel

| Kürzel | Aktion |
|---|---|
| `?` | Shortcut-Overlay öffnen |
| `F` | Fokus-Modus ein/aus |
| `Escape` | Aktives Overlay / Modal schließen |
| `G` + `D` | → Dashboard |
| `G` + `K` | → Kanban |
| `G` + `S` | → Stellensuche |
| `G` + `E` | → Einstellungen |

## Weiterführend

Detaillierte technische Dokumentation: [`docs/accessibility.md`](https://github.com/freddykrueger88/JobHunter/blob/main/docs/accessibility.md)
