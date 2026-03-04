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
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { useAuth } from '../../context/AuthContext'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'

const schema = z.object({
  sku: z.string().min(1, 'SKU is required'),
  name: z.string().min(1, 'Name is required'),
  manufacturer_id: z.string().uuid('Manufacturer is required'),
  unit: z.string().min(1, 'Unit is required'),
  is_active: z.boolean(),
})

type CreateForm = z.infer<typeof schema>
type UpdateForm = Omit<CreateForm, 'sku'>

const productsKey = ['masters', 'products'] as const
const manufacturersKey = ['masters', 'manufacturers'] as const

export function ProductsPage(): ReactNode {
  const queryClient = useQueryClient()
  const { hasRole } = useAuth()
  const canWrite = hasRole('Admin', 'SuperAdmin')

  const [selectedId, setSelectedId] = React.useState<string | null>(null)

  const productsQuery = useQuery({
    queryKey: productsKey,
    queryFn: () => api.masters.listProducts({ limit: 500 }),
  })
  const manufacturersQuery = useQuery({
    queryKey: manufacturersKey,
    queryFn: () => api.masters.listManufacturers({ limit: 500 }),
  })

  const manufacturers = React.useMemo(() => manufacturersQuery.data ?? [], [manufacturersQuery.data])
  const manufacturerMap = React.useMemo(
    () => new Map(manufacturers.map((row) => [row.id, row.name])),
    [manufacturers],
  )

  const selected = (productsQuery.data ?? []).find((row) => row.id === selectedId) ?? null

  const createForm = useForm<CreateForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      sku: '',
      name: '',
      manufacturer_id: '',
      unit: 'EA',
      is_active: true,
    },
  })

  const updateForm = useForm<UpdateForm>({
    resolver: zodResolver(schema.omit({ sku: true })),
    defaultValues: {
      name: '',
      manufacturer_id: '',
      unit: 'EA',
      is_active: true,
    },
  })

  React.useEffect(() => {
    if (!selected) {
      return
    }
    updateForm.reset({
      name: selected.name,
      manufacturer_id: selected.manufacturer_id,
      unit: selected.unit,
      is_active: selected.is_active,
    })
  }, [selected, updateForm])

  const createMutation = useMutation({
    mutationFn: (values: CreateForm) => api.masters.createProduct(values),
    onSuccess: (created) => {
      toast.success('Product created')
      createForm.reset({
        sku: '',
        name: '',
        manufacturer_id: '',
        unit: 'EA',
        is_active: true,
      })
      setSelectedId(created.id)
      void queryClient.invalidateQueries({ queryKey: productsKey })
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const updateMutation = useMutation({
    mutationFn: (values: UpdateForm) => {
      if (!selected) {
        throw new Error('No product selected')
      }
      return api.masters.updateProduct(selected.id, values)
    },
    onSuccess: () => {
      toast.success('Product updated')
      void queryClient.invalidateQueries({ queryKey: productsKey })
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  if (productsQuery.isLoading || manufacturersQuery.isLoading) {
    return <LoadingState message="Loading products..." />
  }

  if (productsQuery.isError || manufacturersQuery.isError) {
    const message = toApiClientError(productsQuery.error ?? manufacturersQuery.error).message
    return <ErrorState message={message} onRetry={() => void productsQuery.refetch()} />
  }

  const rows = productsQuery.data ?? []

  return (
    <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Products</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length === 0 ? (
            <EmptyState
              title="No products"
              subtitle="Create products to enable enquiry items and quotations."
            />
          ) : (
            <TableContainer>
              <Table>
                <thead>
                  <tr>
                    <Th>SKU</Th>
                    <Th>Name</Th>
                    <Th>Manufacturer</Th>
                    <Th>Unit</Th>
                    <Th>Status</Th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr
                      key={row.id}
                      className={`cursor-pointer ${selectedId === row.id ? 'bg-slate-50' : 'hover:bg-slate-50/70'}`}
                      onClick={() => setSelectedId(row.id)}
                    >
                      <Td className="font-medium">{row.sku}</Td>
                      <Td>{row.name}</Td>
                      <Td>{manufacturerMap.get(row.manufacturer_id) ?? row.manufacturer_id}</Td>
                      <Td>{row.unit}</Td>
                      <Td>
                        <Badge value={row.is_active ? 'ACTIVE' : 'INACTIVE'} />
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
              <CardTitle>Create Product</CardTitle>
            </CardHeader>
            <CardContent>
              <form
                className="space-y-3"
                onSubmit={createForm.handleSubmit((values) => createMutation.mutate(values))}
              >
                <FormField label="SKU" error={createForm.formState.errors.sku?.message}>
                  <Input {...createForm.register('sku')} placeholder="SKU-001" />
                </FormField>
                <FormField label="Name" error={createForm.formState.errors.name?.message}>
                  <Input {...createForm.register('name')} placeholder="Paracetamol 500mg" />
                </FormField>
                <FormField
                  label="Manufacturer"
                  error={createForm.formState.errors.manufacturer_id?.message}
                >
                  <Select {...createForm.register('manufacturer_id')}>
                    <option value="">Select manufacturer</option>
                    {manufacturers.map((row) => (
                      <option key={row.id} value={row.id}>
                        {row.name}
                      </option>
                    ))}
                  </Select>
                </FormField>
                <FormField label="Unit" error={createForm.formState.errors.unit?.message}>
                  <Input {...createForm.register('unit')} placeholder="EA" />
                </FormField>
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input type="checkbox" {...createForm.register('is_active')} /> Active
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
            <CardTitle>Product Details</CardTitle>
          </CardHeader>
          <CardContent>
            {!selected ? (
              <p className="text-sm text-slate-500">Select a product to inspect and update.</p>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  <span className="font-medium text-slate-800">SKU:</span> {selected.sku}
                </p>
                {canWrite ? (
                  <form
                    className="space-y-3 border-t border-slate-100 pt-3"
                    onSubmit={updateForm.handleSubmit((values) => updateMutation.mutate(values))}
                  >
                    <FormField label="Name" error={updateForm.formState.errors.name?.message}>
                      <Input {...updateForm.register('name')} />
                    </FormField>
                    <FormField
                      label="Manufacturer"
                      error={updateForm.formState.errors.manufacturer_id?.message}
                    >
                      <Select {...updateForm.register('manufacturer_id')}>
                        <option value="">Select manufacturer</option>
                        {manufacturers.map((row) => (
                          <option key={row.id} value={row.id}>
                            {row.name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                    <FormField label="Unit" error={updateForm.formState.errors.unit?.message}>
                      <Input {...updateForm.register('unit')} />
                    </FormField>
                    <label className="flex items-center gap-2 text-sm text-slate-700">
                      <input type="checkbox" {...updateForm.register('is_active')} /> Active
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
