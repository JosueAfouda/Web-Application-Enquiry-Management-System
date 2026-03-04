import type { ReactNode } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { useAuth } from '../context/AuthContext'
import { toApiClientError } from '../lib/errors'
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
            <Button className="w-full" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
            <p className="text-xs text-slate-500">Demo local credential: admin / admin</p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
