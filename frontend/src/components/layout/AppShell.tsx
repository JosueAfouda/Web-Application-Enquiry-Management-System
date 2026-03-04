import type { ReactNode } from 'react'

import {
  BarChart3,
  ClipboardList,
  Factory,
  FileSpreadsheet,
  FileText,
  LayoutDashboard,
  LogOut,
  Package,
  Quote,
  Users,
} from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import { formatRole } from '../../lib/format'
import { Button } from '../ui/button'

interface NavItem {
  label: string
  to: string
  icon: ReactNode
  roles: string[]
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    to: '/',
    icon: <LayoutDashboard className="h-4 w-4" />,
    roles: ['BD', 'Admin', 'SuperAdmin', 'SupplyChain'],
  },
  {
    label: 'Customers',
    to: '/masters/customers',
    icon: <Users className="h-4 w-4" />,
    roles: ['BD', 'Admin', 'SuperAdmin', 'SupplyChain'],
  },
  {
    label: 'Manufacturers',
    to: '/masters/manufacturers',
    icon: <Factory className="h-4 w-4" />,
    roles: ['BD', 'Admin', 'SuperAdmin', 'SupplyChain'],
  },
  {
    label: 'Products',
    to: '/masters/products',
    icon: <Package className="h-4 w-4" />,
    roles: ['BD', 'Admin', 'SuperAdmin', 'SupplyChain'],
  },
  {
    label: 'Imports',
    to: '/masters/imports',
    icon: <FileSpreadsheet className="h-4 w-4" />,
    roles: ['Admin', 'SuperAdmin'],
  },
  {
    label: 'Enquiries',
    to: '/enquiries',
    icon: <ClipboardList className="h-4 w-4" />,
    roles: ['BD', 'Admin', 'SuperAdmin', 'SupplyChain'],
  },
  {
    label: 'Commercial',
    to: '/commercial',
    icon: <FileText className="h-4 w-4" />,
    roles: ['BD', 'Admin', 'SuperAdmin', 'SupplyChain'],
  },
  {
    label: 'Reports',
    to: '/reports',
    icon: <BarChart3 className="h-4 w-4" />,
    roles: ['Admin', 'SuperAdmin'],
  },
]

function buildBreadcrumb(pathname: string): string {
  const segments = pathname.split('/').filter(Boolean)
  if (segments.length === 0) {
    return 'Dashboard'
  }

  return segments
    .map((segment) => segment.replace(/-/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()))
    .join(' / ')
}

export function AppShell(): ReactNode {
  const { user, hasRole, logout } = useAuth()
  const location = useLocation()

  const allowedItems = navItems.filter((item) => hasRole(...item.roles))

  return (
    <div className="min-h-screen bg-app-gradient text-slate-900">
      <div className="mx-auto flex w-full max-w-[1500px] gap-4 px-4 py-4 lg:px-6">
        <aside className="hidden w-64 shrink-0 rounded-2xl border border-slate-200 bg-white/90 p-4 lg:block">
          <div className="mb-6 flex items-center gap-2 text-slate-900">
            <Quote className="h-5 w-5 text-teal-600" />
            <span className="font-semibold">EMS Frontend</span>
          </div>
          <nav className="space-y-1">
            {allowedItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    isActive ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100',
                  ].join(' ')
                }
              >
                {item.icon}
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="min-w-0 flex-1">
          <header className="mb-4 rounded-2xl border border-slate-200 bg-white/90 px-4 py-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.12em] text-slate-500">{buildBreadcrumb(location.pathname)}</p>
                <h1 className="text-lg font-semibold text-slate-900">Enquiry Management System</h1>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-800">{user?.username}</p>
                  <p className="text-xs text-slate-500">{(user?.roles ?? []).map(formatRole).join(', ')}</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => void logout()}>
                  <LogOut className="mr-2 h-4 w-4" /> Logout
                </Button>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 lg:hidden">
              {allowedItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    [
                      'rounded-md border px-3 py-1.5 text-xs font-medium',
                      isActive
                        ? 'border-slate-900 bg-slate-900 text-white'
                        : 'border-slate-200 bg-white text-slate-700',
                    ].join(' ')
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          </header>

          <main className="space-y-4">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
