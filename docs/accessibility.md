# ♿ Accessibility (WCAG 2.1 AA) / Barrierefreiheit

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter was developed according to the **WCAG 2.1 Level AA** guidelines and includes additional inclusion features beyond the standard.

## Supported Inclusion Themes

| Feature | Implementation |
|---------|----------|
| 🌙 Dark / ☀️ Light / 💙 Boys / 🌸 Girls Mode | 4 visual themes |
| 📚 Dyslexia Theme | OpenDyslexic font + reading optimizations |
| 👁️ Deuteranopia (green weakness) | SVG `feColorMatrix` filter |
| 👁️ Protanopia (red weakness) | SVG `feColorMatrix` filter |
| 👁️ Tritanopia (blue-yellow weakness) | SVG `feColorMatrix` filter |
| 👁️ Achromatopsia (complete color blindness) | `feColorMatrix saturate=0` |
| ♿ Screen Reader | Skip link, aria-live, focus management |

## Dyslexia Theme (OpenDyslexic)

- **Font**: OpenDyslexic (SIL Open Font License, locally hosted, GDPR-compliant)
- **Line spacing**: 1.8 (instead of 1.5)
- **Letter spacing**: +0.05em
- **Word spacing**: +0.1em
- **Line length**: max. 65 characters
- **Background**: Cream white #fffef5 (no harsh white – reduces flickering)

### Font Installation
```bash
curl -L https://github.com/antijingoist/opendyslexic/releases/latest/download/OpenDyslexic-Regular.woff2 \
  -o frontend/public/fonts/OpenDyslexic/OpenDyslexic-Regular.woff2
```

## Color Blindness Filters

All filters are rendered as SVG `feColorMatrix` directly in the browser – no JavaScript, no external dependency.
They are applied as CSS classes on `<html>` and can be combined with all themes.

## Screen Reader Support

### Skip Link
First DOM element in `index.html`: `<a href="#main-content">Skip to main content</a>`.
Only visible via Tab key, shown on focus.

### aria-live Regions
Two global regions in `index.html`:
- `#sr-announcer` (`aria-live="polite"`) – non-critical updates
- `#sr-alert` (`role="alert"`) – errors and critical messages

Usage in code via `useAnnounce()` hook:
```tsx
const { announce, alert } = useAnnounce()
announce('12 new jobs loaded')   // Screen reader reads on next pause
alert('Connection error')         // Screen reader reads immediately
```

### Focus Management
Modals use `useFocusTrap(isOpen)` hook:
- Focus is drawn in when opening (first focusable element)
- Tab navigation stays within the modal
- On close: focus returns to the triggering button

## Keyboard Navigation
- All interactive elements reachable via `Tab`
- Active focus always visible via `focus-visible` (2px outline)
- Drag & Drop in Kanban alternatively operable via status buttons
- `Escape` closes modals and inline editors

## Color Contrast
- Dark Mode: Text `#c9d1d9` on `#0d1117` → Contrast 13:1 ✅
- Light Mode: Text `#111827` on `#ffffff` → Contrast 19:1 ✅
- Girls Mode: Text `#7a1a4b` on `#fff0f7` → Contrast 8:1 ✅
- Dyslexia: Text `#1a1a1a` on `#fffef5` → Contrast 18:1 ✅

## Testing Tools
- [axe DevTools](https://www.deque.com/axe/)
- [WAVE](https://wave.webaim.org/)
- NVDA + Firefox (Windows)
- VoiceOver + Safari (macOS / iOS)
- Lighthouse Accessibility Score: **98/100**

---
---

## Deutsch

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
curl -L https://github.com/antijingoist/opendyslexic/releases/latest/download/OpenDyslexic-Regular.woff2 \
  -o frontend/public/fonts/OpenDyslexic/OpenDyslexic-Regular.woff2
```

## Farbenblindheits-Filter

Alle Filter werden als SVG `feColorMatrix` direkt im Browser gerendert – kein JavaScript, keine externe Abhängigkeit.

## Screenreader-Unterstützung

### Skip-Link
Erstes DOM-Element in `index.html`: `<a href="#main-content">Zum Hauptinhalt springen</a>`.

### aria-live Regionen
- `#sr-announcer` (`aria-live="polite"`) – nicht-kritische Updates
- `#sr-alert` (`role="alert"`) – Fehler und kritische Meldungen

```tsx
const { announce, alert } = useAnnounce()
announce('12 neue Stellen geladen')
alert('Verbindungsfehler')
```

## Tastaturnavigation
- Alle interaktiven Elemente per `Tab` erreichbar
- Fokus immer sichtbar via `focus-visible` (2px Outline)
- `Escape` schließt Modale

## Farbkontrast
- Dark Mode: 13:1 ✅ | Light Mode: 19:1 ✅ | Girls Mode: 8:1 ✅ | Legasthenie: 18:1 ✅

## Prüftools
- [axe DevTools](https://www.deque.com/axe/) · [WAVE](https://wave.webaim.org/) · NVDA · VoiceOver
- Lighthouse Accessibility Score: **98/100**
