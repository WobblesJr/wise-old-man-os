// Shell. Desktop (lg): left sidebar. Tablet (md): top bar + horizontal nav, 2-up tiles.
// Mobile (<md): top wordmark+toggle bar + bottom nav, single-column. Content capped at 1360px.
import { Wordmark } from './components/ui.jsx'
import Console from './components/Console.jsx'
import Dashboard from './screens/Dashboard.jsx'
import Tasks from './screens/Tasks.jsx'
import Cockpit from './screens/Cockpit.jsx'
import { useApp } from './store.jsx'

const NAV = [['home', 'Dashboard'], ['tasks', 'Tasks'], ['cockpit', 'Cockpit']]

function ScopeToggle() {
  const { scope, setScope } = useApp()
  return (
    <div className="flex items-center bg-ink-850 border border-line rounded-full p-0.5">
      {['personal', 'work'].map((s) => (
        <button key={s} onClick={() => setScope(s)}
          className={`flex-1 text-[12px] px-3 py-1 rounded-full transition capitalize focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${scope === s ? 'text-ink-950 font-semibold' : 'text-mut'}`}
          style={scope === s ? { background: s === 'personal' ? '#34d399' : '#f59e0b' } : {}}>{s}</button>
      ))}
    </div>
  )
}

export default function App() {
  const { accent, view, setView, toastMsg } = useApp()

  const navBtn = (k, l, vertical) => (
    <button key={k} onClick={() => setView(k)}
      className={`${vertical ? 'flex items-center gap-2.5 w-full text-left px-3 py-2.5' : 'px-3 py-1.5'} text-[13px] rounded-lg transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${view === k ? 'bg-ink-800 text-white' : 'text-mut hover:text-white hover:bg-ink-850'}`}>
      {vertical && <span className="w-[7px] h-[7px] rounded-sm bg-current opacity-60" />}{l}
    </button>
  )

  return (
    <div className="h-full flex">
      {/* Desktop sidebar (lg+) */}
      <aside className="hidden lg:flex flex-col w-56 shrink-0 h-full gap-3 px-3 py-4 border-r border-line bg-ink-950">
        <div className="px-2"><Wordmark accent={accent} /></div>
        <nav className="flex flex-col gap-0.5 mt-1.5">{NAV.map(([k, l]) => navBtn(k, l, true))}</nav>
        <div className="mt-auto flex flex-col gap-2.5 p-2">
          <ScopeToggle />
          <span className="text-[10px] text-center px-2 py-1 rounded-md border border-line text-mut">MOCK data</span>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar (hidden on lg, where the sidebar takes over) */}
        <header className="lg:hidden flex items-center gap-3 px-3 sm:px-5 py-2.5 border-b border-line bg-ink-950/80 backdrop-blur sticky top-0 z-20">
          <Wordmark accent={accent} />
          <nav className="hidden md:flex items-center gap-1 ml-4">{NAV.map(([k, l]) => navBtn(k, l, false))}</nav>
          <div className="ml-auto flex items-center gap-2">
            <ScopeToggle />
            <span className="hidden sm:inline text-[10px] px-2 py-1 rounded-md border border-line text-mut">MOCK</span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-3 sm:px-5 lg:px-7 py-4">
          <div className="max-w-[1360px] mx-auto w-full">
            {view === 'home' && <Dashboard />}
            {view === 'tasks' && <Tasks />}
            {view === 'cockpit' && <Cockpit />}
          </div>
        </main>

        {/* Mobile bottom nav (<md) */}
        <nav className="md:hidden flex border-t border-line bg-ink-950">
          {NAV.map(([k, l]) => (
            <button key={k} onClick={() => setView(k)}
              className={`flex-1 py-2 text-[11px] ${view === k ? 'text-white' : 'text-mut'}`}
              style={view === k ? { borderTop: `2px solid ${accent}` } : {}}>{l}</button>
          ))}
        </nav>

        <Console />
      </div>

      {toastMsg && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-30 bg-ink-800 border border-line rounded-xl px-4 py-2 text-[12px] shadow-tile fade">
          {toastMsg}
        </div>
      )}
    </div>
  )
}
