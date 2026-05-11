/**
 * Wochen-Ziel-Widget mit Fortschrittsbalken und Streak-Anzeige.
 */
import { useEffect, useState } from 'react'
import axios from 'axios'

interface Progress { wochenziel: number; diese_woche: number; prozent: number }
interface Streak { streak: number; letzte_aktivitaet: string | null }

export default function WeeklyGoalWidget() {
  const [progress, setProgress] = useState<Progress | null>(null)
  const [streak, setStreak] = useState<Streak | null>(null)

  useEffect(() => {
    axios.get('/api/stats/weekly-goal').then(r => setProgress(r.data))
    axios.get('/api/stats/streak').then(r => setStreak(r.data))
  }, [])

  if (!progress) return null

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="font-medium">Wochenziel</span>
          <span className="text-gray-500">{progress.diese_woche} / {progress.wochenziel}</span>
        </div>
        <div className="h-2.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden"
          role="progressbar" aria-valuenow={progress.prozent} aria-valuemin={0} aria-valuemax={100}
          aria-label={`Wochenziel: ${progress.prozent}% erreicht`}>
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-500"
            style={{ width: `${progress.prozent}%` }}
          />
        </div>
      </div>

      {streak && streak.streak > 0 && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-2xl" aria-hidden>🔥</span>
          <div>
            <p className="font-medium">{streak.streak} Tage Streak</p>
            <p className="text-xs text-gray-400">Zuletzt: {streak.letzte_aktivitaet}</p>
          </div>
        </div>
      )}
    </div>
  )
}
