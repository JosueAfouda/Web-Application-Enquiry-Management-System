import { api } from './api'
import { asNumber } from './format'
import type {
  Customer,
  CustomerPO,
  Delivery,
  Enquiry,
  Invoice,
  Manufacturer,
  Payment,
  Product,
  Quotation,
  QuotationRevision,
  RTMPO,
} from '../types/api'

export interface DemoSeedResult {
  customer: Customer
  manufacturer: Manufacturer
  product: Product
  enquiry: Enquiry
  quotation: Quotation
  revision: QuotationRevision
  customerPO: CustomerPO
  rtmPO: RTMPO
  invoice: Invoice
  payment: Payment
  delivery: Delivery
}

function makeSeed(): string {
  return `${Date.now()}-${Math.floor(Math.random() * 1000)
    .toString()
    .padStart(3, '0')}`
}

function asCode(prefix: string, seed: string, maxLength: number): string {
  return `${prefix}-${seed}`.slice(0, maxLength)
}

export async function generateDemoData(): Promise<DemoSeedResult> {
  const seed = makeSeed()

  const customer = await api.masters.createCustomer({
    code: asCode('DEMOC', seed, 50),
    name: `Demo Customer ${seed}`,
    country: 'Spain',
    contact_fields: {
      email: `demo-${seed}@example.com`,
      contact_person: 'Demo Buyer',
      phone: '+34-000-000-000',
    },
    is_active: true,
  })

  const manufacturer = await api.masters.createManufacturer({
    code: asCode('DEMOM', seed, 50),
    name: `Demo Manufacturer ${seed}`,
    country: 'India',
    is_active: true,
  })

  const product = await api.masters.createProduct({
    sku: asCode('DEMO-SKU', seed, 80),
    name: `Demo Product ${seed}`,
    manufacturer_id: manufacturer.id,
    unit: 'BOX',
    is_active: true,
  })

  const enquiry = await api.enquiries.create({
    customer_id: customer.id,
    currency: 'USD',
    notes: `Demo enquiry seed ${seed}`,
    items: [
      {
        product_id: product.id,
        requested_qty: 120,
        target_price: 11.5,
        notes: 'Demo item line',
      },
    ],
  })

  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'IN_REVIEW',
    comment: 'Demo progression',
  })

  const quotation = await api.quotations.createForEnquiry(enquiry.id, {
    quotation_no: asCode('DEMOQ', seed, 80),
  })

  const enquiryItem = enquiry.items[0]
  const revision = await api.quotations.createRevision(quotation.id, {
    freight: 120,
    markup_percent: 8,
    currency: 'USD',
    items: [
      {
        product_id: product.id,
        qty: asNumber(enquiryItem.requested_qty),
        unit_price: 12.35,
        enquiry_item_id: enquiryItem.id,
        notes: 'Demo quotation item',
      },
    ],
  })

  await api.quotations.submitRevision(quotation.id, revision.id, 'Demo submit')
  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'QUOTED',
    comment: 'Demo quotation created',
  })
  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'PENDING_APPROVAL',
    comment: 'Demo awaiting approval',
  })

  const approvedRevision = await api.quotations.approveRevision(
    quotation.id,
    revision.id,
    'Demo approved',
  )
  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'APPROVED',
    comment: 'Demo approval recorded',
  })

  const customerPO = await api.commercial.createCustomerPO(quotation.id, approvedRevision.id, {
    po_no: asCode('DEMOCPO', seed, 80),
    status: 'ISSUED',
  })

  const rtmPO = await api.commercial.createRTMPO(quotation.id, approvedRevision.id, {
    po_no: asCode('DEMORPO', seed, 80),
    manufacturer_id: manufacturer.id,
    status: 'ISSUED',
  })
  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'PO_CREATED',
    comment: 'Demo purchase orders created',
  })

  const invoice = await api.commercial.createInvoice({
    invoice_no: asCode('DEMOINV', seed, 80),
    enquiry_id: enquiry.id,
    customer_po_id: customerPO.id,
    currency: 'USD',
  })
  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'INVOICED',
    comment: 'Demo invoice generated',
  })

  const invoiceTotal = asNumber(invoice.total_amount)
  const payment = await api.commercial.createPayment({
    invoice_id: invoice.id,
    amount: Number((invoiceTotal * 0.5).toFixed(2)),
    method: 'BANK_TRANSFER',
    reference_no: asCode('DEMOPAY', seed, 80),
    notes: 'Demo partial payment',
  })

  const delivery = await api.commercial.createDelivery({
    enquiry_id: enquiry.id,
    invoice_id: invoice.id,
    status: 'PENDING',
    shipment_no: asCode('DEMOSHIP', seed, 80),
    courier_name: 'Demo Courier',
    tracking_no: asCode('TRK', seed, 80),
  })

  await api.commercial.addDeliveryEvent(delivery.id, {
    event_type: 'IN_TRANSIT',
    location: 'Madrid Hub',
    details_jsonb: {
      source: 'demo-seed',
      seed,
    },
  })
  const hydratedDelivery = await api.commercial.getDelivery(delivery.id)
  await api.enquiries.transitionStatus(enquiry.id, {
    to_status: 'IN_DELIVERY',
    comment: 'Demo delivery started',
  })

  return {
    customer,
    manufacturer,
    product,
    enquiry,
    quotation,
    revision: approvedRevision,
    customerPO,
    rtmPO,
    invoice: {
      ...invoice,
      status: 'PARTIAL',
      payments: [payment],
    },
    payment,
    delivery: hydratedDelivery,
  }
}
