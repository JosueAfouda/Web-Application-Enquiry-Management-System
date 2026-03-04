# BRD Gap Analysis — EMS MVP vs `BRD_EMS_for_Proto_Type.pdf`

## 1. BRD Summary
The BRD expands the EMS scope from the current MVP into a full operational workflow covering:
- detailed enquiry lifecycle (17 business statuses)
- richer negotiation and pricing structure (unit/pack, revision rounds, conversion to INR)
- stronger operational modules (user management, product-manufacturer mapping, attachments, reminders)
- broader reporting/dashboard requirements (role-wise dashboard KPIs, ageing, performance, revenue, PDF export)
- additional controls (password reset, user approval, comments enforcement, SLA/deadline alerts)

## 2. New Functional Requirements Identified
## 2.1 Completely New Features
1. Password reset flow.
2. User approval workflow (user activation/approval by privileged role).
3. User management module (create/update/assign roles).
4. Product-Manufacturer mapping module (many-to-many).
5. Attachment management for quotations/invoices.
6. Email notifications/reminders for follow-up and daily status digest.
7. Enquiry deadline alerts and SLA tracking.
8. Manufacturer rating system.
9. PDF report export.

## 2.2 Missing Fields / Data Points
1. Enquiry quantity split by year (1, 2, 3 years).
2. Plant approvals/compliance flags per enquiry item (WHO, EU-GMP, USFDA, etc.).
3. Follow-up sequence tracking (1st/2nd/3rd follow-up) with timestamps.
4. Pricing dimensions: manufacturer price per unit and per pack; final quote per unit and per pack.
5. Currency conversion reference/value to INR.
6. Soft-delete metadata (`is_deleted`) and creator/modifier metadata (`created_by`, `modified_by`) across business tables.

## 2.3 Additional Workflow Steps
BRD lifecycle introduces distinct states not explicitly modeled in current enum/transitions, including:
- `NEW_ENQUIRY`, `OPEN_ENQUIRY`, `SENT_ENQUIRY`, `FOLLOW_UP_ENQUIRY`, `RECEIVED_QUOTATION`, `RESENT_ENQUIRY_WITH_OFFER`, `RECEIVED_REVISED_QUOTATION`, `SENT_QUOTATION_FOR_APPROVAL`, `SENT_APPROVED_QUOTATION_TO_CUSTOMER`, `PO_RECEIVED`, `PO_SENT_TO_MANUFACTURER`, `INVOICE_RECEIVED`, `FINAL_INVOICE_GENERATED`, `PRODUCT_DELIVERY`.

## 2.4 Additional Validations / Calculations
1. Enforce approval/rejection remarks.
2. Price calculation support for both unit and pack dimensions.
3. Currency conversion calculation to INR for standard comparison.

## 2.5 Additional Reports
1. Daily enquiry status report.
2. Enquiry ageing report.
3. Manufacturer performance report.
4. Approval report (beyond KPI aggregate).
5. Closed enquiry report.
6. PO & Invoice tracking report.
7. Revenue report.
8. PDF exports.

## 2.6 Additional Roles / Permissions
1. Manufacturer portal role (optional in BRD).
2. Customer portal role (optional in BRD).
3. More granular action-level permission mapping per module.

## 3. Gap Analysis vs Current System
| BRD Requirement | Current EMS | Gap Status |
|---|---|---|
| Core RBAC for BD/Admin/SuperAdmin/SupplyChain | Implemented | Met |
| Manufacturer/Customer portal roles | Not implemented | Gap |
| Full 17-step enquiry lifecycle | Partial (MVP statuses differ) | Gap |
| Status history with datetime/user/comments | Implemented | Met |
| Password reset | Not implemented | Gap |
| User approval | Not implemented | Gap |
| Users management module | Not implemented | Gap |
| Master modules (customers/products/manufacturers + product import) | Implemented | Partially met |
| Product-manufacturer mapping (many-to-many) | Not implemented (single manufacturer per product) | Gap |
| Enquiry quantity 1/2/3 years | Not implemented | Gap |
| Plant approvals data capture | Not implemented | Gap |
| Admin manufacturer assignment + follow-up tracking | Partial | Gap |
| Quotation revisions + approvals | Implemented | Met |
| Unit + pack pricing, INR conversion | Not implemented | Gap |
| PO, invoice, payments, delivery flow | Implemented | Partially met (missing sales order/invoice-received distinction) |
| Dashboard role-specific KPI widgets | Not implemented (generic dashboard) | Gap |
| Reports + Excel export | Partial (KPI + 4 Excel exports) | Gap |
| PDF export | Not implemented | Gap |
| Audit trail | Implemented | Met |
| Quotation/invoice file uploads | Not implemented | Gap |
| Email integration and alerts | Not implemented | Gap |

## 4. Impacted Modules
- Backend models/schemas: `enquiry`, `quotation`, `commercial`, `user`, `reports`, and new attachment/mapping models.
- Backend services/APIs: enquiries workflow, quotations calculations, commercial process, auth/user admin, reporting, notifications.
- Database migrations: new enums/columns/tables (non-destructive Alembic revisions).
- Frontend pages: dashboard, enquiry detail/list, quotation page, masters pages, reports page, auth/admin user pages.
- Background jobs/scripts: daily digest and reminder scheduler (cron-compatible script/worker).

## 5. Required Changes (Functional)
## 5.1 Must-Have to align BRD core flow
1. Expand enquiry workflow states and transitions to BRD-compatible lifecycle.
2. Add enquiry follow-up structured data (sequence, method, notes, next follow-up date).
3. Add enquiry item business fields: yearly quantities and compliance/plant approvals.
4. Add product-manufacturer mapping and manufacturer assignment per enquiry item.
5. Extend quotation pricing model for unit/pack + INR conversion + full version history.
6. Add attachment support for quotation and invoice documents.
7. Add user management + user approval + password reset APIs/UI.
8. Expand reports to include ageing, approval detail, closed enquiries, PO/invoice tracking, revenue.

## 5.2 Should-Have
1. Role-wise dashboard KPI cards aligned with BRD.
2. Reminder emails and daily status summary generation.
3. Enquiry SLA/deadline alert indicators.

## 5.3 Optional (BRD marked optional)
1. Manufacturer portal access.
2. Customer portal access.

## 6. Implementation Strategy
## Phase 1 — Data & Workflow Foundation
- Add migrations for new enquiry statuses, follow-up table, additional enquiry item fields, and product-manufacturer mapping.
- Update status transition engine and API contracts.

## Phase 2 — Pricing & Commercial Enhancements
- Extend quotation revision item pricing to unit/pack and INR conversion fields.
- Add attachment tables/endpoints for quotation and invoice documents.

## Phase 3 — Auth/Admin Functional Expansion
- Implement user management endpoints/UI, approval flags, and password reset flow.

## Phase 4 — Reporting & Dashboards
- Add missing report endpoints (ageing, performance, revenue, approval detail, closed enquiries).
- Add PDF export support (open-source library).
- Implement role-wise dashboard widgets.

## Phase 5 — Notifications & Alerts
- Add reminder/daily digest job scripts and email dispatch adapter.

## Phase 6 — Test Hardening
- Extend API tests, smoke scripts, and UI manual checklist for new flows.

---
Conclusion: The BRD introduces substantial new functional scope. The current EMS MVP is partially compliant but not fully BRD-compliant.
