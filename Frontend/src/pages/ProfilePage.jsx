import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  AudioWaveform,
  FileText,
  UserCircle,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Edit3,
  Save,
  X,
  Mic,
  Search,
  Star,
  CheckCircle2,
  Clock,
  TrendingUp,
  Shield,
  Bell,
  LogOut,
  Camera,
  ChevronRight,
  Bookmark,
  Activity,
  Award,
} from 'lucide-react'

/* ─────────────────────────────────────────────────────────────── */
/*  Mock Data                                                       */
/* ─────────────────────────────────────────────────────────────── */

const MOCK_USER = {
  name: '',
  email: '',
  phone: '',
  location: '',
  joinDate: '',
  state: '',
  income: '',
  category: '',
}

const SAVED_SCHEMES = [
  {
    id: 1,
    name: 'PM Kisan Samman Nidhi',
    category: 'Agriculture',
    status: 'Eligible',
    gradient: 'from-teal-500 to-emerald-600',
    statusColor: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
  },
  {
    id: 2,
    name: 'Pradhan Mantri Awas Yojana',
    category: 'Housing',
    status: 'Pending',
    gradient: 'from-indigo-500 to-blue-600',
    statusColor: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
  },
  {
    id: 3,
    name: 'Ayushman Bharat PM-JAY',
    category: 'Health',
    status: 'Eligible',
    gradient: 'from-purple-500 to-pink-600',
    statusColor: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
  },
]

const RECENT_ACTIVITY = [
  { icon: Mic, text: 'Voice query: "Housing schemes in Rajasthan"', time: '2 hours ago' },
  { icon: Search, text: 'Searched for "health insurance schemes"', time: '1 day ago' },
  { icon: FileText, text: 'Uploaded Aadhaar for verification', time: '3 days ago' },
  { icon: Bookmark, text: 'Saved PM Kisan Samman Nidhi', time: '5 days ago' },
]

const STATS = [
  { label: 'Schemes Explored', value: '24', icon: Search, color: 'text-teal-400' },
  { label: 'Saved Schemes', value: '3', icon: Bookmark, color: 'text-indigo-400' },
  { label: 'Applications', value: '1', icon: CheckCircle2, color: 'text-emerald-400' },
  { label: 'Queries Made', value: '12', icon: Activity, color: 'text-purple-400' },
]

/* ─────────────────────────────────────────────────────────────── */
/*  Sub-components                                                  */
/* ─────────────────────────────────────────────────────────────── */

function AvatarRing({ name }) {
  const initials = name
    ? name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : '?'

  return (
    <div className="relative inline-block">
      <div className="absolute inset-0 rounded-full bg-gradient-to-br from-teal-400 via-emerald-500 to-indigo-500 opacity-60 blur-[2px]" />
      <div className="relative w-28 h-28 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center border-4 border-slate-950 shadow-2xl shadow-teal-500/30">
        <span className="text-3xl font-bold text-white select-none">{initials}</span>
      </div>
      <button
        className="absolute bottom-1 right-1 w-8 h-8 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center hover:bg-slate-700 transition-all shadow-lg"
        title="Change avatar"
      >
        <Camera className="w-3.5 h-3.5 text-slate-300" />
      </button>
    </div>
  )
}

function StatCard({ stat }) {
  const Icon = stat.icon
  return (
    <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-900/60 border border-white/[0.06] backdrop-blur-sm hover:border-white/[0.10] hover:bg-slate-900/80 transition-all duration-300 group">
      <Icon className={`w-5 h-5 mb-2 ${stat.color} group-hover:scale-110 transition-transform`} />
      <span className="text-2xl font-bold text-white">{stat.value}</span>
      <span className="text-[11px] text-slate-500 mt-0.5 text-center leading-tight">{stat.label}</span>
    </div>
  )
}

