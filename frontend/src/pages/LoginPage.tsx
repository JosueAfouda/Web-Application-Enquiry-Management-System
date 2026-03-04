import { useCallback, useEffect, useState, type ReactNode } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { AlertTriangle, Loader2 } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import { toApiClientError } from '../lib/errors'
import { apiBaseUrl } from '../lib/http'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { FormField } from '../components/ui/form-field'
import { Input } from '../components/ui/input'

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
})

type LoginForm = z.infer<typeof schema>

export function LoginPage(): ReactNode {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated, login, isBootstrapping } = useAuth()
  const [isApiAvailable, setIsApiAvailable] = useState<boolean>(true)
  const [isApiCheckPending, setIsApiCheckPending] = useState<boolean>(true)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      username: 'admin',
      password: 'admin',
    },
  })

  const checkApiHealth = useCallback(async () => {
    setIsApiCheckPending(true)
    try {
      await api.system.health()
      setIsApiAvailable(true)
    } catch {
      setIsApiAvailable(false)
    } finally {
      setIsApiCheckPending(false)
    }
  }, [])

  useEffect(() => {
    void checkApiHealth()
    const intervalId = window.setInterval(() => {
      void checkApiHealth()
    }, 15000)
    return () => window.clearInterval(intervalId)
  }, [checkApiHealth])

  if (isAuthenticated && !isBootstrapping) {
    return <Navigate to="/" replace />
  }

  const from = typeof location.state?.from === 'string' ? location.state.from : '/'

  const onSubmit = handleSubmit(async (values) => {
    try {
      await login(values.username, values.password)
      toast.success('Login successful')
      navigate(from, { replace: true })
    } catch (error) {
      const normalized = toApiClientError(error)
      toast.error(normalized.message)
    }
  })

  return (
    <div className="flex min-h-screen items-center justify-center bg-app-gradient p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>EMS Sign In</CardTitle>
          <p className="mt-1 text-sm text-slate-600">Use your EMS username and password.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-3" onSubmit={onSubmit}>
            <FormField label="Username" error={errors.username?.message}>
              <Input placeholder="admin" autoComplete="username" {...register('username')} />
            </FormField>
            <FormField label="Password" error={errors.password?.message}>
              <Input
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                {...register('password')}
              />
            </FormField>
            <Button
              className="w-full"
              type="submit"
              disabled={isSubmitting || isApiCheckPending || !isApiAvailable}
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
            <div className="rounded-md border border-slate-200 bg-slate-50 p-2 text-xs text-slate-600">
              {isApiCheckPending ? (
                <span className="inline-flex items-center gap-1">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Checking API availability...
                </span>
              ) : null}
              {!isApiCheckPending && !isApiAvailable ? (
                <div className="space-y-1">
                  <span className="inline-flex items-center gap-1 text-amber-700">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    API unavailable at <span className="font-mono">{apiBaseUrl}</span>
                  </span>
                  <Button variant="ghost" size="sm" onClick={() => void checkApiHealth()}>
                    Retry API Check
                  </Button>
                </div>
              ) : null}
              {!isApiCheckPending && isApiAvailable ? (
                <span className="text-teal-700">API reachable. You can sign in.</span>
              ) : null}
            </div>
            <p className="text-xs text-slate-500">Demo local credential: admin / admin</p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
