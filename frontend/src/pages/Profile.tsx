import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { User, Check, AlertCircle } from 'lucide-react'

interface ProfileData {
  ueber_mich: string | null
  kernkompetenzen: string | null
  wunschrolle: string | null
  erfahrungsjahre: number | null
  soft_skills: string | null
  arbeitsstil: string | null
  werte: string | null
}

type SaveStatus = 'idle' | 'pending' | 'saved' | 'error'

const ARBEITSSTIL_OPTIONS = ['egal', 'startup', 'mittelstand', 'konzern', 'behoerde']

export default function Profile() {
  const { t } = useTranslation(['profile', 'common'])
  const qc = useQueryClient()
  const initialized = useRef(false)

  const { data: remote } = useQuery<ProfileData>({
    queryKey: ['profile'],
    queryFn: () => axios.get('/api/profile/').then(r => r.data),
  })

  const [ueberMich, setUeberMich] = useState('')
  const [wunschrolle, setWunschrolle] = useState('')
  const [erfahrungsjahre, setErfahrungsjahre] = useState('')
  const [kernkompetenzen, setKernkompetenzen] = useState('')
  const [softSkills, setSoftSkills] = useState('')
  const [werte, setWerte] = useState('')
  const [arbeitsstil, setArbeitsstil] = useState('egal')
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle')

  useEffect(() => {
    if (remote && !initialized.current) {
      initialized.current = true
      setUeberMich(remote.ueber_mich ?? '')
      setWunschrolle(remote.wunschrolle ?? '')
      setErfahrungsjahre(remote.erfahrungsjahre?.toString() ?? '')
      setKernkompetenzen(remote.kernkompetenzen ?? '')
      setSoftSkills(remote.soft_skills ?? '')
      setWerte(remote.werte ?? '')
      setArbeitsstil(remote.arbeitsstil ?? 'egal')
    }
  }, [remote])

  const saveMutation = useMutation({
    mutationFn: () =>
      axios.patch('/api/profile/', {
        ueber_mich: ueberMich || null,
        wunschrolle: wunschrolle || null,
        erfahrungsjahre: erfahrungsjahre ? parseInt(erfahrungsjahre, 10) : null,
        kernkompetenzen: kernkompetenzen || null,
        soft_skills: softSkills || null,
        werte: werte || null,
        arbeitsstil: arbeitsstil,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['profile'] })
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
    },
    onError: () => setSaveStatus('error'),
  })

  const inputClass =
    'w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500'
  const labelClass = 'block text-sm font-medium mb-1'

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
        <User size={22} aria-hidden /> {t('title')}
      </h1>
      <p className="text-sm text-gray-500 mb-6">{t('subtitle')}</p>

      <form
        className="space-y-5"
        onSubmit={e => {
          e.preventDefault()
          setSaveStatus('pending')
          saveMutation.mutate()
        }}
      >
        <div>
          <label className={labelClass} htmlFor="ueber-mich">{t('ueberMich')}</label>
          <textarea
            id="ueber-mich"
            rows={4}
            value={ueberMich}
            onChange={e => setUeberMich(e.target.value)}
            placeholder={t('ueberMichPlaceholder')}
            className={inputClass}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="wunschrolle">{t('wunschrolle')}</label>
            <input
              id="wunschrolle"
              type="text"
              value={wunschrolle}
              onChange={e => setWunschrolle(e.target.value)}
              placeholder={t('wunschrollePlaceholder')}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass} htmlFor="erfahrungsjahre">{t('erfahrungsjahre')}</label>
            <input
              id="erfahrungsjahre"
              type="number"
              min={0}
              max={60}
              value={erfahrungsjahre}
              onChange={e => setErfahrungsjahre(e.target.value)}
              className={inputClass}
            />
          </div>
        </div>

        <div>
          <label className={labelClass} htmlFor="kernkompetenzen">{t('kernkompetenzen')}</label>
          <textarea
            id="kernkompetenzen"
            rows={2}
            value={kernkompetenzen}
            onChange={e => setKernkompetenzen(e.target.value)}
            placeholder={t('kernkompetenzenPlaceholder')}
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="soft-skills">{t('softSkills')}</label>
          <textarea
            id="soft-skills"
            rows={2}
            value={softSkills}
            onChange={e => setSoftSkills(e.target.value)}
            placeholder={t('softSkillsPlaceholder')}
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="werte">{t('werte')}</label>
          <textarea
            id="werte"
            rows={2}
            value={werte}
            onChange={e => setWerte(e.target.value)}
            placeholder={t('wertePlaceholder')}
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="arbeitsstil">{t('arbeitsstil')}</label>
          <select
            id="arbeitsstil"
            value={arbeitsstil}
            onChange={e => setArbeitsstil(e.target.value)}
            className={inputClass}
          >
            {ARBEITSSTIL_OPTIONS.map(opt => (
              <option key={opt} value={opt}>{t(`arbeitsstilOptions.${opt}`)}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            disabled={saveStatus === 'pending'}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-medium transition-colors disabled:opacity-50"
          >
            <Check size={16} aria-hidden /> {t('common:save')}
          </button>
          {saveStatus === 'saved' && (
            <span className="text-sm text-green-600 flex items-center gap-1">
              <Check size={14} aria-hidden /> {t('saved')}
            </span>
          )}
          {saveStatus === 'error' && (
            <span className="text-sm text-red-500 flex items-center gap-1">
              <AlertCircle size={14} aria-hidden /> {t('saveError')}
            </span>
          )}
        </div>
      </form>
    </div>
  )
}
