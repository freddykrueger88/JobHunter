/**
 * Ghost-Job-Badge: Warnt vor veralteten oder fiktiven Stellenanzeigen.
 */
import clsx from 'clsx'

interface GhostResult {
  ghost_score: number
  ist_ghost_job: boolean
  wahrscheinlichkeit: 'hoch' | 'mittel' | 'niedrig'
  gruende: string[]
}

interface Props {
  result: GhostResult | null | undefined
  className?: string
}

export default function GhostJobBadge({ result, className }: Props) {
  if (!result || !result.ist_ghost_job) return null

  const config = {
    hoch:    { label: '⚠️ Wahrscheinlich Ghost Job', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
    mittel:  { label: '⚠️ Möglicherweise Ghost Job', color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' },
    niedrig: { label: 'ℹ️ Alte Anzeige', color: 'bg-gray-100 text-gray-500 dark:bg-gray-800' },
  }

  const { label, color } = config[result.wahrscheinlichkeit]

  return (
    <span
      className={clsx('inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full cursor-help', color, className)}
      title={result.gruende.join(' · ')}
      aria-label={`${label}: ${result.gruende.join(', ')}`}
    >
      {label}
    </span>
  )
}
