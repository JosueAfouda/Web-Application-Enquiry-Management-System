import type { ReactNode } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useFieldArray, useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { ErrorState, LoadingState } from '../../components/feedback/page-state'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { FormField } from '../../components/ui/form-field'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { Textarea } from '../../components/ui/textarea'
import { useWorkflow } from '../../context/WorkflowContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'

const itemSchema = z.object({
  product_id: z.string().uuid('Product is required'),
  requested_qty: z
    .string()
    .min(1, 'Quantity is required')
    .refine((value) => Number(value) > 0, 'Quantity must be greater than zero'),
  target_price: z
    .string()
    .optional()
    .refine((value) => !value || Number(value) >= 0, 'Target price cannot be negative'),
  notes: z.string().optional(),
})

const schema = z.object({
  customer_id: z.string().uuid('Customer is required'),
  received_date: z.string().optional(),
  currency: z.string().length(3, 'Use 3-letter currency code'),
  notes: z.string().optional(),
  items: z.array(itemSchema).min(1, 'At least one item is required'),
})

type FormValues = z.infer<typeof schema>

export function NewEnquiryPage(): ReactNode {
  const navigate = useNavigate()
  const { setLastEnquiry } = useWorkflow()

  const customersQuery = useQuery({
    queryKey: ['masters', 'customers'],
    queryFn: () => api.masters.listCustomers({ limit: 500 }),
  })
  const productsQuery = useQuery({
    queryKey: ['masters', 'products'],
    queryFn: () => api.masters.listProducts({ limit: 500 }),
  })

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      customer_id: '',
      received_date: '',
      currency: 'USD',
      notes: '',
      items: [
        {
          product_id: '',
          requested_qty: '1',
          target_price: '',
          notes: '',
        },
      ],
    },
  })

  const itemArray = useFieldArray({
    control: form.control,
    name: 'items',
  })

  const createMutation = useMutation({
    mutationFn: (values: FormValues) =>
      api.enquiries.create({
        customer_id: values.customer_id,
        received_date: values.received_date || undefined,
        currency: values.currency.toUpperCase(),
        notes: values.notes || null,
        items: values.items.map((item) => ({
          product_id: item.product_id,
          requested_qty: Number(item.requested_qty),
          target_price: item.target_price === '' || item.target_price == null ? null : Number(item.target_price),
          notes: item.notes || null,
        })),
      }),
    onSuccess: (created) => {
      setLastEnquiry(created.id)
      toast.success('Enquiry created')
      navigate(`/enquiries/${created.id}`)
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  if (customersQuery.isLoading || productsQuery.isLoading) {
    return <LoadingState message="Loading creation form..." />
  }

  if (customersQuery.isError || productsQuery.isError) {
    const message = toApiClientError(customersQuery.error ?? productsQuery.error).message
    return <ErrorState message={message} onRetry={() => void customersQuery.refetch()} />
  }

  const customers = customersQuery.data ?? []
  const products = productsQuery.data ?? []

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create Enquiry</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit((values) => createMutation.mutate(values))}>
          <div className="grid gap-3 md:grid-cols-3">
            <FormField label="Customer" error={form.formState.errors.customer_id?.message}>
              <Select {...form.register('customer_id')}>
                <option value="">Select customer</option>
                {customers.map((row) => (
                  <option key={row.id} value={row.id}>
                    {row.name}
                  </option>
                ))}
              </Select>
            </FormField>
            <FormField label="Received Date">
              <Input type="date" {...form.register('received_date')} />
            </FormField>
            <FormField label="Currency" error={form.formState.errors.currency?.message}>
              <Input {...form.register('currency')} maxLength={3} />
            </FormField>
          </div>

          <FormField label="Notes">
            <Textarea {...form.register('notes')} placeholder="Customer requirement summary" />
          </FormField>

          <div className="space-y-3 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-slate-800">Items</h4>
              <Button
                variant="secondary"
                size="sm"
                type="button"
                onClick={() =>
                  itemArray.append({
                    product_id: '',
                    requested_qty: '1',
                    target_price: '',
                    notes: '',
                  })
                }
              >
                Add Item
              </Button>
            </div>

            {itemArray.fields.map((field, index) => (
              <div key={field.id} className="grid gap-2 rounded-md border border-slate-100 p-3 md:grid-cols-5">
                <FormField
                  label="Product"
                  error={form.formState.errors.items?.[index]?.product_id?.message}
                >
                  <Select {...form.register(`items.${index}.product_id`)}>
                    <option value="">Select product</option>
                    {products.map((row) => (
                      <option key={row.id} value={row.id}>
                        {row.name} ({row.sku})
                      </option>
                    ))}
                  </Select>
                </FormField>
                <FormField
                  label="Qty"
                  error={form.formState.errors.items?.[index]?.requested_qty?.message}
                >
                  <Input type="number" min="0" step="0.01" {...form.register(`items.${index}.requested_qty`)} />
                </FormField>
                <FormField
                  label="Target Price"
                  error={form.formState.errors.items?.[index]?.target_price?.message}
                >
                  <Input type="number" min="0" step="0.01" {...form.register(`items.${index}.target_price`)} />
                </FormField>
                <FormField label="Notes">
                  <Input {...form.register(`items.${index}.notes`)} />
                </FormField>
                <div className="flex items-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    type="button"
                    disabled={itemArray.fields.length === 1}
                    onClick={() => itemArray.remove(index)}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
            <p className="text-xs text-rose-700">{form.formState.errors.items?.message}</p>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" type="button" onClick={() => navigate('/enquiries')}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Enquiry'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
