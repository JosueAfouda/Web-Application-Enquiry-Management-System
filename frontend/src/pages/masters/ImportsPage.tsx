import * as React from 'react'
import type { ReactNode } from 'react'

import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'

import { EmptyState } from '../../components/feedback/page-state'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Select } from '../../components/ui/select'
import { Table, TableContainer, Td, Th } from '../../components/ui/table'
import { api } from '../../lib/api'
import { toApiClientError } from '../../lib/errors'
import type { ImportSummary } from '../../types/api'

type ImportEntity = 'customers' | 'manufacturers' | 'products'

export function ImportsPage(): ReactNode {
  const [entity, setEntity] = React.useState<ImportEntity>('customers')
  const [file, setFile] = React.useState<File | null>(null)
  const [summary, setSummary] = React.useState<ImportSummary | null>(null)

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) {
        throw new Error('Select a file first')
      }
      if (entity === 'customers') {
        return api.masters.importCustomers(file)
      }
      if (entity === 'manufacturers') {
        return api.masters.importManufacturers(file)
      }
      return api.masters.importProducts(file)
    },
    onSuccess: (result) => {
      setSummary(result)
      toast.success('Import processed successfully')
    },
    onError: (error) => {
      toast.error(toApiClientError(error).message)
    },
  })

  return (
    <div className="grid gap-4 xl:grid-cols-[1.2fr_2fr]">
      <Card>
        <CardHeader>
          <CardTitle>Excel Import</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <label className="grid gap-1 text-sm text-slate-700">
            <span className="font-medium">Master Type</span>
            <Select value={entity} onChange={(event) => setEntity(event.target.value as ImportEntity)}>
              <option value="customers">Customers</option>
              <option value="manufacturers">Manufacturers</option>
              <option value="products">Products</option>
            </Select>
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            <span className="font-medium">Excel File (.xlsx, .xls, .csv)</span>
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="rounded-md border border-slate-200 px-3 py-2 text-sm"
            />
          </label>
          <Button className="w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending || !file}>
            {mutation.isPending ? 'Uploading...' : 'Upload and Process'}
          </Button>
          <p className="text-xs text-slate-500">
            Required columns depend on entity: customer/manufacturer codes, product SKU and manufacturer code.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Import Result</CardTitle>
        </CardHeader>
        <CardContent>
          {!summary ? (
            <EmptyState
              title="No import executed"
              subtitle="Upload a file to see created, updated, and error rows."
            />
          ) : (
            <div className="space-y-4">
              <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                <Stat label="Rows" value={summary.total_rows} />
                <Stat label="Created" value={summary.created_count} />
                <Stat label="Updated" value={summary.updated_count} />
                <Stat label="Errors" value={summary.error_count} />
              </div>

              {summary.errors.length > 0 ? (
                <TableContainer>
                  <Table>
                    <thead>
                      <tr>
                        <Th>Row</Th>
                        <Th>Error</Th>
                        <Th>Payload</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.errors.map((row, index) => (
                        <tr key={`${row.row_number}-${index}`}>
                          <Td>{row.row_number}</Td>
                          <Td>{row.error}</Td>
                          <Td>
                            <code className="text-xs">{JSON.stringify(row.payload)}</code>
                          </Td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </TableContainer>
              ) : (
                <p className="text-sm text-emerald-700">No row errors reported.</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }): ReactNode {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-lg font-semibold text-slate-900">{value}</p>
    </div>
  )
}
