import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// Ohne "globals: true" in vite.config.ts registriert @testing-library/react
// sein afterEach(cleanup) nicht automatisch (das haengt an einem globalen
// afterEach-Symbol) - explizit noetig, sonst bleiben DOM-Baeume vorheriger
// Tests stehen und Queries wie getByRole() finden mehrere Treffer.
afterEach(() => {
  cleanup()
})
