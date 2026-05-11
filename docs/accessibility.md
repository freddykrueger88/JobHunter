# Barrierefreiheit (WCAG 2.1 AA)

JobHunter wurde nach den Richtlinien der **WCAG 2.1 Level AA** entwickelt.

## Umgesetzte Maßnahmen

### 1. Tastaturnavigation
- Alle interaktiven Elemente (Buttons, Links, Inputs, Selects) sind per `Tab` erreichbar
- Aktiver Fokus ist immer sichtbar via `focus-visible` (2px Outline)
- Drag & Drop im Kanban-Board ist alternativ per Status-Buttons im Detail-Modal bedienbar
- Modal-Dialoge fangen den Fokus (`role="dialog"`, `aria-modal="true"`)

### 2. ARIA-Attribute
- Navigationsleiste: `role="navigation"`, `aria-label="Hauptnavigation"`
- Menüeinträge: `role="menubar"` / `role="menuitem"`
- Toggle-Buttons: `aria-pressed` (Theme, Ton, Sprache, Status)
- Formular-Inputs: alle haben `aria-label` oder verknüpftes `<label>`
- Icons: `aria-hidden="true"` auf allen dekorativen SVG-Icons
- Modale: `aria-label` auf dem Dialog-Container

### 3. Farbkontrast
- Dark Mode: Text `#c9d1d9` auf `#0d1117` → Kontrast 13:1 ✅
- Light Mode: Text `#111827` auf `#ffffff` → Kontrast 19:1 ✅
- Girls Mode: Text `#7a1a4b` auf `#fff0f7` → Kontrast 8:1 ✅
- Interaktive Elemente haben immer min. 4.5:1 Kontrast

### 4. Semantisches HTML
- Seitenstruktur: `<nav>`, `<main>`, `<section>`, `<h1>`–`<h2>`, `<ul>`/`<li>`
- Keine `div`-Suppe für strukturelle Inhalte
- Tabellen nur für tabellarische Daten (keine Layout-Tabellen)

### 5. Screenreader-Kompatibilität
- Getestet mit NVDA + Firefox (Windows)
- Emoji in Überschriften haben `aria-hidden` wo störend
- Ladezustände geben Text-Feedback (`Lädt...`)
- Fehlermeldungen sind inline, nicht nur visuell

### 6. Responsive & Zoom
- Layout funktioniert bei 200% Zoom ohne horizontales Scrollen
- Mobile Breakpoint: Icons-only Navigation unter `sm`
- Mindest-Touch-Target: 44×44px für alle Buttons

### 7. Reduzierte Bewegung
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
Diese Regel ist in `index.css` enthalten.

## Bekannte Einschränkungen
- Drag & Drop ist für Screenreader-Nutzer nur über das Modal bedienbar (akzeptiertes Trade-off)
- PDF-Download von Anschreiben: Dateiname nicht anpassbar in v1.0

## Prüftools
- [axe DevTools](https://www.deque.com/axe/)
- [WAVE](https://wave.webaim.org/)
- Lighthouse Accessibility Score: **98/100** (gemessen auf Dashboard)
