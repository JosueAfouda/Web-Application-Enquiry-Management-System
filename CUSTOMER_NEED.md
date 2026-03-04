# Client Requirement Document  
## Web Application – Enquiry Management System (EMS)

**Audience:** AI Agents  
**Purpose:** Provide a clear and structured description of the client’s expressed needs without assumptions or technical interpretation.

---

# 1. Project Overview

The client requires the development of a **custom web-based Enquiry Management System (EMS)**.

The system will be used by a **pharmaceutical export/trading company** to manage and track **customer product enquiries** throughout their entire operational lifecycle.

The EMS must enable internal teams to manage the process from the moment an enquiry is received until the final stages of **quotation, approval, purchase orders, invoicing, and delivery tracking**.

The application will be accessed through a **web interface** and must support multiple internal roles.

---

# 2. Business Context

The organization receives **product enquiries from customers** related to pharmaceutical products.

Each enquiry goes through several operational steps, including:

1. Enquiry receipt
2. Price quotation preparation
3. Internal approval
4. Purchase order creation
5. Invoice generation
6. Delivery tracking

The EMS must provide a structured system to manage and monitor this lifecycle.

---

# 3. Core Functional Modules

The EMS must include the following modules.

## 3.1 User Authentication & Role Management

The system must provide **secure login functionality** with role-based access control.

Defined user roles include:

- **BD (Business Development)**
- **Admin**
- **Super Admin**
- **Supply Chain**

Each role must access the system according to its permissions.

---

## 3.2 Master Data Management

The system must maintain master records for key entities:

### Customer Master
Stores information related to customers.

### Product Master
Stores information related to products.

### Manufacturer Master
Stores information related to manufacturers.

The system must support **Excel file import** for populating or updating these master datasets.

---

## 3.3 Enquiry Management

The EMS must track **customer product enquiries**.

Each enquiry must move through a **status-based workflow** representing its lifecycle.

The system must allow users to view and manage enquiries according to their current status.

---

## 3.4 Quotation Management

The EMS must allow users to generate **quotations for enquiries**.

Quotations must support **multiple revisions**, meaning updated versions of a quotation may exist for the same enquiry.

---

## 3.5 Approval Workflow

The system must support an **approval workflow** for quotations.

The workflow includes **price calculations**, which may involve:

- Freight
- Markup

Approvals must occur before subsequent steps in the process.

---

## 3.6 Purchase Order Generation

The EMS must allow generation of:

- **Customer Purchase Orders (Customer PO)**
- **RTM Purchase Orders (RTM PO)**

These must be linked to the relevant enquiry and quotation.

---

## 3.7 Invoice and Payment Tracking

The system must support:

- **Invoice generation**
- **Tracking of payments**

Invoices must be associated with the related transaction records.

---

## 3.8 Reporting Dashboard

The EMS must provide a **reporting dashboard**.

Reports must include the ability to **export data to Excel format**.

---

# 4. System Requirements

The system must satisfy the following requirements.

## 4.1 User Interface

The application must provide a **clean user interface and user experience (UI/UX)**.

---

## 4.2 Security

The system must implement **secure authentication mechanisms**.

---

## 4.3 Audit Trail

The EMS must maintain an **audit trail** that records actions performed within the system.

---

## 4.4 Cloud Deployment Readiness

The system must be **ready for deployment in a cloud environment**.

---

## 4.5 Scalability

The architecture must support **scalability** to handle future system growth.

---

# 5. Technology Context (Client Indication)

The client indicates openness to the following technology options:

Backend frameworks:

- Node
- Laravel
- Django

Frontend frameworks:

- React
- Vue

Database options:

- MySQL
- PostgreSQL

The project description also lists the following skills and technologies:

- .NET Framework
- Web Development
- MySQL
- Web Design
- Web Application Development
- HTML
- CSS
- HTML5
- jQuery
- JavaScript

---

# 6. Project Timeline

The expected project duration is **8 to 12 weeks**.

---

# 7. Vendor Proposal Expectations

The client requests the following information in proposals:

- Examples of **similar CRM or ERP projects**
- **Suggested technology stack**
- **Estimated timeline**
- **Development milestones**
- **Post-delivery support details**

---

# 8. Client Organization

**Company:** Tritan Solutions Private Limited  
**Website:** https://www.tritansolutions.com

---

# 9. Project Budget

**Budget Type:** Fixed Price  
**Budget:** $1,000  
**Project Complexity:** Complex Project

---

# 10. Reference Document

A document titled:

**"BRD EMS for Proto Type.pdf"**

has been provided as an attachment by the client and contains additional information related to the project.

---