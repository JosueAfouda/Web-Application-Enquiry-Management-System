import type { ReactNode } from 'react'

import { AlertTriangle, Inbox, Loader2 } from 'lucide-react'

import { Button } from '../ui/button'

export function LoadingState({ message = 'Loading...' }: { message?: string }): ReactNode {
  return (
    <div className="flex min-h-[220px] items-center justify-center gap-3 rounded-lg border border-dashed border-slate-300 bg-white">
      <Loader2 className="h-5 w-5 animate-spin text-teal-600" />
      <p className="text-sm text-slate-600">{message}</p>
    </div>
  )
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}): ReactNode {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 rounded-lg border border-rose-200 bg-rose-50 p-4 text-center">
      <AlertTriangle className="h-5 w-5 text-rose-600" />
      <p className="max-w-lg text-sm text-rose-700">{message}</p>
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  )
}

export function EmptyState({
  title,
  subtitle,
  action,
}: {
  title: string
  subtitle: string
  action?: ReactNode
}): ReactNode {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-slate-300 bg-white p-4 text-center">
      <Inbox className="h-5 w-5 text-slate-500" />
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      <p className="max-w-lg text-sm text-slate-500">{subtitle}</p>
      {action}
    </div>
  )
}
