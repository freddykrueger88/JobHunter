/**
 * Undo-Toast für destruktive Aktionen.
 * Zeigt 5s lang einen Toast mit "Rückgängig"-Button.
 * Die eigentliche Aktion wird erst nach 5s ausgeführt (oder sofort bei Bestätigung).
 *
 * Verwendung:
 * const { showUndo } = useUndoToast()
 * showUndo('Stelle gelöscht', () => deleteMutation.mutate(id))
 */
import { useState, useRef, useCallback } from 'react'

export interface UndoState {
  message: string
  progress: number  // 0–100
  visible: boolean
}

export function useUndoToast() {
  const [state, setState] = useState<UndoState>({ message: '', progress: 100, visible: false })
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const undoRef = useRef(false)

  const clearTimers = () => {
    if (timerRef.current) clearInterval(timerRef.current)
  }

  const showUndo = useCallback((message: string, action: () => void, delayMs = 5000) => {
    clearTimers()
    undoRef.current = false
    setState({ message, progress: 100, visible: true })

    const start = Date.now()
    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - start
      const progress = Math.max(0, 100 - (elapsed / delayMs) * 100)
      setState(s => ({ ...s, progress }))
      if (elapsed >= delayMs) {
        clearTimers()
        setState(s => ({ ...s, visible: false }))
        if (!undoRef.current) action()
      }
    }, 50)
  }, [])

  const undo = useCallback(() => {
    undoRef.current = true
    clearTimers()
    setState(s => ({ ...s, visible: false }))
  }, [])

  const dismiss = useCallback(() => {
    undoRef.current = true
    clearTimers()
    setState(s => ({ ...s, visible: false }))
  }, [])

  return { state, showUndo, undo, dismiss }
}
