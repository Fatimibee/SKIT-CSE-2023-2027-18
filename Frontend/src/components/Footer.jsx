import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Type, Sun, Volume2, ShieldAlert } from 'lucide-react'

export default function Footer() {
  const [fontSize, setFontSize] = useState('Default')
  const [highContrast, setHighContrast] = useState(false)

  useEffect(() => {
    if (highContrast) {
      document.body.classList.add('high-contrast')
    } else {
      document.body.classList.remove('high-contrast')
    }
  }, [highContrast])

  return (
    <footer className="relative z-50 bg-black text-slate-300 py-16 border-t border-white/[0.1] mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          
          {/* Column 1: Mission Statement */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white tracking-tight">YojVani</h3>
            <p className="text-sm leading-relaxed text-slate-400">
              Your Voice for Every Scheme. Empowering citizens through Voice, Text, and Form AI to discover eligible government welfare programs in local dialects effortlessly.
            </p>
          </div>

          {/* Column 2: Direct Links */}
          <div className="space-y-4">
            <h4 className="text-white font-semibold tracking-wide uppercase text-sm">Quick Links</h4>
            <ul className="space-y-2">
              <li><Link to="/voice" className="text-sm hover:text-white transition-colors">Voice Tool</Link></li>
              <li><Link to="/chat" className="text-sm hover:text-white transition-colors">Text Chat</Link></li>
              <li><Link to="/form-upload" className="text-sm hover:text-white transition-colors">Form Upload</Link></li>
              <li><a href="#schemes" className="text-sm hover:text-white transition-colors">Scheme Directory</a></li>
              <li><a href="#faqs" className="text-sm hover:text-white transition-colors">FAQs</a></li>
            </ul>
          </div>

          {/* Column 3: Accessibility Panel */}
          <div className="space-y-4">
            <h4 className="text-white font-semibold tracking-wide uppercase text-sm">Accessibility</h4>
            <div className="space-y-3 bg-white/[0.03] border border-white/[0.08] p-4 rounded-xl">
              
              <button 
                onClick={() => setFontSize(fontSize === 'Default' ? 'Large' : 'Default')}
                className="flex items-center gap-3 w-full text-left text-sm hover:text-white transition-colors"
              >
                <Type className="w-4 h-4 text-teal-500" />
                Font Size: <span className="font-medium text-white">{fontSize}</span>
              </button>

              <button 
                onClick={() => setHighContrast(!highContrast)}
                className="flex items-center gap-3 w-full text-left text-sm hover:text-white transition-colors"
              >
                <Sun className="w-4 h-4 text-teal-500" />
                High Contrast: <span className="font-medium text-white">{highContrast ? 'On' : 'Off'}</span>
              </button>

              <button 
                className="flex items-center gap-3 w-full text-left text-sm hover:text-white transition-colors"
                onClick={() => alert("Audio Reader coming soon.")}
              >
                <Volume2 className="w-4 h-4 text-teal-500" />
                Audio Reader
              </button>
            </div>
          </div>

          {/* Column 4: Legal Disclaimer */}
          <div className="space-y-4">
            <h4 className="flex items-center gap-2 text-white font-semibold tracking-wide uppercase text-sm">
              <ShieldAlert className="w-4 h-4 text-yellow-500" />
              Disclaimer
            </h4>
            <div className="text-sm text-slate-400 leading-relaxed border-l-2 border-yellow-500/50 pl-3">
              YojVani is an independent AI informational assistant. We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with any official government body.
            </div>
          </div>

        </div>

        <div className="mt-16 pt-8 border-t border-white/[0.08] flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-500">© {new Date().getFullYear()} YojVani. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="text-xs text-slate-500 hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="text-xs text-slate-500 hover:text-white transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
