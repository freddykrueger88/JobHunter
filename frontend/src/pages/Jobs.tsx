import { useTranslation } from 'react-i18next'

export default function Jobs() {
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">{t('jobs.title')}</h1>
      <p className="text-gray-400">🔧 Stellensuche wird in Issue #06 & #07 implementiert.</p>
    </div>
  )
}
