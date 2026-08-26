/**
 * Onboarding-Flow beim ersten Start.
 * Wird angezeigt wenn settings.onboarding_done === false.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { useTheme, type Theme } from '../context/ThemeContext'
import { useTranslation, Trans } from 'react-i18next'
import axios from 'axios'
import api from '../lib/api'
import { CheckCircle, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react'
import clsx from 'clsx'

const STEP_IDS = ['sprache', 'ort', 'ki', 'theme', 'abschluss'] as const

export default function Onboarding() {
  const { t } = useTranslation('onboarding')
  const [step, setStep] = useState(0)
  const [lang, setLang] = useState('de')
  const [ort, setOrt] = useState('')
  const [beruf, setBeruf] = useState('')
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null)
  const [finishing, setFinishing] = useState(false)
  const { theme, setTheme } = useTheme()
  const { i18n } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const checkOllama = async () => {
    try {
      await axios.get('/api/ai/models')
      setOllamaOk(true)
    } catch {
      setOllamaOk(false)
    }
  }

  const finish = async () => {
    setFinishing(true)
    try {
      await api.patch('/settings/', {
        language: lang,
        default_location: ort || null,
        onboarding_done: true,
      })
      // App.tsx haelt die settings-Query mit staleTime: Infinity vor - ohne
      // dieses Invalidieren wuerde needsOnboarding weiterhin true liefern
      // und sofort wieder auf /onboarding umleiten (Endlosschleife).
      await queryClient.invalidateQueries({ queryKey: ['settings'] })
      navigate('/')
    } finally {
      setFinishing(false)
    }
  }

  const THEME_VALUES: Theme[] = ['dark', 'light', 'boys', 'girls', 'dyslexic']

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-white dark:bg-gray-900">
      <div className="w-full max-w-lg">
        {/* Fortschrittsbalken */}
        <div className="flex gap-1 mb-8">
          {STEP_IDS.map((id, i) => (
            <div key={id}
              className={clsx('h-1.5 flex-1 rounded-full transition-colors',
                i <= step ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700')} />
          ))}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
          <p className="text-xs text-gray-400 mb-1">{t('stepCounter', { current: step + 1, total: STEP_IDS.length })}</p>

          {/* Schritt 0: Sprache */}
          {step === 0 && (
            <>
              <h1 className="text-2xl font-bold mb-6">{t('step0.title')}</h1>
              <p className="text-gray-500 mb-6">{t('step0.subtitle')}</p>
              <div className="flex gap-3">
                {['de', 'en'].map(l => (
                  <button key={l} onClick={() => { setLang(l); i18n.changeLanguage(l) }}
                    className={clsx('flex-1 py-4 rounded-xl font-medium border-2 transition-all',
                      lang === l ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-700')}
                    aria-pressed={lang === l}>
                    {l === 'de' ? t('step0.de') : t('step0.en')}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Schritt 1: Ort & Beruf */}
          {step === 1 && (
            <>
              <h1 className="text-2xl font-bold mb-6">{t('step1.title')}</h1>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-500 block mb-1">{t('step1.locationLabel')}</label>
                  <input value={ort} onChange={e => setOrt(e.target.value)}
                    placeholder={t('step1.locationPlaceholder')}
                    className="w-full rounded-xl px-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="text-sm text-gray-500 block mb-1">{t('step1.jobTitleLabel')}</label>
                  <input value={beruf} onChange={e => setBeruf(e.target.value)}
                    placeholder={t('step1.jobTitlePlaceholder')}
                    className="w-full rounded-xl px-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
            </>
          )}

          {/* Schritt 2: Ollama */}
          {step === 2 && (
            <>
              <h1 className="text-2xl font-bold mb-4">{t('step2.title')}</h1>
              <p className="text-gray-500 mb-6">
                <Trans i18nKey="onboarding:step2.description" components={{ strong: <strong /> }} />
              </p>
              {ollamaOk === null && (
                <button onClick={checkOllama}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors">
                  {t('step2.testConnection')}
                </button>
              )}
              {ollamaOk === true && (
                <div className="flex items-center gap-2 text-green-600 font-medium">
                  <CheckCircle size={20} /> {t('step2.connected')}
                </div>
              )}
              {ollamaOk === false && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 text-sm">
                  <p className="font-medium text-yellow-700 dark:text-yellow-400 mb-2">{t('step2.notConnectedTitle')}</p>
                  <p className="text-gray-600 dark:text-gray-400">
                    <Trans
                      i18nKey="onboarding:step2.notConnectedHint"
                      components={{ code: <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded" /> }}
                    />
                  </p>
                  <p className="text-gray-500 mt-1">{t('step2.notConnectedFallback')}</p>
                </div>
              )}
            </>
          )}

          {/* Schritt 3: Theme */}
          {step === 3 && (
            <>
              <h1 className="text-2xl font-bold mb-6">{t('step3.title')}</h1>
              <div className="grid grid-cols-2 gap-3">
                {THEME_VALUES.map(value => (
                  <button key={value} onClick={() => setTheme(value)}
                    className={clsx('py-4 rounded-xl font-medium border-2 transition-all',
                      theme === value ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-700')}
                    aria-pressed={theme === value}>
                    {t(`step3.themes.${value}`)}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Schritt 4: Abschluss */}
          {step === 4 && (
            <>
              <h1 className="text-2xl font-bold mb-4">{t('step4.title')}</h1>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
                <li>{t('step4.features.jobs')}</li>
                <li>{t('step4.features.kanban')}</li>
                <li>{t('step4.features.ai')}</li>
                <li>{t('step4.features.reminders')}</li>
                <li>{t('step4.features.privacy')}</li>
              </ul>
            </>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button onClick={() => setStep(s => s - 1)} disabled={step === 0}
              className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-0 transition-colors">
              <ChevronLeft size={16} /> {t('back')}
            </button>
            {step < STEP_IDS.length - 1 ? (
              <button onClick={() => setStep(s => s + 1)}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-medium transition-colors">
                {t('next')} <ChevronRight size={16} />
              </button>
            ) : (
              <button onClick={finish} disabled={finishing}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl font-medium transition-colors">
                {finishing
                  ? <Loader2 size={16} className="animate-spin" />
                  : <CheckCircle size={16} />} {t('finish')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
