import { http } from './http'
import type {
  Customer,
  CustomerPO,
  CustomerPayload,
  Delivery,
  DeliveryEvent,
  Enquiry,
  EnquiryCreatePayload,
  EnquiryStatusHistory,
  ImportSummary,
  Invoice,
  KPIReport,
  Manufacturer,
  ManufacturerPayload,
  MessageResponse,
  Payment,
  Product,
  ProductPayload,
  Quotation,
  QuotationDetail,
  QuotationRevision,
  QuotationRevisionCreatePayload,
  RTMPO,
  TokenPairResponse,
  UserInfo,
} from '../types/api'

interface ListQuery {
  offset?: number
  limit?: number
}

interface DateWindowQuery {
  date_from?: string
  date_to?: string
}

export interface AuthLoginPayload {
  username: string
  password: string
}

export const api = {
  system: {
    async health(): Promise<{ status: string }> {
      const { data } = await http.get<{ status: string }>('/health')
      return data
    },
  },
  auth: {
    async login(payload: AuthLoginPayload): Promise<TokenPairResponse> {
      const { data } = await http.post<TokenPairResponse>('/auth/login', payload)
      return data
    },
    async refresh(refreshToken: string): Promise<TokenPairResponse> {
      const { data } = await http.post<TokenPairResponse>('/auth/refresh', {
        refresh_token: refreshToken,
      })
      return data
    },
    async logout(refreshToken: string): Promise<MessageResponse> {
      const { data } = await http.post<MessageResponse>('/auth/logout', {
        refresh_token: refreshToken,
      })
      return data
    },
    async me(): Promise<UserInfo> {
      const { data } = await http.get<UserInfo>('/auth/me')
      return data
    },
  },
  masters: {
    async listCustomers(query: ListQuery = {}): Promise<Customer[]> {
      const { data } = await http.get<Customer[]>('/customers', { params: query })
      return data
    },
    async createCustomer(payload: CustomerPayload): Promise<Customer> {
      const { data } = await http.post<Customer>('/customers', payload)
      return data
    },
    async updateCustomer(customerId: string, payload: Partial<CustomerPayload>): Promise<Customer> {
      const { data } = await http.put<Customer>(`/customers/${customerId}`, payload)
      return data
    },
    async getCustomer(customerId: string): Promise<Customer> {
      const { data } = await http.get<Customer>(`/customers/${customerId}`)
      return data
    },

    async listManufacturers(query: ListQuery = {}): Promise<Manufacturer[]> {
      const { data } = await http.get<Manufacturer[]>('/manufacturers', { params: query })
      return data
    },
    async createManufacturer(payload: ManufacturerPayload): Promise<Manufacturer> {
      const { data } = await http.post<Manufacturer>('/manufacturers', payload)
      return data
    },
    async updateManufacturer(
      manufacturerId: string,
      payload: Partial<ManufacturerPayload>,
    ): Promise<Manufacturer> {
      const { data } = await http.put<Manufacturer>(`/manufacturers/${manufacturerId}`, payload)
      return data
    },
    async getManufacturer(manufacturerId: string): Promise<Manufacturer> {
      const { data } = await http.get<Manufacturer>(`/manufacturers/${manufacturerId}`)
      return data
    },

    async listProducts(query: ListQuery = {}): Promise<Product[]> {
      const { data } = await http.get<Product[]>('/products', { params: query })
      return data
    },
    async createProduct(payload: ProductPayload): Promise<Product> {
      const { data } = await http.post<Product>('/products', payload)
      return data
    },
    async updateProduct(productId: string, payload: Partial<ProductPayload>): Promise<Product> {
      const { data } = await http.put<Product>(`/products/${productId}`, payload)
      return data
    },
    async getProduct(productId: string): Promise<Product> {
      const { data } = await http.get<Product>(`/products/${productId}`)
      return data
    },

    async importCustomers(file: File): Promise<ImportSummary> {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await http.post<ImportSummary>('/imports/customers', formData)
      return data
    },
    async importManufacturers(file: File): Promise<ImportSummary> {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await http.post<ImportSummary>('/imports/manufacturers', formData)
      return data
    },
    async importProducts(file: File): Promise<ImportSummary> {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await http.post<ImportSummary>('/imports/products', formData)
      return data
    },
  },
  enquiries: {
    async list(params: { status?: string } & ListQuery = {}): Promise<Enquiry[]> {
      const { data } = await http.get<Enquiry[]>('/enquiries', { params })
      return data
    },
    async create(payload: EnquiryCreatePayload): Promise<Enquiry> {
      const { data } = await http.post<Enquiry>('/enquiries', payload)
      return data
    },
    async get(enquiryId: string): Promise<Enquiry> {
      const { data } = await http.get<Enquiry>(`/enquiries/${enquiryId}`)
      return data
    },
    async history(enquiryId: string): Promise<EnquiryStatusHistory[]> {
      const { data } = await http.get<EnquiryStatusHistory[]>(`/enquiries/${enquiryId}/history`)
      return data
    },
    async transitionStatus(
      enquiryId: string,
      payload: { to_status: string; comment?: string | null },
    ): Promise<Enquiry> {
      const { data } = await http.post<Enquiry>(`/enquiries/${enquiryId}/status`, payload)
      return data
    },
  },
  quotations: {
    async createForEnquiry(
      enquiryId: string,
      payload: { quotation_no?: string | null },
    ): Promise<Quotation> {
      const { data } = await http.post<Quotation>(`/enquiries/${enquiryId}/quotations`, payload)
      return data
    },
    async get(quotationId: string): Promise<QuotationDetail> {
      const { data } = await http.get<QuotationDetail>(`/quotations/${quotationId}`)
      return data
    },
    async getRevision(quotationId: string, revisionId: string): Promise<QuotationRevision> {
      const { data } = await http.get<QuotationRevision>(
        `/quotations/${quotationId}/revisions/${revisionId}`,
      )
      return data
    },
    async createRevision(
      quotationId: string,
      payload: QuotationRevisionCreatePayload,
    ): Promise<QuotationRevision> {
      const { data } = await http.post<QuotationRevision>(
        `/quotations/${quotationId}/revisions`,
        payload,
      )
      return data
    },
    async submitRevision(
      quotationId: string,
      revisionId: string,
      remarks?: string,
    ): Promise<QuotationRevision> {
      const { data } = await http.post<QuotationRevision>(
        `/quotations/${quotationId}/revisions/${revisionId}/submit`,
        { remarks },
      )
      return data
    },
    async approveRevision(
      quotationId: string,
      revisionId: string,
      remarks: string,
    ): Promise<QuotationRevision> {
      const { data } = await http.post<QuotationRevision>(
        `/quotations/${quotationId}/revisions/${revisionId}/approve`,
        { remarks },
      )
      return data
    },
    async rejectRevision(
      quotationId: string,
      revisionId: string,
      remarks: string,
    ): Promise<QuotationRevision> {
      const { data } = await http.post<QuotationRevision>(
        `/quotations/${quotationId}/revisions/${revisionId}/reject`,
        { remarks },
      )
      return data
    },
  },
  commercial: {
    async createCustomerPO(
      quotationId: string,
      revisionId: string,
      payload: {
        po_no?: string
        po_date?: string
        total_amount?: number
        status?: string
      },
    ): Promise<CustomerPO> {
      const { data } = await http.post<CustomerPO>(
        `/quotations/${quotationId}/revisions/${revisionId}/customer-po`,
        payload,
      )
      return data
    },
    async createRTMPO(
      quotationId: string,
      revisionId: string,
      payload: {
        po_no?: string
        manufacturer_id?: string
        po_date?: string
        total_amount?: number
        status?: string
      },
    ): Promise<RTMPO> {
      const { data } = await http.post<RTMPO>(
        `/quotations/${quotationId}/revisions/${revisionId}/rtm-po`,
        payload,
      )
      return data
    },
    async createInvoice(payload: {
      invoice_no?: string
      enquiry_id: string
      customer_po_id?: string
      issue_date?: string
      due_date?: string
      currency: string
      total_amount?: number
    }): Promise<Invoice> {
      const { data } = await http.post<Invoice>('/invoices', payload)
      return data
    },
    async createPayment(payload: {
      invoice_id: string
      payment_date?: string
      amount: number
      method: string
      reference_no?: string
      notes?: string
    }): Promise<Payment> {
      const { data } = await http.post<Payment>('/payments', payload)
      return data
    },
    async createDelivery(payload: {
      enquiry_id: string
      invoice_id?: string
      shipment_no?: string
      courier_name?: string
      tracking_no?: string
      shipped_at?: string
      expected_delivery_at?: string
      delivered_at?: string
      status?: string
    }): Promise<Delivery> {
      const { data } = await http.post<Delivery>('/deliveries', payload)
      return data
    },
    async addDeliveryEvent(
      deliveryId: string,
      payload: {
        event_type: string
        event_time?: string
        location?: string
        details_jsonb?: Record<string, unknown>
      },
    ): Promise<DeliveryEvent> {
      const { data } = await http.post<DeliveryEvent>(`/deliveries/${deliveryId}/events`, payload)
      return data
    },
    async getDelivery(deliveryId: string): Promise<Delivery> {
      const { data } = await http.get<Delivery>(`/deliveries/${deliveryId}`)
      return data
    },
  },
  reports: {
    async kpis(query: DateWindowQuery = {}): Promise<KPIReport> {
      const { data } = await http.get<KPIReport>('/reports/kpis', { params: query })
      return data
    },
    async downloadReport(
      report: 'enquiries' | 'quotations' | 'invoices' | 'payments',
      query: DateWindowQuery & { status?: string; method?: string } = {},
    ): Promise<Blob> {
      const { data } = await http.get<Blob>(`/reports/${report}.xlsx`, {
        params: query,
        responseType: 'blob',
      })
      return data
    },
  },
}
