// Persistent agent console — present on every view. Text + mic placeholder.
import { useEffect, useRef, useState } from 'react'
import { useApp } from '../store.jsx'

export default function Console() {
  const { accent, log, say } = useApp()
  const [v, setV] = useState('')
  const end = useRef(null)

  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }) }, [log])

  function send(text) {
    say('you', text)
    say('WOM', 'Got it — in mock mode I only simulate actions. Wire creds (see NEEDS-FROM-YOU.md) to go live.')
  }

  return (
    <div className="border-t border-line bg-ink-950/90 backdrop-blur px-3 sm:px-5 py-2">
      {log.length > 0 && (
        <div className="max-h-28 overflow-y-auto mb-1.5 space-y-1">
          {log.map((m, i) => (
            <div key={i} className="text-[11px] flex gap-2">
              <span className="shrink-0" style={{ color: m.who === 'you' ? accent : '#8a94a6' }}>
                {m.who === 'you' ? 'you' : 'WOM'}
              </span>
              <span className="text-gray-300">{m.text}</span>
            </div>
          ))}
          <div ref={end} />
        </div>
      )}
      <form onSubmit={(e) => { e.preventDefault(); if (v.trim()) { send(v); setV('') } }}
            className="flex items-center gap-2">
        <span className="text-mut text-sm">›</span>
        <input value={v} onChange={(e) => setV(e.target.value)}
          placeholder="Ask Wise Old Man…  (persistent console — every view)"
          className="flex-1 bg-transparent outline-none text-[13px] py-1.5" />
        <button type="button" title="Voice (placeholder)"
          onClick={() => send('🎙️ (voice input placeholder)')}
          className="w-8 h-8 grid place-items-center rounded-lg border border-line text-mut hover:text-white">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="9" y="2" width="6" height="12" rx="3" /><path d="M5 10a7 7 0 0 0 14 0M12 17v4" />
          </svg>
        </button>
        <button className="px-3 h-8 rounded-lg text-[12px] font-semibold text-ink-950"
          style={{ background: accent }}>Send</button>
      </form>
    </div>
  )
}
