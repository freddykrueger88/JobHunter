/**
 * Abzeichen-Anzeige fuer das Dashboard.
 * Freigeschaltete Abzeichen werden hervorgehoben, gesperrte ausgegraut.
 */
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'

interface Badge {
  key: string
  label: string
  beschreibung: string
  freigeschaltet: boolean
}

export default function BadgesPanel() {
  const { t } = useTranslation('badgesPanel')
  const [badges, setBadges] = useState<Badge[]>([])

  useEffect(() => {
    axios.get('/api/badges/').then(r => setBadges(r.data))
  }, [])

  const unlocked = badges.filter(b => b.freigeschaltet)
  const locked = badges.filter(b => !b.freigeschaltet)

  return (
    <section aria-labelledby="badges-heading">
      <h2 id="badges-heading" className="font-semibold text-sm text-gray-500 mb-3">{t('heading')}</h2>
      <div className="flex flex-wrap gap-2">
        {unlocked.map(b => (
          <div key={b.key}
            title={b.beschreibung}
            className="px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
            aria-label={`${b.label} – ${b.beschreibung}`}>
            {b.label}
          </div>
        ))}
        {locked.map(b => (
          <div key={b.key}
            title={t('lockedTitle', { description: b.beschreibung })}
            className="px-3 py-1.5 rounded-full text-sm font-medium bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600 select-none"
            aria-label={t('lockedAriaLabel', { label: b.label })}>
            🔒 {b.label.split(' ').slice(1).join(' ')}
          </div>
        ))}
      </div>
    </section>
  )
}
