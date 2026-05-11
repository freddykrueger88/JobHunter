/**
 * Wiederverwendbarer Bestätigungs-Dialog Hook.
 *
 * Verwendung:
 * const { confirmState, confirm } = useConfirm()
 * const ok = await confirm('Wirklich löschen?', 'Diese Aktion kann nicht rückgängig gemacht werden.')
 * if (ok) deleteMutation.mutate(id)
 */
import { useState, useRef, useCallback } from 'react'

export interface ConfirmState {
  isOpen: boolean
  title: string
  description: string
  danger: boolean
}

export function useConfirm() {
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    isOpen: false, title: '', description: '', danger: true,
  })
  const resolverRef = useRef<((v: boolean) => void) | null>(null)

  const confirm = useCallback((title: string, description = '', danger = true): Promise<boolean> => {
    setConfirmState({ isOpen: true, title, description, danger })
    return new Promise(resolve => { resolverRef.current = resolve })
  }, [])

  const resolve = useCallback((value: boolean) => {
    setConfirmState(s => ({ ...s, isOpen: false }))
    resolverRef.current?.(value)
    resolverRef.current = null
  }, [])

  return { confirmState, confirm, resolveConfirm: resolve }
}
