import { useEffect } from 'react'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { SHORTCUTS } from '../hooks/useKeyboardShortcuts'
import { X, Keyboard } from 'lucide-react'

interface Props {
  isOpen: boolean
  onClose: () => void
}

export default function ShortcutOverlay({ isOpen, onClose }: Props) {
  const containerRef = useFocusTrap(isOpen)

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  if (!isOpen) return null

  const categories = [...new Set(SHORTCUTS.map(s => s.category))]

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      role="dialog" aria-modal="true" aria-label="Tastaturkürzel"
      onClick={onClose}>
      <div ref={containerRef}
        className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl"
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Keyboard size={20} aria-hidden /> Tastaturkürzel
          </h2>
          <button onClick={onClose} aria-label="Schließen"
            className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={20} aria-hidden />
          </button>
        </div>

        <div className="space-y-5">
          {categories.map(cat => (
            <div key={cat}>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{cat}</h3>
              <ul className="space-y-1.5">
                {SHORTCUTS.filter(s => s.category === cat).map(s => (
                  <li key={s.key} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">{s.description}</span>
                    <kbd className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200
                      border border-gray-300 dark:border-gray-600 rounded px-2 py-0.5
                      text-xs font-mono ml-4 shrink-0">
                      {s.label}
                    </kbd>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <p className="text-xs text-gray-400 mt-5 text-center">
          Shortcuts sind deaktiviert wenn du in einem Eingabefeld tippst.
        </p>
      </div>
    </div>
  )
}
