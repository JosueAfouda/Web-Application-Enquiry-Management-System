import type { ReactNode } from 'react'

import { Link } from 'react-router-dom'

import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

export function NotFoundPage(): ReactNode {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>Page Not Found</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-600">The requested route does not exist in this EMS frontend.</p>
          <Link
            to="/"
            className="inline-flex h-10 items-center justify-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-700"
          >
            Back to dashboard
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
