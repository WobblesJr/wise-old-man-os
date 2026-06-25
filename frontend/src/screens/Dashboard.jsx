// Bento dashboard home. Hero suggestions + tiles, fetched from /api/dashboard.
import { useState } from 'react'
import { Tile, Pill } from '../components/ui.jsx'
import { useApi } from '../components/useApi.js'
import { useApp } from '../store.jsx'
import { api } from '../api.js'
import { ACTION_SPINE, STATUS, ACTION_LABEL, URGENCY, fmtTokens } from '../constants'

export default function Dashboard() {
  const { scope, accent, setView, toast } = useApp()
  const { data, loading, error } = useApi(() => api.dashboard(scope), [scope])
  const [cap, setCap] = useState('')

  if (loading) return <Loading />
  if (error || !data) return <ApiDown error={error} />

  const { suggestions, approvals, today, task_counts: tc, inbox, usage: u, memory } = data
  const a = approvals?.approvals || approvals || []
  const unread = (inbox || []).filter((i) => i.unread).length

  return (
    <div className="grid gap-3 fade" style={{ gridTemplateColumns: 'repeat(12,minmax(0,1fr))' }}>
      {/* HERO */}
      <section className="col-span-12 lg:col-span-8 bg-gradient-to-br from-ink-850 to-ink-900 border border-line rounded-2xl shadow-tile p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: accent }} />
            <h2 className="text-sm font-semibold">Suggested next steps</h2>
            <span className="text-[10px] text-mut">agent-generated · {scope}</span>
          </div>
          <span className="text-[10px] text-mut">refreshed just now</span>
        </div>
        <div className="grid sm:grid-cols-2 gap-2.5">
          {(suggestions || []).map((s) => (
            <div key={s.id} className="bg-ink-850 border border-line rounded-xl p-3 hover:border-ink-500 transition">
              <div className="flex items-start gap-2">
                <span className="mt-1 w-1.5 h-1.5 rounded-full shrink-0" style={{ background: URGENCY[s.urgency] }} />
                <div className="min-w-0">
                  <div className="text-[13px] font-medium leading-snug">{s.title}</div>
                  <div className="text-[11px] text-mut mt-0.5 leading-snug">{s.rationale}</div>
                </div>
              </div>
              <button onClick={() => api.runSuggestion(s.ref || s.id, scope).then(() => toast(`${s.action_label} → ${s.title}`))}
                className="mt-2.5 w-full text-[11px] font-semibold py-1.5 rounded-lg text-ink-950 active:scale-[.98] transition"
                style={{ background: accent }}>{s.action_label}</button>
            </div>
          ))}
        </div>
      </section>

      {/* APPROVALS */}
      <div className="col-span-12 lg:col-span-4">
        <Tile title="Approvals" action={<Pill color={accent}>{a.length} pending</Pill>}>
          <div className="space-y-2">
            {a.map((ap) => (
              <div key={ap.id} className="bg-ink-850 border border-line rounded-xl p-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[12px] font-medium truncate">{ap.title}</span>
                  <Pill color={ap.risk === 'medium' || ap.risk === 'med' ? '#eab308' : '#22c55e'}>{ap.risk}</Pill>
                </div>
                <div className="text-[11px] text-mut mt-0.5 leading-snug">{ap.summary}</div>
                <div className="text-[10px] text-mut mt-1">→ {ap.target}</div>
                <div className="flex gap-1.5 mt-2">
                  <button onClick={() => api.decide(ap.id, 'approve').then(() => toast(`Approved: ${ap.title}`))}
                    className="flex-1 text-[11px] font-semibold py-1 rounded-lg text-ink-950" style={{ background: accent }}>Approve</button>
                  <button onClick={() => api.decide(ap.id, 'reject').then(() => toast(`Dismissed: ${ap.title}`))}
                    className="px-2 text-[11px] py-1 rounded-lg border border-line text-mut hover:text-white">Skip</button>
                </div>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      {/* TODAY */}
      <div className="col-span-12 sm:col-span-6 lg:col-span-4">
        <Tile title="Today">
          <div className="space-y-1.5">
            {(today || []).map((e) => (
              <div key={e.id} className="flex items-center gap-2.5 bg-ink-850 border border-line rounded-lg px-2.5 py-2">
                <span className="w-1.5 self-stretch rounded-full" style={{ background: ACTION_SPINE[e.kind] || '#3b82f6' }} />
                <span className="text-[11px] text-mut tnum w-16 shrink-0">{e.time}</span>
                <div className="min-w-0"><div className="text-[12px] truncate">{e.title}</div>
                  <div className="text-[10px] text-mut">{e.where}</div></div>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      {/* TASKS AT A GLANCE */}
      <div className="col-span-12 sm:col-span-6 lg:col-span-4">
        <Tile title="Tasks at a glance" action={<button onClick={() => setView('tasks')} className="text-[10px] text-mut hover:text-white">open →</button>}>
          <div className="flex items-baseline gap-3 mb-3">
            <div><div className="text-2xl font-bold tnum">{tc?.open ?? 0}</div><div className="text-[10px] text-mut">open</div></div>
            <div><div className="text-2xl font-bold tnum" style={{ color: accent }}>{tc?.mine ?? 0}</div><div className="text-[10px] text-mut">on me</div></div>
          </div>
          <div className="flex flex-wrap gap-1.5 mb-2">
            {Object.keys(ACTION_SPINE).map((k) => tc?.by_action?.[k] ? (
              <span key={k} className="text-[10px] px-1.5 py-0.5 rounded-md flex items-center gap-1"
                style={{ background: ACTION_SPINE[k] + '1f', color: ACTION_SPINE[k] }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: ACTION_SPINE[k] }} />
                {ACTION_LABEL[k]} {tc.by_action[k]}</span>
            ) : null)}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {Object.keys(tc?.by_status || {}).map((k) => (
              <span key={k} className="text-[10px] px-1.5 py-0.5 rounded-md border border-line text-mut flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: STATUS[k]?.dot }} />
                {STATUS[k]?.label} {tc.by_status[k]}</span>
            ))}
          </div>
        </Tile>
      </div>

      {/* INBOX */}
      <div className="col-span-12 sm:col-span-6 lg:col-span-4">
        <Tile title="Inbox" action={<Pill color={accent}>{unread} unread</Pill>}>
          <div className="space-y-1.5">
            {(inbox || []).map((i) => (
              <div key={i.id} className="flex items-start gap-2 bg-ink-850 border border-line rounded-lg px-2.5 py-2">
                <span className="text-[9px] mt-0.5 px-1 py-0.5 rounded uppercase tracking-wide"
                  style={{ background: i.source === 'gmail' ? '#ea433520' : '#5865f220', color: i.source === 'gmail' ? '#f87171' : '#a5b4fc' }}>
                  {i.source === 'gmail' ? 'mail' : 'dsc'}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1">
                    {i.unread && <span className="w-1.5 h-1.5 rounded-full" style={{ background: accent }} />}
                    <span className="text-[12px] font-medium truncate">{i.from}</span>
                    <span className="text-[10px] text-mut ml-auto">{i.ts}</span>
                  </div>
                  <div className="text-[11px] truncate">{i.subject}</div>
                  <div className="text-[10px] text-mut truncate">{i.snippet}</div>
                </div>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      {/* AGENT / USAGE */}
      <div className="col-span-12 sm:col-span-6 lg:col-span-4">
        <Tile title="Agent · usage" action={<button onClick={() => setView('cockpit')} className="text-[10px] text-mut hover:text-white">cockpit →</button>}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[12px]">{u?.plan}</span>
            <span className="text-[10px] text-mut">resets {u?.window_resets_in}</span>
          </div>
          <div className="h-2 rounded-full bg-ink-700 overflow-hidden mb-1">
            <div className="h-full rounded-full" style={{ width: (u?.plan_usage_pct || 0) + '%', background: accent }} />
          </div>
          <div className="text-[10px] text-mut mb-3">{u?.plan_usage_pct}% of window used</div>
          <div className="flex items-end gap-1 h-12">
            {(u?.by_day || []).map((d) => (
              <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full rounded-t" style={{ height: Math.max(8, d.tokens / 1.51e6 * 44), background: accent + '66' }} />
                <span className="text-[8px] text-mut">{d.day}</span>
              </div>
            ))}
          </div>
          <div className="text-[10px] text-mut mt-2 tnum">Today {fmtTokens(u?.tokens_today || 0)} · Week {fmtTokens(u?.tokens_week || 0)} tokens</div>
        </Tile>
      </div>

      {/* MEMORY + QUICK CAPTURE */}
      <div className="col-span-12 sm:col-span-6 lg:col-span-4">
        <Tile title="Memory · quick capture">
          <form onSubmit={(e) => { e.preventDefault(); if (cap.trim()) { api.capture({ scope, text: cap, kind: 'note' }).then(() => toast(`Captured: ${cap}`)); setCap('') } }}
                className="flex gap-1.5 mb-2.5">
            <input value={cap} onChange={(e) => setCap(e.target.value)} placeholder="Capture a thought…"
              className="flex-1 bg-ink-850 border border-line rounded-lg px-2.5 py-1.5 text-[12px] outline-none focus:border-ink-500" />
            <button className="px-3 rounded-lg text-[12px] font-semibold text-ink-950" style={{ background: accent }}>+</button>
          </form>
          <div className="space-y-1.5">
            {(memory || []).map((m) => (
              <div key={m.id} className="flex items-start gap-2 text-[11px]">
                <span className="text-[9px] px-1 py-0.5 rounded bg-ink-700 text-mut shrink-0 mt-0.5">{m.tag}</span>
                <span className="text-gray-300 leading-snug">{m.text}</span>
                <span className="text-[10px] text-mut ml-auto shrink-0">{m.ts}</span>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      {/* CONSOLE hint */}
      <div className="col-span-12 lg:col-span-8">
        <Tile title="Console" action={<span className="text-[10px] text-mut">always at the bottom ↓</span>}>
          <div className="text-[12px] text-mut">Ask the agent anything, or use the mic. Try:
            <span className="text-gray-300"> "what needs me today?"</span>,
            <span className="text-gray-300"> "draft a reply to the GC"</span>,
            <span className="text-gray-300"> "add task: order site signage".</span>
          </div>
        </Tile>
      </div>
    </div>
  )
}

function Loading() {
  return <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(12,minmax(0,1fr))' }}>
    {[8, 4, 4, 4, 4, 4, 4, 8].map((c, i) => (
      <div key={i} className={`col-span-12 lg:col-span-${c} h-40 rounded-2xl bg-ink-900 border border-line animate-pulse`} />
    ))}
  </div>
}

function ApiDown({ error }) {
  return (
    <div className="bg-ink-900 border border-line rounded-2xl p-6 text-center">
      <div className="text-sm font-semibold mb-1">Backend not reachable</div>
      <div className="text-[12px] text-mut">Start it with <code className="text-gray-300">./run.ps1</code> (or <code className="text-gray-300">./run.sh</code>), then reload.</div>
      {error && <div className="text-[10px] text-mut mt-2">{String(error.message || error)}</div>}
    </div>
  )
}
