import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Shield, LayoutDashboard, Monitor, AlertTriangle, Search,
  Network, Globe, Bug, Mail, Bot, FileText, Bell,
  ScrollText, Settings, Users, ChevronLeft,
} from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import { cn } from '@utils/cn'

interface NavItem {
  label: string
  path: string
  icon: React.ElementType
  roles?: string[]
  badge?: string
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',      path: '/dashboard',    icon: LayoutDashboard },
  { label: 'Assets',         path: '/assets',       icon: Monitor },
  { label: 'Alerts',         path: '/alerts',       icon: AlertTriangle },
  { label: 'Vuln Scanner',   path: '/scanner',      icon: Search },
  { label: 'Network IDS',    path: '/ids',          icon: Network },
  { label: 'Threat Intel',   path: '/threat-intel', icon: Globe },
  { label: 'Malware',        path: '/malware',      icon: Bug },
  { label: 'Phishing',       path: '/phishing',     icon: Mail },
  { label: 'AI Assistant',   path: '/ai-assistant', icon: Bot },
  { label: 'Reports',        path: '/reports',      icon: FileText },
  { label: 'Notifications',  path: '/notifications',icon: Bell },
  { label: 'Logs',           path: '/logs',         icon: ScrollText },
  { label: 'Settings',       path: '/settings',     icon: Settings },
  { label: 'Admin',          path: '/admin',        icon: Users, roles: ['admin'] },
]

interface SidebarProps {
  onClose: () => void
}

export default function Sidebar({ onClose }: SidebarProps) {
  const user = useAuthStore((s) => s.user)

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role))
  )

  return (
    <aside className="w-64 h-full bg-dark-100 border-r border-cyber-900/50 flex flex-col">
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-cyber-900/50">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            <Shield className="w-7 h-7 text-cyber-400" />
          </motion.div>
          <div>
            <p className="text-white font-bold text-sm leading-none">CyberShield</p>
            <p className="text-cyber-500 text-xs font-mono">XDR Platform</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-cyber-400 transition-colors p-1 rounded"
          aria-label="Close sidebar"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-cyber-500/10 text-cyber-400 border border-cyber-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={cn(
                    'w-4 h-4 flex-shrink-0 transition-colors',
                    isActive ? 'text-cyber-400' : 'text-gray-500 group-hover:text-gray-300'
                  )}
                />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="active-indicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-cyber-400"
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User info */}
      {user && (
        <div className="px-4 py-3 border-t border-cyber-900/50">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-cyber-700 flex items-center justify-center text-xs font-bold text-white">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-white text-xs font-medium truncate">{user.full_name}</p>
              <p className="text-gray-500 text-xs capitalize">{user.role.replace('_', ' ')}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
