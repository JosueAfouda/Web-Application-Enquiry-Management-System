import { format } from 'date-fns'

export function asNumber(value: string | number | null | undefined): number {
  if (value == null) {
    return 0
  }
  const numeric = typeof value === 'string' ? Number(value) : value
  return Number.isFinite(numeric) ? numeric : 0
}

export function formatDate(value: string | null | undefined, includeTime = false): string {
  if (!value) {
    return '-'
  }
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return includeTime ? format(parsed, 'yyyy-MM-dd HH:mm') : format(parsed, 'yyyy-MM-dd')
}

export function formatMoney(value: string | number | null | undefined, currency = 'USD'): string {
  const numeric = asNumber(value)
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numeric)
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

export function formatRole(role: string): string {
  return role.replace(/([a-z])([A-Z])/g, '$1 $2')
}
