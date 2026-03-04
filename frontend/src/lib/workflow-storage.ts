import type { CustomerPO, Delivery, Invoice, RTMPO, WorkflowState } from '../types/api'

const WORKFLOW_STORAGE_KEY = 'ems.workflow'

const defaultState: WorkflowState = {
  revisionByQuotation: {},
  customerPOs: [],
  rtmPOs: [],
  invoices: [],
  deliveries: [],
}

export function loadWorkflowState(): WorkflowState {
  const raw = localStorage.getItem(WORKFLOW_STORAGE_KEY)
  if (!raw) {
    return defaultState
  }

  try {
    const state = JSON.parse(raw) as WorkflowState
    return {
      ...defaultState,
      ...state,
      revisionByQuotation: state.revisionByQuotation ?? {},
      customerPOs: state.customerPOs ?? [],
      rtmPOs: state.rtmPOs ?? [],
      invoices: state.invoices ?? [],
      deliveries: state.deliveries ?? [],
    }
  } catch {
    return defaultState
  }
}

export function saveWorkflowState(state: WorkflowState): void {
  localStorage.setItem(WORKFLOW_STORAGE_KEY, JSON.stringify(state))
}

function upsertById<T extends { id: string }>(items: T[], value: T): T[] {
  const index = items.findIndex((item) => item.id === value.id)
  if (index === -1) {
    return [value, ...items]
  }
  const next = [...items]
  next[index] = value
  return next
}

export function recordCustomerPO(state: WorkflowState, customerPO: CustomerPO): WorkflowState {
  return {
    ...state,
    customerPOs: upsertById(state.customerPOs, customerPO),
  }
}

export function recordRTMPO(state: WorkflowState, rtmPO: RTMPO): WorkflowState {
  return {
    ...state,
    rtmPOs: upsertById(state.rtmPOs, rtmPO),
  }
}

export function recordInvoice(state: WorkflowState, invoice: Invoice): WorkflowState {
  return {
    ...state,
    invoices: upsertById(state.invoices, invoice),
  }
}

export function recordDelivery(state: WorkflowState, delivery: Delivery): WorkflowState {
  return {
    ...state,
    deliveries: upsertById(state.deliveries, delivery),
  }
}
