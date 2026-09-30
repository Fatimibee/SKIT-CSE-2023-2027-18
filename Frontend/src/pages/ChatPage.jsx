import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Mic, MicOff, Play, Pause, RotateCcw, Send, 
  Paperclip, ChevronLeft, Globe, Sparkles, AudioWaveform, 
  FileText, IndianRupee, Bookmark, BookmarkCheck, Copy, Check
} from 'lucide-react'

/* ------------------------------------------------------------------ */
/*  Mock Data                                                           */
/* ------------------------------------------------------------------ */

const LANGUAGES = [
  { code: 'EN', label: 'English', native: 'English' },
  { code: 'HI', label: 'Hindi', native: 'हिंदी' },
  { code: 'MR', label: 'Marathi', native: 'मराठी' },
  { code: 'TA', label: 'Tamil', native: 'தமிழ்' },
  { code: 'TE', label: 'Telugu', native: 'తెలుగు' }
]

const DEMO_SUGGESTED_SCHEMES = [
  {
    id: 'pm-kisan',
    title: 'PM Kisan Samman Nidhi',
    category: 'Agriculture',
    payout: '₹6,000 / year',
    gradient: 'from-teal-500 to-emerald-600',
    description: 'Financial assistance of ₹6,000 per year to small and marginal farmers.',
  },
  {
    id: 'pmay-urban',
    title: 'PM Awas Yojana',
    category: 'Housing',
    payout: '₹2.67 L subsidy',
    gradient: 'from-indigo-500 to-blue-600',
    description: 'Credit-linked subsidy for construction or purchase of houses.',
  }
]

/* ------------------------------------------------------------------ */
/*  Components                                                          */
/* ------------------------------------------------------------------ */

function AudioWaveBars({ count = 12 }) {
  return (
    <div className="flex items-center justify-center gap-1 h-8">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className="w-1.5 bg-teal-400 rounded-full"
          animate={{ height: ['20%', '80%', '20%'] }}
          transition={{ duration: 0.8 + Math.random() * 0.5, repeat: Infinity, delay: Math.random() * 0.5 }}
        />
      ))}
    </div>
  )
}

