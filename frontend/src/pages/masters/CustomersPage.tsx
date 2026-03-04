import * as React from 'react'
import type { ReactNode } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { z } from 'zod'

import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/page-state'
import { Badge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { FormField } from '../../components/ui/form-field'
import { Input } from '../../components/ui/input'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { useAuth } from '../../context/AuthContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'

const createSchema = z.object({
  code: z.string().min(1, 'Code is required'),
  name: z.string().min(1, 'Name is required'),
  country: z.string().min(1, 'Country is required'),
  contactEmail: z.string().email('Invalid email').optional().or(z.literal('')),
  contactPhone: z.string().optional(),
  is_active: z.boolean(),
})

const updateSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  country: z.string().min(1, 'Country is required'),
  contactEmail: z.string().email('Invalid email').optional().or(z.literal('')),
  contactPhone: z.string().optional(),
  is_active: z.boolean(),
})

type CreateForm = z.infer<typeof createSchema>
type UpdateForm = z.infer<typeof updateSchema>

const queryKey = ['masters', 'customers'] as const

export function CustomersPage(): ReactNode {
  const queryClient = useQueryClient()
  const { hasRole } = useAuth()
  const canWrite = hasRole('Admin', 'SuperAdmin')

  const [selectedId, setSelectedId] = React.useState<string | null>(null)

  const listQuery = useQuery({
    queryKey,
    queryFn: () => api.masters.listCustomers({ limit: 500 }),
  })

  const customers = listQuery.data ?? []
  const selected = customers.find((item) => item.id === selectedId) ?? null

  const createForm = useForm<CreateForm>({
    resolver: zodResolver(createSchema),
    defaultValues: {
      code: '',
      name: '',
      country: '',
      contactEmail: '',
      contactPhone: '',
      is_active: true,
    },
  })

  const updateForm = useForm<UpdateForm>({
    resolver: zodResolver(updateSchema),
    defaultValues: {
      name: '',
      country: '',
      contactEmail: '',
      contactPhone: '',
      is_active: true,
    },
  })

  React.useEffect(() => {
    if (!selected) {
      return
    }
    updateForm.reset({
      name: selected.name,
      country: selected.country,
      contactEmail: String(selected.contact_fields.contact_email ?? ''),
      contactPhone: String(selected.contact_fields.contact_phone ?? ''),
      is_active: selected.is_active,
    })
  }, [selected, updateForm])

  const createMutation = useMutation({
    mutationFn: (values: CreateForm) =>
      api.masters.createCustomer({
        code: values.code.trim(),
        name: values.name.trim(),
        country: values.country.trim(),
        is_active: values.is_active,
        contact_fields: {
          contact_email: values.contactEmail?.trim() || null,
          contact_phone: values.contactPhone?.trim() || null,
        },
      }),
    onSuccess: (created) => {
      toast.success('Customer created')
      createForm.reset()
      setSelectedId(created.id)
      void queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => {
      toast.error(toApiClientError(error).message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: (values: UpdateForm) => {
      if (!selected) {
        throw new Error('No customer selected')
      }
      return api.masters.updateCustomer(selected.id, {
        name: values.name.trim(),
        country: values.country.trim(),
        is_active: values.is_active,
        contact_fields: {
          contact_email: values.contactEmail?.trim() || null,
          contact_phone: values.contactPhone?.trim() || null,
        },
      })
    },
    onSuccess: () => {
      toast.success('Customer updated')
      void queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => {
      toast.error(toApiClientError(error).message)
    },
  })

  if (listQuery.isLoading) {
    return <LoadingState message="Loading customers..." />
  }

  if (listQuery.isError) {
    return <ErrorState message={toApiClientError(listQuery.error).message} onRetry={() => void listQuery.refetch()} />
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Customers</CardTitle>
        </CardHeader>
        <CardContent>
          {customers.length === 0 ? (
            <EmptyState
              title="No customers yet"
              subtitle="Create your first customer record to start the enquiry process."
            />
          ) : (
            <TableContainer>
              <Table>
                <thead>
                  <tr>
                    <Th>Code</Th>
                    <Th>Name</Th>
                    <Th>Country</Th>
                    <Th>Status</Th>
                  </tr>
                </thead>
                <tbody>
                  {customers.map((customer) => (
                    <tr
                      key={customer.id}
                      className={`cursor-pointer ${customer.id === selectedId ? 'bg-slate-50' : 'hover:bg-slate-50/70'}`}
                      onClick={() => setSelectedId(customer.id)}
                    >
                      <Td className="font-medium">{customer.code}</Td>
                      <Td>{customer.name}</Td>
                      <Td>{customer.country}</Td>
                      <Td>
                        <Badge value={customer.is_active ? 'ACTIVE' : 'INACTIVE'} />
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <div className="space-y-4">
        {canWrite ? (
          <Card>
            <CardHeader>
              <CardTitle>Create Customer</CardTitle>
            </CardHeader>
            <CardContent>
              <form
                className="space-y-3"
                onSubmit={createForm.handleSubmit((values) => createMutation.mutate(values))}
              >
                <FormField label="Code" error={createForm.formState.errors.code?.message}>
                  <Input {...createForm.register('code')} placeholder="CUST001" />
                </FormField>
                <FormField label="Name" error={createForm.formState.errors.name?.message}>
                  <Input {...createForm.register('name')} placeholder="Acme Pharma" />
                </FormField>
                <FormField label="Country" error={createForm.formState.errors.country?.message}>
                  <Input {...createForm.register('country')} placeholder="India" />
                </FormField>
                <FormField label="Contact Email" error={createForm.formState.errors.contactEmail?.message}>
                  <Input {...createForm.register('contactEmail')} placeholder="ops@example.com" />
                </FormField>
                <FormField label="Contact Phone">
                  <Input {...createForm.register('contactPhone')} placeholder="+91..." />
                </FormField>
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input type="checkbox" {...createForm.register('is_active')} />
                  Active
                </label>
                <Button className="w-full" type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create'}
                </Button>
              </form>
            </CardContent>
          </Card>
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle>Customer Details</CardTitle>
          </CardHeader>
          <CardContent>
            {!selected ? (
              <p className="text-sm text-slate-500">Select a customer from the list to view details.</p>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  <span className="font-medium text-slate-800">Code:</span> {selected.code}
                </p>
                <p className="text-sm text-slate-600">
                  <span className="font-medium text-slate-800">Email:</span>{' '}
                  {String(selected.contact_fields.contact_email ?? '-')}
                </p>
                <p className="text-sm text-slate-600">
                  <span className="font-medium text-slate-800">Phone:</span>{' '}
                  {String(selected.contact_fields.contact_phone ?? '-')}
                </p>
                {canWrite ? (
                  <form
                    className="space-y-3 border-t border-slate-100 pt-3"
                    onSubmit={updateForm.handleSubmit((values) => updateMutation.mutate(values))}
                  >
                    <FormField label="Name" error={updateForm.formState.errors.name?.message}>
                      <Input {...updateForm.register('name')} />
                    </FormField>
                    <FormField label="Country" error={updateForm.formState.errors.country?.message}>
                      <Input {...updateForm.register('country')} />
                    </FormField>
                    <FormField
                      label="Contact Email"
                      error={updateForm.formState.errors.contactEmail?.message}
                    >
                      <Input {...updateForm.register('contactEmail')} />
                    </FormField>
                    <FormField label="Contact Phone">
                      <Input {...updateForm.register('contactPhone')} />
                    </FormField>
                    <label className="flex items-center gap-2 text-sm text-slate-700">
                      <input type="checkbox" {...updateForm.register('is_active')} />
                      Active
                    </label>
                    <Button className="w-full" type="submit" disabled={updateMutation.isPending}>
                      {updateMutation.isPending ? 'Saving...' : 'Update'}
                    </Button>
                  </form>
                ) : null}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
