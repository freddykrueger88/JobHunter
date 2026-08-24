/**
 * Globales Tastaturkürzel-System.
 * Shortcuts werden nur ausgelöst wenn der Nutzer NICHT in einem Input-Feld tippt.
 */
import { useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

const INPUT_TAGS = new Set(['INPUT', 'TEXTAREA', 'SELECT'])

function isTyping(): boolean {
  const el = document.activeElement
  return !!el && (INPUT_TAGS.has(el.tagName) || (el as HTMLElement).isContentEditable)
}

export interface ShortcutDef {
  key: string
  label: string
  // i18n-Schluessel statt Klartext (Namespace "shortcutOverlay"), siehe
  // components/ShortcutOverlay.tsx, das diese per t() aufloest.
  descriptionKey: string
  categoryKey: string
}

export const SHORTCUTS: ShortcutDef[] = [
  { key: '?',   label: '?',       descriptionKey: 'shortcuts.help', categoryKey: 'categories.general' },
  { key: 'f',   label: 'F',       descriptionKey: 'shortcuts.toggleFocus', categoryKey: 'categories.general' },
  { key: 'Escape', label: 'Esc', descriptionKey: 'shortcuts.closeModal', categoryKey: 'categories.general' },
  { key: 'g d', label: 'G → D',   descriptionKey: 'shortcuts.goDashboard', categoryKey: 'categories.navigation' },
  { key: 'g j', label: 'G → J',   descriptionKey: 'shortcuts.goJobs', categoryKey: 'categories.navigation' },
  { key: 'g k', label: 'G → K',   descriptionKey: 'shortcuts.goKanban', categoryKey: 'categories.navigation' },
  { key: 'g r', label: 'G → R',   descriptionKey: 'shortcuts.goReminders', categoryKey: 'categories.navigation' },
  { key: 'g s', label: 'G → S',   descriptionKey: 'shortcuts.goSettings', categoryKey: 'categories.navigation' },
  { key: 'g p', label: 'G → P',   descriptionKey: 'shortcuts.goSearchProfiles', categoryKey: 'categories.navigation' },
]

export function useKeyboardShortcuts(
  onOpenHelp: () => void,
  onToggleFocus: () => void,
) {
  const navigate = useNavigate()
  let gPressed = false
  let gTimer: ReturnType<typeof setTimeout> | null = null

  const handleKey = useCallback((e: KeyboardEvent) => {
    if (isTyping()) return
    if (e.metaKey || e.ctrlKey || e.altKey) return

    const key = e.key.toLowerCase()

    // G-Sequenz (g dann j/k/d/s/r/p)
    if (gPressed) {
      gPressed = false
      if (gTimer) clearTimeout(gTimer)
      switch (key) {
        case 'd': navigate('/'); break
        case 'j': navigate('/jobs'); break
        case 'k': navigate('/kanban'); break
        case 'r': navigate('/reminders'); break
        case 's': navigate('/settings'); break
        case 'p': navigate('/search-profiles'); break
      }
      return
    }

    switch (key) {
      case '?': e.preventDefault(); onOpenHelp(); break
      case 'f': e.preventDefault(); onToggleFocus(); break
      case 'g':
        gPressed = true
        gTimer = setTimeout(() => { gPressed = false }, 1000)
        break
    }
  }, [navigate, onOpenHelp, onToggleFocus])

  useEffect(() => {
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [handleKey])
}
