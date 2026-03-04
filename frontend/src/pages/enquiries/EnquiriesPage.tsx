import type { ReactNode } from 'react'

import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/page-state'
import { Badge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { useAuth } from '../../context/AuthContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'
import { formatDate } from '../../lib/format'

const statuses = [
  'RECEIVED',
  'IN_REVIEW',
  'QUOTED',
  'PENDING_APPROVAL',
  'APPROVED',
  'REJECTED',
  'PO_CREATED',
  'INVOICED',
  'IN_DELIVERY',
  'DELIVERED',
  'CLOSED',
  'CANCELLED',
]

export function EnquiriesPage(): ReactNode {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { hasRole } = useAuth()
  const canCreate = hasRole('BD', 'Admin', 'SuperAdmin')

  const status = searchParams.get('status') ?? ''
  const customer = searchParams.get('customer') ?? ''
  const dateFrom = searchParams.get('from') ?? ''
  const dateTo = searchParams.get('to') ?? ''

  const enquiriesQuery = useQuery({
    queryKey: ['enquiries', status],
    queryFn: () => api.enquiries.list({ status: status || undefined, limit: 500 }),
  })

  const customersQuery = useQuery({
    queryKey: ['masters', 'customers'],
    queryFn: () => api.masters.listCustomers({ limit: 500 }),
  })

  if (enquiriesQuery.isLoading || customersQuery.isLoading) {
    return <LoadingState message="Loading enquiries..." />
  }

  if (enquiriesQuery.isError || customersQuery.isError) {
    const message = toApiClientError(enquiriesQuery.error ?? customersQuery.error).message
    return <ErrorState message={message} onRetry={() => void enquiriesQuery.refetch()} />
  }

  const customers = customersQuery.data ?? []
  const customerMap = new Map(customers.map((row) => [row.id, row.name]))

  const filtered = (enquiriesQuery.data ?? []).filter((enquiry) => {
    if (customer && enquiry.customer_id !== customer) {
      return false
    }
    if (dateFrom && enquiry.received_date < dateFrom) {
      return false
    }
    if (dateTo && enquiry.received_date > dateTo) {
      return false
    }
    return true
  })

  const updateFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value) {
      next.set(key, value)
    } else {
      next.delete(key)
    }
    setSearchParams(next)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle>Enquiries</CardTitle>
          {canCreate ? (
            <Button onClick={() => navigate('/enquiries/new')}>Create Enquiry</Button>
          ) : null}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-2 md:grid-cols-4">
          <Select value={status} onChange={(event) => updateFilter('status', event.target.value)}>
            <option value="">All statuses</option>
            {statuses.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </Select>
          <Select value={customer} onChange={(event) => updateFilter('customer', event.target.value)}>
            <option value="">All customers</option>
            {customers.map((row) => (
              <option key={row.id} value={row.id}>
                {row.name}
              </option>
            ))}
          </Select>
          <Input type="date" value={dateFrom} onChange={(event) => updateFilter('from', event.target.value)} />
          <Input type="date" value={dateTo} onChange={(event) => updateFilter('to', event.target.value)} />
        </div>

        {filtered.length === 0 ? (
          <EmptyState title="No enquiries" subtitle="Try adjusting filters or create a new enquiry." />
        ) : (
          <TableContainer>
            <Table>
              <thead>
                <tr>
                  <Th>Enquiry #</Th>
                  <Th>Customer</Th>
                  <Th>Received</Th>
                  <Th>Currency</Th>
                  <Th>Status</Th>
                  <Th>Items</Th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((enquiry) => (
                  <tr key={enquiry.id} className="hover:bg-slate-50/70">
                    <Td>
                      <Link to={`/enquiries/${enquiry.id}`} className="font-medium text-teal-700 hover:text-teal-600">
                        {enquiry.enquiry_no}
                      </Link>
                    </Td>
                    <Td>{customerMap.get(enquiry.customer_id) ?? enquiry.customer_id}</Td>
                    <Td>{formatDate(enquiry.received_date)}</Td>
                    <Td>{enquiry.currency}</Td>
                    <Td>
                      <Badge value={enquiry.status} />
                    </Td>
                    <Td>{enquiry.items.length}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  )
}
