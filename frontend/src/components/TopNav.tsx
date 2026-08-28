import { useEffect, useRef, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  LayoutDashboard, Search, KanbanSquare, History, Settings, Bell, Bot, FileText,
  User, Radar, Mic, Building2, Ban, BookOpen, ChevronDown, TrendingUp,
} from 'lucide-react'
import clsx from 'clsx'
import CoachChatDrawer from './CoachChatDrawer'

// Haeufig genutzte Kernseiten bleiben direkt sichtbar. Die uebrigen
// Werkzeuge/Recherche-Seiten (urspruenglich alle flach in einer Reihe -
// mit Blocklist/Diary aus dieser Session waren es 13 Eintraege, zu
// unuebersichtlich fuer eine einzelne Zeile) sind unter "Werkzeuge"
// gruppiert. Profil/Einstellungen bleiben als eigener Account-Bereich
// separat, wie zuvor.
const primaryItems = [
  { to: '/',         icon: LayoutDashboard, key: 'dashboard' },
  { to: '/jobs',      icon: Search,          key: 'jobs' },
  { to: '/kanban',    icon: KanbanSquare,    key: 'kanban' },
  { to: '/reminders', icon: Bell,            key: 'reminders' },
]

const toolItems = [
  { to: '/search-profiles',     icon: Radar,     key: 'searchProfiles' },
  { to: '/interview-simulator', icon: Mic,       key: 'interviewSimulator' },
  { to: '/company-dossier',     icon: Building2, key: 'companyDossier' },
  { to: '/templates',           icon: FileText,  key: 'templates' },
  { to: '/diary',                icon: BookOpen,  key: 'diary' },
  { to: '/blocklist',           icon: Ban,       key: 'blocklist' },
  { to: '/history',             icon: History,   key: 'history' },
  { to: '/branchen-radar',      icon: TrendingUp, key: 'branchenRadar' },
]

const accountItems = [
  { to: '/profile',  icon: User,     key: 'profile' },
  { to: '/settings', icon: Settings, key: 'settings' },
]

function navLinkClass({ isActive }: { isActive: boolean }) {
  return clsx(
    'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors focus-visible:ring-2',
    isActive
      ? 'bg-blue-600 text-white'
      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
  )
}

export default function TopNav() {
  const { t, i18n } = useTranslation('nav')
  const [coachOpen, setCoachOpen] = useState(false)
  const [toolsOpen, setToolsOpen] = useState(false)
  const toolsRef = useRef<HTMLLIElement>(null)
  const location = useLocation()

  const isToolActive = toolItems.some(item => item.to === location.pathname)

  // Menü schließen bei Klick außerhalb oder Escape - Standard-ARIA-
  // Menu-Button-Verhalten, da kein Dropdown ohne eigene Bibliothek im
  // Projekt existiert.
  useEffect(() => {
    if (!toolsOpen) return
    const onClick = (e: MouseEvent) => {
      if (toolsRef.current && !toolsRef.current.contains(e.target as Node)) {
        setToolsOpen(false)
      }
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setToolsOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [toolsOpen])

  // Beim Navigieren (Klick auf einen Werkzeug-Link) automatisch schließen
  useEffect(() => { setToolsOpen(false) }, [location.pathname])

  return (
    <>
      <nav
        className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-gray-800 dark:bg-gray-950 shadow-md"
        role="navigation"
        aria-label="Hauptnavigation"
      >
        <NavLink to="/" className="shrink-0 flex items-center" aria-label="JobHunter – Startseite">
          <img src="/logo.png" alt="JobHunter" className="h-8 w-auto" />
        </NavLink>

        <ul className="flex flex-wrap items-center gap-1" role="menubar">
          {primaryItems.map(({ to, icon: Icon, key }) => (
            <li key={key} role="none">
              <NavLink to={to} end={to === '/'} role="menuitem" className={navLinkClass} aria-label={t(key, key)}>
                <Icon size={16} aria-hidden="true" />
                <span className="hidden sm:inline">{t(key, key)}</span>
              </NavLink>
            </li>
          ))}

          {/* Werkzeuge-Dropdown */}
          <li role="none" className="relative" ref={toolsRef}>
            <button
              onClick={() => setToolsOpen(o => !o)}
              role="menuitem"
              aria-haspopup="menu"
              aria-expanded={toolsOpen}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors focus-visible:ring-2',
                isToolActive || toolsOpen
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              )}
            >
              <span className="hidden sm:inline">{t('tools', 'Werkzeuge')}</span>
              <span className="sm:hidden">{t('toolsShort', 'Mehr')}</span>
              <ChevronDown size={14} aria-hidden className={clsx('transition-transform', toolsOpen && 'rotate-180')} />
            </button>
            {toolsOpen && (
              <ul
                role="menu"
                aria-label={t('tools', 'Werkzeuge')}
                className="absolute left-0 mt-1 w-56 bg-gray-800 dark:bg-gray-900 rounded-lg shadow-lg border border-gray-700 py-1 z-50"
              >
                {toolItems.map(({ to, icon: Icon, key }) => (
                  <li key={key} role="none">
                    <NavLink
                      to={to}
                      role="menuitem"
                      className={({ isActive }) =>
                        clsx(
                          'flex items-center gap-2 px-4 py-2 text-sm transition-colors',
                          isActive
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        )
                      }
                    >
                      <Icon size={16} aria-hidden="true" />
                      {t(key, key)}
                    </NavLink>
                  </li>
                ))}
              </ul>
            )}
          </li>

          {/* Account-Bereich */}
          {accountItems.map(({ to, icon: Icon, key }) => (
            <li key={key} role="none">
              <NavLink to={to} role="menuitem" className={navLinkClass} aria-label={t(key, key)}>
                <Icon size={16} aria-hidden="true" />
                <span className="hidden sm:inline">{t(key, key)}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2">
          {/* Coach-Button */}
          <button
            onClick={() => setCoachOpen(true)}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors',
              coachOpen
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            )}
            aria-label="Bewerbungscoach öffnen"
          >
            <Bot size={16} aria-hidden />
            <span className="hidden sm:inline">Coach</span>
          </button>

          {/* Sprache – schneller Wechsel ohne Umweg über Einstellungen */}
          <button
            onClick={() => {
              const next = i18n.language === 'de' ? 'en' : 'de'
              i18n.changeLanguage(next)
              localStorage.setItem('lang', next)
            }}
            className="text-sm text-gray-300 hover:text-white px-2 py-1 rounded hover:bg-gray-700 transition-colors"
            aria-label="Sprache wechseln"
          >
            {i18n.language === 'de' ? '🇬🇧 EN' : '🇩🇪 DE'}
          </button>
        </div>
      </nav>

      {/* Globaler Coach-Drawer – ohne Bewerbungskontext */}
      <CoachChatDrawer
        open={coachOpen}
        onClose={() => setCoachOpen(false)}
      />
    </>
  )
}