function ChatMessage({ msg }) {
  const isUser = msg.role === 'user'
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(msg.text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 max-w-3xl mx-auto w-full mb-6 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center shadow-lg mt-1 ${isUser ? 'bg-slate-800 border border-white/[0.08]' : 'bg-gradient-to-br from-teal-500 to-emerald-600 shadow-teal-500/25'}`}>
        {isUser ? <FileText className="w-4 h-4 text-slate-400" /> : <Sparkles className="w-4 h-4 text-white" />}
      </div>

      {/* Bubble */}
      <div className={`group relative px-5 py-4 rounded-3xl max-w-[85%] ${isUser ? 'bg-slate-800 text-slate-200 border border-white/[0.05] rounded-tr-sm' : 'bg-slate-900/60 backdrop-blur-md border border-teal-500/10 text-slate-300 rounded-tl-sm shadow-xl'}`}>
        <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.text}</p>
        
        {/* Timestamp & Actions */}
        <div className={`flex items-center gap-3 mt-3 text-[11px] ${isUser ? 'justify-end text-slate-500' : 'justify-between text-slate-400'}`}>
          {!isUser && (
            <button onClick={handleCopy} className="flex items-center gap-1.5 hover:text-white transition-colors">
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? <span className="text-emerald-400">Copied</span> : <span>Copy</span>}
            </button>
          )}
          <span>{msg.timestamp}</span>
        </div>
      </div>
    </motion.div>
  )
}

/* ------------------------------------------------------------------ */
/*  Main Page                                                           */
/* ------------------------------------------------------------------ */

export default function ChatPage() {
  const navigate = useNavigate()
  const [langOpen, setLangOpen] = useState(false)
  const [selectedLang, setSelectedLang] = useState(LANGUAGES[0])
  const [voiceState, setVoiceState] = useState('IDLE') // IDLE, LISTENING, PROCESSING
  
  const [messages, setMessages] = useState([
    { id: 1, role: 'ai', text: 'Namaste! I am YojVani, your AI guide to government schemes. You can ask me anything about welfare programs, scholarships, or financial assistance by typing below or tapping the microphone.', timestamp: '10:00 AM' }
  ])
  
  const [inputText, setInputText] = useState('')
  const [savedIds, setSavedIds] = useState(new Set())
  const messagesEndRef = useRef(null)

  const handleToggleSave = (id) => {
    setSavedIds(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = (e) => {
    e?.preventDefault()
    if (!inputText.trim()) return

    const newMsg = { id: Date.now(), role: 'user', text: inputText, timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }
    setMessages(prev => [...prev, newMsg])
    setInputText('')
    setVoiceState('PROCESSING')

    // Simulate AI response
    setTimeout(() => {
      setVoiceState('IDLE')
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'ai',
        text: 'Based on your query, I found some schemes that might be relevant for you. You can check the "Suggested Schemes" panel on the right for quick access, or ask me for more detailed eligibility criteria.',
        timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      }])
    }, 2000)
  }

  const toggleMic = () => {
    if (voiceState === 'IDLE') {
      setVoiceState('LISTENING')
      setTimeout(() => setVoiceState('PROCESSING'), 3000)
      setTimeout(() => {
        setVoiceState('IDLE')
        setInputText('What are the benefits of PM Kisan?')
      }, 5000)
    } else {
      setVoiceState('IDLE')
    }
  }

  return (
    <div className="h-screen bg-[#0B0F17] flex flex-col font-sans text-slate-200 overflow-hidden">
      
      {/* Ambient background */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 left-1/4 w-[500px] h-[500px] bg-teal-600/[0.04] rounded-full blur-[100px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-indigo-600/[0.04] rounded-full blur-[100px]" />
      </div>

      {/* ── HEADER ── */}
      <header className="relative z-20 flex items-center justify-between px-4 sm:px-6 h-16 border-b border-white/[0.06] bg-slate-950/80 backdrop-blur-xl flex-shrink-0">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors group w-24">
          <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
          <span className="text-sm font-medium">Back</span>
        </button>

        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/25">
            <AudioWaveform className="w-3.5 h-3.5 text-white absolute transform -translate-x-0.5" />
            <FileText className="w-3.5 h-3.5 text-white/70 absolute transform translate-x-1 translate-y-0.5 scale-75" />
          </div>
          <span className="text-base font-bold text-white tracking-tight">YojVani</span>
        </div>

        <div className="flex items-center justify-end gap-3 w-24">
          <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">Ready</span>
          </div>

          {/* Language picker */}
          <div className="relative z-50">
            <button onClick={() => setLangOpen(o => !o)} className="flex items-center justify-center w-8 h-8 rounded-full border border-white/[0.10] bg-slate-900 text-slate-300 hover:border-teal-500/40 hover:text-white transition-all">
              <Globe className="w-4 h-4" />
            </button>
            <AnimatePresence>
              {langOpen && (
                <motion.div initial={{ opacity: 0, scale: .95, y: -4 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: .95, y: -4 }} transition={{ duration: .15 }}
                  className="absolute right-0 top-10 w-40 rounded-xl border border-white/[0.08] bg-slate-900/95 backdrop-blur-xl shadow-2xl overflow-hidden">
                  {LANGUAGES.map(lang => (
                    <button key={lang.code} onClick={() => { setSelectedLang(lang); setLangOpen(false) }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 text-[13px] hover:bg-slate-800 transition-colors ${selectedLang.code === lang.code ? 'text-teal-400' : 'text-slate-300'}`}>
                      <span>{lang.label}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* ── MAIN CONTENT ── */}
      <div className="flex-1 flex overflow-hidden relative z-10">
        
        {/* Chat Area */}
        <main className="flex-1 flex flex-col min-w-0">
          
          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-8" style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(20,184,166,0.15) transparent' }}>
            {messages.map(msg => (
              <ChatMessage key={msg.id} msg={msg} />
            ))}
            
            {/* Typing Indicator */}
            {voiceState === 'PROCESSING' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 max-w-3xl mx-auto w-full mb-6">
                <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div className="px-5 py-4 rounded-3xl bg-slate-900/60 backdrop-blur-md border border-teal-500/10 rounded-tl-sm flex items-center">
                  <AudioWaveBars count={4} />
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} className="h-4" />
          </div>

          {/* Input Area */}
          <div className="p-4 sm:p-6 bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent">
            <div className="max-w-3xl mx-auto relative flex items-end gap-2 bg-slate-900/80 backdrop-blur-xl border border-white/[0.08] p-2 rounded-3xl focus-within:border-teal-500/50 focus-within:ring-1 focus-within:ring-teal-500/30 transition-all shadow-2xl">
              
              <button className="p-3 text-slate-400 hover:text-white transition-colors rounded-full hover:bg-white/[0.05]">
                <Paperclip className="w-5 h-5" />
              </button>
              
              <form onSubmit={handleSend} className="flex-1 mb-1">
                <textarea
                  rows="1"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Ask YojVani anything..."
                  className="w-full bg-transparent text-white placeholder-slate-500 text-[15px] resize-none focus:outline-none py-2.5 max-h-32 overflow-y-auto"
                  style={{ scrollbarWidth: 'none' }}
                />
              </form>

              <div className="flex items-center gap-1.5 p-1.5">
                {inputText.trim() ? (
                  <button onClick={handleSend} className="w-10 h-10 rounded-full bg-teal-500 flex items-center justify-center text-white hover:bg-teal-400 hover:scale-105 transition-all shadow-lg shadow-teal-500/25">
                    <Send className="w-4 h-4 translate-x-0.5" />
                  </button>
                ) : (
                  <button 
                    onClick={toggleMic}
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-white transition-all shadow-lg ${
                      voiceState === 'LISTENING' 
                        ? 'bg-red-500 shadow-red-500/30 animate-pulse' 
                        : 'bg-slate-800 border border-white/[0.08] hover:bg-slate-700'
                    }`}
                  >
                    <Mic className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
            <div className="text-center mt-3">
              <span className="text-[11px] text-slate-500">YojVani can make mistakes. Verify important scheme details.</span>
            </div>
          </div>
        </main>

        {/* ── RIGHT PANEL (Suggested Schemes) ── */}
        <aside className="hidden lg:flex flex-col w-80 xl:w-96 border-l border-white/[0.06] bg-slate-950/40 backdrop-blur-md">
          <div className="p-5 border-b border-white/[0.05]">
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-teal-400" />
              Suggested Schemes
            </h2>
            <p className="text-[11px] text-slate-400 mt-1">Based on your conversation</p>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(20,184,166,0.15) transparent' }}>
            {DEMO_SUGGESTED_SCHEMES.map((scheme, idx) => {
              const isSaved = savedIds.has(scheme.id)
              return (
                <motion.div
                  key={scheme.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="rounded-2xl border border-white/[0.08] bg-slate-900/60 overflow-hidden hover:border-white/[0.15] transition-all group"
                >
                  <div className={`h-1 bg-gradient-to-r ${scheme.gradient}`} />
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="min-w-0">
                        <h3 className="text-[14px] font-bold text-white leading-tight">{scheme.title}</h3>
                        <p className="text-[11px] text-slate-500 mt-0.5">{scheme.category}</p>
                      </div>
                      <button
                        onClick={() => handleToggleSave(scheme.id)}
                        className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center border transition-all ${
                          isSaved
                            ? 'bg-teal-500/20 border-teal-500/40 text-teal-400'
                            : 'bg-slate-800/60 border-white/[0.07] text-slate-500 hover:text-teal-400'
                        }`}
                      >
                        {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                      </button>
                    </div>
                    <p className="text-[12px] text-slate-400 leading-relaxed mb-3 line-clamp-2">{scheme.description}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-semibold text-white bg-teal-500/15 border border-teal-500/25 px-2 py-0.5 rounded-full">{scheme.payout}</span>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </aside>

      </div>
    </div>
  )
}
