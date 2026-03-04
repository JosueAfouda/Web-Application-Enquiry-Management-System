import type { ReactNode } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { z } from 'zod'

import { EmptyState } from '../../components/feedback/page-state'
import { Badge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { FormField } from '../../components/ui/form-field'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { Textarea } from '../../components/ui/textarea'
import { useWorkflow } from '../../context/WorkflowContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'
import { asNumber, formatDate, formatMoney } from '../../lib/format'
import type { Invoice, Payment } from '../../types/api'

const invoiceSchema = z.object({
  invoice_no: z.string().optional(),
  enquiry_id: z.string().uuid('Enquiry is required'),
  customer_po_id: z.string().optional(),
  issue_date: z.string().optional(),
  due_date: z.string().optional(),
  currency: z.string().length(3),
  total_amount: z
    .string()
    .optional()
    .refine((value) => !value || Number(value) >= 0, 'Total amount must be 0 or greater'),
})

type InvoiceForm = z.infer<typeof invoiceSchema>

const paymentSchema = z.object({
  invoice_id: z.string().uuid('Invoice is required'),
  payment_date: z.string().optional(),
  amount: z
    .string()
    .min(1, 'Amount is required')
    .refine((value) => Number(value) > 0, 'Amount must be greater than zero'),
  method: z.string().min(1, 'Method is required'),
  reference_no: z.string().optional(),
  notes: z.string().optional(),
})

type PaymentForm = z.infer<typeof paymentSchema>

const deliverySchema = z.object({
  enquiry_id: z.string().uuid('Enquiry is required'),
  invoice_id: z.string().optional(),
  shipment_no: z.string().optional(),
  courier_name: z.string().optional(),
  tracking_no: z.string().optional(),
  shipped_at: z.string().optional(),
  expected_delivery_at: z.string().optional(),
  delivered_at: z.string().optional(),
  status: z.string().min(1, 'Status is required'),
})

type DeliveryForm = z.infer<typeof deliverySchema>

const eventSchema = z.object({
  delivery_id: z.string().uuid('Delivery is required'),
  event_type: z.string().min(1),
  event_time: z.string().optional(),
  location: z.string().optional(),
  details_json: z.string().optional(),
})

type EventForm = z.infer<typeof eventSchema>

export function CommercialPage(): ReactNode {
  const { workflow, addInvoice, addDelivery, setWorkflow } = useWorkflow()

  const enquiriesQuery = useQuery({
    queryKey: ['enquiries', 'commercial'],
    queryFn: () => api.enquiries.list({ limit: 500 }),
  })

  const invoiceForm = useForm<InvoiceForm>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: {
      invoice_no: '',
      enquiry_id: workflow.lastEnquiryId ?? '',
      customer_po_id: workflow.customerPOs[0]?.id ?? '',
      issue_date: '',
      due_date: '',
      currency: 'USD',
      total_amount: '',
    },
  })

  const paymentForm = useForm<PaymentForm>({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      invoice_id: workflow.invoices[0]?.id ?? '',
      payment_date: '',
      amount: '',
      method: 'BANK_TRANSFER',
      reference_no: '',
      notes: '',
    },
  })

  const deliveryForm = useForm<DeliveryForm>({
    resolver: zodResolver(deliverySchema),
    defaultValues: {
      enquiry_id: workflow.lastEnquiryId ?? '',
      invoice_id: workflow.invoices[0]?.id ?? '',
      shipment_no: '',
      courier_name: '',
      tracking_no: '',
      shipped_at: '',
      expected_delivery_at: '',
      delivered_at: '',
      status: 'PENDING',
    },
  })

  const eventForm = useForm<EventForm>({
    resolver: zodResolver(eventSchema),
    defaultValues: {
      delivery_id: workflow.deliveries[0]?.id ?? '',
      event_type: 'IN_TRANSIT',
      event_time: '',
      location: '',
      details_json: '',
    },
  })

  const createInvoiceMutation = useMutation({
    mutationFn: (values: InvoiceForm) =>
      api.commercial.createInvoice({
        invoice_no: values.invoice_no || undefined,
        enquiry_id: values.enquiry_id,
        customer_po_id: values.customer_po_id || undefined,
        issue_date: values.issue_date || undefined,
        due_date: values.due_date || undefined,
        currency: values.currency.toUpperCase(),
        total_amount: values.total_amount === '' || values.total_amount == null ? undefined : Number(values.total_amount),
      }),
    onSuccess: (created) => {
      addInvoice(created)
      toast.success('Invoice created')
      paymentForm.setValue('invoice_id', created.id)
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const createPaymentMutation = useMutation({
    mutationFn: (values: PaymentForm) =>
      api.commercial.createPayment({
        invoice_id: values.invoice_id,
        payment_date: values.payment_date || undefined,
        amount: Number(values.amount),
        method: values.method,
        reference_no: values.reference_no || undefined,
        notes: values.notes || undefined,
      }),
    onSuccess: (payment) => {
      setWorkflow((previous) => ({
        ...previous,
        invoices: previous.invoices.map((invoice) =>
          invoice.id === payment.invoice_id ? applyPaymentToInvoice(invoice, payment) : invoice,
        ),
      }))
      toast.success('Payment created')
    },
    onError: (error) => {
      const normalized = toApiClientError(error)
      if (normalized.status === 400 && normalized.message.includes('exceeds invoice total')) {
        toast.error(`Overpayment blocked: ${normalized.message}`)
        return
      }
      toast.error(normalized.message)
    },
  })

  const createDeliveryMutation = useMutation({
    mutationFn: (values: DeliveryForm) =>
      api.commercial.createDelivery({
        enquiry_id: values.enquiry_id,
        invoice_id: values.invoice_id || undefined,
        shipment_no: values.shipment_no || undefined,
        courier_name: values.courier_name || undefined,
        tracking_no: values.tracking_no || undefined,
        shipped_at: values.shipped_at || undefined,
        expected_delivery_at: values.expected_delivery_at || undefined,
        delivered_at: values.delivered_at || undefined,
        status: values.status,
      }),
    onSuccess: (created) => {
      addDelivery(created)
      eventForm.setValue('delivery_id', created.id)
      toast.success('Delivery created')
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const addEventMutation = useMutation({
    mutationFn: async (values: EventForm) => {
      let parsedDetails: Record<string, unknown> = {}
      if (values.details_json?.trim()) {
        parsedDetails = JSON.parse(values.details_json) as Record<string, unknown>
      }
      await api.commercial.addDeliveryEvent(values.delivery_id, {
        event_type: values.event_type,
        event_time: values.event_time || undefined,
        location: values.location || undefined,
        details_jsonb: parsedDetails,
      })
      return api.commercial.getDelivery(values.delivery_id)
    },
    onSuccess: (delivery) => {
      addDelivery(delivery)
      toast.success('Delivery event added')
    },
    onError: (error) => {
      if (error instanceof SyntaxError) {
        toast.error('details_json must be valid JSON')
        return
      }
      toast.error(toApiClientError(error).message)
    },
  })

  const enquiries = enquiriesQuery.data ?? []

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Create Invoice</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-2" onSubmit={invoiceForm.handleSubmit((values) => createInvoiceMutation.mutate(values))}>
              <FormField label="Enquiry" error={invoiceForm.formState.errors.enquiry_id?.message}>
                <Select {...invoiceForm.register('enquiry_id')}>
                  <option value="">Select enquiry</option>
                  {enquiries.map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.enquiry_no}
                    </option>
                  ))}
                </Select>
              </FormField>
              <FormField label="Customer PO (optional)">
                <Select {...invoiceForm.register('customer_po_id')}>
                  <option value="">None</option>
                  {workflow.customerPOs.map((po) => (
                    <option key={po.id} value={po.id}>
                      {po.po_no}
                    </option>
                  ))}
                </Select>
              </FormField>
              <Input placeholder="Invoice no (optional)" {...invoiceForm.register('invoice_no')} />
              <div className="grid grid-cols-2 gap-2">
                <Input type="date" {...invoiceForm.register('issue_date')} />
                <Input type="date" {...invoiceForm.register('due_date')} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Input maxLength={3} {...invoiceForm.register('currency')} />
                <Input type="number" step="0.01" min="0" placeholder="Total (optional)" {...invoiceForm.register('total_amount')} />
              </div>
              <Button className="w-full" type="submit" disabled={createInvoiceMutation.isPending}>
                Create Invoice
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Add Payment</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-2" onSubmit={paymentForm.handleSubmit((values) => createPaymentMutation.mutate(values))}>
              <FormField label="Invoice" error={paymentForm.formState.errors.invoice_id?.message}>
                <Select {...paymentForm.register('invoice_id')}>
                  <option value="">Select invoice</option>
                  {workflow.invoices.map((invoice) => (
                    <option key={invoice.id} value={invoice.id}>
                      {invoice.invoice_no}
                    </option>
                  ))}
                </Select>
              </FormField>
              <div className="grid grid-cols-2 gap-2">
                <Input type="date" {...paymentForm.register('payment_date')} />
                <Input type="number" step="0.01" min="0" {...paymentForm.register('amount')} />
              </div>
              <Input placeholder="Method" {...paymentForm.register('method')} />
              <Input placeholder="Reference" {...paymentForm.register('reference_no')} />
              <Textarea placeholder="Notes" {...paymentForm.register('notes')} />
              <Button className="w-full" type="submit" disabled={createPaymentMutation.isPending}>
                Add Payment
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>PO Context</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-slate-700">
            <p className="font-medium text-slate-900">Customer POs</p>
            {workflow.customerPOs.length === 0 ? <p className="text-slate-500">None</p> : null}
            {workflow.customerPOs.map((po) => (
              <p key={po.id} className="rounded border border-slate-100 p-2">
                {po.po_no} ({formatMoney(po.total_amount)})
              </p>
            ))}

            <p className="pt-2 font-medium text-slate-900">RTM POs</p>
            {workflow.rtmPOs.length === 0 ? <p className="text-slate-500">None</p> : null}
            {workflow.rtmPOs.map((po) => (
              <p key={po.id} className="rounded border border-slate-100 p-2">
                {po.po_no} ({formatMoney(po.total_amount)})
              </p>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Create Delivery + Timeline Event</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form className="space-y-2" onSubmit={deliveryForm.handleSubmit((values) => createDeliveryMutation.mutate(values))}>
              <p className="text-sm font-medium text-slate-900">Delivery</p>
              <Select {...deliveryForm.register('enquiry_id')}>
                <option value="">Select enquiry</option>
                {enquiries.map((row) => (
                  <option key={row.id} value={row.id}>
                    {row.enquiry_no}
                  </option>
                ))}
              </Select>
              <Select {...deliveryForm.register('invoice_id')}>
                <option value="">No invoice link</option>
                {workflow.invoices.map((invoice) => (
                  <option key={invoice.id} value={invoice.id}>
                    {invoice.invoice_no}
                  </option>
                ))}
              </Select>
              <Input placeholder="Shipment no (optional)" {...deliveryForm.register('shipment_no')} />
              <Input placeholder="Courier" {...deliveryForm.register('courier_name')} />
              <Input placeholder="Tracking no" {...deliveryForm.register('tracking_no')} />
              <Select {...deliveryForm.register('status')}>
                {['PENDING', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'CANCELLED'].map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </Select>
              <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                <Input type="datetime-local" {...deliveryForm.register('shipped_at')} />
                <Input type="datetime-local" {...deliveryForm.register('expected_delivery_at')} />
              </div>
              <Input type="datetime-local" {...deliveryForm.register('delivered_at')} />
              <Button className="w-full" type="submit" disabled={createDeliveryMutation.isPending}>
                Create Delivery
              </Button>
            </form>

            <form className="space-y-2 border-t border-slate-100 pt-3" onSubmit={eventForm.handleSubmit((values) => addEventMutation.mutate(values))}>
              <p className="text-sm font-medium text-slate-900">Add Delivery Event</p>
              <Select {...eventForm.register('delivery_id')}>
                <option value="">Select delivery</option>
                {workflow.deliveries.map((delivery) => (
                  <option key={delivery.id} value={delivery.id}>
                    {delivery.shipment_no ?? delivery.id}
                  </option>
                ))}
              </Select>
              <Input placeholder="Event type (e.g. IN_TRANSIT, DELIVERED)" {...eventForm.register('event_type')} />
              <Input type="datetime-local" {...eventForm.register('event_time')} />
              <Input placeholder="Location" {...eventForm.register('location')} />
              <Textarea placeholder='Details JSON, e.g. {"checkpoint":"MAD"}' {...eventForm.register('details_json')} />
              <Button className="w-full" type="submit" disabled={addEventMutation.isPending}>
                Add Event
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Invoices and Deliveries (Session)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <section>
              <h4 className="mb-2 text-sm font-semibold text-slate-900">Invoices</h4>
              {workflow.invoices.length === 0 ? (
                <EmptyState title="No invoices yet" subtitle="Create an invoice to track payments." />
              ) : (
                <TableContainer>
                  <Table>
                    <thead>
                      <tr>
                        <Th>Invoice #</Th>
                        <Th>Status</Th>
                        <Th>Total</Th>
                        <Th>Paid</Th>
                        <Th>Due</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {workflow.invoices.map((invoice) => {
                        const total = asNumber(invoice.total_amount)
                        const paid = sumPaid(invoice.payments)
                        return (
                          <tr key={invoice.id}>
                            <Td>{invoice.invoice_no}</Td>
                            <Td>
                              <Badge value={invoice.status} />
                            </Td>
                            <Td>{formatMoney(total, invoice.currency)}</Td>
                            <Td>{formatMoney(paid, invoice.currency)}</Td>
                            <Td>{formatMoney(total - paid, invoice.currency)}</Td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </Table>
                </TableContainer>
              )}
            </section>

            <section>
              <h4 className="mb-2 text-sm font-semibold text-slate-900">Deliveries</h4>
              {workflow.deliveries.length === 0 ? (
                <EmptyState title="No deliveries yet" subtitle="Create a delivery and add timeline events." />
              ) : (
                <div className="space-y-2">
                  {workflow.deliveries.map((delivery) => (
                    <div key={delivery.id} className="rounded-lg border border-slate-200 p-3">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-sm font-medium text-slate-900">
                          {delivery.shipment_no ?? delivery.id}
                        </p>
                        <Badge value={delivery.status} />
                      </div>
                      <p className="text-xs text-slate-500">Tracking: {delivery.tracking_no ?? '-'}</p>
                      <p className="text-xs text-slate-500">Events: {delivery.events.length}</p>
                      <ul className="mt-2 space-y-1 text-xs text-slate-600">
                        {delivery.events.slice(-3).map((event) => (
                          <li key={event.id}>
                            {formatDate(event.event_time, true)} - {event.event_type} ({event.location ?? 'N/A'})
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function sumPaid(payments: Payment[]): number {
  return payments.reduce((total, payment) => total + asNumber(payment.amount), 0)
}

function applyPaymentToInvoice(invoice: Invoice, payment: Payment): Invoice {
  const payments = [...invoice.payments, payment]
  const total = asNumber(invoice.total_amount)
  const paid = sumPaid(payments)

  let status = invoice.status
  if (paid <= 0) {
    status = 'UNPAID'
  } else if (paid < total) {
    status = 'PARTIAL'
  } else {
    status = 'PAID'
  }

  return {
    ...invoice,
    payments,
    status,
    updated_at: new Date().toISOString(),
  }
}
