import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LayoutDashboard, Search, KanbanSquare, History, Settings, Bell, Bot, FileText } from 'lucide-react'
import clsx from 'clsx'
import CoachChatDrawer from './CoachChatDrawer'

const navItems = [
  { to: '/',          icon: LayoutDashboard, key: 'dashboard' },
  { to: '/jobs',      icon: Search,          key: 'jobs' },
  { to: '/kanban',    icon: KanbanSquare,    key: 'kanban' },
  { to: '/reminders', icon: Bell,            key: 'reminders' },
  { to: '/templates', icon: FileText,        key: 'templates' },
  { to: '/history',   icon: History,         key: 'history' },
  { to: '/settings',  icon: Settings,        key: 'settings' },
]

export default function TopNav() {
  const { t, i18n } = useTranslation()
  const [coachOpen, setCoachOpen] = useState(false)

  return (
    <>
      <nav
        className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-gray-800 dark:bg-gray-950 shadow-md"
        role="navigation"
        aria-label="Hauptnavigation"
      >
        <span className="text-xl font-bold text-white select-none">🎯 JobHunter</span>

        <ul className="flex gap-1" role="menubar">
          {navItems.map(({ to, icon: Icon, key }) => (
            <li key={key} role="none">
              <NavLink
                to={to}
                end={to === '/'}
                role="menuitem"
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors focus-visible:ring-2',
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  )
                }
                aria-label={t(`nav.${key}`, key)}
              >
                <Icon size={16} aria-hidden="true" />
                <span className="hidden sm:inline">{t(`nav.${key}`, key)}</span>
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
