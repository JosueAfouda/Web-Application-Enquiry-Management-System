import type { ReactNode } from 'react'

import { cn } from '../../lib/cn'

const styles: Record<string, string> = {
  RECEIVED: 'bg-slate-100 text-slate-700',
  IN_REVIEW: 'bg-amber-100 text-amber-800',
  QUOTED: 'bg-indigo-100 text-indigo-800',
  PENDING_APPROVAL: 'bg-orange-100 text-orange-800',
  APPROVED: 'bg-emerald-100 text-emerald-800',
  REJECTED: 'bg-rose-100 text-rose-800',
  PO_CREATED: 'bg-cyan-100 text-cyan-800',
  INVOICED: 'bg-blue-100 text-blue-800',
  IN_DELIVERY: 'bg-violet-100 text-violet-800',
  DELIVERED: 'bg-lime-100 text-lime-800',
  CLOSED: 'bg-zinc-200 text-zinc-700',
  CANCELLED: 'bg-zinc-100 text-zinc-500',
  DRAFT: 'bg-slate-100 text-slate-700',
  ISSUED: 'bg-blue-100 text-blue-700',
  CONFIRMED: 'bg-emerald-100 text-emerald-700',
  PARTIAL: 'bg-orange-100 text-orange-700',
  UNPAID: 'bg-rose-100 text-rose-700',
  PAID: 'bg-emerald-100 text-emerald-700',
}

export function Badge({ value, className }: { value: string; className?: string }): ReactNode {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold tracking-wide',
        styles[value] ?? 'bg-slate-100 text-slate-700',
        className,
      )}
    >
      {value}
    </span>
  )
}
