import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

export type Theme = 'dark' | 'light' | 'boys' | 'girls' | 'dyslexic'
export type ColorBlindMode = 'none' | 'deuteranopia' | 'protanopia' | 'tritanopia' | 'achromatopsia'

const CB_CLASSES: ColorBlindMode[] = ['deuteranopia', 'protanopia', 'tritanopia', 'achromatopsia']

interface ThemeContextType {
  theme: Theme
  setTheme: (t: Theme) => void
  colorBlindMode: ColorBlindMode
  setColorBlindMode: (m: ColorBlindMode) => void
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark', setTheme: () => {},
  colorBlindMode: 'none', setColorBlindMode: () => {},
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem('theme') as Theme) ?? 'dark'
  )
  const [colorBlindMode, setColorBlindModeState] = useState<ColorBlindMode>(
    () => (localStorage.getItem('colorBlindMode') as ColorBlindMode) ?? 'none'
  )

  const applyTheme = (t: Theme) => {
    const html = document.documentElement
    // Dark/Light-Klasse
    html.classList.remove('dark', 'light', 'boys', 'girls', 'dyslexic')
    html.classList.add(t === 'dark' || t === 'boys' || t === 'dyslexic' ? 'dark' : 'light')
    html.classList.add(t)
  }

  const applyColorBlind = (m: ColorBlindMode) => {
    const html = document.documentElement
    CB_CLASSES.forEach(c => html.classList.remove(`cb-${c}`))
    if (m !== 'none') html.classList.add(`cb-${m}`)
  }

  const setTheme = (t: Theme) => {
    setThemeState(t)
    localStorage.setItem('theme', t)
    applyTheme(t)
  }

  const setColorBlindMode = (m: ColorBlindMode) => {
    setColorBlindModeState(m)
    localStorage.setItem('colorBlindMode', m)
    applyColorBlind(m)
  }

  useEffect(() => { applyTheme(theme) }, [])
  useEffect(() => { applyColorBlind(colorBlindMode) }, [])

  return (
    <ThemeContext.Provider value={{ theme, setTheme, colorBlindMode, setColorBlindMode }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
