import * as React from 'react'
import type { ReactNode } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useFieldArray, useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useNavigate, useParams } from 'react-router-dom'
import { z } from 'zod'

import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/page-state'
import { Badge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { FormField } from '../../components/ui/form-field'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { Textarea } from '../../components/ui/textarea'
import { useAuth } from '../../context/AuthContext'
import { useWorkflow } from '../../context/WorkflowContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'
import { asNumber, formatDate, formatMoney } from '../../lib/format'

const revisionItemSchema = z.object({
  product_id: z.string().uuid('Product is required'),
  qty: z
    .string()
    .min(1, 'Qty is required')
    .refine((value) => Number(value) > 0, 'Qty must be greater than 0'),
  unit_price: z
    .string()
    .min(1, 'Unit price is required')
    .refine((value) => Number(value) >= 0, 'Unit price cannot be negative'),
  enquiry_item_id: z.string().optional(),
  notes: z.string().optional(),
})

const revisionSchema = z.object({
  freight: z
    .string()
    .min(1, 'Freight is required')
    .refine((value) => Number(value) >= 0, 'Freight cannot be negative'),
  markup_percent: z
    .string()
    .min(1, 'Markup is required')
    .refine((value) => Number(value) >= 0, 'Markup cannot be negative'),
  currency: z.string().length(3),
  items: z.array(revisionItemSchema).min(1, 'At least one line item is required'),
})

type RevisionForm = z.infer<typeof revisionSchema>

const poSchema = z.object({
  po_no: z.string().optional(),
  po_date: z.string().optional(),
  total_amount: z
    .string()
    .optional()
    .refine((value) => !value || Number(value) >= 0, 'Total amount cannot be negative'),
  status: z.string().min(1, 'Status is required'),
})

type POForm = z.infer<typeof poSchema>

export function QuotationPage(): ReactNode {
  const { quotationId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { hasRole } = useAuth()
  const { setQuotationRevision, addCustomerPO, addRTMPO } = useWorkflow()

  const [selectedRevisionId, setSelectedRevisionId] = React.useState<string>('')
  const [actionRemarks, setActionRemarks] = React.useState('')

  const quotationQuery = useQuery({
    queryKey: ['quotations', quotationId],
    queryFn: () => api.quotations.get(quotationId),
    enabled: Boolean(quotationId),
  })

  const enquiryId = quotationQuery.data?.enquiry_id

  const enquiryQuery = useQuery({
    queryKey: ['enquiries', enquiryId],
    queryFn: () => api.enquiries.get(enquiryId ?? ''),
    enabled: Boolean(enquiryId),
  })

  const productsQuery = useQuery({
    queryKey: ['masters', 'products'],
    queryFn: () => api.masters.listProducts({ limit: 500 }),
  })

  const manufacturersQuery = useQuery({
    queryKey: ['masters', 'manufacturers'],
    queryFn: () => api.masters.listManufacturers({ limit: 500 }),
  })

  const revisionForm = useForm<RevisionForm>({
    resolver: zodResolver(revisionSchema),
    defaultValues: {
      freight: '0',
      markup_percent: '0',
      currency: 'USD',
      items: [{ product_id: '', qty: '1', unit_price: '0', enquiry_item_id: '', notes: '' }],
    },
  })

  const revisionItems = useFieldArray({
    control: revisionForm.control,
    name: 'items',
  })

  const customerPOForm = useForm<POForm>({
    resolver: zodResolver(poSchema),
    defaultValues: {
      po_no: '',
      po_date: '',
      total_amount: '',
      status: 'ISSUED',
    },
  })

  const rtmPOForm = useForm<POForm & { manufacturer_id?: string }>({
    resolver: zodResolver(poSchema.extend({ manufacturer_id: z.string().optional() })),
    defaultValues: {
      po_no: '',
      po_date: '',
      total_amount: '',
      status: 'ISSUED',
      manufacturer_id: '',
    },
  })

  const refreshQuote = () => {
    void queryClient.invalidateQueries({ queryKey: ['quotations', quotationId] })
  }

  const createRevisionMutation = useMutation({
    mutationFn: (values: RevisionForm) =>
      api.quotations.createRevision(quotationId, {
        freight: Number(values.freight),
        markup_percent: Number(values.markup_percent),
        currency: values.currency.toUpperCase(),
        items: values.items.map((item) => ({
          product_id: item.product_id,
          qty: Number(item.qty),
          unit_price: Number(item.unit_price),
          enquiry_item_id: item.enquiry_item_id || undefined,
          notes: item.notes || null,
        })),
      }),
    onSuccess: (revision) => {
      toast.success(`Revision ${revision.revision_no} created`)
      setSelectedRevisionId(revision.id)
      setQuotationRevision(quotationId, revision.id)
      refreshQuote()
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const submitMutation = useMutation({
    mutationFn: () => api.quotations.submitRevision(quotationId, selectedRevisionId, actionRemarks || undefined),
    onSuccess: () => {
      toast.success('Revision submitted')
      setActionRemarks('')
      refreshQuote()
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const approveMutation = useMutation({
    mutationFn: () => api.quotations.approveRevision(quotationId, selectedRevisionId, actionRemarks.trim()),
    onSuccess: () => {
      toast.success('Revision approved')
      setActionRemarks('')
      refreshQuote()
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const rejectMutation = useMutation({
    mutationFn: () => api.quotations.rejectRevision(quotationId, selectedRevisionId, actionRemarks.trim()),
    onSuccess: () => {
      toast.success('Revision rejected')
      setActionRemarks('')
      refreshQuote()
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const createCustomerPOMutation = useMutation({
    mutationFn: (values: POForm) =>
      api.commercial.createCustomerPO(quotationId, selectedRevisionId, {
        po_no: values.po_no || undefined,
        po_date: values.po_date || undefined,
        total_amount: values.total_amount === '' || values.total_amount == null ? undefined : Number(values.total_amount),
        status: values.status,
      }),
    onSuccess: (created) => {
      addCustomerPO(created)
      toast.success('Customer PO created')
      customerPOForm.reset({ po_no: '', po_date: '', total_amount: '', status: 'ISSUED' })
      navigate('/commercial')
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const createRTMPOMutation = useMutation({
    mutationFn: (values: POForm & { manufacturer_id?: string }) =>
      api.commercial.createRTMPO(quotationId, selectedRevisionId, {
        po_no: values.po_no || undefined,
        manufacturer_id: values.manufacturer_id || undefined,
        po_date: values.po_date || undefined,
        total_amount: values.total_amount === '' || values.total_amount == null ? undefined : Number(values.total_amount),
        status: values.status,
      }),
    onSuccess: (created) => {
      addRTMPO(created)
      toast.success('RTM PO created')
      rtmPOForm.reset({ po_no: '', po_date: '', total_amount: '', status: 'ISSUED', manufacturer_id: '' })
      navigate('/commercial')
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  React.useEffect(() => {
    const quotation = quotationQuery.data
    if (!quotation || quotation.revisions.length === 0) {
      return
    }

    const sorted = [...quotation.revisions].sort((a, b) => b.revision_no - a.revision_no)
    const target = sorted[0]
    setSelectedRevisionId((prev) => prev || target.id)
    setQuotationRevision(quotation.id, target.id)
  }, [quotationQuery.data, setQuotationRevision])

  React.useEffect(() => {
    const enquiry = enquiryQuery.data
    if (!enquiry || !productsQuery.data) {
      return
    }

    if (revisionItems.fields.length > 1 || revisionItems.fields[0]?.product_id) {
      return
    }

    const prefilled = enquiry.items.map((item) => ({
      product_id: item.product_id,
      qty: String(asNumber(item.requested_qty) || 1),
      unit_price: String(asNumber(item.target_price)),
      enquiry_item_id: item.id,
      notes: item.notes ?? '',
    }))

    revisionForm.reset({
      freight: '0',
      markup_percent: '0',
      currency: enquiry.currency,
      items:
        prefilled.length > 0
          ? prefilled
          : [{ product_id: '', qty: '1', unit_price: '0', enquiry_item_id: '', notes: '' }],
    })
  }, [enquiryQuery.data, productsQuery.data, revisionForm, revisionItems.fields])

  if (quotationQuery.isLoading || enquiryQuery.isLoading || productsQuery.isLoading || manufacturersQuery.isLoading) {
    return <LoadingState message="Loading quotation..." />
  }

  if (
    quotationQuery.isError ||
    enquiryQuery.isError ||
    productsQuery.isError ||
    manufacturersQuery.isError ||
    !quotationQuery.data ||
    !enquiryQuery.data
  ) {
    const message = toApiClientError(
      quotationQuery.error ?? enquiryQuery.error ?? productsQuery.error ?? manufacturersQuery.error,
    ).message
    return <ErrorState message={message} onRetry={() => void quotationQuery.refetch()} />
  }

  const quotation = quotationQuery.data
  const enquiry = enquiryQuery.data
  const products = productsQuery.data ?? []
  const manufacturers = manufacturersQuery.data ?? []

  const revision = quotation.revisions.find((row) => row.id === selectedRevisionId) ?? null

  const canEditRevisions = hasRole('BD', 'Admin', 'SuperAdmin')
  const canApproveReject = hasRole('Admin', 'SuperAdmin')
  const canCreateCustomerPO = hasRole('BD', 'Admin', 'SuperAdmin')
  const canCreateRTMPO = hasRole('SupplyChain', 'Admin', 'SuperAdmin')

  const pendingApproval = Boolean(revision?.submitted_at && !revision.approved_at && !revision.rejected_at)
  const approvedRevision = Boolean(revision?.approved_at && !revision?.rejected_at)
  const approvalRemarks = actionRemarks.trim()

  const productMap = new Map(products.map((row) => [row.id, row.name]))

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle>{quotation.quotation_no}</CardTitle>
            <Badge value={quotation.status} />
          </div>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm text-slate-700 md:grid-cols-2">
          <p>
            <span className="font-medium text-slate-900">Enquiry:</span> {enquiry.enquiry_no}
          </p>
          <p>
            <span className="font-medium text-slate-900">Current Revision:</span> {quotation.current_revision_no}
          </p>
          <p>
            <span className="font-medium text-slate-900">Created:</span> {formatDate(quotation.created_at, true)}
          </p>
          <p>
            <span className="font-medium text-slate-900">Updated:</span> {formatDate(quotation.updated_at, true)}
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Revision Detail</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {quotation.revisions.length === 0 ? (
              <EmptyState title="No revisions" subtitle="Create a revision to build pricing and totals." />
            ) : (
              <>
                <Select value={selectedRevisionId} onChange={(event) => setSelectedRevisionId(event.target.value)}>
                  {quotation.revisions
                    .slice()
                    .sort((a, b) => b.revision_no - a.revision_no)
                    .map((row) => (
                      <option key={row.id} value={row.id}>
                        Revision {row.revision_no}
                      </option>
                    ))}
                </Select>

                {revision ? (
                  <>
                    <div className="grid gap-2 md:grid-cols-3">
                      <Stat label="Subtotal" value={formatMoney(revision.subtotal, revision.currency)} />
                      <Stat label="Freight" value={formatMoney(revision.freight, revision.currency)} />
                      <Stat label="Total" value={formatMoney(revision.total, revision.currency)} />
                    </div>

                    <TableContainer>
                      <Table>
                        <thead>
                          <tr>
                            <Th>Product</Th>
                            <Th>Qty</Th>
                            <Th>Unit Price</Th>
                            <Th>Line Total</Th>
                            <Th>Notes</Th>
                          </tr>
                        </thead>
                        <tbody>
                          {revision.items.map((item) => (
                            <tr key={item.id}>
                              <Td>{productMap.get(item.product_id) ?? item.product_id}</Td>
                              <Td>{asNumber(item.qty).toFixed(2)}</Td>
                              <Td>{formatMoney(item.unit_price, revision.currency)}</Td>
                              <Td>{formatMoney(item.line_total, revision.currency)}</Td>
                              <Td>{item.notes ?? '-'}</Td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </TableContainer>

                    <div className="space-y-2 rounded-md border border-slate-200 p-3">
                      <p className="text-sm font-medium text-slate-900">Approval Actions</p>
                      <Textarea
                        value={actionRemarks}
                        onChange={(event) => setActionRemarks(event.target.value)}
                        placeholder="Action remarks (required for approve/reject)"
                      />
                      {canApproveReject && pendingApproval && !approvalRemarks ? (
                        <p className="text-xs text-rose-700">Approval or rejection remarks are required.</p>
                      ) : null}
                      <div className="flex flex-wrap gap-2">
                        {canEditRevisions ? (
                          <Button
                            onClick={() => submitMutation.mutate()}
                            disabled={Boolean(revision.submitted_at) || submitMutation.isPending}
                          >
                            Submit Revision
                          </Button>
                        ) : null}
                        {canApproveReject ? (
                          <Button
                            variant="secondary"
                            onClick={() => approveMutation.mutate()}
                            disabled={!pendingApproval || !approvalRemarks || approveMutation.isPending}
                          >
                            Approve
                          </Button>
                        ) : null}
                        {canApproveReject ? (
                          <Button
                            variant="danger"
                            onClick={() => rejectMutation.mutate()}
                            disabled={!pendingApproval || !approvalRemarks || rejectMutation.isPending}
                          >
                            Reject
                          </Button>
                        ) : null}
                      </div>
                    </div>

                    <div className="space-y-2 rounded-md border border-slate-200 p-3">
                      <p className="text-sm font-medium text-slate-900">Approval Timeline</p>
                      {revision.approvals.map((approval) => (
                        <div key={approval.id} className="rounded border border-slate-100 p-2 text-sm text-slate-700">
                          <p>
                            <span className="font-medium">{approval.step_name}:</span>{' '}
                            <Badge value={approval.decision} />
                          </p>
                          <p>Decided at: {formatDate(approval.decided_at, true)}</p>
                          <p>Remarks: {approval.remarks ?? '-'}</p>
                        </div>
                      ))}
                    </div>
                  </>
                ) : null}
              </>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          {canEditRevisions ? (
            <Card>
              <CardHeader>
                <CardTitle>Create Revision</CardTitle>
              </CardHeader>
              <CardContent>
                <form
                  className="space-y-3"
                  onSubmit={revisionForm.handleSubmit((values) => createRevisionMutation.mutate(values))}
                >
                  <div className="grid gap-2 md:grid-cols-3">
                    <FormField label="Freight">
                      <Input type="number" min="0" step="0.01" {...revisionForm.register('freight')} />
                    </FormField>
                    <FormField label="Markup %">
                      <Input type="number" min="0" step="0.01" {...revisionForm.register('markup_percent')} />
                    </FormField>
                    <FormField label="Currency">
                      <Input maxLength={3} {...revisionForm.register('currency')} />
                    </FormField>
                  </div>
                  <div className="space-y-2 rounded-md border border-slate-100 p-2">
                    <div className="flex justify-between">
                      <p className="text-sm font-medium">Line Items</p>
                      <Button
                        size="sm"
                        variant="ghost"
                        type="button"
                        onClick={() =>
                          revisionItems.append({
                            product_id: '',
                            qty: '1',
                            unit_price: '0',
                            enquiry_item_id: '',
                            notes: '',
                          })
                        }
                      >
                        Add Row
                      </Button>
                    </div>
                    {revisionItems.fields.map((field, index) => (
                      <div key={field.id} className="grid gap-2 border-b border-slate-100 pb-2 md:grid-cols-5">
                        <Select {...revisionForm.register(`items.${index}.product_id`)}>
                          <option value="">Product</option>
                          {products.map((row) => (
                            <option key={row.id} value={row.id}>
                              {row.name}
                            </option>
                          ))}
                        </Select>
                        <Input type="number" min="0" step="0.01" {...revisionForm.register(`items.${index}.qty`)} />
                        <Input
                          type="number"
                          min="0"
                          step="0.01"
                          {...revisionForm.register(`items.${index}.unit_price`)}
                        />
                        <Select {...revisionForm.register(`items.${index}.enquiry_item_id`)}>
                          <option value="">Linked enquiry item</option>
                          {enquiry.items.map((item) => (
                            <option key={item.id} value={item.id}>
                              {productMap.get(item.product_id) ?? item.product_id}
                            </option>
                          ))}
                        </Select>
                        <div className="flex gap-2">
                          <Input placeholder="Notes" {...revisionForm.register(`items.${index}.notes`)} />
                          <Button
                            size="sm"
                            variant="ghost"
                            type="button"
                            disabled={revisionItems.fields.length === 1}
                            onClick={() => revisionItems.remove(index)}
                          >
                            X
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full" type="submit" disabled={createRevisionMutation.isPending}>
                    {createRevisionMutation.isPending ? 'Creating...' : 'Create Revision'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          ) : null}

          {approvedRevision ? (
            <Card>
              <CardHeader>
                <CardTitle>Create Customer PO / RTM PO</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {canCreateCustomerPO ? (
                  <form
                    className="space-y-2 rounded-md border border-slate-100 p-3"
                    onSubmit={customerPOForm.handleSubmit((values) => createCustomerPOMutation.mutate(values))}
                  >
                    <p className="text-sm font-medium">Customer PO</p>
                    <Input placeholder="PO No (optional)" {...customerPOForm.register('po_no')} />
                    <Input type="date" {...customerPOForm.register('po_date')} />
                    <Input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="Total amount (optional)"
                      {...customerPOForm.register('total_amount')}
                    />
                    <Select {...customerPOForm.register('status')}>
                      {['DRAFT', 'ISSUED', 'CONFIRMED', 'CLOSED', 'CANCELLED'].map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </Select>
                    <Button className="w-full" type="submit" disabled={createCustomerPOMutation.isPending}>
                      Create Customer PO
                    </Button>
                  </form>
                ) : null}

                {canCreateRTMPO ? (
                  <form
                    className="space-y-2 rounded-md border border-slate-100 p-3"
                    onSubmit={rtmPOForm.handleSubmit((values) => createRTMPOMutation.mutate(values))}
                  >
                    <p className="text-sm font-medium">RTM PO</p>
                    <Input placeholder="PO No (optional)" {...rtmPOForm.register('po_no')} />
                    <Select {...rtmPOForm.register('manufacturer_id')}>
                      <option value="">Manufacturer (optional)</option>
                      {manufacturers.map((row) => (
                        <option key={row.id} value={row.id}>
                          {row.name}
                        </option>
                      ))}
                    </Select>
                    <Input type="date" {...rtmPOForm.register('po_date')} />
                    <Input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="Total amount (optional)"
                      {...rtmPOForm.register('total_amount')}
                    />
                    <Select {...rtmPOForm.register('status')}>
                      {['DRAFT', 'ISSUED', 'CONFIRMED', 'CLOSED', 'CANCELLED'].map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </Select>
                    <Button className="w-full" type="submit" disabled={createRTMPOMutation.isPending}>
                      Create RTM PO
                    </Button>
                  </form>
                ) : null}
              </CardContent>
            </Card>
          ) : null}
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }): ReactNode {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-sm font-semibold text-slate-900">{value}</p>
    </div>
  )
}
