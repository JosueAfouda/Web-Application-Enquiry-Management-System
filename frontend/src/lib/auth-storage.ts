import type { TokenPairResponse, UserInfo } from '../types/api'

const AUTH_STORAGE_KEY = 'ems.auth.session'

export interface AuthSession {
  accessToken: string
  refreshToken: string
  accessTokenExpiresAt: string
  user: UserInfo
}

export function saveAuthSession(payload: TokenPairResponse): AuthSession {
  const session: AuthSession = {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
    accessTokenExpiresAt: payload.access_token_expires_at,
    user: payload.user,
  }
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
  return session
}

export function getAuthSession(): AuthSession | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY)
  if (!raw) {
    return null
  }

  try {
    const session = JSON.parse(raw) as AuthSession
    if (!session.accessToken || !session.refreshToken || !session.user) {
      return null
    }
    return session
  } catch {
    return null
  }
}

export function clearAuthSession(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}
