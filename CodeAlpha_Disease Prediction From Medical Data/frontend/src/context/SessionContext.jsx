import { createContext, useContext, useMemo, useState } from 'react'

const SessionContext = createContext(null)

export function SessionProvider({ children }) {
  const [cases, setCases] = useState([])
  const [draft, setDraft] = useState(null)
  const [lastResult, setLastResult] = useState(null)

  const value = useMemo(() => ({
    cases,
    draft,
    lastResult,
    setDraft,
    recordCase(input, result) {
      const item = {
        id: `HT-${String(Date.now()).slice(-6)}`,
        createdAt: new Date().toISOString(),
        input,
        result,
      }
      setCases((items) => [item, ...items])
      setLastResult(item)
      return item
    },
    clearCases() {
      setCases([])
      setLastResult(null)
    },
  }), [cases, draft, lastResult])

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
}

export function useSession() {
  return useContext(SessionContext)
}
