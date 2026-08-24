import { useTranslation } from 'react-i18next'
import { Undo2, X } from 'lucide-react'
import type { UndoState } from '../hooks/useUndoToast'

interface Props {
  state: UndoState
  onUndo: () => void
  onDismiss: () => void
}

export default function UndoToast({ state, onUndo, onDismiss }: Props) {
  const { t } = useTranslation('undoToast')
  if (!state.visible) return null

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="fixed bottom-6 right-6 z-50 bg-gray-900 dark:bg-gray-100
        text-white dark:text-gray-900 rounded-xl shadow-2xl
        overflow-hidden min-w-64 max-w-sm"
    >
      {/* Countdown-Balken */}
      <div
        className="h-1 bg-blue-500 transition-none"
        style={{ width: `${state.progress}%` }}
        aria-hidden
      />
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <span className="text-sm font-medium">{state.message}</span>
        <div className="flex items-center gap-1 shrink-0">
          <button
            onClick={onUndo}
            className="flex items-center gap-1 text-blue-400 dark:text-blue-600
              hover:text-blue-300 dark:hover:text-blue-700 text-sm font-semibold
              px-2 py-1 rounded transition-colors"
            aria-label={t('undoAriaLabel')}
          >
            <Undo2 size={14} aria-hidden /> {t('undo')}
          </button>
          <button
            onClick={onDismiss}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-200
              dark:hover:text-gray-700 p-1 rounded transition-colors"
            aria-label={t('dismissAriaLabel')}
          >
            <X size={14} aria-hidden />
          </button>
        </div>
      </div>
    </div>
  )
}
