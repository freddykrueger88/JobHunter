import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Plus, Play, Pause, Trash2, RefreshCw, Loader2, Clock } from 'lucide-react'
import clsx from 'clsx'

interface SearchProfile {
  id: number
  name: string
  keywords: string
  location: string
  radius_km: number
  schedule: string
  is_active: boolean
  last_run: string | null
  last_result_count: number
}

const SCHEDULE_LABELS: Record<string, string> = {
  daily: '🗓️ Täglich (08:00)',
  weekly: '🗓️ Wöchentlich (Mo 08:00)',
}

export default function SearchProfiles() {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('')
  const [radius, setRadius] = useState(25)
  const [schedule, setSchedule] = useState('daily')
  const [runningId, setRunningId] = useState<number | null>(null)

  const { data: profiles = [], isLoading } = useQuery<SearchProfile[]>({
    queryKey: ['search-profiles'],
    queryFn: () => axios.get('/api/search-profiles/').then(r => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => axios.post('/api/search-profiles/', { name, keywords, location, radius_km: radius, schedule }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['search-profiles'] })
      setName(''); setKeywords(''); setLocation('')
    },
  })

  const toggleMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/search-profiles/${id}/toggle`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['search-profiles'] }),
  })

  const runNowMutation = useMutation({
    mutationFn: async (id: number) => {
      setRunningId(id)
      const r = await axios.post(`/api/search-profiles/${id}/run-now`)
      return r.data
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['search-profiles'] })
      qc.invalidateQueries({ queryKey: ['jobs'] })
      setRunningId(null)
    },
    onError: () => setRunningId(null),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/search-profiles/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['search-profiles'] }),
  })

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Clock size={22} aria-hidden /> Automatische Suche
      </h1>

      {/* Neues Profil */}
      <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 mb-6 space-y-3">
        <h2 className="text-sm font-semibold text-gray-500">Neues Suchprofil</h2>
        <input className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Name, z.B. IT-Support Bremen" value={name} onChange={e => setName(e.target.value)} aria-label="Profilname" />
        <div className="flex gap-2">
          <input className="flex-1 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Suchbegriff" value={keywords} onChange={e => setKeywords(e.target.value)} aria-label="Suchbegriff" />
          <input className="w-36 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ort" value={location} onChange={e => setLocation(e.target.value)} aria-label="Ort" />
          <select className="w-24 rounded-lg px-2 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
            value={radius} onChange={e => setRadius(Number(e.target.value))} aria-label="Radius">
            {[10, 25, 50, 100].map(r => <option key={r} value={r}>{r} km</option>)}
          </select>
        </div>
        <div className="flex items-center gap-3">
          <select className="rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
            value={schedule} onChange={e => setSchedule(e.target.value)} aria-label="Zeitplan">
            <option value="daily">🗓️ Täglich</option>
            <option value="weekly">🗓️ Wöchentlich</option>
          </select>
          <button onClick={() => createMutation.mutate()}
            disabled={!name || !keywords || !location || createMutation.isPending}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium ml-auto transition-colors">
            <Plus size={15} aria-hidden /> Profil anlegen
          </button>
        </div>
      </div>

      {/* Profil-Liste */}
      {isLoading && <p className="text-gray-400 text-sm">Lädt...</p>}
      <ul className="space-y-3">
        {profiles.map(p => (
          <li key={p.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className={clsx('w-2 h-2 rounded-full shrink-0', p.is_active ? 'bg-green-500' : 'bg-gray-400')} aria-hidden />
                  <p className="font-semibold truncate">{p.name}</p>
                </div>
                <p className="text-sm text-gray-500 mt-0.5">
                  „{p.keywords}“ • {p.location} • {p.radius_km} km
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  {SCHEDULE_LABELS[p.schedule] ?? p.schedule}
                  {p.last_run && ` • Letzter Lauf: ${new Date(p.last_run).toLocaleString('de-DE')}`}
                  {p.last_result_count > 0 && ` • ${p.last_result_count} neue Treffer`}
                </p>
              </div>
              <div className="flex gap-1 shrink-0">
                <button onClick={() => runNowMutation.mutate(p.id)}
                  disabled={runningId === p.id}
                  className="text-blue-500 hover:text-blue-700 p-2 rounded transition-colors disabled:opacity-50"
                  aria-label="Jetzt ausführen">
                  {runningId === p.id
                    ? <Loader2 size={15} className="animate-spin" aria-hidden />
                    : <RefreshCw size={15} aria-hidden />}
                </button>
                <button onClick={() => toggleMutation.mutate(p.id)}
                  className={clsx('p-2 rounded transition-colors', p.is_active ? 'text-yellow-500 hover:text-yellow-700' : 'text-green-500 hover:text-green-700')}
                  aria-label={p.is_active ? 'Deaktivieren' : 'Aktivieren'}>
                  {p.is_active ? <Pause size={15} aria-hidden /> : <Play size={15} aria-hidden />}
                </button>
                <button onClick={() => deleteMutation.mutate(p.id)}
                  className="text-red-400 hover:text-red-600 p-2 rounded transition-colors"
                  aria-label="Profil löschen">
                  <Trash2 size={15} aria-hidden />
                </button>
              </div>
            </div>
          </li>
        ))}
        {!isLoading && profiles.length === 0 && (
          <li className="text-gray-400 text-sm text-center py-8">
            Noch keine Suchprofile – lege oben eines an 👆
          </li>
        )}
      </ul>
    </div>
  )
}
