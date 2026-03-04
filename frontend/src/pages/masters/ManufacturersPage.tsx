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

const schema = z.object({
  code: z.string().min(1, 'Code is required'),
  name: z.string().min(1, 'Name is required'),
  country: z.string().min(1, 'Country is required'),
  is_active: z.boolean(),
})

type FormValues = z.infer<typeof schema>

const queryKey = ['masters', 'manufacturers'] as const

export function ManufacturersPage(): ReactNode {
  const queryClient = useQueryClient()
  const { hasRole } = useAuth()
  const canWrite = hasRole('Admin', 'SuperAdmin')

  const [selectedId, setSelectedId] = React.useState<string | null>(null)

  const listQuery = useQuery({
    queryKey,
    queryFn: () => api.masters.listManufacturers({ limit: 500 }),
  })

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      code: '',
      name: '',
      country: '',
      is_active: true,
    },
  })

  const updateForm = useForm<Omit<FormValues, 'code'>>({
    resolver: zodResolver(schema.omit({ code: true })),
    defaultValues: {
      name: '',
      country: '',
      is_active: true,
    },
  })

  const selected = (listQuery.data ?? []).find((row) => row.id === selectedId) ?? null

  React.useEffect(() => {
    if (!selected) {
      return
    }
    updateForm.reset({
      name: selected.name,
      country: selected.country,
      is_active: selected.is_active,
    })
  }, [selected, updateForm])

  const createMutation = useMutation({
    mutationFn: (values: FormValues) =>
      api.masters.createManufacturer({
        code: values.code.trim(),
        name: values.name.trim(),
        country: values.country.trim(),
        is_active: values.is_active,
      }),
    onSuccess: (created) => {
      toast.success('Manufacturer created')
      form.reset()
      setSelectedId(created.id)
      void queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  const updateMutation = useMutation({
    mutationFn: (values: Omit<FormValues, 'code'>) => {
      if (!selected) {
        throw new Error('No manufacturer selected')
      }
      return api.masters.updateManufacturer(selected.id, values)
    },
    onSuccess: () => {
      toast.success('Manufacturer updated')
      void queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => toast.error(toApiClientError(error).message),
  })

  if (listQuery.isLoading) {
    return <LoadingState message="Loading manufacturers..." />
  }

  if (listQuery.isError) {
    return <ErrorState message={toApiClientError(listQuery.error).message} onRetry={() => void listQuery.refetch()} />
  }

  const rows = listQuery.data ?? []

  return (
    <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Manufacturers</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length === 0 ? (
            <EmptyState title="No manufacturers" subtitle="Create a manufacturer to build the product catalog." />
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
                  {rows.map((row) => (
                    <tr
                      key={row.id}
                      className={`cursor-pointer ${selectedId === row.id ? 'bg-slate-50' : 'hover:bg-slate-50/70'}`}
                      onClick={() => setSelectedId(row.id)}
                    >
                      <Td className="font-medium">{row.code}</Td>
                      <Td>{row.name}</Td>
                      <Td>{row.country}</Td>
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
              <CardTitle>Create Manufacturer</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-3" onSubmit={form.handleSubmit((values) => createMutation.mutate(values))}>
                <FormField label="Code" error={form.formState.errors.code?.message}>
                  <Input {...form.register('code')} placeholder="MFG001" />
                </FormField>
                <FormField label="Name" error={form.formState.errors.name?.message}>
                  <Input {...form.register('name')} placeholder="Sunrise Labs" />
                </FormField>
                <FormField label="Country" error={form.formState.errors.country?.message}>
                  <Input {...form.register('country')} placeholder="India" />
                </FormField>
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input type="checkbox" {...form.register('is_active')} /> Active
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
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent>
            {!selected ? (
              <p className="text-sm text-slate-500">Select a row to view details.</p>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  <span className="font-medium text-slate-800">Code:</span> {selected.code}
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
