export interface ApiErrorPayload {
  error: {
    code: string
    message: string
    request_id: string
    details: unknown
  }
}

export interface UserInfo {
  id: string
  username: string
  email: string
  is_active: boolean
  roles: string[]
}

export interface TokenPairResponse {
  access_token: string
  refresh_token: string
  token_type: string
  access_token_expires_at: string
  user: UserInfo
}

export interface MessageResponse {
  message: string
}

export interface Customer {
  id: string
  code: string
  name: string
  country: string
  contact_fields: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CustomerPayload {
  code: string
  name: string
  country: string
  contact_fields: Record<string, unknown>
  is_active: boolean
}

export interface Manufacturer {
  id: string
  code: string
  name: string
  country: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ManufacturerPayload {
  code: string
  name: string
  country: string
  is_active: boolean
}

export interface Product {
  id: string
  sku: string
  name: string
  manufacturer_id: string
  unit: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductPayload {
  sku: string
  name: string
  manufacturer_id: string
  unit: string
  is_active: boolean
}

export interface ImportErrorRow {
  row_number: number
  error: string
  payload: Record<string, unknown>
}

export interface ImportSummary {
  entity: string
  total_rows: number
  created_count: number
  updated_count: number
  error_count: number
  errors: ImportErrorRow[]
}

export interface EnquiryItem {
  id: string
  product_id: string
  requested_qty: number | string
  target_price: number | string | null
  notes: string | null
  created_at: string
}

export interface Enquiry {
  id: string
  enquiry_no: string
  customer_id: string
  owner_user_id: string
  status: string
  received_date: string
  currency: string
  notes: string | null
  created_at: string
  updated_at: string
  items: EnquiryItem[]
}

export interface EnquiryItemCreatePayload {
  product_id: string
  requested_qty: number
  target_price?: number | null
  notes?: string | null
}

export interface EnquiryCreatePayload {
  customer_id: string
  received_date?: string | null
  currency: string
  notes?: string | null
  items: EnquiryItemCreatePayload[]
}

export interface EnquiryStatusHistory {
  id: string
  enquiry_id: string
  from_status: string | null
  to_status: string
  changed_by: string
  changed_at: string
  comment: string | null
}

export interface Quotation {
  id: string
  enquiry_id: string
  quotation_no: string
  current_revision_no: number
  status: string
  created_at: string
  updated_at: string
}

export interface QuotationItem {
  id: string
  revision_id: string
  enquiry_item_id: string | null
  product_id: string
  qty: number | string
  unit_price: number | string
  line_total: number | string
  notes: string | null
}

export interface Approval {
  id: string
  revision_id: string
  step_name: string
  decision: string
  decided_by: string | null
  decided_at: string | null
  remarks: string | null
  created_at: string
}

export interface QuotationRevision {
  id: string
  quotation_id: string
  revision_no: number
  freight: number | string
  markup_percent: number | string
  subtotal: number | string
  total: number | string
  currency: string
  submitted_at: string | null
  approved_at: string | null
  rejected_at: string | null
  created_by: string
  created_at: string
  items: QuotationItem[]
  approvals: Approval[]
}

export interface QuotationDetail extends Quotation {
  revisions: QuotationRevision[]
}

export interface QuotationRevisionCreatePayload {
  freight: number
  markup_percent: number
  currency: string
  items: {
    product_id: string
    qty: number
    unit_price: number
    enquiry_item_id?: string | null
    notes?: string | null
  }[]
}

export interface CustomerPO {
  id: string
  po_no: string
  enquiry_id: string
  quotation_revision_id: string
  customer_id: string
  po_date: string
  total_amount: number | string
  status: string
  created_at: string
  updated_at: string
}

export interface RTMPO {
  id: string
  po_no: string
  enquiry_id: string
  quotation_revision_id: string
  manufacturer_id: string | null
  po_date: string
  total_amount: number | string
  status: string
  created_at: string
  updated_at: string
}

export interface Payment {
  id: string
  invoice_id: string
  payment_date: string
  amount: number | string
  method: string
  reference_no: string | null
  notes: string | null
  created_at: string
}

export interface Invoice {
  id: string
  invoice_no: string
  enquiry_id: string
  customer_po_id: string | null
  issue_date: string
  due_date: string | null
  currency: string
  total_amount: number | string
  status: string
  created_at: string
  updated_at: string
  payments: Payment[]
}

export interface DeliveryEvent {
  id: string
  delivery_id: string
  event_type: string
  event_time: string
  location: string | null
  details_jsonb: Record<string, unknown>
  created_by: string | null
  created_at: string
}

export interface Delivery {
  id: string
  enquiry_id: string
  invoice_id: string | null
  shipment_no: string | null
  courier_name: string | null
  tracking_no: string | null
  shipped_at: string | null
  expected_delivery_at: string | null
  delivered_at: string | null
  status: string
  created_at: string
  updated_at: string
  events: DeliveryEvent[]
}

export interface KPIReport {
  window: {
    date_from: string | null
    date_to: string | null
  }
  enquiry_counts_by_status: Array<{ status: string; count: number }>
  quotation_approval: {
    approved_count: number
    decided_count: number
    approval_rate: number
  }
  po_conversion: {
    enquiries_with_po: number
    total_enquiries: number
    conversion_rate: number
  }
  invoice_collection: {
    invoiced_total: number | string
    collected_total: number | string
    outstanding_total: number | string
  }
  delivery_completion: {
    delivered_count: number
    total_deliveries: number
    completion_rate: number
  }
}

export interface WorkflowState {
  lastEnquiryId?: string
  lastQuotationId?: string
  revisionByQuotation: Record<string, string>
  customerPOs: CustomerPO[]
  rtmPOs: RTMPO[]
  invoices: Invoice[]
  deliveries: Delivery[]
}
