# Barrierefreiheit

JobHunter enthält Accessibility- und Inklusions-Funktionen über den üblichen WCAG-Basisumfang hinaus.

## WCAG-Basis

- Sichtbarer Fokuszustand
- Tastaturbedienbarkeit
- reduzierte Bewegung
- Kontrastoptimierung
- Mindestgrößen für Touch-Ziele

## Screenreader

- Skip-Link zu `#main-content`
- `aria-live="polite"` für Statusmeldungen
- `role="alert"` für kritische Meldungen
- Fokus-Management für Modale

## Legasthenie

- OpenDyslexic-Font
- erhöhter Zeilenabstand
- größerer Buchstaben- und Wortabstand
- cremefarbener Hintergrund statt hartem Weiß
- begrenzte Zeilenlänge

## Farbenblindheit

SVG-basierte Filter für:

- Deuteranopie
- Protanopie
- Tritanopie
- Achromatopsie

## ADHS / Kognition

- Fokus-Modus
- reduzierte Animationen
- umschaltbare Informationsdichte
- Shortcut-Overlay
- Undo-Toast und Bestätigungsdialoge

## Tastaturkürzel

- `?` öffnet Shortcut-Overlay
- `F` toggelt Fokus-Modus
- `G`-Sequenzen für Navigation
- `Escape` schließt Overlays

## Hinweis

Details befinden sich zusätzlich in `docs/accessibility.md` im Haupt-Repository.
