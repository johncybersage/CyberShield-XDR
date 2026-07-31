/**
 * CyberShield XDR — Forgot Password Page
 * Submits email for password reset. Shows success state after submission.
 */
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import authService from '@services/authService'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})

type FormData = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false)
  const [submittedEmail, setSubmittedEmail] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    await authService.forgotPassword(data.email)
    setSubmittedEmail(data.email)
    setSubmitted(true)
  }

  return (
    <AnimatePresence mode="wait">
      {submitted ? (
        <motion.div
          key="success"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-5 text-center"
        >
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-threat-low/10 border border-threat-low/30 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-threat-low" />
            </div>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Check your email</h2>
            <p className="text-gray-400 text-sm mt-2">
              If <span className="text-cyber-400">{submittedEmail}</span> is registered,
              you'll receive a password reset link within a few minutes.
            </p>
          </div>
          <p className="text-xs text-gray-500">
            Didn't receive it? Check your spam folder or{' '}
            <button
              onClick={() => setSubmitted(false)}
              className="text-cyber-400 hover:underline"
            >
              try again
            </button>
            .
          </p>
          <Link to="/login">
            <Button variant="outline" size="md" className="w-full" leftIcon={<ArrowLeft className="w-4 h-4" />}>
              Back to login
            </Button>
          </Link>
        </motion.div>
      ) : (
        <motion.div
          key="form"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-5"
        >
          <div>
            <h2 className="text-xl font-bold text-white">Reset your password</h2>
            <p className="text-gray-500 text-sm mt-1">
              Enter your email and we'll send you a reset link.
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

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? 'Sending...' : 'Send Reset Link'}
            </Button>
          </form>

          <Link to="/login">
            <Button variant="ghost" size="md" className="w-full" leftIcon={<ArrowLeft className="w-4 h-4" />}>
              Back to login
            </Button>
          </Link>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
