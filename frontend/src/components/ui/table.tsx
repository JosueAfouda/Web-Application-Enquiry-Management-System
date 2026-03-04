import type { HTMLAttributes, ReactNode, TableHTMLAttributes } from 'react'

import { cn } from '../../lib/cn'

export function TableContainer({ className, ...props }: HTMLAttributes<HTMLDivElement>): ReactNode {
  return <div className={cn('overflow-auto', className)} {...props} />
}

export function Table({ className, ...props }: TableHTMLAttributes<HTMLTableElement>): ReactNode {
  return <table className={cn('w-full border-collapse text-sm', className)} {...props} />
}

export function Th({ className, ...props }: HTMLAttributes<HTMLTableCellElement>): ReactNode {
  return (
    <th
      className={cn('border-b border-slate-200 px-3 py-2 text-left font-semibold text-slate-600', className)}
      {...props}
    />
  )
}

export function Td({ className, ...props }: HTMLAttributes<HTMLTableCellElement>): ReactNode {
  return <td className={cn('border-b border-slate-100 px-3 py-2 align-top', className)} {...props} />
}
