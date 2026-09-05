import React from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Mic, FileText, Search, Sparkles, ArrowRight } from 'lucide-react'

/**
 * DashboardPage — Mock dashboard shown after successful login.
 * Demonstrates route transition; will be replaced with the real
 * dashboard when AI/backend integration is ready.
 */
export default function DashboardPage() {
  const navigate = useNavigate()

  const actions = [
    {
      icon: Mic,
      title: 'Voice Query',
      description: 'Ask about schemes using your voice',
      gradient: 'from-teal-500 to-emerald-600',
      glow: 'shadow-teal-500/20',
    },
    {
      icon: FileText,
      title: 'Upload Document',
      description: 'Verify eligibility via Aadhaar, PAN, etc.',
      gradient: 'from-indigo-500 to-blue-600',
      glow: 'shadow-indigo-500/20',
    },
    {
      icon: Search,
      title: 'Browse Schemes',
      description: 'Explore all government welfare schemes',
      gradient: 'from-purple-500 to-pink-600',
      glow: 'shadow-purple-500/20',
    },
  ]

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">

      {/* Background */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-32 -right-32 w-[400px] h-[400px] bg-indigo-600/[0.08] rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] bg-purple-600/[0.06] rounded-full blur-[140px] animate-pulse-slow animation-delay-2000" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/[0.06] bg-slate-900/50 backdrop-blur-xl">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-[18px] h-[18px] text-white" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">YojVani</span>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="
              flex items-center gap-2 px-4 py-2 rounded-lg
              text-[13px] font-medium text-slate-400
              border border-white/[0.06] bg-white/[0.02]
              hover:text-white hover:border-white/[0.12] hover:bg-white/[0.04]
              transition-all duration-200 active:scale-95
            "
          >
            <LogOut size={15} />
            Sign Out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-5xl mx-auto px-6 py-10 animate-fade-in-up">
        {/* Welcome */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back! 👋
          </h1>
          <p className="text-slate-400 text-[15px]">
            Find the government schemes you're eligible for — powered by AI.
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {actions.map((action) => (
            <button
              key={action.title}
              className={`
                group text-left p-6 rounded-2xl
                border border-white/[0.06] bg-slate-900/50 backdrop-blur-sm
                hover:border-white/[0.10] hover:bg-slate-900/70
                transition-all duration-300 hover:scale-[1.02]
                hover:shadow-xl ${action.glow}
              `}
            >
              <div className={`
                w-11 h-11 rounded-xl bg-gradient-to-br ${action.gradient}
                flex items-center justify-center mb-4 shadow-lg ${action.glow}
              `}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-[15px] font-semibold text-white mb-1 flex items-center gap-1.5">
                {action.title}
                <ArrowRight size={14} className="opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200 text-slate-400" />
              </h3>
              <p className="text-[13px] text-slate-500 leading-relaxed">
                {action.description}
              </p>
            </button>
          ))}
        </div>

        {/* Mock status banner */}
        <div className="mt-8 p-4 rounded-xl border border-indigo-500/[0.15] bg-indigo-500/[0.05] flex items-start gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-400 mt-1.5 animate-pulse flex-shrink-0" />
          <div>
            <p className="text-[13px] font-medium text-slate-300">
              This is a mock dashboard — authentication will connect to your Spring Boot backend.
            </p>
            <p className="text-[12px] text-slate-500 mt-0.5">
              Voice query, document upload, and scheme search features are coming next.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
