import { motion } from 'framer-motion'
import { Shield } from 'lucide-react'

export default function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-dark-200 flex items-center justify-center z-50">
      <div className="flex flex-col items-center gap-4">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <Shield className="w-12 h-12 text-cyber-500" />
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-cyber-400 font-mono text-sm tracking-widest uppercase"
        >
          Initializing...
        </motion.p>
      </div>
    </div>
  )
}
