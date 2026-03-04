import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { api } from '../lib/api'
import { clearAuthSession, getAuthSession, saveAuthSession, type AuthSession } from '../lib/auth-storage'
import { toApiClientError } from '../lib/errors'
import { setAccessToken } from '../lib/http'
import type { UserInfo } from '../types/api'

interface AuthContextValue {
  user: UserInfo | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isBootstrapping: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  hasRole: (...roles: string[]) => boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function readInitialSession(): AuthSession | null {
  if (typeof window === 'undefined') {
    return null
  }
  return getAuthSession()
}

export function AuthProvider({ children }: { children: ReactNode }): ReactNode {
  const [session, setSession] = useState<AuthSession | null>(() => readInitialSession())
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  const applySession = useCallback((next: AuthSession | null) => {
    setSession(next)
    setAccessToken(next?.accessToken ?? null)
  }, [])

  const logout = useCallback(async () => {
    const current = getAuthSession()
    if (current?.refreshToken) {
      try {
        await api.auth.logout(current.refreshToken)
      } catch {
        // Ignore logout API errors; local session must still be cleared.
      }
    }

    clearAuthSession()
    applySession(null)
  }, [applySession])

  const login = useCallback(
    async (username: string, password: string) => {
      const response = await api.auth.login({ username, password })
      const next = saveAuthSession(response)
      applySession(next)
    },
    [applySession],
  )

  useEffect(() => {
    let cancelled = false

    async function bootstrap(): Promise<void> {
      const existing = getAuthSession()
      if (!existing) {
        if (!cancelled) {
          setIsBootstrapping(false)
        }
        return
      }

      applySession(existing)

      try {
        const me = await api.auth.me()
        if (!cancelled) {
          const persisted = saveAuthSession({
            access_token: existing.accessToken,
            refresh_token: existing.refreshToken,
            token_type: 'bearer',
            access_token_expires_at: existing.accessTokenExpiresAt,
            user: me,
          })
          applySession(persisted)
        }
      } catch {
        try {
          const refreshed = await api.auth.refresh(existing.refreshToken)
          if (!cancelled) {
            const persisted = saveAuthSession(refreshed)
            applySession(persisted)
          }
        } catch (error) {
          const normalized = toApiClientError(error)
          if (normalized.status >= 400 && normalized.status < 500) {
            clearAuthSession()
            if (!cancelled) {
              applySession(null)
            }
          }
        }
      } finally {
        if (!cancelled) {
          setIsBootstrapping(false)
        }
      }
    }

    void bootstrap()

    return () => {
      cancelled = true
    }
  }, [applySession])

  const value = useMemo<AuthContextValue>(
    () => ({
      user: session?.user ?? null,
      accessToken: session?.accessToken ?? null,
      refreshToken: session?.refreshToken ?? null,
      isAuthenticated: Boolean(session?.accessToken),
      isBootstrapping,
      login,
      logout,
      hasRole: (...roles: string[]) => {
        if (!session?.user) {
          return false
        }
        return session.user.roles.some((role) => roles.includes(role))
      },
    }),
    [isBootstrapping, login, logout, session],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
