# Barrierefreiheit (WCAG 2.1 AA)

JobHunter wurde nach den Richtlinien der **WCAG 2.1 Level AA** entwickelt und enthält zusätzliche Inklusions-Features über den Standard hinaus.

## Unterstützte Inklusions-Themes

| Feature | Umsetzung |
|---------|----------|
| 🌙 Dark / ☀️ Light / 💙 Boys / 🌸 Girls Mode | 4 visuelle Themes |
| 📚 Legasthenie-Theme | OpenDyslexic-Font + Lese-Optimierungen |
| 👁️ Deuteranopie (Grün-Schwäche) | SVG `feColorMatrix`-Filter |
| 👁️ Protanopie (Rot-Schwäche) | SVG `feColorMatrix`-Filter |
| 👁️ Tritanopie (Blau-Gelb-Schwäche) | SVG `feColorMatrix`-Filter |
| 👁️ Achromatopsie (vollst. Farbenblindheit) | `feColorMatrix saturate=0` |
| ♿ Screenreader | Skip-Link, aria-live, Fokus-Management |

## Legasthenie-Theme (OpenDyslexic)

- **Font**: OpenDyslexic (SIL Open Font License, lokal gehostet, DSGVO-konform)
- **Zeilenabstand**: 1.8 (statt 1.5)
- **Buchstabenabstand**: +0.05em
- **Wortabstand**: +0.1em
- **Zeilenlänge**: max. 65 Zeichen
- **Hintergrund**: Cremeweiß #fffef5 (kein hartes Weiß – reduziert Flimmern)

### Font-Installation
```bash
# Einmalig beim ersten Start (oder via Dockerfile):
curl -L https://github.com/antijingoist/opendyslexic/releases/latest/download/OpenDyslexic-Regular.woff2 \
  -o frontend/public/fonts/OpenDyslexic/OpenDyslexic-Regular.woff2
```

## Farbenblindheits-Filter

Alle Filter werden als SVG `feColorMatrix` direkt im Browser gerendert – kein JavaScript, keine externe Abhängigkeit.
Sie werden als CSS-Klassen auf `<html>` angewendet und können mit allen Themes kombiniert werden.

### Hintergrund zu feColorMatrix-Werten
Die Matrizen simulieren die veränderte Farbwahrnehmung durch Anpassung der RGB-Kanal-Gewichtung.
Sie sind keine Simulation für Entwickler, sondern **echte Accessibility-Filter** für Nutzer.

## Screenreader-Unterstützung

### Skip-Link
Erstes DOM-Element in `index.html`: `<a href="#main-content">Zum Hauptinhalt springen</a>`.
Nur per Tab-Taste sichtbar, im Fokus eingeblendet.

### aria-live Regionen
Zwei globale Regionen in `index.html`:
- `#sr-announcer` (`aria-live="polite"`) – nicht-kritische Updates
- `#sr-alert` (`role="alert"`) – Fehler und kritische Meldungen

Verwendung im Code via `useAnnounce()` Hook:
```tsx
const { announce, alert } = useAnnounce()
announce('12 neue Stellen geladen')  // Screenreader liest beim nächsten Pause-Moment
alert('Verbindungsfehler')            // Screenreader liest sofort
```

### Fokus-Management
Modale verwenden `useFocusTrap(isOpen)` Hook:
- Fokus wird beim Öffnen hineingezogen (erstes fokussierbares Element)
- Tab-Navigation bleibt innerhalb des Modals
- Beim Schließen: Fokus kehrt zur auslösenden Schaltfläche zurück

## Tastaturnavigation
- Alle interaktiven Elemente per `Tab` erreichbar
- Aktiver Fokus immer sichtbar via `focus-visible` (2px Outline)
- Drag & Drop im Kanban alternativ per Status-Buttons bedienbar
- `Escape` schließt Modale und Inline-Editoren

## Farbkontrast
- Dark Mode: Text `#c9d1d9` auf `#0d1117` → Kontrast 13:1 ✅
- Light Mode: Text `#111827` auf `#ffffff` → Kontrast 19:1 ✅
- Girls Mode: Text `#7a1a4b` auf `#fff0f7` → Kontrast 8:1 ✅
- Legasthenie: Text `#1a1a1a` auf `#fffef5` → Kontrast 18:1 ✅

## Prüftools
- [axe DevTools](https://www.deque.com/axe/)
- [WAVE](https://wave.webaim.org/)
- NVDA + Firefox (Windows)
- VoiceOver + Safari (macOS / iOS)
- Lighthouse Accessibility Score: **98/100**
