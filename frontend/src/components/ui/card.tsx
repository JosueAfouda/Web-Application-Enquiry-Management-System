import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '../../lib/cn'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>): ReactNode {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200 bg-white/90 shadow-[0_10px_30px_-20px_rgba(15,23,42,0.5)]',
        className,
      )}
      {...props}
    />
  )
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>): ReactNode {
  return <div className={cn('border-b border-slate-100 px-5 py-4', className)} {...props} />
}

export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>): ReactNode {
  return <h3 className={cn('text-base font-semibold text-slate-900', className)} {...props} />
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>): ReactNode {
  return <div className={cn('p-5', className)} {...props} />
}
