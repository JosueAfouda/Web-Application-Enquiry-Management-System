import type { ReactNode } from 'react'

export function FormField({
  label,
  error,
  children,
}: {
  label: string
  error?: string
  children: ReactNode
}): ReactNode {
  return (
    <label className="grid gap-1.5 text-sm text-slate-700">
      <span className="font-medium">{label}</span>
      {children}
      {error ? <span className="text-xs text-rose-700">{error}</span> : null}
    </label>
  )
}
