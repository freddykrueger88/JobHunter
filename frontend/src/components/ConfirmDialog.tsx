import { useEffect } from 'react'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { AlertTriangle } from 'lucide-react'
import type { ConfirmState } from '../hooks/useConfirm'
import clsx from 'clsx'

interface Props {
  state: ConfirmState
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({ state, onConfirm, onCancel }: Props) {
  const containerRef = useFocusTrap(state.isOpen)

  useEffect(() => {
    if (!state.isOpen) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel()
      if (e.key === 'Enter') onConfirm()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [state.isOpen, onConfirm, onCancel])

  if (!state.isOpen) return null

  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      role="dialog" aria-modal="true"
      aria-labelledby="confirm-title"
      aria-describedby={state.description ? 'confirm-desc' : undefined}
      onClick={onCancel}
    >
      <div
        ref={containerRef}
        className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-sm shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-start gap-3 mb-4">
          {state.danger && (
            <AlertTriangle className="text-red-500 shrink-0 mt-0.5" size={22} aria-hidden />
          )}
          <div>
            <h2 id="confirm-title" className="text-base font-bold">{state.title}</h2>
            {state.description && (
              <p id="confirm-desc" className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {state.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-lg text-sm font-medium
              bg-gray-100 dark:bg-gray-700 hover:bg-gray-200
              dark:hover:bg-gray-600 transition-colors"
          >
            Abbrechen
          </button>
          <button
            onClick={onConfirm}
            className={clsx(
              'px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors',
              state.danger
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-blue-600 hover:bg-blue-700'
            )}
            autoFocus
          >
            Bestätigen
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center mt-3">
          <kbd className="font-mono">Enter</kbd> = Bestätigen • <kbd className="font-mono">Esc</kbd> = Abbrechen
        </p>
      </div>
    </div>
  )
}
