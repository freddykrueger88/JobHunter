import { describe, it, expect } from 'vitest'
import { AxiosError } from 'axios'
import type { TFunction } from 'i18next'
import { getApiErrorMessage } from './api'

// Rework-Plan Phase E.2 (docs/analysis/REWORK_PLAN_DE.md): Testpyramide -
// getApiErrorMessage() ist die zentrale Uebersetzungslogik fuer den in
// Phase D.1 eingefuehrten Error-Toast (siehe components/ErrorToastContainer.tsx),
// deckt aber mehrere Fallback-Pfade ab, die bislang nur manuell per curl
// (Phase C.4) verifiziert wurden.

const TRANSLATIONS: Record<string, string> = {
  'common:errors.cv.not_found': 'CV nicht gefunden (übersetzt)',
  'common:errors.unknown': 'Unbekannter Fehler',
}

function makeFakeT(): TFunction {
  return ((key: string, opts?: { defaultValue?: string }) => {
    if (key in TRANSLATIONS) return TRANSLATIONS[key]
    return opts?.defaultValue ?? key
  }) as TFunction
}

function makeAxiosError(opts: {
  headers?: Record<string, string>
  data?: unknown
  message?: string
}): AxiosError {
  return new AxiosError(
    opts.message ?? 'Request failed',
    'ERR_BAD_REQUEST',
    undefined,
    undefined,
    {
      status: 404,
      statusText: 'Not Found',
      headers: opts.headers ?? {},
      // @ts-expect-error - Test-Fake, config wird von getApiErrorMessage nicht gelesen
      config: {},
      data: opts.data,
    },
  )
}

describe('getApiErrorMessage', () => {
  it('uebersetzt einen bekannten X-Error-Code aus dem Response-Header', () => {
    const err = makeAxiosError({ headers: { 'x-error-code': 'cv.not_found' } })
    expect(getApiErrorMessage(err, makeFakeT())).toBe('CV nicht gefunden (übersetzt)')
  })

  it('faellt bei unbekanntem Error-Code auf response.data.detail zurueck', () => {
    const err = makeAxiosError({
      headers: { 'x-error-code': 'noch.nicht.migriert' },
      data: { detail: 'Rohtext vom Backend' },
    })
    expect(getApiErrorMessage(err, makeFakeT())).toBe('Rohtext vom Backend')
  })

  it('faellt ohne Error-Code und ohne detail auf error.message zurueck', () => {
    const err = makeAxiosError({ message: 'Network Error' })
    expect(getApiErrorMessage(err, makeFakeT())).toBe('Network Error')
  })

  it('nutzt common:errors.unknown fuer Nicht-Axios-Fehler', () => {
    expect(getApiErrorMessage(new Error('irgendwas'), makeFakeT())).toBe('Unbekannter Fehler')
    expect(getApiErrorMessage('kein Error-Objekt', makeFakeT())).toBe('Unbekannter Fehler')
  })
})
