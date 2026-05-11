import { useTranslation } from 'react-i18next'
import { useTheme } from '../context/ThemeContext'
import type { Theme } from '../context/ThemeContext'

const themes: { value: Theme; label: string; desc: string }[] = [
  { value: 'dark',  label: '🌙 Dark Mode',               desc: 'Dunkel, klassisch' },
  { value: 'light', label: '☀️ Light Mode',              desc: 'Hell, klar' },
  { value: 'boys',  label: '💙 Boys Mode',               desc: 'Dark Blue, typisch Boys' },
  { value: 'girls', label: '🌸 Girls Mode',              desc: 'Pink Fluffy Wonderfully ✨' },
]

export default function Settings() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme } = useTheme()

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">{t('settings.title')}</h1>

      {/* Theme */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">{t('settings.theme')}</h2>
        <div className="grid grid-cols-2 gap-3">
          {themes.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setTheme(opt.value)}
              className={`rounded-xl p-4 text-left border-2 transition-all ${
                theme === opt.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              }`}
              aria-pressed={theme === opt.value}
            >
              <div className="font-medium">{opt.label}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">{opt.desc}</div>
            </button>
          ))}
        </div>
      </section>

      {/* Sprache */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">{t('settings.language')}</h2>
        <div className="flex gap-3">
          {['de', 'en'].map((lang) => (
            <button
              key={lang}
              onClick={() => { i18n.changeLanguage(lang); localStorage.setItem('lang', lang) }}
              className={`px-6 py-2 rounded-lg font-medium border-2 transition-all ${
                i18n.language === lang
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              }`}
              aria-pressed={i18n.language === lang}
            >
              {lang === 'de' ? '🇩🇪 Deutsch' : '🇬🇧 English'}
            </button>
          ))}
        </div>
      </section>

      {/* KI (Platzhalter) */}
      <section>
        <h2 className="text-lg font-semibold mb-3">{t('settings.ai')}</h2>
        <p className="text-gray-400 text-sm">🔧 KI-Einstellungen (Modell, Laune, API-Keys) folgen in Issue #13.</p>
      </section>
    </div>
  )
}
