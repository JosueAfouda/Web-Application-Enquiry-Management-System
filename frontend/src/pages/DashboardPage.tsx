import type { ReactNode } from 'react'

import { Link } from 'react-router-dom'

import { useWorkflow } from '../context/WorkflowContext'
import { formatDate } from '../lib/format'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

function QuickLink({ to, label, hint }: { to: string; label: string; hint: string }): ReactNode {
  return (
    <Link
      to={to}
      className="rounded-lg border border-slate-200 bg-white px-4 py-3 transition-colors hover:border-teal-300 hover:bg-teal-50"
    >
      <p className="font-medium text-slate-900">{label}</p>
      <p className="mt-1 text-sm text-slate-600">{hint}</p>
    </Link>
  )
}

export function DashboardPage(): ReactNode {
  const { workflow } = useWorkflow()

  return (
    <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Workflow Shortcuts</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <QuickLink to="/masters/customers" label="Manage Masters" hint="Customers, manufacturers, products" />
          <QuickLink to="/enquiries/new" label="Create Enquiry" hint="Start a new enquiry with multiple items" />
          <QuickLink to="/enquiries" label="Track Enquiries" hint="Review status and perform transitions" />
          <QuickLink to="/commercial" label="Commercial Ops" hint="Create invoices, payments, and delivery logs" />
          <QuickLink to="/reports" label="KPI Reporting" hint="View KPIs and export Excel reports" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Session Context</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-slate-700">
          <p>
            Last enquiry ID: <span className="font-mono text-xs">{workflow.lastEnquiryId ?? '-'}</span>
          </p>
          <p>
            Last quotation ID: <span className="font-mono text-xs">{workflow.lastQuotationId ?? '-'}</span>
          </p>
          <p>Invoices in session: {workflow.invoices.length}</p>
          <p>Deliveries in session: {workflow.deliveries.length}</p>
          <p>Dashboard refreshed: {formatDate(new Date().toISOString(), true)}</p>
        </CardContent>
      </Card>
    </div>
  )
}
