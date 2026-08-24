/**
 * PWA Install-Banner.
 * Erscheint wenn der Browser das beforeinstallprompt-Event feuert.
 * Wird nach Ablehnung 7 Tage nicht mehr gezeigt.
 */
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Download, X } from 'lucide-react'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export default function PwaInstallBanner() {
  const { t } = useTranslation('pwaInstallBanner')
  const [prompt, setPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const dismissed = localStorage.getItem('pwa_install_dismissed')
    if (dismissed && Date.now() - Number(dismissed) < 7 * 24 * 60 * 60 * 1000) return

    const handler = (e: Event) => {
      e.preventDefault()
      setPrompt(e as BeforeInstallPromptEvent)
      setVisible(true)
    }
    window.addEventListener('beforeinstallprompt', handler)
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const install = async () => {
    if (!prompt) return
    await prompt.prompt()
    const { outcome } = await prompt.userChoice
    if (outcome === 'accepted') setVisible(false)
  }

  const dismiss = () => {
    setVisible(false)
    localStorage.setItem('pwa_install_dismissed', String(Date.now()))
  }

  if (!visible) return null

  return (
    <div className="fixed bottom-20 left-4 right-4 md:left-auto md:right-6 md:w-80
      bg-blue-600 text-white rounded-2xl shadow-2xl p-4 z-50
      flex items-center gap-3"
      role="banner">
      <Download size={22} className="shrink-0" aria-hidden />
      <div className="flex-1">
        <p className="font-semibold text-sm">{t('title')}</p>
        <p className="text-xs text-blue-100">{t('subtitle')}</p>
      </div>
      <button onClick={install}
        className="bg-white text-blue-600 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-50 transition-colors">
        {t('install')}
      </button>
      <button onClick={dismiss} aria-label={t('close')}
        className="text-blue-200 hover:text-white transition-colors">
        <X size={16} aria-hidden />
      </button>
    </div>
  )
}
