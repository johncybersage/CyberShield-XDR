/**
 * CyberShield XDR — Register Page
 * Registration form with live password strength meter.
 */
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, User, AtSign } from 'lucide-react'

import toast from 'react-hot-toast'

import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import { useAuthStore } from '@store/authStore'
import authService, { extractErrorMessage } from '@services/authService'
import { cn } from '@utils/cn'

const schema = z
  .object({
    full_name: z.string().min(2, 'Full name must be at least 2 characters'),
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .max(50)
      .regex(/^[a-zA-Z0-9_-]+$/, 'Only letters, numbers, underscores, hyphens'),
    email: z.string().email('Enter a valid email address'),
    password: z
      .string()
      .min(8, 'At least 8 characters')
      .regex(/[A-Z]/, 'Must contain uppercase letter')
      .regex(/[a-z]/, 'Must contain lowercase letter')
      .regex(/\d/, 'Must contain a number')
      .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Must contain a special character'),
    confirm_password: z.string(),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type FormData = z.infer<typeof schema>

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: '8+ characters', pass: password.length >= 8 },
    { label: 'Uppercase', pass: /[A-Z]/.test(password) },
    { label: 'Lowercase', pass: /[a-z]/.test(password) },
    { label: 'Number', pass: /\d/.test(password) },
    { label: 'Special char', pass: /[!@#$%^&*(),.?":{}|<>]/.test(password) },
  ]
  const score = checks.filter((c) => c.pass).length

  const strengthLabel = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'][score]
  const strengthColor = [
    '',
    'bg-threat-critical',
    'bg-threat-high',
    'bg-threat-medium',
    'bg-cyber-500',
    'bg-threat-low',
  ][score]

  if (!password) return null

  return (
    <div className="space-y-2">
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={cn(
              'h-1 flex-1 rounded-full transition-all duration-300',
              i <= score ? strengthColor : 'bg-dark-300'
            )}
          />
        ))}
      </div>
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-x-3 gap-y-1">
          {checks.map((c) => (
            <span
              key={c.label}
              className={cn(
                'text-xs transition-colors',
                c.pass ? 'text-threat-low' : 'text-gray-600'
              )}
            >
              {c.pass ? '✓' : '○'} {c.label}
            </span>
          ))}
        </div>
        <span className={cn('text-xs font-medium', score >= 4 ? 'text-threat-low' : 'text-gray-500')}>
          {strengthLabel}
        </span>
      </div>
    </div>
  )
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const password = watch('password', '')

  const onSubmit = async (data: FormData) => {
    try {
      const response = await authService.register(data)
      sessionStorage.setItem('refresh_token', response.refresh_token)
      setAuth(response.user, response.access_token)
      toast.success('Account created successfully!')
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const message = extractErrorMessage(err)
      if (message.toLowerCase().includes('email') || message.toLowerCase().includes('username')) {
        setError('email', { message })
      } else {
        toast.error(message)
      }
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-white">Create your account</h2>
        <p className="text-gray-500 text-sm mt-1">Join the CyberShield XDR platform</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <Input
          label="Full name"
          placeholder="John Smith"
          autoComplete="name"
          leftIcon={<User className="w-4 h-4" />}
          error={errors.full_name?.message}
          {...register('full_name')}
        />

        <Input
          label="Username"
          placeholder="jsmith"
          autoComplete="username"
          leftIcon={<AtSign className="w-4 h-4" />}
          error={errors.username?.message}
          {...register('username')}
        />

        <Input
          label="Email address"
          type="email"
          placeholder="analyst@company.com"
          autoComplete="email"
          leftIcon={<Mail className="w-4 h-4" />}
          error={errors.email?.message}
          {...register('email')}
        />

        <div className="space-y-2">
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            leftIcon={<Lock className="w-4 h-4" />}
            error={errors.password?.message}
            {...register('password')}
          />
          <PasswordStrength password={password} />
        </div>

        <Input
          label="Confirm password"
          type="password"
          placeholder="••••••••"
          autoComplete="new-password"
          leftIcon={<Lock className="w-4 h-4" />}
          error={errors.confirm_password?.message}
          {...register('confirm_password')}
        />

        <p className="text-xs text-gray-500">
          By creating an account you agree to our{' '}
          <span className="text-cyber-400 cursor-pointer hover:underline">Terms of Service</span>
          {' '}and{' '}
          <span className="text-cyber-400 cursor-pointer hover:underline">Privacy Policy</span>.
        </p>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? 'Creating account...' : 'Create Account'}
        </Button>
      </form>

      <p className="text-center text-sm text-gray-500">
        Already have an account?{' '}
        <Link to="/login" className="text-cyber-400 hover:text-cyber-300 transition-colors font-medium">
          Sign in
        </Link>
      </p>
    </div>
  )
}
