import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../api/client.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    api.me().then((value) => alive && setUser(value)).catch(() => alive && setUser(null)).finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const value = useMemo(() => ({
    user,
    loading,
    async login(email, password) {
      const response = await api.login({ email, password })
      setUser(response.user)
      return response.user
    },
    async register(full_name, email, password) {
      const response = await api.register({ full_name, email, password })
      setUser(response.user)
      return response.user
    },
    async updateProfile(display_name, email) {
      const response = await api.updateProfile({ display_name, email })
      setUser(response)
      return response
    },
    async logout() {
      await api.logout()
      setUser(null)
    },
  }), [user, loading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
