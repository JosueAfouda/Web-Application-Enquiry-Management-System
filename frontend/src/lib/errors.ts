import axios from 'axios'

import type { ApiErrorPayload } from '../types/api'

export class ApiClientError extends Error {
  readonly status: number
  readonly code: string
  readonly requestId: string
  readonly details: unknown

  constructor(params: {
    status: number
    code: string
    message: string
    requestId: string
    details: unknown
  }) {
    super(params.message)
    this.name = 'ApiClientError'
    this.status = params.status
    this.code = params.code
    this.requestId = params.requestId
    this.details = params.details
  }
}

function isApiErrorPayload(payload: unknown): payload is ApiErrorPayload {
  if (typeof payload !== 'object' || payload === null) {
    return false
  }
  const candidate = payload as Partial<ApiErrorPayload>
  return typeof candidate.error?.code === 'string' && typeof candidate.error?.message === 'string'
}

export function toApiClientError(error: unknown): ApiClientError {
  if (error instanceof ApiClientError) {
    return error
  }

  if (axios.isAxiosError(error)) {
    const status = error.response?.status ?? 500
    const payload = error.response?.data
    if (isApiErrorPayload(payload)) {
      return new ApiClientError({
        status,
        code: payload.error.code,
        message: payload.error.message,
        requestId: payload.error.request_id,
        details: payload.error.details,
      })
    }

    return new ApiClientError({
      status,
      code: `http_${status}`,
      message: error.message || 'Request failed',
      requestId: error.response?.headers?.['x-request-id'] ?? 'unknown',
      details: payload,
    })
  }

  const message = error instanceof Error ? error.message : 'Unexpected error'
  return new ApiClientError({
    status: 500,
    code: 'unknown_error',
    message,
    requestId: 'unknown',
    details: null,
  })
}

export function extractErrorMessage(error: unknown): string {
  return toApiClientError(error).message
}
