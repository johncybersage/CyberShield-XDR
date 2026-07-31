import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield } from 'lucide-react'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-dark-200 bg-cyber-grid flex items-center justify-center p-4">
      {/* Animated background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-cyber-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-cyber-700/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Brand header */}
        <div className="text-center mb-8">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
            className="inline-flex items-center justify-center w-16 h-16 bg-cyber-500/10 border border-cyber-500/30 rounded-2xl mb-4"
          >
            <Shield className="w-8 h-8 text-cyber-400" />
          </motion.div>
          <h1 className="text-2xl font-bold text-white">CyberShield XDR</h1>
          <p className="text-gray-500 text-sm mt-1">AI-Powered Extended Detection & Response</p>
        </div>

        {/* Auth form card */}
        <div className="bg-dark-100 border border-cyber-900/50 rounded-xl p-8 shadow-2xl shadow-black/50">
          <Outlet />
        </div>
      </motion.div>
    </div>
  )
}
