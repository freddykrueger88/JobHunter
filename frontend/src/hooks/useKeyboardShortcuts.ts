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
  description: string
  category: string
}

export const SHORTCUTS: ShortcutDef[] = [
  { key: '?',   label: '?',       description: 'Shortcut-Übersicht', category: 'Allgemein' },
  { key: 'f',   label: 'F',       description: 'Fokus-Modus umschalten', category: 'Allgemein' },
  { key: 'Escape', label: 'Esc', description: 'Modal / Overlay schließen', category: 'Allgemein' },
  { key: 'g d', label: 'G → D',   description: 'Zum Dashboard', category: 'Navigation' },
  { key: 'g j', label: 'G → J',   description: 'Zu Stellen', category: 'Navigation' },
  { key: 'g k', label: 'G → K',   description: 'Zum Kanban', category: 'Navigation' },
  { key: 'g r', label: 'G → R',   description: 'Zu Erinnerungen', category: 'Navigation' },
  { key: 'g s', label: 'G → S',   description: 'Zu Einstellungen', category: 'Navigation' },
  { key: 'g p', label: 'G → P',   description: 'Zu Suchprofilen', category: 'Navigation' },
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
