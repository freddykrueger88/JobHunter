import { useState, lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { AccessibilityProvider, useA11y } from './context/AccessibilityContext'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import { useTranslation } from 'react-i18next'
import { Loader2 } from 'lucide-react'
import TopNav from './components/TopNav'
import ShortcutOverlay from './components/ShortcutOverlay'
import UndoToast from './components/UndoToast'
import ErrorToastContainer from './components/ErrorToastContainer'
import SakuraPetals from './components/SakuraPetals'
import Dashboard from './pages/Dashboard'
import { useUndoToast } from './hooks/useUndoToast'

// Rework-Plan D.4: Routen ausser der Startseite per Code-Splitting nachladen
// (vite build zeigte einen einzelnen 470KB/144KB-gzip-Hauptchunk fuer alle
// Seiten). Dashboard bleibt eager, damit der erste sichtbare Screen ohne
// Suspense-Fallback-Flackern erscheint.
const Jobs = lazy(() => import('./pages/Jobs'))
const Kanban = lazy(() => import('./pages/Kanban'))
const History = lazy(() => import('./pages/History'))
const Settings = lazy(() => import('./pages/Settings'))
const Reminders = lazy(() => import('./pages/Reminders'))
const SearchProfiles = lazy(() => import('./pages/SearchProfiles'))
const InterviewSimulator = lazy(() => import('./pages/InterviewSimulator'))
const CompanyDossierPage = lazy(() => import('./pages/CompanyDossierPage'))
const Templates = lazy(() => import('./pages/Templates'))

function RouteFallback() {
  const { t } = useTranslation('common')
  return (
    <div className="flex items-center justify-center py-24" role="status" aria-label={t('loading')}>
      <Loader2 size={28} className="animate-spin text-gray-400" aria-hidden />
    </div>
  )
}

function AppInner() {
  const [shortcutOpen, setShortcutOpen] = useState(false)
  const { focusMode, setFocusMode } = useA11y()
  const { state: undoState, undo, dismiss } = useUndoToast()

  useKeyboardShortcuts(
    () => setShortcutOpen(true),
    () => setFocusMode(!focusMode),
  )

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      <TopNav />

      <main id="main-content" className="container mx-auto px-4 py-6">
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/kanban" element={<Kanban />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/reminders" element={<Reminders />} />
            <Route path="/search-profiles" element={<SearchProfiles />} />
            <Route path="/interview-simulator" element={<InterviewSimulator />} />
            <Route path="/company-dossier" element={<CompanyDossierPage />} />
            <Route path="/templates" element={<Templates />} />
          </Routes>
        </Suspense>
      </main>

      <ShortcutOverlay isOpen={shortcutOpen} onClose={() => setShortcutOpen(false)} />
      <UndoToast state={undoState} onUndo={undo} onDismiss={dismiss} />
      <ErrorToastContainer />
      <SakuraPetals />
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AccessibilityProvider>
        <AppInner />
      </AccessibilityProvider>
    </ThemeProvider>
  )
}
