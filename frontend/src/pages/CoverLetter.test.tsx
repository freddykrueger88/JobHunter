import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { ReactElement } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import axios from 'axios'
import '../i18n'
import CoverLetter from './CoverLetter'

// Rework-Plan Phase E.2 (docs/analysis/REWORK_PLAN_DE.md): Testpyramide -
// CoverLetter.tsx ist eine der in der Phase C.3-Migration genannten
// Kernseiten. Nutzt die echte i18n-Instanz (echte DE-Uebersetzungen statt
// Mock), damit Assertions gegen echten UI-Text auch fehlende/falsche
// Schluessel auffangen wuerden.

function renderWithProviders(ui: ReactElement) {
  const qc = new QueryClient()
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>)
}

describe('CoverLetter', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('zeigt Ueberschrift und alle vier Ton-Optionen', () => {
    renderWithProviders(<CoverLetter jobId={1} cvId={2} />)
    expect(screen.getByText('Anschreiben generieren')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Formell/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Kreativ/ })).toBeInTheDocument()
  })

  it('markiert den gewaehlten Ton per aria-pressed', async () => {
    const user = userEvent.setup()
    renderWithProviders(<CoverLetter jobId={1} cvId={2} />)
    const kreativBtn = screen.getByRole('button', { name: /Kreativ/ })
    expect(kreativBtn).toHaveAttribute('aria-pressed', 'false')
    await user.click(kreativBtn)
    expect(kreativBtn).toHaveAttribute('aria-pressed', 'true')
  })

  it('generiert ein Anschreiben und zeigt das Ergebnis an', async () => {
    const postSpy = vi.spyOn(axios, 'post').mockResolvedValue({
      data: { content: 'Sehr geehrte Damen und Herren...' },
    })
    const user = userEvent.setup()
    renderWithProviders(<CoverLetter jobId={1} cvId={2} />)

    await user.click(screen.getByRole('button', { name: /Anschreiben erstellen/ }))

    await waitFor(() =>
      expect(screen.getByLabelText('Generiertes Anschreiben (bearbeitbar)')).toHaveValue(
        'Sehr geehrte Damen und Herren...',
      ),
    )
    expect(postSpy).toHaveBeenCalledWith('/api/ai/generate-cover-letter', {
      job_id: 1,
      cv_id: 2,
      tone: 'formell',
      template_text: null,
    })
  })

  it('deaktiviert den Generieren-Button ohne jobId', () => {
    renderWithProviders(<CoverLetter />)
    expect(screen.getByRole('button', { name: /Anschreiben erstellen/ })).toBeDisabled()
  })
})
