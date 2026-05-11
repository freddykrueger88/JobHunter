/**
 * Globaler Accessibility-Kontext.
 * Verwaltet ADHS-Modus, Kompaktansicht, Animations-Toggle.
 */
import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

export type Density = 'normal' | 'compact' | 'minimal'

interface A11yState {
  focusMode: boolean
  setFocusMode: (v: boolean) => void
  density: Density
  setDensity: (v: Density) => void
  reduceMotion: boolean
  setReduceMotion: (v: boolean) => void
  adhdMode: boolean
  setAdhdMode: (v: boolean) => void
}

const A11yContext = createContext<A11yState>({
  focusMode: false, setFocusMode: () => {},
  density: 'normal', setDensity: () => {},
  reduceMotion: false, setReduceMotion: () => {},
  adhdMode: false, setAdhdMode: () => {},
})

function ls<T>(key: string, fallback: T): T {
  try { const v = localStorage.getItem(key); return v !== null ? JSON.parse(v) : fallback }
  catch { return fallback }
}

export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const [focusMode, setFocusModeState] = useState(() => ls('a11y_focusMode', false))
  const [density, setDensityState] = useState<Density>(() => ls('a11y_density', 'normal'))
  const [reduceMotion, setReduceMotionState] = useState(() => ls('a11y_reduceMotion', false))
  const [adhdMode, setAdhdModeState] = useState(() => ls('a11y_adhdMode', false))

  const apply = (html: HTMLElement, fm: boolean, rm: boolean, d: Density, adhd: boolean) => {
    html.classList.toggle('focus-mode', fm)
    html.classList.toggle('reduce-motion', rm)
    html.classList.remove('density-normal', 'density-compact', 'density-minimal')
    html.classList.add(`density-${d}`)
    html.classList.toggle('adhd-mode', adhd)
  }

  useEffect(() => { apply(document.documentElement, focusMode, reduceMotion, density, adhdMode) }, [])

  const setFocusMode = (v: boolean) => {
    setFocusModeState(v); localStorage.setItem('a11y_focusMode', JSON.stringify(v))
    document.documentElement.classList.toggle('focus-mode', v)
  }
  const setReduceMotion = (v: boolean) => {
    setReduceMotionState(v); localStorage.setItem('a11y_reduceMotion', JSON.stringify(v))
    document.documentElement.classList.toggle('reduce-motion', v)
  }
  const setDensity = (v: Density) => {
    setDensityState(v); localStorage.setItem('a11y_density', JSON.stringify(v))
    const html = document.documentElement
    html.classList.remove('density-normal', 'density-compact', 'density-minimal')
    html.classList.add(`density-${v}`)
  }
  const setAdhdMode = (v: boolean) => {
    setAdhdModeState(v); localStorage.setItem('a11y_adhdMode', JSON.stringify(v))
    document.documentElement.classList.toggle('adhd-mode', v)
    // ADHS-Modus impliziert reduce-motion
    if (v) setReduceMotion(true)
  }

  return (
    <A11yContext.Provider value={{ focusMode, setFocusMode, density, setDensity, reduceMotion, setReduceMotion, adhdMode, setAdhdMode }}>
      {children}
    </A11yContext.Provider>
  )
}

export const useA11y = () => useContext(A11yContext)
