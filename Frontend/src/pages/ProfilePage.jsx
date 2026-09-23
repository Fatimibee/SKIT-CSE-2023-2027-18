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

/* ------------------------------------------------------------------ */
/*  Mock Data                                                           */
/* ------------------------------------------------------------------ */

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
  { id: 1, name: 'PM Kisan Samman Nidhi',      category: 'Agriculture', status: 'Eligible', gradient: 'from-teal-500 to-emerald-600',  statusColor: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' },
  { id: 2, name: 'Pradhan Mantri Awas Yojana', category: 'Housing',     status: 'Pending',  gradient: 'from-indigo-500 to-blue-600',   statusColor: 'text-amber-400 bg-amber-400/10 border-amber-400/20' },
  { id: 3, name: 'Ayushman Bharat PM-JAY',      category: 'Health',      status: 'Eligible', gradient: 'from-purple-500 to-pink-600',  statusColor: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' },
]

const RECENT_ACTIVITY = [
  { icon: Mic,      text: 'Voice query: Housing schemes in Rajasthan', time: '2 hours ago' },
  { icon: Search,   text: 'Searched for health insurance schemes',     time: '1 day ago' },
  { icon: FileText, text: 'Uploaded Aadhaar for verification',         time: '3 days ago' },
  { icon: Bookmark, text: 'Saved PM Kisan Samman Nidhi',               time: '5 days ago' },
]

const STATS = [
  { label: 'Schemes Explored', value: '24', icon: Search,       color: 'text-teal-400' },
  { label: 'Saved Schemes',    value: '3',  icon: Bookmark,     color: 'text-indigo-400' },
  { label: 'Applications',     value: '1',  icon: CheckCircle2, color: 'text-emerald-400' },
  { label: 'Queries Made',     value: '12', icon: Activity,     color: 'text-purple-400' },
]

/* ------------------------------------------------------------------ */
/*  Sub-components                                                      */
/* ------------------------------------------------------------------ */

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

/**
 * InfoField — per-field inline editing.
 * readOnly=true hides the edit button.
 * The pencil button appears on row hover (group-hover) or focus.
 */
function InfoField({
  fieldKey,
  label,
  value,
  isEditing,
  onEdit,
  onSave,
  onCancel,
  onChange,
  icon: Icon,
  type = 'text',
  placeholder = '',
  readOnly = false,
}) {
  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-xl border transition-all duration-200 ${
        isEditing
          ? 'bg-slate-900/70 border-teal-500/30 shadow-lg shadow-teal-500/5'
          : 'bg-slate-900/40 border-white/[0.04] hover:border-white/[0.08] group'
      }`}
    >
      {/* Field icon */}
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors ${
          isEditing ? 'bg-teal-500/20' : 'bg-slate-800'
        }`}
      >
        <Icon className={`w-4 h-4 transition-colors ${isEditing ? 'text-teal-300' : 'text-teal-400'}`} />
      </div>

      {/* Label + value / input */}
      <div className="flex-1 min-w-0">
        <p className="text-[11px] text-slate-500 mb-1 font-medium uppercase tracking-wider">{label}</p>
        {isEditing ? (
          <input
            type={type}
            value={value}
            placeholder={placeholder}
            onChange={(e) => onChange(e.target.value)}
            autoFocus
            className="w-full bg-slate-800 border border-teal-500/50 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-500/30 transition-all"
          />
        ) : (
          <p className={`text-[14px] font-medium truncate ${value ? 'text-slate-200' : 'text-slate-600 italic'}`}>
            {value || placeholder}
          </p>
        )}
      </div>

      {/* Action buttons */}
      {!readOnly && (
        <div className="flex items-center gap-1 flex-shrink-0 mt-0.5">
          {isEditing ? (
            <>
              <button
                id={`field-save-${fieldKey}`}
                onClick={onSave}
                title="Save"
                className="w-7 h-7 rounded-lg bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400 hover:bg-teal-500/30 hover:text-teal-300 transition-all active:scale-95"
              >
                <Save className="w-3.5 h-3.5" />
              </button>
              <button
                id={`field-cancel-${fieldKey}`}
                onClick={onCancel}
                title="Cancel"
                className="w-7 h-7 rounded-lg bg-slate-800 border border-white/[0.06] flex items-center justify-center text-slate-400 hover:bg-slate-700 hover:text-white transition-all active:scale-95"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </>
          ) : (
            <button
              id={`field-edit-${fieldKey}`}
              onClick={onEdit}
              title={`Edit ${label}`}
              className="w-7 h-7 rounded-lg bg-slate-800 border border-white/[0.06] flex items-center justify-center text-slate-500 hover:bg-slate-700 hover:text-teal-400 hover:border-teal-500/30 transition-all active:scale-95 opacity-0 group-hover:opacity-100 focus:opacity-100"
            >
              <Edit3 className="w-3 h-3" />
            </button>
          )}
        </div>
      )}
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

/* ------------------------------------------------------------------ */
/*  Main Page                                                           */
/* ------------------------------------------------------------------ */

export default function ProfilePage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('info')
  const [user, setUser] = useState(MOCK_USER)
  const [fieldEdits, setFieldEdits] = useState({})

  const tabs = [
    { id: 'info',     label: 'Personal Info', icon: UserCircle },
    { id: 'schemes',  label: 'Saved Schemes', icon: Bookmark },
    { id: 'activity', label: 'Activity',      icon: Activity },
  ]

  const handleFieldEdit   = (k) => setFieldEdits((p) => ({ ...p, [k]: user[k] }))
  const handleFieldSave   = (k) => {
    setUser((p) => ({ ...p, [k]: fieldEdits[k] }))
    setFieldEdits((p) => { const n = { ...p }; delete n[k]; return n })
  }
  const handleFieldCancel = (k) =>
    setFieldEdits((p) => { const n = { ...p }; delete n[k]; return n })

  const isEditing  = (k) => k in fieldEdits
  const fieldValue = (k) => isEditing(k) ? fieldEdits[k] : user[k]

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">

      {/* Background orbs */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-teal-600/[0.07] rounded-full blur-[130px]" />
        <div className="absolute top-1/2 -left-40 w-[400px] h-[400px] bg-indigo-600/[0.06] rounded-full blur-[120px]" />
        <div className="absolute -bottom-40 right-1/3 w-[450px] h-[450px] bg-purple-600/[0.05] rounded-full blur-[140px]" />
      </div>

      {/* Navbar */}
      <nav className="sticky top-0 z-50 w-full bg-slate-950/80 backdrop-blur-xl border-b border-white/[0.08]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/25">
              <AudioWaveform className="w-4 h-4 text-white absolute transform -translate-x-1" />
              <FileText className="w-4 h-4 text-white/70 absolute transform translate-x-1.5 translate-y-0.5 scale-75" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">YojVani</span>
          </Link>
          <button
            id="profile-signout-btn"
            onClick={() => navigate('/login')}
            className="flex items-center justify-center w-9 h-9 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:text-red-300 hover:bg-red-500/20 transition-all"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </nav>

      {/* Main content */}
      <main className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-8">

        {/* Hero card */}
        <div className="relative rounded-3xl border border-white/[0.08] bg-slate-900/50 backdrop-blur-xl overflow-hidden mb-6">
          <div className="h-32 bg-gradient-to-r from-teal-600/30 via-emerald-600/20 to-indigo-600/30 relative overflow-hidden">
            <div
              className="absolute inset-0 opacity-30"
              style={{ backgroundImage: 'radial-gradient(circle at 20% 50%,rgba(20,184,166,.3) 0%,transparent 50%),radial-gradient(circle at 80% 20%,rgba(99,102,241,.3) 0%,transparent 50%)' }}
            />
          </div>
          <div className="px-6 pb-6">
            <div className="flex flex-col sm:flex-row sm:items-end gap-4 -mt-14 mb-5">
              <AvatarRing name={user.name} />
              <div className="sm:mb-1 flex-1">
                <h1 className="text-2xl font-bold text-white">
                  {user.name || <span className="text-slate-600 italic font-normal text-lg">No name set</span>}
                </h1>
                <p className="text-slate-400 text-sm flex items-center gap-1.5 mt-0.5">
                  <MapPin className="w-3.5 h-3.5 text-teal-400" />
                  {user.location || <span className="text-slate-600 italic">No location set</span>}
                </p>
              </div>
              <div className="sm:mb-2">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-teal-400/10 border border-teal-400/20">
                  <Award className="w-3.5 h-3.5 text-teal-400" />
                  <span className="text-[12px] font-semibold text-teal-400">Verified User</span>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {STATS.map((s) => <StatCard key={s.label} stat={s} />)}
            </div>
          </div>
        </div>

        {/* Tabs + Sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Tab panel */}
          <div className="lg:col-span-2 space-y-4">

            {/* Tab bar */}
            <div className="flex gap-1 p-1 rounded-xl bg-slate-900/60 border border-white/[0.06] backdrop-blur-sm">
              {tabs.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  id={`profile-tab-${id}`}
                  onClick={() => setActiveTab(id)}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-[13px] font-medium transition-all duration-200 ${
                    activeTab === id
                      ? 'bg-gradient-to-r from-teal-500 to-emerald-600 text-white shadow-lg shadow-teal-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{label}</span>
                </button>
              ))}
            </div>

            {/* Personal Info */}
            {activeTab === 'info' && (
              <div className="space-y-3">
                <p className="text-[12px] text-slate-600 px-1 flex items-center gap-1.5">
                  <Edit3 className="w-3 h-3" />
                  Hover over a field and click the pencil icon to edit
                </p>

                <InfoField fieldKey="name" label="Full Name" icon={UserCircle}
                  value={fieldValue('name')} isEditing={isEditing('name')}
                  placeholder="e.g. Ramesh Kumar"
                  onEdit={() => handleFieldEdit('name')}
                  onSave={() => handleFieldSave('name')}
                  onCancel={() => handleFieldCancel('name')}
                  onChange={(v) => setFieldEdits((p) => ({ ...p, name: v }))} />

                <InfoField fieldKey="email" label="Email Address" icon={Mail} type="email"
                  value={fieldValue('email')} isEditing={isEditing('email')}
                  placeholder="e.g. name@example.com"
                  onEdit={() => handleFieldEdit('email')}
                  onSave={() => handleFieldSave('email')}
                  onCancel={() => handleFieldCancel('email')}
                  onChange={(v) => setFieldEdits((p) => ({ ...p, email: v }))} />

                <InfoField fieldKey="phone" label="Phone Number" icon={Phone} type="tel"
                  value={fieldValue('phone')} isEditing={isEditing('phone')}
                  placeholder="e.g. +91 98765 43210"
                  onEdit={() => handleFieldEdit('phone')}
                  onSave={() => handleFieldSave('phone')}
                  onCancel={() => handleFieldCancel('phone')}
                  onChange={(v) => setFieldEdits((p) => ({ ...p, phone: v }))} />

                <InfoField fieldKey="location" label="Location" icon={MapPin}
                  value={fieldValue('location')} isEditing={isEditing('location')}
                  placeholder="e.g. Jaipur, Rajasthan"
                  onEdit={() => handleFieldEdit('location')}
                  onSave={() => handleFieldSave('location')}
                  onCancel={() => handleFieldCancel('location')}
                  onChange={(v) => setFieldEdits((p) => ({ ...p, location: v }))} />

                <InfoField fieldKey="joinDate" label="Member Since" icon={Calendar}
                  value={user.joinDate} isEditing={false}
                  placeholder="Not available" readOnly
                  onEdit={() => {}} onSave={() => {}} onCancel={() => {}} onChange={() => {}} />

                {/* Eligibility profile */}
                <div className="mt-2 p-4 rounded-xl border border-indigo-500/[0.15] bg-indigo-500/[0.05]">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-sm font-semibold text-white">Eligibility Profile</h3>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {[
                      { label: 'State',          value: user.state },
                      { label: 'Income Bracket', value: user.income },
                      { label: 'Category',       value: user.category },
                    ].map((item) => (
                      <div key={item.label} className="bg-slate-900/60 rounded-lg px-3 py-2">
                        <p className="text-[11px] text-slate-500 uppercase tracking-wider">{item.label}</p>
                        <p className="text-[13px] text-slate-200 font-medium mt-0.5">
                          {item.value || <span className="text-slate-600 italic font-normal">&#8212;</span>}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Saved Schemes */}
            {activeTab === 'schemes' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm text-slate-400">{SAVED_SCHEMES.length} saved schemes</p>
                  <button className="text-[12px] text-teal-400 hover:text-teal-300 transition-colors">Browse More &#8594;</button>
                </div>
                {SAVED_SCHEMES.map((s) => <SchemeCard key={s.id} scheme={s} />)}
              </div>
            )}

            {/* Activity */}
            {activeTab === 'activity' && (
              <div className="p-4 rounded-xl border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="w-4 h-4 text-teal-400" />
                  <h3 className="text-sm font-semibold text-white">Recent Activity</h3>
                </div>
                {RECENT_ACTIVITY.map((item, i) => <ActivityItem key={i} item={item} />)}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">

            {/* Quick Actions */}
            <div className="p-4 rounded-2xl border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm">
              <h3 className="text-sm font-semibold text-white mb-3">Quick Actions</h3>
              <div className="space-y-1">
                {[
                  { label: 'Voice Query',    icon: Mic,      to: '/voice',       color: 'text-teal-400',   bg: 'bg-teal-400/10' },
                  { label: 'Scan Documents', icon: FileText, to: '/form-upload', color: 'text-indigo-400', bg: 'bg-indigo-400/10' },
                  { label: 'Browse Schemes', icon: Search,   to: '/',            color: 'text-purple-400', bg: 'bg-purple-400/10' },
                  { label: 'Notifications',  icon: Bell,     to: '#',            color: 'text-amber-400',  bg: 'bg-amber-400/10' },
                ].map((item) => (
                  <Link key={item.label} to={item.to} className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-slate-800/60 transition-all group">
                    <div className={`w-8 h-8 rounded-lg ${item.bg} flex items-center justify-center flex-shrink-0`}>
                      <item.icon className={`w-4 h-4 ${item.color}`} />
                    </div>
                    <span className="text-[13px] text-slate-300 group-hover:text-white transition-colors flex-1">{item.label}</span>
                    <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
                  </Link>
                ))}
              </div>
            </div>

            {/* Account Security */}
            <div className="p-4 rounded-2xl border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-white">Account Security</h3>
              </div>
              <div className="space-y-1">
                {[
                  { label: 'Email Verified',  done: true },
                  { label: 'Phone Linked',    done: true },
                  { label: 'Two-Factor Auth', done: false },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0">
                    <span className="text-[13px] text-slate-400">{item.label}</span>
                    {item.done
                      ? <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      : <button className="text-[11px] text-teal-400 hover:text-teal-300 font-medium transition-colors">Enable &#8594;</button>
                    }
                  </div>
                ))}
              </div>
            </div>

            {/* Danger Zone */}
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
