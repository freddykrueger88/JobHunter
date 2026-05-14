import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { AccessibilityProvider, useA11y } from './context/AccessibilityContext'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import TopNav from './components/TopNav'
import ShortcutOverlay from './components/ShortcutOverlay'
import UndoToast from './components/UndoToast'
import SakuraPetals from './components/SakuraPetals'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Kanban from './pages/Kanban'
import History from './pages/History'
import Settings from './pages/Settings'
import Reminders from './pages/Reminders'
import SearchProfiles from './pages/SearchProfiles'
import InterviewSimulator from './pages/InterviewSimulator'
import CompanyDossier from './pages/CompanyDossier'
import { useUndoToast } from './hooks/useUndoToast'

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
      <TopNav focusMode={focusMode} />

      <main id="main-content" className="container mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/kanban" element={<Kanban />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/search-profiles" element={<SearchProfiles />} />
          <Route path="/interview-simulator" element={<InterviewSimulator />} />
          <Route path="/company-dossier" element={<CompanyDossier />} />
        </Routes>
      </main>

      <ShortcutOverlay isOpen={shortcutOpen} onClose={() => setShortcutOpen(false)} />
      <UndoToast state={undoState} onUndo={undo} onDismiss={dismiss} />
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
