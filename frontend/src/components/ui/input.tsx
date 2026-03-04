import * as React from 'react'

import { cn } from '../../lib/cn'

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...props }, ref) {
    return (
      <input
        ref={ref}
        className={cn(
          'h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900',
          'placeholder:text-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200',
          className,
        )}
        {...props}
      />
    )
  },
)
