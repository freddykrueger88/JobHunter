/**
 * Ampel-Badge fuer Bewerbungsfristen.
 * Gruen: >7 Tage, Gelb: 3-7 Tage, Rot: <3 Tage, Grau: abgelaufen
 */
import { differenceInDays } from 'date-fns'
import clsx from 'clsx'

interface Props {
  frist: string | null | undefined
  className?: string
}

export default function DeadlineBadge({ frist, className }: Props) {
  if (!frist) return null

  const days = differenceInDays(new Date(frist), new Date())

  const config = (() => {
    if (days < 0)  return { label: 'Abgelaufen',      color: 'bg-gray-200 text-gray-500 dark:bg-gray-700' }
    if (days < 3)  return { label: `Noch ${days}T`,   color: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400' }
    if (days < 7)  return { label: `Noch ${days}T`,   color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400' }
    return           { label: `Noch ${days}T`,         color: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' }
  })()

  return (
    <span
      className={clsx(
        'inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full',
        config.color, className
      )}
      title={`Bewerbungsfrist: ${new Date(frist).toLocaleDateString('de-DE')}`}
      aria-label={`Bewerbungsfrist in ${days} Tagen`}
    >
      {config.label}
    </span>
  )
}
