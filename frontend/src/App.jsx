// Shell: top bar (wordmark, nav, scope toggle), main view, mobile nav, console, toast.
import { Wordmark } from './components/ui.jsx'
import Console from './components/Console.jsx'
import Dashboard from './screens/Dashboard.jsx'
import Tasks from './screens/Tasks.jsx'
import Cockpit from './screens/Cockpit.jsx'
import { useApp } from './store.jsx'

const NAV = [['home', 'Dashboard'], ['tasks', 'Tasks'], ['cockpit', 'Cockpit']]

export default function App() {
  const { scope, setScope, accent, view, setView, toastMsg } = useApp()

  return (
    <div className="h-full flex flex-col">
      <header className="flex items-center gap-3 px-3 sm:px-5 py-2.5 border-b border-line bg-ink-950/80 backdrop-blur sticky top-0 z-20">
        <Wordmark accent={accent} />
        <nav className="hidden sm:flex items-center gap-1 ml-4">
          {NAV.map(([k, l]) => (
            <button key={k} onClick={() => setView(k)}
              className={`text-[13px] px-3 py-1.5 rounded-lg transition ${view === k ? 'bg-ink-800 text-white' : 'text-mut hover:text-white'}`}>{l}</button>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <div className="flex items-center bg-ink-850 border border-line rounded-full p-0.5">
            {['personal', 'work'].map((s) => (
              <button key={s} onClick={() => setScope(s)}
                className={`text-[12px] px-3 py-1 rounded-full transition capitalize ${scope === s ? 'text-ink-950 font-semibold' : 'text-mut'}`}
                style={scope === s ? { background: s === 'personal' ? '#34d399' : '#f59e0b' } : {}}>{s}</button>
            ))}
          </div>
          <span className="hidden sm:inline text-[10px] px-2 py-1 rounded-md border border-line text-mut">MOCK</span>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-3 sm:px-5 py-4">
        {view === 'home' && <Dashboard />}
        {view === 'tasks' && <Tasks />}
        {view === 'cockpit' && <Cockpit />}
      </main>

      <nav className="sm:hidden flex border-t border-line bg-ink-950">
        {NAV.map(([k, l]) => (
          <button key={k} onClick={() => setView(k)}
            className={`flex-1 py-2 text-[11px] ${view === k ? 'text-white' : 'text-mut'}`}
            style={view === k ? { borderTop: `2px solid ${accent}` } : {}}>{l}</button>
        ))}
      </nav>

      <Console />

      {toastMsg && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-30 bg-ink-800 border border-line rounded-xl px-4 py-2 text-[12px] shadow-tile fade">
          {toastMsg}
        </div>
      )}
    </div>
  )
}
