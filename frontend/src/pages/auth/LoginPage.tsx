/**
 * CyberShield XDR — Login Page
 * Professional login form with validation, loading state, and error feedback.
 */
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, Shield } from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import { useAuthStore } from '@store/authStore'
import authService, { extractErrorMessage } from '@services/authService'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    try {
      const response = await authService.login(data)
      // Store refresh token separately (not in Zustand to limit exposure)
      sessionStorage.setItem('refresh_token', response.refresh_token)
      setAuth(response.user, response.access_token)
      toast.success(`Welcome back, ${response.user.full_name}!`)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const message = extractErrorMessage(err)
      if (message.includes('locked')) {
        toast.error(message, { duration: 6000 })
      } else {
        setError('password', { message })
      }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Sign in to your account</h2>
        <p className="text-gray-500 text-sm mt-1">
          Enter your credentials to access the platform
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <Input
          label="Email address"
          type="email"
          placeholder="analyst@company.com"
          autoComplete="email"
          leftIcon={<Mail className="w-4 h-4" />}
          error={errors.email?.message}
          {...register('email')}
        />

        <Input
          label="Password"
          type="password"
          placeholder="••••••••"
          autoComplete="current-password"
          leftIcon={<Lock className="w-4 h-4" />}
          error={errors.password?.message}
          {...register('password')}
        />

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="w-3.5 h-3.5 rounded border-cyber-800 bg-dark-300 text-cyber-500 focus:ring-cyber-500/30"
            />
            <span className="text-sm text-gray-400">Remember me</span>
          </label>
          <Link
            to="/forgot-password"
            className="text-sm text-cyber-400 hover:text-cyber-300 transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          className="w-full"
          leftIcon={<Shield className="w-4 h-4" />}
        >
          {isSubmitting ? 'Authenticating...' : 'Sign In'}
        </Button>
      </form>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-cyber-900/50" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-dark-100 px-3 text-gray-500">New to CyberShield?</span>
        </div>
      </div>

      <Link to="/register">
        <Button variant="outline" size="lg" className="w-full">
          Create an account
        </Button>
      </Link>

      {/* Demo credentials hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="bg-cyber-900/20 border border-cyber-900/40 rounded-lg p-3"
      >
        <p className="text-xs text-gray-500 text-center">
          <span className="text-cyber-500 font-mono">Demo:</span>{' '}
          admin@cybershield.com / Admin@123!
        </p>
      </motion.div>
    </div>
  )
}
