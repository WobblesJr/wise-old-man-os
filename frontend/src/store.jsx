// App-wide context: scope (personal/work), accent, view, console log + toasts.
import { createContext, useContext, useState, useCallback } from 'react'
import { ACCENT } from './constants'

const Ctx = createContext(null)

export function AppProvider({ children }) {
  const [scope, setScope] = useState('personal')
  const [view, setView] = useState('home')
  const [log, setLog] = useState([])
  const [toastMsg, setToastMsg] = useState(null)

  const accent = ACCENT[scope]

  const toast = useCallback((text) => {
    setToastMsg(text)
    setLog((l) => [...l, { who: 'WOM', text: '✓ ' + text + ' (mock — nothing left the machine)' }])
    setTimeout(() => setToastMsg(null), 2600)
  }, [])

  const say = useCallback((who, text) => setLog((l) => [...l, { who, text }]), [])

  const value = { scope, setScope, accent, view, setView, log, say, toast, toastMsg }
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useApp = () => useContext(Ctx)
