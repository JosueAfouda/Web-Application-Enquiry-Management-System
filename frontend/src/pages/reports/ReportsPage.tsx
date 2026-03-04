import * as React from 'react'
import type { ReactNode } from 'react'

import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'

import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/page-state'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'
import { formatMoney, formatPercent } from '../../lib/format'

export function ReportsPage(): ReactNode {
  const [dateFrom, setDateFrom] = React.useState('')
  const [dateTo, setDateTo] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState('')

  const query = useQuery({
    queryKey: ['reports', 'kpis', dateFrom, dateTo],
    queryFn: () =>
      api.reports.kpis({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  })

  const downloadMutation = useMutation({
    mutationFn: async (report: 'enquiries' | 'quotations' | 'invoices' | 'payments') => {
      const blob = await api.reports.downloadReport(report, {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        status: statusFilter || undefined,
      })
      const objectUrl = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = objectUrl
      link.download = `${report}.xlsx`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(objectUrl)
    },
    onSuccess: () => {
      toast.success('Report downloaded')
    },
    onError: (error) => {
      toast.error(toApiClientError(error).message)
    },
  })

  if (query.isLoading) {
    return <LoadingState message="Loading KPI report..." />
  }

  if (query.isError || !query.data) {
    return <ErrorState message={toApiClientError(query.error).message} onRetry={() => void query.refetch()} />
  }

  const report = query.data

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Reporting Filters</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 md:grid-cols-4">
          <Input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          <Input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          <Select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">Any status</option>
            {['APPROVED', 'REJECTED', 'INVOICED', 'DELIVERED', 'PAID'].map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </Select>
          <Button variant="secondary" onClick={() => void query.refetch()}>
            Refresh KPIs
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Approval Rate" value={formatPercent(report.quotation_approval.approval_rate)} />
        <KpiCard label="PO Conversion" value={formatPercent(report.po_conversion.conversion_rate)} />
        <KpiCard
          label="Collected"
          value={formatMoney(report.invoice_collection.collected_total)}
          subtitle={`Outstanding ${formatMoney(report.invoice_collection.outstanding_total)}`}
        />
        <KpiCard
          label="Delivery Completion"
          value={formatPercent(report.delivery_completion.completion_rate)}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Enquiry Status Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          {report.enquiry_counts_by_status.length === 0 ? (
            <EmptyState title="No enquiry data" subtitle="No rows found for selected period." />
          ) : (
            <TableContainer>
              <Table>
                <thead>
                  <tr>
                    <Th>Status</Th>
                    <Th>Count</Th>
                  </tr>
                </thead>
                <tbody>
                  {report.enquiry_counts_by_status.map((row) => (
                    <tr key={row.status}>
                      <Td>{row.status}</Td>
                      <Td>{row.count}</Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Excel Export</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => downloadMutation.mutate('enquiries')}>
            enquiries.xlsx
          </Button>
          <Button variant="secondary" onClick={() => downloadMutation.mutate('quotations')}>
            quotations.xlsx
          </Button>
          <Button variant="secondary" onClick={() => downloadMutation.mutate('invoices')}>
            invoices.xlsx
          </Button>
          <Button variant="secondary" onClick={() => downloadMutation.mutate('payments')}>
            payments.xlsx
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>KPI Details</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm text-slate-700 md:grid-cols-2">
          <p>Approved quotations: {report.quotation_approval.approved_count}</p>
          <p>Decided quotations: {report.quotation_approval.decided_count}</p>
          <p>Enquiries with PO: {report.po_conversion.enquiries_with_po}</p>
          <p>Total enquiries: {report.po_conversion.total_enquiries}</p>
          <p>Invoiced total: {formatMoney(report.invoice_collection.invoiced_total)}</p>
          <p>Collected total: {formatMoney(report.invoice_collection.collected_total)}</p>
          <p>Outstanding total: {formatMoney(report.invoice_collection.outstanding_total)}</p>
          <p>
            Delivered/Total: {report.delivery_completion.delivered_count}/{report.delivery_completion.total_deliveries}
          </p>
          <p>Window from: {report.window.date_from ?? '-'}</p>
          <p>Window to: {report.window.date_to ?? '-'}</p>
        </CardContent>
      </Card>
    </div>
  )
}

function KpiCard({ label, value, subtitle }: { label: string; value: string; subtitle?: string }): ReactNode {
  return (
    <Card>
      <CardContent className="space-y-1 py-4">
        <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
        <p className="text-2xl font-semibold text-slate-900">{value}</p>
        {subtitle ? <p className="text-xs text-slate-500">{subtitle}</p> : null}
      </CardContent>
    </Card>
  )
}
