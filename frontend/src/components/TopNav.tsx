import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LayoutDashboard, Search, KanbanSquare, History, Settings } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import type { Theme } from '../context/ThemeContext'
import clsx from 'clsx'

const navItems = [
  { to: '/',        icon: LayoutDashboard, key: 'dashboard' },
  { to: '/jobs',    icon: Search,          key: 'jobs' },
  { to: '/kanban',  icon: KanbanSquare,    key: 'kanban' },
  { to: '/history', icon: History,         key: 'history' },
  { to: '/settings',icon: Settings,        key: 'settings' },
]

const themeOptions: { value: Theme; label: string }[] = [
  { value: 'dark',  label: '🌙 Dark' },
  { value: 'light', label: '☀️ Light' },
  { value: 'boys',  label: '💙 Boys' },
  { value: 'girls', label: '🌸 Girls' },
]

export default function TopNav() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme } = useTheme()

  return (
    <nav
      className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-gray-800 dark:bg-gray-950 shadow-md"
      role="navigation"
      aria-label="Hauptnavigation"
    >
      {/* Logo */}
      <span className="text-xl font-bold text-white select-none">🎯 JobHunter</span>

      {/* Nav Links */}
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
              aria-label={t(`nav.${key}`)}
            >
              <Icon size={16} aria-hidden="true" />
              <span className="hidden sm:inline">{t(`nav.${key}`)}</span>
            </NavLink>
          </li>
        ))}
      </ul>

      {/* Theme + Lang */}
      <div className="flex items-center gap-2">
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value as Theme)}
          className="bg-gray-700 text-white text-sm rounded px-2 py-1 border-0 focus:ring-2"
          aria-label="Design wählen"
        >
          {themeOptions.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
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
  )
}
