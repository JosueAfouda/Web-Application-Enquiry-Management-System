# EMS User Manual

## 1. Introduction
The Enquiry Management System (EMS) is a business application used to manage the full commercial lifecycle of customer enquiries in pharmaceutical export/trading operations.

EMS helps teams work in one shared system instead of spreadsheets and email chains.

Typical users include:
- Business Development (BD)
- Admin users
- Super Admin users
- Supply Chain users

With EMS, users can:
- register and track enquiries
- prepare quotations and revisions
- run approval decisions
- create purchase-order records
- create invoices and record payments
- track deliveries
- monitor KPIs and export reports

## 2. Getting Started
### 2.1 User account creation
At the current stage, user accounts are created by a system administrator.

1. Request access from your EMS administrator.
2. Provide your name, email, and required role (BD/Admin/SuperAdmin/Supply Chain).
3. Wait for confirmation that your account is active.

Note: There is no self-signup screen in the current interface.

### 2.2 Log in
1. Open the EMS web URL provided by your team.
2. On the **Login** page, enter:
   - **Username**
   - **Password**
3. Click **Sign in**.
4. If successful, you will be redirected to the Dashboard.

If an API connectivity warning appears, click **Retry API Check** and try again.

### 2.3 Password reset
Self-service password reset is not currently available in the UI.

If you forgot your password:
1. Contact your EMS administrator.
2. Request a password reset.
3. Log in again with the new password.

## 3. Navigating the Interface
After login, EMS uses a standard layout:

- **Left navigation menu** (desktop): main modules
- **Top header**: page title, breadcrumb, current user, logout
- **Main content area**: lists, forms, actions, and details

Main sections:
- **Dashboard**
- **Customers**
- **Manufacturers**
- **Products**
- **Imports** (Admin/SuperAdmin)
- **Enquiries**
- **Commercial**
- **Reports** (Admin/SuperAdmin)

Useful navigation tips:
1. Click any menu item to open a module.
2. In list pages, click a row to load details/edit forms.
3. Use **Back** buttons in detail screens.
4. Watch toast notifications (top-right) for success/error feedback.

## 4. Managing Master Data
Master data includes Customers, Manufacturers, and Products.

### 4.1 Customers
1. Go to **Customers**.
2. In **Create Customer**, fill:
   - Code
   - Name
   - Country
   - Contact Email/Phone (optional)
   - Active checkbox
3. Click **Create**.
4. To edit, click a row in the customer table.
5. Update fields in **Customer Details** and click **Update**.
6. To deactivate, uncheck **Active** and save.

### 4.2 Manufacturers
1. Go to **Manufacturers**.
2. In **Create Manufacturer**, fill code, name, country, Active.
3. Click **Create**.
4. Select a row to edit details.
5. Update and click **Update**.
6. To deactivate, uncheck **Active** and save.

### 4.3 Products
1. Go to **Products**.
2. In **Create Product**, fill:
   - SKU
   - Name
   - Manufacturer
   - Unit
   - Active
3. Click **Create**.
4. Select a product row to edit details.
5. Click **Update** to save.
6. To deactivate, uncheck **Active** and save.

### 4.4 Excel import (if enabled for your role)
1. Go to **Imports**.
2. Choose **Master Type**: Customers / Manufacturers / Products.
3. Upload an Excel/CSV file.
4. Click **Upload and Process**.
5. Review summary:
   - Rows
   - Created
   - Updated
   - Errors
6. If errors exist, fix source file and re-import.

## 5. Managing Enquiries
### 5.1 Create a new enquiry
1. Go to **Enquiries**.
2. Click **Create Enquiry**.
3. Fill header fields:
   - Customer
   - Received Date
   - Currency
   - Notes (optional)
4. Add one or more item lines:
   - Product
   - Quantity
   - Target Price (optional)
   - Notes (optional)
5. Click **Create Enquiry**.

### 5.2 Track enquiries
In **Enquiries** list, use filters:
- Status
- Customer
- Date from / date to

Click the enquiry number to open details.

### 5.3 View enquiry history
In **Enquiry Details**:
- **Status History** shows timeline of transitions.
- **Enquiry Items** shows requested lines.
- **Transition Status** allows authorized users to move to next status with comments.

## 6. Creating Quotations
### 6.1 Create quotation from an enquiry
1. Open an enquiry in **Enquiry Details**.
2. Click **Create Quotation**.
3. EMS opens the quotation page for that enquiry.

### 6.2 Create a quotation revision
1. In **Create Revision**, set:
   - Freight
   - Markup %
   - Currency
2. Add/edit line items:
   - Product
   - Qty
   - Unit Price
   - Linked enquiry item (optional)
   - Notes (optional)
3. Click **Create Revision**.

