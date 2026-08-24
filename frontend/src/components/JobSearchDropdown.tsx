/**
 * JobSearchDropdown – wiederverwendbares Kombobox-Dropdown zur Job-Suche.
 *
 * Props:
 *   jobs        – komplette Liste aller Jobs (aus React Query Cache)
 *   onSelect    – Callback mit ausgewähltem Job-Objekt
 *   onCancel    – Callback wenn ESC/Abbrechen gedrückt
 *   placeholder – optionaler Platzhaltertext
 *
 * Features:
 *   - Clientseitiges Fuzzy-Filtern (Titel + Firma + Stadt)
 *   - Keyboard-Navigation (↑↓ in Liste, Enter bestätigen, Esc abbrechen)
 *   - Zeigt bereits beworbene Jobs mit Badge
 *   - Autofokus
 *   - Accessible (role="combobox", aria-activedescendant, aria-expanded)
 */
import { useState, useRef, useEffect, useId } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, X, Briefcase } from 'lucide-react'
import clsx from 'clsx'

export interface JobOption {
  id: number
  title: string
  company: string
  city: string | null
}

interface Props {
  jobs: JobOption[]
  appliedJobIds?: Set<number>   // Jobs die schon eine Bewerbung haben
  onSelect: (job: JobOption) => void
  onCancel: () => void
  placeholder?: string
  loading?: boolean
}

function highlight(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text
  const idx = text.toLowerCase().indexOf(query.toLowerCase())
  if (idx === -1) return text
  return (
    <>
      {text.slice(0, idx)}
      <mark className="bg-yellow-200 dark:bg-yellow-700 rounded-sm not-italic">
        {text.slice(idx, idx + query.length)}
      </mark>
      {text.slice(idx + query.length)}
    </>
  )
}

export default function JobSearchDropdown({
  jobs,
  appliedJobIds = new Set(),
  onSelect,
  onCancel,
  placeholder,
  loading = false,
}: Props) {
  const { t } = useTranslation(['jobSearchDropdown', 'common'])
  const effectivePlaceholder = placeholder ?? t('defaultPlaceholder')
  const [query, setQuery] = useState('')
  const [activeIdx, setActiveIdx] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLUListElement>(null)
  const uid = useId()

  // Autofokus
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  // Fuzzy-Filter: title + company + city
  const filtered = query.trim()
    ? jobs.filter(j => {
        const haystack = `${j.title} ${j.company} ${j.city ?? ''}`.toLowerCase()
        return query
          .toLowerCase()
          .split(' ')
          .every(word => haystack.includes(word))
      })
    : jobs.slice(0, 20) // Default: erste 20 anzeigen

  // Wenn Filter sich ändert, Index zurücksetzen
  useEffect(() => {
    setActiveIdx(0)
  }, [query])

  // Aktives Item in View scrollen
  useEffect(() => {
    const item = listRef.current?.querySelector<HTMLElement>(`[data-idx="${activeIdx}"]`)
    item?.scrollIntoView({ block: 'nearest' })
  }, [activeIdx])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setActiveIdx(i => Math.min(i + 1, filtered.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setActiveIdx(i => Math.max(i - 1, 0))
        break
      case 'Enter':
        e.preventDefault()
        if (filtered[activeIdx]) onSelect(filtered[activeIdx])
        break
      case 'Escape':
        e.preventDefault()
        onCancel()
        break
    }
  }

  return (
    <div className="relative">
      {/* Search input */}
      <div className="flex items-center gap-1.5 bg-white dark:bg-gray-700 border border-blue-400 rounded-lg px-2 py-1.5 shadow-sm">
        <Search size={13} className="text-gray-400 shrink-0" aria-hidden />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={effectivePlaceholder}
          className="flex-1 text-xs bg-transparent focus:outline-none min-w-0 placeholder:text-gray-400"
          role="combobox"
          aria-expanded={filtered.length > 0}
          aria-autocomplete="list"
          aria-controls={`${uid}-list`}
          aria-activedescendant={filtered[activeIdx] ? `${uid}-opt-${filtered[activeIdx].id}` : undefined}
          aria-label={t('searchAriaLabel')}
        />
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors shrink-0"
          aria-label={t('common:cancel')}
          tabIndex={-1}
        >
          <X size={13} aria-hidden />
        </button>
      </div>

      {/* Results list */}
      {loading ? (
        <div className="mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 text-xs text-gray-400 text-center shadow-md">
          {t('common:loading')}
        </div>
      ) : filtered.length === 0 ? (
        <div className="mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 text-xs text-gray-400 text-center shadow-md">
          {query ? t('noJobFound') : t('noJobs')}
        </div>
      ) : (
        <ul
          ref={listRef}
          id={`${uid}-list`}
          role="listbox"
          aria-label={t('resultsAriaLabel')}
          className="mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md max-h-48 overflow-y-auto"
        >
          {filtered.map((job, idx) => {
            const isActive = idx === activeIdx
            const isApplied = appliedJobIds.has(job.id)
            return (
              <li
                key={job.id}
                id={`${uid}-opt-${job.id}`}
                data-idx={idx}
                role="option"
                aria-selected={isActive}
                onClick={() => onSelect(job)}
                onMouseEnter={() => setActiveIdx(idx)}
                className={clsx(
                  'flex items-start gap-2 px-3 py-2 cursor-pointer transition-colors',
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/30'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                )}
              >
                <Briefcase
                  size={12}
                  className="mt-0.5 text-gray-300 shrink-0"
                  aria-hidden
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium truncate leading-tight">
                    {highlight(job.title, query)}
                  </p>
                  <p className="text-xs text-gray-400 truncate">
                    {highlight(job.company, query)}
                    {job.city && (
                      <span className="text-gray-300">
                        {' · '}{highlight(job.city, query)}
                      </span>
                    )}
                  </p>
                </div>
                {isApplied && (
                  <span
                    className="shrink-0 text-xs bg-gray-100 dark:bg-gray-700 text-gray-400 rounded-full px-1.5 py-0.5 leading-none"
                    title={t('alreadyApplied')}
                  >
                    ✓
                  </span>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
