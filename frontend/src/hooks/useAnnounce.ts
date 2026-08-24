/**
 * Screenreader-Announcements über die globalen aria-live Regionen.
 *
 * Verwendung:
 * const { announce, alert } = useAnnounce()
 * announce('12 neue Stellen geladen')   // polite (unterbricht nicht)
 * alert('Verbindungsfehler')             // assertive (sofort)
 */
export function useAnnounce() {
  const announce = (message: string) => {
    const el = document.getElementById('sr-announcer')
    if (!el) return
    // Kurze Pause damit gleiche Nachricht erneut gelesen wird
    el.textContent = ''
    requestAnimationFrame(() => { el.textContent = message })
  }

  const alert = (message: string) => {
    const el = document.getElementById('sr-alert')
    if (!el) return
    el.textContent = ''
    requestAnimationFrame(() => { el.textContent = message })
  }

  return { announce, alert }
}