### 6.3 Understand totals
For each revision, EMS displays:
- Subtotal (sum of line totals)
- Freight
- Final Total (including markup)

You can switch between revisions from the revision selector.

## 7. Approval Workflow
### 7.1 Submit for approval
1. Open the target revision.
2. In **Approval Actions**, click **Submit Revision**.

### 7.2 Approve or reject
Authorized approvers (Admin/SuperAdmin) can:
1. Enter remarks in the text area.
2. Click **Approve** or **Reject**.

Important:
- Remarks are required for approve/reject actions.
- The **Approval Timeline** records decisions and comments.

## 8. Purchase Orders
PO actions become available after a revision is approved.

### 8.1 Customer PO
1. On the quotation page, go to **Create Customer PO / RTM PO**.
2. Fill optional fields (PO No, date, amount, status).
3. Click **Create Customer PO**.

### 8.2 RTM PO
1. In the same section, fill RTM PO form.
2. Choose manufacturer if needed.
3. Click **Create RTM PO**.

How POs relate to quotations:
- Both PO types are linked to the approved quotation revision.
- They provide commercial context for invoicing and downstream operations.

## 9. Invoice and Payment Tracking
Use the **Commercial** page.

### 9.1 Create invoice
1. In **Create Invoice**, select enquiry.
2. Optionally link Customer PO.
3. Enter dates, currency, and amount (if needed).
4. Click **Create Invoice**.

### 9.2 Record payment
1. In **Add Payment**, select invoice.
2. Enter payment date, amount, method, reference, notes.
3. Click **Add Payment**.

### 9.3 Overpayment prevention
If payment amount exceeds invoice total:
- EMS blocks the action.
- You see an error message.
- Record a valid amount and retry.

### 9.4 Delivery tracking
1. In **Create Delivery**, enter shipment details.
2. Click **Create Delivery**.
3. In **Add Delivery Event**, add timeline events (e.g., `IN_TRANSIT`, `DELIVERED`).

## 10. Reporting
Go to **Reports** (Admin/SuperAdmin).

### 10.1 View KPI report
1. Set optional filters:
   - Date from
   - Date to
   - Status
2. Click **Refresh KPIs**.

Available KPI blocks include:
- Approval Rate
- PO Conversion
- Collected / Outstanding
- Delivery Completion

### 10.2 Export Excel reports
Use **Excel Export** buttons to download:
- `enquiries.xlsx`
- `quotations.xlsx`
- `invoices.xlsx`
- `payments.xlsx`

## 11. Roles and Permissions
### Business Development (BD)
Typical actions:
- create and track enquiries
- work on quotations/revisions
- follow enquiry flow
- collaborate on customer-facing steps

### Admin
Typical actions:
- all BD operational actions
- approvals (with SuperAdmin)
- imports and broader commercial control

### Super Admin
Typical actions:
- full oversight
- critical approval decisions
- high-level reporting access

### Supply Chain
Typical actions:
- commercial execution support
- RTM PO participation
- delivery tracking operations

Note: Menus and actions are automatically shown/hidden by role.

## 12. Common Use Case
Example: complete lifecycle

1. Create customer, manufacturer, and product masters.
2. Create an enquiry with product lines.
3. Open enquiry details and create a quotation.
4. Create revision with pricing, freight, and markup.
5. Submit revision for approval.
6. Approver reviews and approves with remarks.
7. Create Customer PO and/or RTM PO.
8. Go to Commercial and create invoice.
9. Record customer payment(s).
10. Create delivery and add tracking events.
11. Open Reports and export KPI/Excel evidence.

## 13. Troubleshooting
### Issue: Cannot log in
- Verify username/password.
- Check if your account is active.
- If API warning appears, click **Retry API Check**.
- Contact admin if issue persists.

### Issue: Data not visible in lists
- Clear filters (status/customer/date).
- Refresh page.
- Confirm your role has access to that module.

### Issue: Approval action fails
- Confirm revision was submitted first.
- Add mandatory remarks before approve/reject.
- Verify your role is allowed to approve.

### Issue: Validation errors on forms
- Fill all required fields.
- Use valid formats (dates, numeric values, currency code length).
- Correct highlighted fields and submit again.

### Issue: Payment rejected
- Check invoice total vs payment amount.
- Reduce payment to avoid overpayment.

## 14. Best Practices
1. Keep master data clean (no duplicates, consistent naming).
2. Always enter meaningful comments during status changes and approvals.
3. Use revisions instead of overwriting pricing assumptions.
4. Apply date/customer/status filters to keep worklists focused.
5. Export reports regularly for business reviews.
6. Deactivate obsolete master records instead of creating near-duplicates.
7. Use the Dashboard shortcuts for faster navigation.
8. For demos/training, Admin/SuperAdmin can use **DEMO DATA** to preload sample flow.
