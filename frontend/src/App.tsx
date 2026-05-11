import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import TopNav from './components/TopNav'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Kanban from './pages/Kanban'
import History from './pages/History'
import Settings from './pages/Settings'
import Reminders from './pages/Reminders'
import SearchProfiles from './pages/SearchProfiles'

export default function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
        <TopNav />
        {/* main-content Anker für Skip-Link (WCAG 2.4.1) */}
        <main id="main-content" className="container mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/kanban" element={<Kanban />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/reminders" element={<Reminders />} />
            <Route path="/search-profiles" element={<SearchProfiles />} />
          </Routes>
        </main>
      </div>
    </ThemeProvider>
  )
}
