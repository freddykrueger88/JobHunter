/**
 * Onboarding-Flow beim ersten Start.
 * Wird angezeigt wenn settings.onboarding_done === false.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme, type Theme } from '../context/ThemeContext'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { CheckCircle, ChevronRight, ChevronLeft } from 'lucide-react'
import clsx from 'clsx'

const STEPS = [
  { id: 'sprache',    label: 'Sprache' },
  { id: 'ort',        label: 'Ort & Beruf' },
  { id: 'ki',         label: 'KI prüfen' },
  { id: 'theme',      label: 'Erscheinungsbild' },
  { id: 'abschluss',  label: 'Fertig!' },
]

export default function Onboarding() {
  const [step, setStep] = useState(0)
  const [lang, setLang] = useState('de')
  const [ort, setOrt] = useState('')
  const [beruf, setBeruf] = useState('')
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null)
  const { theme, setTheme } = useTheme()
  const { i18n } = useTranslation()
  const navigate = useNavigate()

  const checkOllama = async () => {
    try {
      await axios.get('/api/ai/models')
      setOllamaOk(true)
    } catch {
      setOllamaOk(false)
    }
  }

  const finish = async () => {
    await axios.patch('/api/settings/', {
      language: lang,
      default_location: ort || null,
      onboarding_done: true,
    })
    navigate('/')
  }

  const THEMES: { value: Theme; label: string }[] = [
    { value: 'dark', label: '🌙 Dark' },
    { value: 'light', label: '☀️ Light' },
    { value: 'boys', label: '💙 Boys' },
    { value: 'girls', label: '🌸 Girls' },
    { value: 'dyslexic', label: '📚 Legasthenie' },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-white dark:bg-gray-900">
      <div className="w-full max-w-lg">
        {/* Fortschrittsbalken */}
        <div className="flex gap-1 mb-8">
          {STEPS.map((s, i) => (
            <div key={s.id}
              className={clsx('h-1.5 flex-1 rounded-full transition-colors',
                i <= step ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700')} />
          ))}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
          <p className="text-xs text-gray-400 mb-1">Schritt {step + 1} von {STEPS.length}</p>

          {/* Schritt 0: Sprache */}
          {step === 0 && (
            <>
              <h1 className="text-2xl font-bold mb-6">Willkommen bei JobHunter 👋</h1>
              <p className="text-gray-500 mb-6">In welcher Sprache möchtest du JobHunter nutzen?</p>
              <div className="flex gap-3">
                {['de', 'en'].map(l => (
                  <button key={l} onClick={() => { setLang(l); i18n.changeLanguage(l) }}
                    className={clsx('flex-1 py-4 rounded-xl font-medium border-2 transition-all',
                      lang === l ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-700')}
                    aria-pressed={lang === l}>
                    {l === 'de' ? '🇩🇪 Deutsch' : '🇬🇧 English'}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Schritt 1: Ort & Beruf */}
          {step === 1 && (
            <>
              <h1 className="text-2xl font-bold mb-6">Wo suchst du?</h1>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-500 block mb-1">Standard-Ort (optional)</label>
                  <input value={ort} onChange={e => setOrt(e.target.value)}
                    placeholder="z.B. Bremen"
                    className="w-full rounded-xl px-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="text-sm text-gray-500 block mb-1">Gesuchte Berufsbezeichnung (optional)</label>
                  <input value={beruf} onChange={e => setBeruf(e.target.value)}
                    placeholder="z.B. IT-Support"
                    className="w-full rounded-xl px-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
            </>
          )}

          {/* Schritt 2: Ollama */}
          {step === 2 && (
            <>
              <h1 className="text-2xl font-bold mb-4">KI-Verbindung prüfen</h1>
              <p className="text-gray-500 mb-6">
                JobHunter nutzt <strong>Ollama</strong> für lokale KI-Funktionen.
                Stelle sicher dass Ollama läuft.
              </p>
              {ollamaOk === null && (
                <button onClick={checkOllama}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors">
                  Verbindung testen
                </button>
              )}
              {ollamaOk === true && (
                <div className="flex items-center gap-2 text-green-600 font-medium">
                  <CheckCircle size={20} /> Ollama erreichbar – KI-Funktionen aktiv ✅
                </div>
              )}
              {ollamaOk === false && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 text-sm">
                  <p className="font-medium text-yellow-700 dark:text-yellow-400 mb-2">⚠️ Ollama nicht erreichbar</p>
                  <p className="text-gray-600 dark:text-gray-400">Starte Ollama lokal: <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">ollama serve</code></p>
                  <p className="text-gray-500 mt-1">Du kannst JobHunter trotzdem nutzen – KI-Funktionen sind ohne Ollama nicht verfügbar.</p>
                </div>
              )}
            </>
          )}

          {/* Schritt 3: Theme */}
          {step === 3 && (
            <>
              <h1 className="text-2xl font-bold mb-6">Wie soll JobHunter aussehen?</h1>
              <div className="grid grid-cols-2 gap-3">
                {THEMES.map(t => (
                  <button key={t.value} onClick={() => setTheme(t.value)}
                    className={clsx('py-4 rounded-xl font-medium border-2 transition-all',
                      theme === t.value ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-700')}
                    aria-pressed={theme === t.value}>
                    {t.label}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Schritt 4: Abschluss */}
          {step === 4 && (
            <>
              <h1 className="text-2xl font-bold mb-4">Alles bereit! 🎉</h1>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
                <li>✅ Stellen suchen und verwalten</li>
                <li>✅ Kanban-Board für Bewerbungsstatus</li>
                <li>✅ KI-Anschreiben generieren (mit Ollama)</li>
                <li>✅ Erinnerungen und Benachrichtigungen</li>
                <li>✅ DSGVO-konform, lokal, ohne Cloud</li>
              </ul>
            </>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button onClick={() => setStep(s => s - 1)} disabled={step === 0}
              className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-0 transition-colors">
              <ChevronLeft size={16} /> Zurück
            </button>
            {step < STEPS.length - 1 ? (
              <button onClick={() => setStep(s => s + 1)}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-medium transition-colors">
                Weiter <ChevronRight size={16} />
              </button>
            ) : (
              <button onClick={finish}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-2.5 rounded-xl font-medium transition-colors">
                <CheckCircle size={16} /> Loslegen!
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