function InfoField({ label, value, editing, onChange, icon: Icon, type = 'text', placeholder = '' }) {
  return (
    <div className="flex items-start gap-3 p-4 rounded-xl bg-slate-900/40 border border-white/[0.04] group hover:border-white/[0.08] transition-all">
      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
        <Icon className="w-4 h-4 text-teal-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] text-slate-500 mb-1 font-medium uppercase tracking-wider">{label}</p>
        {editing ? (
          <input
            type={type}
            value={value}
            placeholder={placeholder}
            onChange={(e) => onChange(e.target.value)}
            className="w-full bg-slate-800 border border-teal-500/40 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500/80 transition-colors"
          />
        ) : (
          <p className={`text-[14px] font-medium truncate ${value ? 'text-slate-200' : 'text-slate-600 italic'}`}>
            {value || placeholder}
          </p>
        )}
      </div>
    </div>
  )
}

function SchemeCard({ scheme }) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-xl border border-white/[0.06] bg-slate-900/50 hover:border-white/[0.10] hover:bg-slate-900/70 transition-all duration-300 group cursor-pointer">
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${scheme.gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
        <Star className="w-4 h-4 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[14px] font-semibold text-white truncate">{scheme.name}</p>
        <p className="text-[12px] text-slate-500">{scheme.category}</p>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${scheme.statusColor}`}>
          {scheme.status}
        </span>
        <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
      </div>
    </div>
  )
}

function ActivityItem({ item }) {
  const Icon = item.icon
  return (
    <div className="flex items-start gap-3 py-3 border-b border-white/[0.04] last:border-0">
      <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
        <Icon className="w-3.5 h-3.5 text-teal-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[13px] text-slate-300 leading-snug">{item.text}</p>
        <div className="flex items-center gap-1 mt-1">
          <Clock className="w-3 h-3 text-slate-600" />
          <span className="text-[11px] text-slate-600">{item.time}</span>
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────── */
/*  Main Page                                                       */
/* ─────────────────────────────────────────────────────────────── */

export default function ProfilePage() {
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)
  const [activeTab, setActiveTab] = useState('info')
  const [user, setUser] = useState(MOCK_USER)
  const [draft, setDraft] = useState(MOCK_USER)

  const tabs = [
    { id: 'info', label: 'Personal Info', icon: UserCircle },
    { id: 'schemes', label: 'Saved Schemes', icon: Bookmark },
    { id: 'activity', label: 'Activity', icon: Activity },
  ]

  const handleEdit = () => {
    setDraft({ ...user })
    setEditing(true)
  }

  const handleSave = () => {
    setUser({ ...draft })
    setEditing(false)
  }

  const handleCancel = () => {
    setDraft({ ...user })
    setEditing(false)
  }

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">

      {/* ── Background Orbs ── */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-teal-600/[0.07] rounded-full blur-[130px]" />
        <div className="absolute top-1/2 -left-40 w-[400px] h-[400px] bg-indigo-600/[0.06] rounded-full blur-[120px]" />
        <div className="absolute -bottom-40 right-1/3 w-[450px] h-[450px] bg-purple-600/[0.05] rounded-full blur-[140px]" />
      </div>

      {/* ── Top Navbar ── */}
      <nav className="sticky top-0 z-50 w-full bg-slate-950/80 backdrop-blur-xl border-b border-white/[0.08]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/25">
              <AudioWaveform className="w-4 h-4 text-white absolute transform -translate-x-1" />
              <FileText className="w-4 h-4 text-white/70 absolute transform translate-x-1.5 translate-y-0.5 scale-75" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">YojVani</span>
          </Link>

          <div className="flex items-center gap-3">
            {editing ? (
              <>
                <button
                  id="profile-save-btn"
                  onClick={handleSave}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-600 text-white text-sm font-semibold hover:from-teal-400 hover:to-emerald-500 transition-all active:scale-95 shadow-lg shadow-teal-500/25"
                >
                  <Save className="w-4 h-4" />
                  Save Changes
                </button>
                <button
                  id="profile-cancel-btn"
                  onClick={handleCancel}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl border border-white/[0.08] bg-slate-900 text-slate-300 text-sm font-medium hover:text-white hover:bg-slate-800 transition-all"
                >
                  <X className="w-4 h-4" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                id="profile-edit-btn"
                onClick={handleEdit}
                className="flex items-center gap-2 px-4 py-2 rounded-xl border border-white/[0.08] bg-slate-900 text-slate-300 text-sm font-medium hover:text-white hover:bg-slate-800 transition-all"
              >
                <Edit3 className="w-4 h-4" />
                Edit Profile
              </button>
            )}
            <button
              id="profile-signout-btn"
              onClick={() => navigate('/login')}
              className="flex items-center justify-center w-9 h-9 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:text-red-300 hover:bg-red-500/20 transition-all"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      {/* ── Page Content ── */}
      <main className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-8">

        {/* ── Hero Card ── */}
        <div className="relative rounded-3xl border border-white/[0.08] bg-slate-900/50 backdrop-blur-xl overflow-hidden mb-6">
          {/* Gradient banner */}
          <div className="h-32 bg-gradient-to-r from-teal-600/30 via-emerald-600/20 to-indigo-600/30 relative overflow-hidden">
            <div className="absolute inset-0 opacity-30" style={{backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(20,184,166,0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(99,102,241,0.3) 0%, transparent 50%)'}} />
          </div>

          <div className="px-6 pb-6">
            {/* Avatar + Name row */}
            <div className="flex flex-col sm:flex-row sm:items-end gap-4 -mt-14 mb-5">
              <AvatarRing name={user.name} />
              <div className="sm:mb-1 flex-1">
                <h1 className="text-2xl font-bold text-white">{user.name}</h1>
                <p className="text-slate-400 text-sm flex items-center gap-1.5 mt-0.5">
                  <MapPin className="w-3.5 h-3.5 text-teal-400" />
                  {user.location}
                </p>
              </div>
              <div className="sm:mb-2">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-teal-400/10 border border-teal-400/20">
                  <Award className="w-3.5 h-3.5 text-teal-400" />
                  <span className="text-[12px] font-semibold text-teal-400">Verified User</span>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {STATS.map((stat) => (
                <StatCard key={stat.label} stat={stat} />
              ))}
            </div>
          </div>
        </div>

        {/* ── Tabs + Sidebar ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left: Tab panel */}
          <div className="lg:col-span-2 space-y-4">
            {/* Tab bar */}
            <div className="flex gap-1 p-1 rounded-xl bg-slate-900/60 border border-white/[0.06] backdrop-blur-sm">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    id={`profile-tab-${tab.id}`}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-[13px] font-medium transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-teal-500 to-emerald-600 text-white shadow-lg shadow-teal-500/20'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </button>
                )
              })}
            </div>

            {/* Personal Info Tab */}
            {activeTab === 'info' && (
              <div className="space-y-3">
                <InfoField label="Full Name" icon={UserCircle}
                  value={editing ? draft.name : user.name}
                  editing={editing}
                  placeholder="e.g. Ramesh Kumar"
                  onChange={(v) => setDraft({ ...draft, name: v })}
                />
                <InfoField label="Email Address" icon={Mail} type="email"
                  value={editing ? draft.email : user.email}
                  editing={editing}
                  placeholder="e.g. name@example.com"
                  onChange={(v) => setDraft({ ...draft, email: v })}
                />
                <InfoField label="Phone Number" icon={Phone} type="tel"
                  value={editing ? draft.phone : user.phone}
                  editing={editing}
                  placeholder="e.g. +91 98765 43210"
                  onChange={(v) => setDraft({ ...draft, phone: v })}
                />
                <InfoField label="Location" icon={MapPin}
                  value={editing ? draft.location : user.location}
                  editing={editing}
                  placeholder="e.g. Jaipur, Rajasthan"
                  onChange={(v) => setDraft({ ...draft, location: v })}
                />
                <InfoField label="Member Since" icon={Calendar}
                  value={user.joinDate}
                  editing={false}
                  placeholder="Not available"
                  onChange={() => {}}
                />

                {/* Eligibility profile */}
                <div className="mt-2 p-4 rounded-xl border border-indigo-500/[0.15] bg-indigo-500/[0.05]">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-sm font-semibold text-white">Eligibility Profile</h3>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {[
                      { label: 'State', value: user.state },
                      { label: 'Income Bracket', value: user.income },
                      { label: 'Category', value: user.category },
                    ].map((item) => (
                      <div key={item.label} className="bg-slate-900/60 rounded-lg px-3 py-2">
                        <p className="text-[11px] text-slate-500 uppercase tracking-wider">{item.label}</p>
                        <p className="text-[13px] text-slate-200 font-medium mt-0.5">{item.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Saved Schemes Tab */}
            {activeTab === 'schemes' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm text-slate-400">{SAVED_SCHEMES.length} saved schemes</p>
                  <button className="text-[12px] text-teal-400 hover:text-teal-300 transition-colors">
                    Browse More →
                  </button>
                </div>
                {SAVED_SCHEMES.map((scheme) => (
                  <SchemeCard key={scheme.id} scheme={scheme} />
                ))}
              </div>
            )}

            {/* Activity Tab */}
            {activeTab === 'activity' && (
              <div className="p-4 rounded-xl border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="w-4 h-4 text-teal-400" />
                  <h3 className="text-sm font-semibold text-white">Recent Activity</h3>
                </div>
                {RECENT_ACTIVITY.map((item, i) => (
                  <ActivityItem key={i} item={item} />
                ))}
              </div>
            )}
          </div>

          {/* Right: Sidebar */}
          <div className="space-y-4">
            {/* Quick Actions */}
            <div className="p-4 rounded-2xl border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm">
              <h3 className="text-sm font-semibold text-white mb-3">Quick Actions</h3>
              <div className="space-y-1">
                {[
                  { label: 'Voice Query', icon: Mic, to: '/voice', color: 'text-teal-400', bg: 'bg-teal-400/10' },
                  { label: 'Scan Documents', icon: FileText, to: '/form-upload', color: 'text-indigo-400', bg: 'bg-indigo-400/10' },
                  { label: 'Browse Schemes', icon: Search, to: '/', color: 'text-purple-400', bg: 'bg-purple-400/10' },
                  { label: 'Notifications', icon: Bell, to: '#', color: 'text-amber-400', bg: 'bg-amber-400/10' },
                ].map((item) => (
                  <Link
                    key={item.label}
                    to={item.to}
                    className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-slate-800/60 transition-all group"
                  >
                    <div className={`w-8 h-8 rounded-lg ${item.bg} flex items-center justify-center flex-shrink-0`}>
                      <item.icon className={`w-4 h-4 ${item.color}`} />
                    </div>
                    <span className="text-[13px] text-slate-300 group-hover:text-white transition-colors flex-1">
                      {item.label}
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
                  </Link>
                ))}
              </div>
            </div>

            {/* Security */}
            <div className="p-4 rounded-2xl border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-white">Account Security</h3>
              </div>
              <div className="space-y-1">
                {[
                  { label: 'Email Verified', done: true },
                  { label: 'Phone Linked', done: true },
                  { label: 'Two-Factor Auth', done: false },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0">
                    <span className="text-[13px] text-slate-400">{item.label}</span>
                    {item.done ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <button className="text-[11px] text-teal-400 hover:text-teal-300 font-medium transition-colors">
                        Enable →
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Danger zone */}
            <div className="p-4 rounded-2xl border border-red-500/[0.12] bg-red-500/[0.04]">
              <h3 className="text-sm font-semibold text-red-400 mb-3">Danger Zone</h3>
              <button
                id="profile-danger-signout"
                onClick={() => navigate('/login')}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 hover:text-red-300 hover:bg-red-500/20 text-[13px] font-medium transition-all"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
