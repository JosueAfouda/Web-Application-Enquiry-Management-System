import type { ReactNode } from 'react'

import { Navigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'

export function RoleGuard({ roles, children }: { roles: string[]; children: ReactNode }): ReactNode {
  const { hasRole } = useAuth()

  if (!hasRole(...roles)) {
    return <Navigate to="/" replace />
  }

  return children
}
