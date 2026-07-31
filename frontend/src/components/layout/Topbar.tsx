import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Menu, Bell, LogOut, User, ChevronDown } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@store/authStore'
import { format } from 'date-fns'

interface TopbarProps {
  // sidebarOpen removed as unused
  onToggleSidebar: () => void
}

export default function Topbar({ onToggleSidebar }: TopbarProps) {
  const [time, setTime] = useState(new Date())
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-14 bg-dark-100 border-b border-cyber-900/50 flex items-center justify-between px-4 flex-shrink-0">
      {/* Left */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="text-gray-400 hover:text-cyber-400 transition-colors p-1.5 rounded"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="hidden sm:flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-threat-low animate-pulse" />
          <span className="text-xs text-gray-500 font-mono">SYSTEM ONLINE</span>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-3">
        {/* Live clock */}
        <span className="hidden md:block text-xs font-mono text-cyber-600">
          {format(time, 'HH:mm:ss')} UTC
        </span>

        {/* Notifications */}
        <button
          onClick={() => navigate('/notifications')}
          className="relative text-gray-400 hover:text-cyber-400 transition-colors p-1.5 rounded"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-0.5 right-0.5 w-2 h-2 bg-threat-critical rounded-full" />
        </button>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen((v) => !v)}
            className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
          >
            <div className="w-7 h-7 rounded-full bg-cyber-700 flex items-center justify-center text-xs font-bold">
              {user?.full_name.charAt(0).toUpperCase()}
            </div>
            <span className="hidden sm:block text-sm">{user?.full_name}</span>
            <ChevronDown className="w-3 h-3 text-gray-500" />
          </button>

          <AnimatePresence>
            {userMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-10 w-44 bg-dark-50 border border-cyber-900/50 rounded-lg shadow-xl z-50 overflow-hidden"
              >
                <button
                  onClick={() => { navigate('/profile'); setUserMenuOpen(false) }}
                  className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
                >
                  <User className="w-4 h-4" /> Profile
                </button>
                <div className="border-t border-cyber-900/50" />
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-threat-critical hover:bg-threat-critical/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" /> Logout
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  )
}
