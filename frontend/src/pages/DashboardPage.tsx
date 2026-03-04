import type { ReactNode } from 'react'

import { useMutation } from '@tanstack/react-query'
import { FlaskConical, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import { useWorkflow } from '../context/WorkflowContext'
import { generateDemoData } from '../lib/demo-data'
import { formatDate } from '../lib/format'
import { toApiClientError } from '../lib/errors'
import { Button } from '../components/ui/button'
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
  const { hasRole } = useAuth()
  const { workflow, addCustomerPO, addRTMPO, addInvoice, addDelivery, setLastEnquiry, setQuotationRevision } =
    useWorkflow()
  const canSeedDemoData = hasRole('Admin', 'SuperAdmin')

  const demoSeedMutation = useMutation({
    mutationFn: generateDemoData,
    onSuccess: (seeded) => {
      setLastEnquiry(seeded.enquiry.id)
      setQuotationRevision(seeded.quotation.id, seeded.revision.id)
      addCustomerPO(seeded.customerPO)
      addRTMPO(seeded.rtmPO)
      addInvoice(seeded.invoice)
      addDelivery(seeded.delivery)
      toast.success('Demo data generated successfully')
    },
    onError: (error) => {
      toast.error(toApiClientError(error).message)
    },
  })

  return (
    <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle>Workflow Shortcuts</CardTitle>
          {canSeedDemoData ? (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => demoSeedMutation.mutate()}
              disabled={demoSeedMutation.isPending}
            >
              {demoSeedMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <FlaskConical className="mr-2 h-4 w-4" />
              )}
              DEMO DATA
            </Button>
          ) : null}
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <QuickLink to="/masters/customers" label="Manage Masters" hint="Customers, manufacturers, products" />
          <QuickLink to="/enquiries/new" label="Create Enquiry" hint="Start a new enquiry with multiple items" />
          <QuickLink to="/enquiries" label="Track Enquiries" hint="Review status and perform transitions" />
          <QuickLink to="/commercial" label="Commercial Ops" hint="Create invoices, payments, and delivery logs" />
          <QuickLink to="/reports" label="KPI Reporting" hint="View KPIs and export Excel reports" />
          {!canSeedDemoData ? (
            <p className="col-span-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
              DEMO DATA is available for Admin/SuperAdmin roles.
            </p>
          ) : null}
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
