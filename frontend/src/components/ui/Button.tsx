/**
 * CyberShield XDR — Button Component
 * Variants: primary (cyber blue), secondary, danger, ghost
 */
import { forwardRef } from 'react'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { cn } from '@utils/cn'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const variants = {
  primary:   'bg-cyber-500 hover:bg-cyber-400 text-dark-500 font-semibold shadow-lg shadow-cyber-500/20',
  secondary: 'bg-dark-50 hover:bg-dark-100 text-white border border-cyber-900/50',
  danger:    'bg-threat-critical/10 hover:bg-threat-critical/20 text-threat-critical border border-threat-critical/30',
  ghost:     'hover:bg-white/5 text-gray-400 hover:text-white',
  outline:   'border border-cyber-700 text-cyber-400 hover:bg-cyber-500/10',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs rounded-md',
  md: 'px-4 py-2 text-sm rounded-lg',
  lg: 'px-6 py-3 text-base rounded-lg',
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <motion.button
        ref={ref}
        whileTap={{ scale: 0.97 }}
        className={cn(
          'inline-flex items-center justify-center gap-2 transition-all duration-150',
          'focus:outline-none focus:ring-2 focus:ring-cyber-500/50 focus:ring-offset-2 focus:ring-offset-dark-200',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || loading}
        {...(props as React.ComponentProps<typeof motion.button>)}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          leftIcon && <span className="flex-shrink-0">{leftIcon}</span>
        )}
        {children}
        {!loading && rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </motion.button>
    )
  }
)

Button.displayName = 'Button'
export default Button
