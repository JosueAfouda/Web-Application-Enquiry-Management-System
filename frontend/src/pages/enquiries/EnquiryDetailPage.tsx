import * as React from 'react'
import type { ReactNode } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/page-state'
import { Badge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { FormField } from '../../components/ui/form-field'
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { Textarea } from '../../components/ui/textarea'
import { useAuth } from '../../context/AuthContext'
import { useWorkflow } from '../../context/WorkflowContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'
import { asNumber, formatDate } from '../../lib/format'

const allowedTransitions: Record<string, string[]> = {
  RECEIVED: ['IN_REVIEW', 'CANCELLED'],
  IN_REVIEW: ['QUOTED', 'CANCELLED'],
  QUOTED: ['PENDING_APPROVAL', 'IN_REVIEW', 'CANCELLED'],
  PENDING_APPROVAL: ['APPROVED', 'REJECTED', 'CANCELLED'],
  APPROVED: ['PO_CREATED', 'CANCELLED'],
  REJECTED: ['IN_REVIEW', 'CANCELLED'],
  PO_CREATED: ['INVOICED', 'IN_DELIVERY', 'CANCELLED'],
  INVOICED: ['IN_DELIVERY', 'CLOSED', 'CANCELLED'],
  IN_DELIVERY: ['DELIVERED', 'CANCELLED'],
  DELIVERED: ['CLOSED'],
  CLOSED: [],
  CANCELLED: [],
}

export function EnquiryDetailPage(): ReactNode {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { enquiryId = '' } = useParams()
  const { hasRole } = useAuth()
  const { setLastEnquiry } = useWorkflow()

  const [nextStatus, setNextStatus] = React.useState('')
  const [comment, setComment] = React.useState('')

  const enquiryQuery = useQuery({
    queryKey: ['enquiries', enquiryId],
    queryFn: () => api.enquiries.get(enquiryId),
    enabled: Boolean(enquiryId),
  })
  const historyQuery = useQuery({
    queryKey: ['enquiries', enquiryId, 'history'],
    queryFn: () => api.enquiries.history(enquiryId),
    enabled: Boolean(enquiryId),
  })
  const productsQuery = useQuery({
    queryKey: ['masters', 'products'],
    queryFn: () => api.masters.listProducts({ limit: 500 }),
  })
  const customersQuery = useQuery({
    queryKey: ['masters', 'customers'],
    queryFn: () => api.masters.listCustomers({ limit: 500 }),
  })

  const transitionMutation = useMutation({
    mutationFn: () => api.enquiries.transitionStatus(enquiryId, { to_status: nextStatus, comment }),
    onSuccess: () => {
      toast.success('Status updated')
      setComment('')
      setNextStatus('')
      void queryClient.invalidateQueries({ queryKey: ['enquiries', enquiryId] })
      void queryClient.invalidateQueries({ queryKey: ['enquiries', enquiryId, 'history'] })
      void queryClient.invalidateQueries({ queryKey: ['enquiries'] })
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const createQuotationMutation = useMutation({
    mutationFn: () => api.quotations.createForEnquiry(enquiryId, {}),
    onSuccess: (quotation) => {
      setLastEnquiry(enquiryId)
      toast.success('Quotation created')
      navigate(`/quotations/${quotation.id}`)
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  if (enquiryQuery.isLoading || historyQuery.isLoading || productsQuery.isLoading || customersQuery.isLoading) {
    return <LoadingState message="Loading enquiry details..." />
  }

  if (
    enquiryQuery.isError ||
    historyQuery.isError ||
    productsQuery.isError ||
    customersQuery.isError ||
    !enquiryQuery.data
  ) {
    const message = toApiClientError(
      enquiryQuery.error ?? historyQuery.error ?? productsQuery.error ?? customersQuery.error,
    ).message
    return <ErrorState message={message} onRetry={() => void enquiryQuery.refetch()} />
  }

  const enquiry = enquiryQuery.data
  const historyRows = historyQuery.data ?? []
  const productMap = new Map((productsQuery.data ?? []).map((row) => [row.id, row.name]))
  const customerMap = new Map((customersQuery.data ?? []).map((row) => [row.id, row.name]))

  const availableTransitions = allowedTransitions[enquiry.status] ?? []

  const canTransition = hasRole('BD', 'Admin', 'SuperAdmin', 'SupplyChain')
  const canCreateQuotation = hasRole('BD', 'Admin', 'SuperAdmin')

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle>{enquiry.enquiry_no}</CardTitle>
            <div className="flex items-center gap-2">
              <Badge value={enquiry.status} />
              <Button variant="ghost" size="sm" onClick={() => navigate('/enquiries')}>
                Back
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-slate-700">
          <p>
            <span className="font-medium text-slate-900">Customer:</span>{' '}
            {customerMap.get(enquiry.customer_id) ?? enquiry.customer_id}
          </p>
          <p>
            <span className="font-medium text-slate-900">Received:</span> {formatDate(enquiry.received_date)}
          </p>
          <p>
            <span className="font-medium text-slate-900">Currency:</span> {enquiry.currency}
          </p>
          <p>
            <span className="font-medium text-slate-900">Notes:</span> {enquiry.notes ?? '-'}
          </p>

          <div className="mt-3 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
            {canCreateQuotation ? (
              <Button onClick={() => createQuotationMutation.mutate()} disabled={createQuotationMutation.isPending}>
                {createQuotationMutation.isPending ? 'Creating...' : 'Create Quotation'}
              </Button>
            ) : null}
            {canCreateQuotation ? (
              <Button variant="secondary" onClick={() => navigate('/commercial')}>
                Continue to Commercial
              </Button>
            ) : null}
            <Link to="/enquiries/new" className="inline-flex items-center text-sm font-medium text-teal-700">
              Create another enquiry
            </Link>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Enquiry Items</CardTitle>
        </CardHeader>
        <CardContent>
          <TableContainer>
            <Table>
              <thead>
                <tr>
                  <Th>Product</Th>
                  <Th>Requested Qty</Th>
                  <Th>Target Price</Th>
                  <Th>Notes</Th>
                </tr>
              </thead>
              <tbody>
                {enquiry.items.map((item) => (
                  <tr key={item.id}>
                    <Td>{productMap.get(item.product_id) ?? item.product_id}</Td>
                    <Td>{asNumber(item.requested_qty).toFixed(2)}</Td>
                    <Td>{item.target_price ? asNumber(item.target_price).toFixed(2) : '-'}</Td>
                    <Td>{item.notes ?? '-'}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[1.3fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Status History</CardTitle>
          </CardHeader>
          <CardContent>
            {historyRows.length === 0 ? (
              <EmptyState title="No history" subtitle="Status changes will be listed here." />
            ) : (
              <TableContainer>
                <Table>
                  <thead>
                    <tr>
                      <Th>When</Th>
                      <Th>From</Th>
                      <Th>To</Th>
                      <Th>Comment</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyRows.map((row) => (
                      <tr key={row.id}>
                        <Td>{formatDate(row.changed_at, true)}</Td>
                        <Td>{row.from_status ?? '-'}</Td>
                        <Td>
                          <Badge value={row.to_status} />
                        </Td>
                        <Td>{row.comment ?? '-'}</Td>
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
            <CardTitle>Transition Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {canTransition ? (
              <>
                <FormField label="Next status">
                  <Select value={nextStatus} onChange={(event) => setNextStatus(event.target.value)}>
                    <option value="">Choose status</option>
                    {availableTransitions.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </Select>
                </FormField>
                <FormField label="Comment">
                  <Textarea value={comment} onChange={(event) => setComment(event.target.value)} />
                </FormField>
                <Button
                  className="w-full"
                  onClick={() => transitionMutation.mutate()}
                  disabled={!nextStatus || transitionMutation.isPending}
                >
                  {transitionMutation.isPending ? 'Applying...' : 'Apply Transition'}
                </Button>
              </>
            ) : (
              <p className="text-sm text-slate-500">Your role has read-only access to enquiry status.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
