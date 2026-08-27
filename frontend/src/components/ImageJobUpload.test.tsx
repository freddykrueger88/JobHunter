import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'
import axios from 'axios'
import '../i18n'
import ImageJobUpload from './ImageJobUpload'

// Regressionsschutz: preview nutzte URL.createObjectURL(file), aber nie
// URL.revokeObjectURL() - jeder Upload-Versuch (auch fehlgeschlagene und
// wiederholte) haeufte einen weiteren Blob im Speicher an, den der
// Browser nie mehr freigab.

function makeFile(name = 'anzeige.png', type = 'image/png') {
  return new File(['x'], name, { type })
}

describe('ImageJobUpload', () => {
  let createSpy: ReturnType<typeof vi.fn>
  let revokeSpy: ReturnType<typeof vi.fn>

  beforeEach(() => {
    let counter = 0
    createSpy = vi.fn(() => `blob:mock-${++counter}`)
    revokeSpy = vi.fn()
    vi.stubGlobal('URL', { ...URL, createObjectURL: createSpy, revokeObjectURL: revokeSpy })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
    cleanup()
  })

  it('revoke die vorherige Vorschau-URL, wenn eine neue Datei hochgeladen wird', async () => {
    vi.spyOn(axios, 'post').mockRejectedValue(new Error('network'))

    const { container } = render(<ImageJobUpload onJobCreated={vi.fn()} />)
    const input = container.querySelector('input[type="file"]') as HTMLInputElement

    fireEvent.change(input, { target: { files: [makeFile('erste.png')] } })
    await waitFor(() => expect(createSpy).toHaveBeenCalledTimes(1))
    const firstUrl = createSpy.mock.results[0].value

    fireEvent.change(input, { target: { files: [makeFile('zweite.png')] } })
    await waitFor(() => expect(createSpy).toHaveBeenCalledTimes(2))

    await waitFor(() => expect(revokeSpy).toHaveBeenCalledWith(firstUrl))
  })

  it('revoke die Vorschau-URL beim Unmount', async () => {
    vi.spyOn(axios, 'post').mockImplementation(() => new Promise(() => {}))

    const { container, unmount } = render(<ImageJobUpload onJobCreated={vi.fn()} />)
    const input = container.querySelector('input[type="file"]') as HTMLInputElement

    fireEvent.change(input, { target: { files: [makeFile()] } })
    await waitFor(() => expect(createSpy).toHaveBeenCalledTimes(1))
    const url = createSpy.mock.results[0].value

    unmount()

    expect(revokeSpy).toHaveBeenCalledWith(url)
  })
})
