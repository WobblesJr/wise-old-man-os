// Agent/System cockpit: connections, scheduled jobs, skills, usage ledger.
import { Tile, Pill } from '../components/ui.jsx'
import { useApi } from '../components/useApi.js'
import { useApp } from '../store.jsx'
import { api } from '../api.js'
import { CONN_STATUS, fmtTokens } from '../constants'

export default function Cockpit() {
  const { accent } = useApp()
  const { data, loading, error } = useApi(() => Promise.all([api.cockpit(), api.usage()]).then(([c, u]) => ({ ...c, usage: u })), [])

  if (loading) return <div className="h-64 rounded-2xl bg-ink-900 border border-line animate-pulse" />
  if (error || !data) return <div className="bg-ink-900 border border-line rounded-2xl p-6 text-center text-[12px] text-mut">Backend not reachable — start it with ./run.ps1</div>

  const { connections = [], scheduled_jobs = [], skills = [], usage: u = {} } = data

  return (
    <div className="grid gap-3 fade" style={{ gridTemplateColumns: 'repeat(12,minmax(0,1fr))' }}>
      <div className="col-span-12 lg:col-span-6">
        <Tile title="Connections">
          <div className="space-y-1.5">
            {connections.map((c) => (
              <div key={c.id} className="flex items-center gap-2.5 bg-ink-850 border border-line rounded-lg px-2.5 py-2">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: CONN_STATUS[c.status] }} />
                <div className="min-w-0 flex-1"><div className="text-[12px] font-medium truncate">{c.name}</div>
                  <div className="text-[10px] text-mut truncate">{c.detail}</div></div>
                <div className="text-right"><Pill color={CONN_STATUS[c.status]}>{c.status}</Pill>
                  <div className="text-[9px] text-mut mt-0.5">{c.note}</div></div>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      <div className="col-span-12 lg:col-span-6">
        <Tile title="Scheduled jobs" action={<span className="text-[10px] text-mut">Hermes cron</span>}>
          <div className="space-y-1.5">
            {scheduled_jobs.map((j) => (
              <div key={j.id} className="flex items-center gap-2.5 bg-ink-850 border border-line rounded-lg px-2.5 py-2">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: CONN_STATUS[j.status] }} />
                <div className="min-w-0 flex-1"><div className="text-[12px] font-medium truncate">{j.name}</div>
                  <div className="text-[10px] text-mut tnum">{j.cron} · last {j.last}</div></div>
                <span className="text-[10px] text-mut tnum">{j.next}</span>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      <div className="col-span-12 lg:col-span-5">
        <Tile title="Skills inventory">
          <div className="grid sm:grid-cols-2 gap-1.5">
            {skills.map((s) => (
              <div key={s.id} className="bg-ink-850 border border-line rounded-lg p-2.5">
                <div className="flex items-center justify-between"><span className="text-[12px] font-medium">{s.name}</span>
                  <span className="text-[9px] px-1 rounded bg-ink-700 text-mut">{s.scope}</span></div>
                <div className="text-[10px] text-mut mt-0.5 leading-snug">{s.desc}</div>
              </div>
            ))}
          </div>
        </Tile>
      </div>

      <div className="col-span-12 lg:col-span-7">
        <Tile title="Usage ledger" action={<Pill color={accent}>{u.plan}</Pill>}>
          <div className="grid grid-cols-3 gap-2 mb-3">
            <Stat label="Window used" value={`${u.plan_usage_pct ?? 0}%`} color={accent} />
            <Stat label="Today" value={fmtTokens(u.tokens_today || 0)} />
            <Stat label="Week" value={fmtTokens(u.tokens_week || 0)} />
          </div>
          <table className="w-full text-[11px]">
            <thead><tr className="text-[9px] uppercase tracking-wide text-mut border-b border-line">
              {['Time', 'Agent', 'Model', 'Tokens', 'Scope'].map((h) => <th key={h} className="text-left font-medium py-1.5">{h}</th>)}</tr></thead>
            <tbody>{(u.ledger || []).map((l) => (
              <tr key={l.id} className="border-b border-ink-850">
                <td className="py-1.5 text-mut tnum">{l.ts}</td><td className="py-1.5">{l.agent}</td>
                <td className="py-1.5 text-mut">{l.model}</td><td className="py-1.5 tnum">{fmtTokens(l.tokens)}</td>
                <td className="py-1.5"><span className="text-[9px] px-1 rounded bg-ink-700 text-mut">{l.scope}</span></td>
              </tr>))}</tbody>
          </table>
        </Tile>
      </div>
    </div>
  )
}

function Stat({ label, value, color }) {
  return (
    <div className="bg-ink-850 border border-line rounded-lg p-2.5">
      <div className="text-[10px] text-mut">{label}</div>
      <div className="text-lg font-bold tnum" style={color ? { color } : {}}>{value}</div>
    </div>
  )
}
