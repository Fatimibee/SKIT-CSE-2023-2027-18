import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { AudioWaveform, FileText, Globe, ChevronDown, Rocket, UserCircle, LogOut } from 'lucide-react'

export default function Navbar() {
  const [langMenuOpen, setLangMenuOpen] = useState(false)

  const languages = [
    { code: 'EN', name: 'English' },
    { code: 'HI', name: 'हिंदी' },
  ]

  const [activeLang, setActiveLang] = useState(languages[0])

  return (
    <nav className="sticky top-0 z-50 w-full bg-slate-950/80 backdrop-blur-xl border-b border-white/[0.08]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* ── Logo ── */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/25 group-hover:shadow-teal-500/40 transition-shadow">
              <AudioWaveform className="w-5 h-5 text-white absolute transform -translate-x-1.5" />
              <FileText className="w-5 h-5 text-white/70 absolute transform translate-x-2 translate-y-1 scale-75" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">YojVani</span>
          </Link>

          {/* ── Center Links (Desktop) ── */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/voice" className="text-[14px] font-medium text-slate-300 hover:text-teal-400 transition-colors">Voice Mode</Link>
            <Link to="/chat" className="text-[14px] font-medium text-slate-300 hover:text-teal-400 transition-colors">Text Chat</Link>
            <Link to="/form-upload" className="text-[14px] font-medium text-slate-300 hover:text-teal-400 transition-colors">Form Scanner</Link>
            <a href="#schemes" className="text-[14px] font-medium text-slate-300 hover:text-teal-400 transition-colors">Schemes Directory</a>
            <a href="#how-it-works" className="text-[14px] font-medium text-slate-300 hover:text-teal-400 transition-colors">How It Works</a>
          </div>

          {/* ── Right Actions ── */}
          <div className="flex items-center gap-4">
            {/* Language Selector */}
            <div className="relative">
              <button 
                onClick={() => setLangMenuOpen(!langMenuOpen)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-900 border border-white/[0.06] text-slate-300 hover:text-white hover:bg-slate-800 transition-all text-sm font-medium"
              >
                <Globe className="w-4 h-4 text-teal-500" />
                {activeLang.code}
                <ChevronDown className="w-4 h-4" />
              </button>
              
              {langMenuOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-slate-900 border border-white/[0.08] rounded-xl shadow-2xl py-2 animate-fade-in">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setActiveLang(lang);
                        setLangMenuOpen(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Profile Icon */}
            <Link
              to="/profile"
              className="flex items-center justify-center w-10 h-10 rounded-xl bg-slate-900 border border-white/[0.06] text-slate-300 hover:text-white hover:bg-slate-800 transition-all"
              title="My Profile"
            >
              <UserCircle className="w-5 h-5" />
            </Link>

            {/* CTA */}
            <Link 
              to="/login"
              className="hidden sm:flex items-center gap-2 bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-400 hover:to-emerald-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-teal-500/25 transition-all transform active:scale-95"
            >
              <Rocket className="w-4 h-4" />
              Launch YojVani
            </Link>

            {/* Sign Out */}
            <Link
              to="/login"
              className="flex items-center justify-center w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:text-red-300 hover:bg-red-500/20 transition-all ml-1"
              title="Sign Out"
            >
              <LogOut className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
