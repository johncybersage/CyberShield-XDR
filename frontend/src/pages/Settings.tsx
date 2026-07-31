import { useState } from 'react'
import { User, Lock, Bell, Key, Save, Shield } from 'lucide-react'
import Button from '@components/ui/Button'
import toast from 'react-hot-toast'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('account')

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success('Settings saved successfully')
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-6 text-white pb-6 max-w-5xl mx-auto w-full">
      
      <div className="flex justify-between items-end shrink-0 pt-4">
        <div>
          <h1 className="text-2xl font-bold font-heading text-white">Settings</h1>
          <p className="text-gray-400 text-sm mt-1">Manage your account preferences and platform configurations.</p>
        </div>
      </div>

      <div className="flex flex-1 gap-8 overflow-hidden">
        
        {/* Navigation Sidebar */}
        <div className="w-64 shrink-0 flex flex-col gap-2">
          <button 
            className={`flex items-center gap-3 w-full p-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'account' ? 'bg-brand-500/20 text-brand-400' : 'text-gray-400 hover:bg-dark-300'}`}
            onClick={() => setActiveTab('account')}
          >
            <User className="w-4 h-4" /> Account Profile
          </button>
          <button 
            className={`flex items-center gap-3 w-full p-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'security' ? 'bg-brand-500/20 text-brand-400' : 'text-gray-400 hover:bg-dark-300'}`}
            onClick={() => setActiveTab('security')}
          >
            <Lock className="w-4 h-4" /> Security & MFA
          </button>
          <button 
            className={`flex items-center gap-3 w-full p-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'notifications' ? 'bg-brand-500/20 text-brand-400' : 'text-gray-400 hover:bg-dark-300'}`}
            onClick={() => setActiveTab('notifications')}
          >
            <Bell className="w-4 h-4" /> Notifications
          </button>
          <button 
            className={`flex items-center gap-3 w-full p-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'api' ? 'bg-brand-500/20 text-brand-400' : 'text-gray-400 hover:bg-dark-300'}`}
            onClick={() => setActiveTab('api')}
          >
            <Key className="w-4 h-4" /> API Keys
          </button>
        </div>

        {/* Settings Content */}
        <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 overflow-y-auto">
          <form onSubmit={handleSave} className="p-8 space-y-8 max-w-2xl">
            
            {activeTab === 'account' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <h2 className="text-lg font-bold border-b border-dark-200 pb-2">Profile Information</h2>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-20 h-20 bg-dark-400 rounded-full border border-dark-200 flex items-center justify-center text-2xl font-bold text-gray-500">
                      JD
                    </div>
                    <Button variant="secondary" type="button">Change Avatar</Button>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">First Name</label>
                      <input type="text" defaultValue="John" className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Last Name</label>
                      <input type="text" defaultValue="Doe" className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Email Address</label>
                    <input type="email" defaultValue="admin@cybershield.com" className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none text-gray-500" disabled />
                    <p className="text-xs text-gray-500 mt-1">Email address cannot be changed. Contact IT support.</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <h2 className="text-lg font-bold border-b border-dark-200 pb-2">Security Settings</h2>
                
                <div className="bg-dark-400 p-4 rounded-lg border border-dark-200 flex items-center justify-between">
                  <div>
                    <h3 className="font-medium flex items-center gap-2"><Shield className="w-4 h-4 text-green-500" /> Multi-Factor Authentication</h3>
                    <p className="text-sm text-gray-400 mt-1">Secure your account with TOTP or hardware keys.</p>
                  </div>
                  <Button variant="primary" type="button">Configure MFA</Button>
                </div>

                <div className="space-y-4 pt-4">
                  <h3 className="font-medium text-gray-300">Change Password</h3>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Current Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">New Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Confirm New Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-dark-400 border border-dark-200 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none" />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <h2 className="text-lg font-bold border-b border-dark-200 pb-2">Notification Preferences</h2>
                <div className="space-y-4">
                  
                  <div className="flex items-center justify-between p-3 bg-dark-400 rounded-lg border border-dark-200">
                    <div>
                      <div className="font-medium">Critical Alerts</div>
                      <div className="text-xs text-gray-400">Receive immediate emails for Critical severity alerts.</div>
                    </div>
                    <input type="checkbox" className="w-4 h-4 accent-brand-500" defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-dark-400 rounded-lg border border-dark-200">
                    <div>
                      <div className="font-medium">Daily Digest</div>
                      <div className="text-xs text-gray-400">Receive a daily summary of low and medium alerts.</div>
                    </div>
                    <input type="checkbox" className="w-4 h-4 accent-brand-500" />
                  </div>

                  <div className="flex items-center justify-between p-3 bg-dark-400 rounded-lg border border-dark-200">
                    <div>
                      <div className="font-medium">System Updates</div>
                      <div className="text-xs text-gray-400">Platform maintenance and feature announcements.</div>
                    </div>
                    <input type="checkbox" className="w-4 h-4 accent-brand-500" defaultChecked />
                  </div>

                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <h2 className="text-lg font-bold border-b border-dark-200 pb-2">API Keys</h2>
                <p className="text-sm text-gray-400 mb-4">Manage API keys to access the CyberShield XDR platform programmatically.</p>
                
                <div className="bg-dark-400 p-6 text-center rounded-lg border border-dark-200 border-dashed">
                  <Key className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm mb-4">No active API keys found.</p>
                  <Button variant="secondary" type="button">Generate New Key</Button>
                </div>
              </div>
            )}

            <div className="pt-6 mt-6 border-t border-dark-200">
              <Button variant="primary" type="submit" className="w-full sm:w-auto">
                <Save className="w-4 h-4 mr-2" /> Save Changes
              </Button>
            </div>
          </form>
        </div>

      </div>
    </div>
  )
}
