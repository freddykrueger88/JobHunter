/**
 * Timing-Hinweis-Badge (#74, G.3.9 "Bewerbungs-Timing-KI"): zeigt pro
 * Job, ob sein aktuelles Alter (Tage seit Veroeffentlichung) in den
 * eigenen historischen Daten mit der besten Ruecklaufquote
 * korrespondiert. Bewusst clientseitig aus den bereits vom Dashboard
 * geladenen /api/stats/response-rates-Daten abgeleitet statt einem
 * eigenen Backend-Computed-Field pro Job (anders als GhostJobBadge) -
 * die Bewertungsgrundlage ist eine Aggregat-Kurve ueber ALLE
 * Bewerbungen, keine Eigenschaft des einzelnen Jobs, waere also pro Job
 * dieselbe Query N-mal wiederholt.
 *
 * Zeigt bewusst NICHTS an, solange keine Bucket-Empfehlung mit genug
 * Stichprobe existiert (gleiche MIN_SAMPLE-Schwelle wie im Backend) -
 * lieber schweigen als eine unbelegte Standardempfehlung erfinden (z.B.
 * die im GitHub-Issue vorgeschlagene "Jan/Feb Hochsaison"-Pauschale,
 * bewusst nicht uebernommen, siehe response_rate_analyzer.py).
 */
import { useTranslation } from 'react-i18next'
import { Clock } from 'lucide-react'

interface DaysUntilEntry {
  key: string
  total: number
  beantwortet: number
  quote: number
}

interface Props {
  publishedAt: string | null
  createdAt: string
  byDaysUntilApplied: DaysUntilEntry[] | undefined
}

const MIN_SAMPLE = 3

function bucketFor(days: number): string {
  if (days <= 0) return 'sofort'
  if (days <= 3) return 'kurz'
  if (days <= 7) return 'mittel'
  return 'spaet'
}

export default function TimingHintBadge({ publishedAt, createdAt, byDaysUntilApplied }: Props) {
  const { t } = useTranslation('timingHint')
  if (!byDaysUntilApplied) return null

  const qualified = byDaysUntilApplied.filter(e => e.total >= MIN_SAMPLE)
  if (qualified.length < 2) return null

  const best = qualified.reduce((a, b) => (b.quote > a.quote ? b : a))
  const referenceDate = new Date(publishedAt ?? createdAt)
  const ageDays = Math.floor((Date.now() - referenceDate.getTime()) / 86400000)
  const currentBucket = bucketFor(ageDays)
  const current = qualified.find(e => e.key === currentBucket)

  if (!current || current.quote >= best.quote - 10) {
    if (currentBucket === best.key) {
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
          <Clock size={11} aria-hidden />
          {t('goodTiming')}
        </span>
      )
    }
    return null
  }

  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">
      <Clock size={11} aria-hidden />
      {t('windowClosing')}
    </span>
  )
}
