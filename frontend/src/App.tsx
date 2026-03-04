import type { ReactNode } from 'react'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { RequireAuth } from './components/layout/RequireAuth'
import { RoleGuard } from './components/layout/RoleGuard'
import { AuthProvider } from './context/AuthContext'
import { WorkflowProvider } from './context/WorkflowContext'
import { CommercialPage } from './pages/commercial/CommercialPage'
import { DashboardPage } from './pages/DashboardPage'
import { EnquiriesPage } from './pages/enquiries/EnquiriesPage'
import { EnquiryDetailPage } from './pages/enquiries/EnquiryDetailPage'
import { NewEnquiryPage } from './pages/enquiries/NewEnquiryPage'
import { LoginPage } from './pages/LoginPage'
import { CustomersPage } from './pages/masters/CustomersPage'
import { ImportsPage } from './pages/masters/ImportsPage'
import { ManufacturersPage } from './pages/masters/ManufacturersPage'
import { ProductsPage } from './pages/masters/ProductsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { QuotationPage } from './pages/quotations/QuotationPage'
import { ReportsPage } from './pages/reports/ReportsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 20000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App(): ReactNode {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WorkflowProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route element={<RequireAuth />}>
                <Route element={<AppShell />}>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/masters/customers" element={<CustomersPage />} />
                  <Route path="/masters/manufacturers" element={<ManufacturersPage />} />
                  <Route path="/masters/products" element={<ProductsPage />} />
                  <Route
                    path="/masters/imports"
                    element={
                      <RoleGuard roles={['Admin', 'SuperAdmin']}>
                        <ImportsPage />
                      </RoleGuard>
                    }
                  />
                  <Route path="/enquiries" element={<EnquiriesPage />} />
                  <Route path="/enquiries/new" element={<NewEnquiryPage />} />
                  <Route path="/enquiries/:enquiryId" element={<EnquiryDetailPage />} />
                  <Route path="/quotations/:quotationId" element={<QuotationPage />} />
                  <Route path="/commercial" element={<CommercialPage />} />
                  <Route
                    path="/reports"
                    element={
                      <RoleGuard roles={['Admin', 'SuperAdmin']}>
                        <ReportsPage />
                      </RoleGuard>
                    }
                  />
                  <Route path="/404" element={<NotFoundPage />} />
                  <Route path="*" element={<Navigate to="/404" replace />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                borderRadius: '0.625rem',
                border: '1px solid #e2e8f0',
                padding: '12px 14px',
                color: '#0f172a',
              },
            }}
          />
        </WorkflowProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}
