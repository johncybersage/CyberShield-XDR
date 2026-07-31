import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import AppLayout from '@components/layout/AppLayout'
import AuthLayout from '@components/layout/AuthLayout'
import LoadingScreen from '@components/common/LoadingScreen'

// Lazy-loaded pages for code splitting
const LoginPage        = lazy(() => import('@pages/auth/LoginPage'))
const RegisterPage     = lazy(() => import('@pages/auth/RegisterPage'))
const ForgotPassword   = lazy(() => import('@pages/auth/ForgotPasswordPage'))
const Dashboard        = lazy(() => import('@pages/Dashboard'))
const Assets           = lazy(() => import('@pages/Assets'))
const Alerts           = lazy(() => import('@pages/Alerts'))
const VulnScanner      = lazy(() => import('@pages/VulnerabilityScanner'))
const NetworkIDS       = lazy(() => import('@pages/NetworkIDS'))
const ThreatIntel      = lazy(() => import('@pages/ThreatIntelligence'))
const MalwareAnalysis  = lazy(() => import('@pages/MalwareAnalysis'))
const PhishingDetector = lazy(() => import('@pages/PhishingDetector'))
const AIAssistant      = lazy(() => import('@pages/AIAssistant'))
const Reports          = lazy(() => import('@pages/Reports'))
const Notifications    = lazy(() => import('@pages/Notifications'))
const Logs             = lazy(() => import('@pages/Logs'))
const Settings         = lazy(() => import('@pages/Settings'))
const Profile          = lazy(() => import('@pages/Profile'))
const AdminPanel       = lazy(() => import('@pages/AdminPanel'))
const NotFound         = lazy(() => import('@pages/NotFound'))

/** Route guard — redirects unauthenticated users to login */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

/** Route guard — redirects authenticated users away from auth pages */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>
}

export default function App() {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        {/* Public */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Auth */}
        <Route element={<AuthLayout />}>
          <Route path="/login"           element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register"        element={<PublicRoute><RegisterPage /></PublicRoute>} />
          <Route path="/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
        </Route>

        {/* Protected App */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard"          element={<Dashboard />} />
          <Route path="/assets"             element={<Assets />} />
          <Route path="/alerts"             element={<Alerts />} />
          <Route path="/scanner"            element={<VulnScanner />} />
          <Route path="/ids"                element={<NetworkIDS />} />
          <Route path="/threat-intel"       element={<ThreatIntel />} />
          <Route path="/malware"            element={<MalwareAnalysis />} />
          <Route path="/phishing"           element={<PhishingDetector />} />
          <Route path="/ai-assistant"       element={<AIAssistant />} />
          <Route path="/reports"            element={<Reports />} />
          <Route path="/notifications"      element={<Notifications />} />
          <Route path="/logs"               element={<Logs />} />
          <Route path="/settings"           element={<Settings />} />
          <Route path="/profile"            element={<Profile />} />
          <Route path="/admin"              element={<AdminPanel />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}
