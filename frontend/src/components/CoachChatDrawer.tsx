import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { X, Send, Bot, User, Trash2, Lightbulb } from 'lucide-react'
import clsx from 'clsx'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Props {
  open: boolean
  onClose: () => void
  // optionaler Bewerbungskontext
  jobTitle?: string
  company?: string
  status?: string
  coverLetterSnippet?: string
}

const QUICK_QUESTIONS = [
  'Wie formuliere ich eine höfliche Nachfass-Mail?',
  'Wie erkläre ich eine Lücke im Lebenslauf?',
  'Wann sollte ich nach dem Interview nachfragen?',
  'Wie nenne ich meine Gehaltsvorstellung?',
  'Was tun nach einer Absage?',
]

export default function CoachChatDrawer({
  open,
  onClose,
  jobTitle,
  company,
  status,
  coverLetterSnippet,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Focus input when drawer opens
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 100)
  }, [open])

  const sendMessage = async (text?: string) => {
    const content = (text ?? input).trim()
    if (!content || loading) return

    const newMessages: Message[] = [...messages, { role: 'user', content }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const { data } = await axios.post('/api/ai/chat', {
        messages: newMessages,
        job_title: jobTitle,
        company,
        status,
        cover_letter_snippet: coverLetterSnippet,
      })
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Fehler: KI nicht erreichbar. Ist Ollama gestartet?',
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!open) return null

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/30 z-40"
        onClick={onClose}
        aria-hidden
      />

      {/* Drawer */}
      <aside
        role="dialog"
        aria-label="Bewerbungscoach"
        aria-modal="true"
        className="fixed right-0 top-0 h-full w-full max-w-md z-50 flex flex-col bg-white dark:bg-gray-900 shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-blue-600 text-white">
          <Bot size={20} aria-hidden />
          <div className="flex-1">
            <div className="font-semibold text-sm">Bewerbungscoach</div>
            {(jobTitle || company) && (
              <div className="text-xs opacity-75 truncate">
                {jobTitle}{company ? ` • ${company}` : ''}
              </div>
            )}
          </div>
          <button
            onClick={() => { setMessages([]); setInput('') }}
            className="p-1 rounded hover:bg-white/20 transition-colors"
            aria-label="Chat löschen"
          >
            <Trash2 size={16} aria-hidden />
          </button>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-white/20 transition-colors"
            aria-label="Schließen"
          >
            <X size={18} aria-hidden />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center py-6">
              <Bot size={40} className="mx-auto text-blue-400 mb-3" aria-hidden />
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Hallo! Ich bin dein Bewerbungscoach.</p>
              <p className="text-xs text-gray-400 mb-5">Stell mir alles rund um deine Jobsuche &amp; Bewerbung.</p>
              <div className="space-y-2 text-left">
                <p className="text-xs text-gray-400 flex items-center gap-1">
                  <Lightbulb size={12} aria-hidden /> Schnellfragen:
                </p>
                {QUICK_QUESTIONS.map(q => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="block w-full text-left text-xs px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={clsx('flex gap-2', msg.role === 'user' ? 'justify-end' : 'justify-start')}
            >
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot size={14} className="text-blue-600 dark:text-blue-400" aria-hidden />
                </div>
              )}
              <div
                className={clsx(
                  'max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap',
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-100 rounded-tl-sm'
                )}
              >
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User size={14} className="text-white" aria-hidden />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-2 justify-start">
              <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                <Bot size={14} className="text-blue-600 dark:text-blue-400" aria-hidden />
              </div>
              <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <span className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex gap-2 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Frag mich was... (Enter zum Senden)"
              rows={1}
              disabled={loading}
              className="flex-1 resize-none rounded-xl px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              style={{ maxHeight: 120 }}
              aria-label="Nachricht eingeben"
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              className="flex-shrink-0 w-9 h-9 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
              aria-label="Senden"
            >
              <Send size={16} aria-hidden />
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-1.5">Shift+Enter für Zeilenumbruch • läuft lokal via Ollama</p>
        </div>
      </aside>
    </>
  )
}
