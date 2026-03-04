import {
  createContext,
  useContext,
  useMemo,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from 'react'

import {
  loadWorkflowState,
  recordCustomerPO,
  recordDelivery,
  recordInvoice,
  recordRTMPO,
  saveWorkflowState,
} from '../lib/workflow-storage'
import type { CustomerPO, Delivery, Invoice, RTMPO, WorkflowState } from '../types/api'

interface WorkflowContextValue {
  workflow: WorkflowState
  setWorkflow: Dispatch<SetStateAction<WorkflowState>>
  setLastEnquiry: (enquiryId: string) => void
  setQuotationRevision: (quotationId: string, revisionId: string) => void
  addCustomerPO: (customerPO: CustomerPO) => void
  addRTMPO: (rtmPO: RTMPO) => void
  addInvoice: (invoice: Invoice) => void
  addDelivery: (delivery: Delivery) => void
}

const WorkflowContext = createContext<WorkflowContextValue | undefined>(undefined)

export function WorkflowProvider({ children }: { children: ReactNode }): ReactNode {
  const [workflow, setWorkflow] = useState<WorkflowState>(() => loadWorkflowState())

  const setAndPersist: Dispatch<SetStateAction<WorkflowState>> = (value) => {
    setWorkflow((previous) => {
      const next = typeof value === 'function' ? value(previous) : value
      saveWorkflowState(next)
      return next
    })
  }

  const value = useMemo<WorkflowContextValue>(
    () => ({
      workflow,
      setWorkflow: setAndPersist,
      setLastEnquiry: (enquiryId) => {
        setAndPersist((prev) => ({ ...prev, lastEnquiryId: enquiryId }))
      },
      setQuotationRevision: (quotationId, revisionId) => {
        setAndPersist((prev) => ({
          ...prev,
          lastQuotationId: quotationId,
          revisionByQuotation: {
            ...prev.revisionByQuotation,
            [quotationId]: revisionId,
          },
        }))
      },
      addCustomerPO: (customerPO) => {
        setAndPersist((prev) => recordCustomerPO(prev, customerPO))
      },
      addRTMPO: (rtmPO) => {
        setAndPersist((prev) => recordRTMPO(prev, rtmPO))
      },
      addInvoice: (invoice) => {
        setAndPersist((prev) => recordInvoice(prev, invoice))
      },
      addDelivery: (delivery) => {
        setAndPersist((prev) => recordDelivery(prev, delivery))
      },
    }),
    [workflow],
  )

  return <WorkflowContext.Provider value={value}>{children}</WorkflowContext.Provider>
}

export function useWorkflow(): WorkflowContextValue {
  const context = useContext(WorkflowContext)
  if (!context) {
    throw new Error('useWorkflow must be used inside WorkflowProvider')
  }
  return context
}
