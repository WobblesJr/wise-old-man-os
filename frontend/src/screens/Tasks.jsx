// Task list: dense table (desktop) / cards (mobile). Columns from the sheet.
import { useState } from 'react'
import { useApi } from '../components/useApi.js'
import { useApp } from '../store.jsx'
import { api } from '../api.js'
import { ACTION_SPINE, ACTION_LABEL, STATUS, TASK_FILTERS } from '../constants'

const HEADERS = ['!', 'Description', 'Start', 'Follow-up', 'Due', 'Owner', 'Ball in Court', 'Category', 'Subcategory', 'Action', 'Status']

export default function Tasks() {
  const { scope, accent, toast } = useApp()
  const [filter, setFilter] = useState('all')
  const [nonce, setNonce] = useState(0)
  const [desc, setDesc] = useState('')
  const [act, setAct] = useState('action')
  const { data, loading, error } = useApi(() => api.tasks(scope, filter), [scope, filter, nonce])

  const rows = data?.tasks || []

  function add(e) {
    e.preventDefault()
    if (!desc.trim()) return
    api.addTask({ scope, description: desc, action: act }).then(() => {
      toast(`Added (mock write → sheet): ${desc}`)
      setDesc(''); setNonce((n) => n + 1)
    })
  }

  return (
    <div className="fade">
      <form onSubmit={add} className="flex flex-wrap gap-1.5 mb-3">
        <input value={desc} onChange={(e) => setDesc(e.target.value)}
          placeholder="Quick-add a task… (writes via the sheet adapter)"
          className="flex-1 min-w-[200px] bg-ink-900 border border-line rounded-lg px-3 py-2 text-[13px] outline-none focus:border-ink-500" />
        <select value={act} onChange={(e) => setAct(e.target.value)}
          className="bg-ink-900 border border-line rounded-lg px-2 py-2 text-[12px] outline-none">
          {Object.keys(ACTION_LABEL).map((k) => <option key={k} value={k}>{ACTION_LABEL[k]}</option>)}
        </select>
        <button className="px-4 rounded-lg text-[13px] font-semibold text-ink-950" style={{ background: accent }}>Add</button>
      </form>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {TASK_FILTERS.map(([k, l]) => (
          <button key={k} onClick={() => setFilter(k)}
            className={`text-[12px] px-3 py-1 rounded-full border transition ${filter === k ? 'text-ink-950 font-semibold' : 'text-mut border-line hover:text-white'}`}
            style={filter === k ? { background: accent, borderColor: accent } : {}}>
            {l}{k !== 'all' && k !== 'mine' ? <span className="ml-1" style={{ color: filter === k ? '#000' : ACTION_SPINE[k] }}>●</span> : ''}
          </button>
        ))}
        <span className="ml-auto text-[11px] text-mut self-center">{rows.length} shown</span>
      </div>

      {loading && <div className="h-40 rounded-2xl bg-ink-900 border border-line animate-pulse" />}
      {error && <div className="bg-ink-900 border border-line rounded-2xl p-6 text-center text-[12px] text-mut">Backend not reachable — start it with ./run.ps1</div>}

      {!loading && !error && (
        <>
          {/* desktop table */}
          <div className="hidden md:block bg-ink-900 border border-line rounded-2xl overflow-hidden">
            <table className="w-full text-[12px]">
              <thead><tr className="text-[10px] uppercase tracking-wide text-mut border-b border-line">
                {HEADERS.map((h) => <th key={h} className="text-left font-medium px-2.5 py-2 whitespace-nowrap">{h}</th>)}
              </tr></thead>
              <tbody>
                {rows.map((t) => (
                  <tr key={t.id} className="border-b border-ink-850 hover:bg-ink-850/60 transition">
                    <td className="pl-0 pr-1 py-2" style={{ borderLeft: `4px solid ${ACTION_SPINE[t.action]}` }}>
                      <span className="pl-2 font-bold text-red-500">{t.bang}</span></td>
                    <td className="px-2.5 py-2 max-w-[280px]"><span className={t.status === 'completed' ? 'line-through text-mut' : ''}>{t.description}</span></td>
                    <td className="px-2.5 py-2 text-mut tnum">{t.start}</td>
                    <td className="px-2.5 py-2 text-mut tnum">{t.followup || '—'}</td>
                    <td className="px-2.5 py-2 tnum">{t.due || '—'}</td>
                    <td className="px-2.5 py-2 text-mut">{t.owner}</td>
                    <td className="px-2.5 py-2">{t.ball_in_court === 'Me'
                      ? <span className="font-semibold" style={{ color: accent }}>Me</span>
                      : <span className="text-mut">{t.ball_in_court}</span>}</td>
                    <td className="px-2.5 py-2 text-mut">{t.category}</td>
                    <td className="px-2.5 py-2 text-mut">{t.subcategory || '—'}</td>
                    <td className="px-2.5 py-2"><span className="flex items-center gap-1" style={{ color: ACTION_SPINE[t.action] }}>
                      <span className="w-1.5 h-1.5 rounded-full" style={{ background: ACTION_SPINE[t.action] }} />{ACTION_LABEL[t.action]}</span></td>
                    <td className="px-2.5 py-2"><span className="flex items-center gap-1 text-mut">
                      <span className="w-1.5 h-1.5 rounded-full" style={{ background: STATUS[t.status]?.dot }} />{STATUS[t.status]?.label}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* mobile cards */}
          <div className="md:hidden space-y-2">
            {rows.map((t) => (
              <div key={t.id} className="bg-ink-900 border border-line rounded-xl p-3"
                style={{ borderLeft: `4px solid ${ACTION_SPINE[t.action]}` }}>
                <div className="flex items-center gap-1.5">
                  {t.bang && <span className="font-bold text-red-500">!</span>}
                  <span className={`text-[13px] font-medium ${t.status === 'completed' ? 'line-through text-mut' : ''}`}>{t.description}</span>
                </div>
                <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1 text-[10px] text-mut tnum">
                  <span>Due {t.due || '—'}</span><span>F/U {t.followup || '—'}</span>
                  <span>{t.category}{t.subcategory ? ' · ' + t.subcategory : ''}</span>
                </div>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-[10px] flex items-center gap-1" style={{ color: ACTION_SPINE[t.action] }}>
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: ACTION_SPINE[t.action] }} />{ACTION_LABEL[t.action]}</span>
                  <span className="text-[10px] flex items-center gap-1 text-mut">
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: STATUS[t.status]?.dot }} />{STATUS[t.status]?.label}</span>
                  <span className="text-[10px] ml-auto">{t.ball_in_court === 'Me'
                    ? <b style={{ color: accent }}>Me</b> : <span className="text-mut">{t.ball_in_court}</span>}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
