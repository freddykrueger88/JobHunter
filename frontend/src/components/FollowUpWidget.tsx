/**
 * FollowUpWidget – Wiedervorlagen-Dashboard-Widget (Issue #64, v1.9)
 *
 * Zeigt alle offenen Wiedervorlagen mit Ampel-Farbcodierung.
 * Laedt Daten vom neuen /api/followups/-Endpoint statt aus notes-JSON-Hack.
 *
 * Features:
 *  - Ampel: urgent (rot) / soon (gelb) / later (gruen)
 *  - Erledigen mit optimistischem UI-Update
 *  - 1-Klick Nachfass-Vorlage kopieren
 *  - Skeleton-Loader, Empty-State, Fehler-State
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import axios from 'axios'
import {
  AlertCircle,
  Bell,
  Check,
  ChevronRight,
  Clock,
  Copy,
  Loader2,
} from 'lucide-react'
import { Link } from 'react-router-dom'

// ---------------------------------------------------------------------------
// Typen (spiegeln FollowUpResponse vom Backend wider)
// ---------------------------------------------------------------------------

export type AmpelStatus = 'urgent' | 'soon' | 'later' | 'done'

export interface FollowUpItem {
  id: number
  application_id: number
  faellig_am: string       // ISO-String
  notiz: string | null
  erledigt: boolean
  tage_bis_faellig: number // negativ = ueberfaellig
  ampel: AmpelStatus
  firma: string | null
  stelle: string | null
}

export interface FollowUpStats {
  urgent: number
  soon: number
  later: number
  done: number
  gesamt_offen: number
}

// ---------------------------------------------------------------------------
// Ampel-Konfiguration
// ---------------------------------------------------------------------------

const AMPEL: Record<
  Exclude<AmpelStatus, 'done'>,
  { icon: typeof AlertCircle; dot: string; text: string; badge: string; label: string }
> = {
  urgent: {
    icon: AlertCircle,
    dot: 'bg-red-500',
    text: 'text-red-500 dark:text-red-400',
    badge: 'bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400 ring-1 ring-red-200 dark:ring-red-800',
    label: 'Heute fällig',
  },
  soon: {
    icon: Clock,
    dot: 'bg-yellow-400',
    text: 'text-yellow-600 dark:text-yellow-400',
    badge: 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 ring-1 ring-yellow-200 dark:ring-yellow-800',
    label: 'Morgen fällig',
  },
  later: {
    icon: Clock,
    dot: 'bg-green-500',
    text: 'text-green-600 dark:text-green-400',
    badge: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400 ring-1 ring-green-200 dark:ring-green-800',
    label: '',
  },
}

function formatDue(item: FollowUpItem): string {
  const diff = item.tage_bis_faellig
  if (diff < 0)  return `${Math.abs(diff)} Tage überfällig`
  if (diff === 0) return 'Heute'
  if (diff === 1) return 'Morgen'
  return `in ${diff} Tagen`
}

// ---------------------------------------------------------------------------
// Sub-Komponente: Skeleton
// ---------------------------------------------------------------------------

function Skeleton() {
  return (
    <div className="space-y-2" aria-busy="true" aria-label="Lade Wiedervorlagen…">
      {[1, 2, 3].map(i => (
        <div
          key={i}
          className="h-14 rounded-xl bg-gray-100 dark:bg-gray-700/60 animate-pulse"
        />
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sub-Komponente: Stats-Chips
// ---------------------------------------------------------------------------

function StatsRow({ stats }: { stats: FollowUpStats }) {
  if (stats.gesamt_offen === 0) return null
  return (
    <div className="flex gap-2 flex-wrap mb-3" role="status" aria-label="Wiedervorlagen-Übersicht">
      {stats.urgent > 0 && (
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${AMPEL.urgent.badge}`}>
          🔴 {stats.urgent} heute
        </span>
      )}
      {stats.soon > 0 && (
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${AMPEL.soon.badge}`}>
          🟡 {stats.soon} morgen
        </span>
      )}
      {stats.later > 0 && (
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${AMPEL.later.badge}`}>
          🟢 {stats.later} diese Woche
        </span>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sub-Komponente: Einzelne Zeile
// ---------------------------------------------------------------------------

interface RowProps {
  item: FollowUpItem
  onDone: (id: number) => void
  onCopy: (id: number) => void
  copyingId: number | null
  donePending: Set<number>
}

function FollowUpRow({ item, onDone, onCopy, copyingId, donePending }: RowProps) {
  const cfg = item.ampel !== 'done' ? AMPEL[item.ampel] : AMPEL.later
  const Icon = cfg.icon
  const isPending = donePending.has(item.id)

  return (
    <li
      className={`group flex items-center gap-2 px-3 py-2.5 rounded-xl transition-all duration-200
        hover:bg-gray-50 dark:hover:bg-gray-700/50
        ${isPending ? 'opacity-40 pointer-events-none' : ''}`}
    >
      {/* Ampel-Dot */}
      <span
        className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot}`}
        aria-hidden
      />

      {/* Content */}
      <Link
        to={`/applications/${item.application_id}`}
        className="flex-1 min-w-0 flex items-center gap-2"
        aria-label={`${item.stelle ?? 'Stelle'} bei ${item.firma ?? 'Firma'} – ${formatDue(item)}`}
      >
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">
            {item.stelle ?? 'Unbekannte Stelle'}
          </p>
          <p className="text-xs text-gray-400 truncate">
            {item.firma ?? 'Unbekannte Firma'}
            <span className={`ml-2 font-semibold ${cfg.text}`}>
              {formatDue(item)}
            </span>
          </p>
          {item.notiz && (
            <p className="text-xs text-gray-400 truncate italic mt-0.5">
              {item.notiz}
            </p>
          )}
        </div>
        <ChevronRight
          size={14}
          className="text-gray-300 group-hover:text-gray-500 flex-shrink-0 dark:text-gray-600"
          aria-hidden
        />
      </Link>

      {/* Vorlage-Copy-Button */}
      <button
        onClick={() => onCopy(item.id)}
        className="flex-shrink-0 p-1.5 rounded-lg text-gray-400 hover:text-gray-600
          hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        title="Nachfass-Vorlage kopieren"
        aria-label="Nachfass-E-Mail-Vorlage in Zwischenablage kopieren"
      >
        {copyingId === item.id
          ? <Check size={14} className="text-green-500" />
          : <Copy size={14} />}
      </button>

      {/* Erledigt-Button */}
      <button
        onClick={() => onDone(item.id)}
        className="flex-shrink-0 p-1.5 rounded-lg text-gray-400 hover:text-green-600
          hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors"
        title="Als erledigt markieren"
        aria-label="Wiedervorlage als erledigt markieren"
      >
        <Check size={14} />
      </button>
    </li>
  )
}

// ---------------------------------------------------------------------------
// Haupt-Widget
// ---------------------------------------------------------------------------

interface FollowUpWidgetProps {
  /** Maximale Anzahl anzuzeigender Eintraege (Default: 5) */
  maxItems?: number
  /** Callback nach erfolgreichem Erledigen – z.B. fuer UndoToast */
  onDone?: (item: FollowUpItem) => void
}

export default function FollowUpWidget({ maxItems = 5, onDone }: FollowUpWidgetProps) {
  const [items, setItems]           = useState<FollowUpItem[]>([])
  const [stats, setStats]           = useState<FollowUpStats | null>(null)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(false)
  const [copyingId, setCopyingId]   = useState<number | null>(null)
  const [donePending, setDonePending] = useState<Set<number>>(new Set())
  const copyTimerRef                = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Daten laden
  const load = useCallback(async () => {
    try {
      setError(false)
      const [listRes, statsRes] = await Promise.all([
        axios.get<FollowUpItem[]>('/api/followups/'),
        axios.get<FollowUpStats>('/api/followups/stats'),
      ])
      setItems(listRes.data)
      setStats(statsRes.data)
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  // Erledigen – optimistisches UI-Update
  const handleDone = useCallback(async (id: number) => {
    const item = items.find(i => i.id === id)
    if (!item) return

    // Optimistisch entfernen
    setDonePending(prev => new Set(prev).add(id))
    setItems(prev => prev.filter(i => i.id !== id))
    setStats(prev => prev
      ? { ...prev, [item.ampel]: Math.max(0, prev[item.ampel as keyof FollowUpStats] as number - 1),
          gesamt_offen: Math.max(0, prev.gesamt_offen - 1),
          done: prev.done + 1 }
      : prev
    )

    try {
      await axios.patch(`/api/followups/${id}/erledigt`)
      onDone?.(item)
    } catch {
      // Rollback bei Fehler
      setItems(prev => [...prev, item].sort(
        (a, b) => new Date(a.faellig_am).getTime() - new Date(b.faellig_am).getTime()
      ))
      setStats(prev => prev
        ? { ...prev, [item.ampel]: (prev[item.ampel as keyof FollowUpStats] as number) + 1,
            gesamt_offen: prev.gesamt_offen + 1,
            done: Math.max(0, prev.done - 1) }
        : prev
      )
    } finally {
      setDonePending(prev => { const s = new Set(prev); s.delete(id); return s })
    }
  }, [items, onDone])

  // Vorlage kopieren
  const handleCopy = useCallback(async (id: number) => {
    if (copyTimerRef.current) clearTimeout(copyTimerRef.current)
    try {
      const { data } = await axios.get<{ vorlage: string }>(`/api/followups/${id}/vorlage`)
      await navigator.clipboard.writeText(data.vorlage)
      setCopyingId(id)
      copyTimerRef.current = setTimeout(() => setCopyingId(null), 2000)
    } catch {
      // Clipboard nicht verfuegbar – still fail
    }
  }, [])

  // Cleanup
  useEffect(() => () => {
    if (copyTimerRef.current) clearTimeout(copyTimerRef.current)
  }, [])

  // ── Render-States ────────────────────────────────────────────────────────

  if (loading) return <Skeleton />

  if (error) {
    return (
      <div className="flex flex-col items-center py-6 text-gray-400 text-sm gap-2">
        <AlertCircle size={24} className="text-red-400" aria-hidden />
        <p>Wiedervorlagen konnten nicht geladen werden.</p>
        <button
          onClick={load}
          className="text-xs text-blue-500 hover:underline"
        >
          Erneut versuchen
        </button>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div
        className="flex flex-col items-center py-6 text-gray-400"
        role="status"
        aria-label="Keine Wiedervorlagen fällig"
      >
        <Bell size={28} className="mb-2" aria-hidden />
        <p className="text-sm">Keine offenen Wiedervorlagen</p>
        <Link
          to="/followups"
          className="mt-2 text-xs text-blue-500 hover:underline"
        >
          Alle anzeigen
        </Link>
      </div>
    )
  }

  const visible = items.slice(0, maxItems)
  const hidden  = items.length - visible.length

  return (
    <div>
      {stats && <StatsRow stats={stats} />}

      <ul className="space-y-0.5" role="list" aria-label="Offene Wiedervorlagen">
        {visible.map(item => (
          <FollowUpRow
            key={item.id}
            item={item}
            onDone={handleDone}
            onCopy={handleCopy}
            copyingId={copyingId}
            donePending={donePending}
          />
        ))}
      </ul>

      {hidden > 0 && (
        <Link
          to="/followups"
          className="mt-3 flex items-center gap-1 text-xs text-blue-500 hover:underline px-3"
          aria-label={`${hidden} weitere Wiedervorlagen anzeigen`}
        >
          <ChevronRight size={12} aria-hidden />
          {hidden} weitere anzeigen
        </Link>
      )}
    </div>
  )
}
