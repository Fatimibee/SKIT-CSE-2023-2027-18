import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Mic, MicOff, Volume2, VolumeX, RotateCcw,
  ChevronLeft, AudioWaveform, FileText,
  Sparkles, Globe, IndianRupee, ArrowRight,
  Bookmark, BookmarkCheck,
} from 'lucide-react'

/* ------------------------------------------------------------------ */
/*  Constants & Mock data                                               */
/* ------------------------------------------------------------------ */

const LANGUAGES = [
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'en', label: 'English', native: 'English' },
]

const DEMO_TURNS = [
  {
    transcript: 'मुझे किसानों के लिए सरकारी योजनाओं के बारे में जानकारी चाहिए।',
    response: 'PM किसान सम्मान निधि योजना के तहत पात्र किसानों को प्रति वर्ष ₹6,000 की आर्थिक सहायता प्रदान की जाती है। यह राशि ₹2,000 की तीन समान किश्तों में दी जाती है।',
    scheme: {
      id: 'pm-kisan',
      title: 'PM Kisan Samman Nidhi',
      category: 'Agriculture',
      payout: '₹6,000 / year',
      status: 'Eligible',
      gradient: 'from-teal-500 to-emerald-600',
    },
  },
  {
    transcript: 'What housing schemes are available for low-income families?',
    response: 'Pradhan Mantri Awas Yojana (PMAY) provides financial assistance for construction of houses for economically weaker sections. Beneficiaries can receive up to ₹2.67 lakh subsidy.',
    scheme: {
      id: 'pmay',
      title: 'PM Awas Yojana (Urban)',
      category: 'Housing',
      payout: '₹2.67 L subsidy',
      status: 'Check Eligibility',
      gradient: 'from-indigo-500 to-blue-600',
    },
  },
]

/* ------------------------------------------------------------------ */
/*  Audio Wave Bars                                                     */
/* ------------------------------------------------------------------ */

function AudioWaveBars({ count = 12 }) {
  return (
    <div className="flex items-center justify-center gap-[3px] h-10">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className="w-1 rounded-full bg-gradient-to-t from-teal-500 to-emerald-400"
          animate={{ height: ['6px', `${18 + Math.random() * 22}px`, '6px'] }}
          transition={{ duration: 0.5 + Math.random() * 0.4, repeat: Infinity, delay: i * 0.07, ease: 'easeInOut' }}
          style={{ height: '6px' }}
        />
      ))}
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Desktop Large Orb                                                   */
/* ------------------------------------------------------------------ */

function DesktopVoiceOrb({ voiceState, onPress }) {
  const isListening = voiceState === 'LISTENING'
  const isProcessing = voiceState === 'PROCESSING'
  const isSpeaking = voiceState === 'SPEAKING'
  const isIdle = voiceState === 'IDLE'

  const glowColor = isListening
    ? 'radial-gradient(circle,rgba(239,68,68,.15) 0%,transparent 70%)'
    : isSpeaking
    ? 'radial-gradient(circle,rgba(16,185,129,.15) 0%,transparent 70%)'
    : isProcessing
    ? 'radial-gradient(circle,rgba(99,102,241,.18) 0%,transparent 70%)'
    : 'radial-gradient(circle,rgba(20,184,166,.13) 0%,transparent 70%)'

  const orbClass = isListening
    ? 'bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/40'
    : isSpeaking
    ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/40'
    : isProcessing
    ? 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-indigo-500/40'
    : 'bg-gradient-to-br from-teal-500 to-emerald-600 shadow-teal-500/40'

  return (
    <div className="relative flex flex-col items-center gap-5">
      {/* Outer glow backdrop */}
      <div
        className="absolute rounded-full pointer-events-none"
        style={{ width: 340, height: 340, background: glowColor, top: '50%', left: '50%', transform: 'translate(-50%,-50%)' }}
      />

      <div className="relative flex items-center justify-center w-72 h-72">
        {/* Idle pulse */}
        {isIdle && (
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{ background: 'radial-gradient(circle,rgba(20,184,166,.10) 0%,transparent 70%)' }}
            animate={{ scale: [1, 1.18, 1], opacity: [.5, 1, .5] }}
            transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}
        {/* Listening ripples */}
        {isListening && [0, 1, 2].map(i => (
          <motion.div key={i} className="absolute rounded-full border border-red-400/30"
            initial={{ width: 176, height: 176, opacity: .9 }}
            animate={{ width: 285, height: 285, opacity: 0 }}
            transition={{ duration: 1.8, repeat: Infinity, delay: i * .55, ease: 'easeOut' }} />
        ))}
        {/* Processing spinner */}
        {isProcessing && (
          <motion.div className="absolute inset-[-8px] rounded-full"
            style={{ background: 'conic-gradient(from 0deg,#14b8a6,#6366f1,#a855f7,#14b8a6)', WebkitMask: 'radial-gradient(farthest-side,transparent calc(100% - 8px),black calc(100% - 7px))' }}
            animate={{ rotate: 360 }} transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }} />
        )}
        {/* Speaking pulse */}
        {isSpeaking && (
          <motion.div className="absolute inset-[-5px] rounded-full border-2 border-emerald-400/50"
            animate={{ scale: [1, 1.07, 1], opacity: [.5, 1, .5] }}
            transition={{ duration: .9, repeat: Infinity, ease: 'easeInOut' }} />
        )}

        {/* Main button */}
        <motion.button
          id="voice-orb-btn"
          onClick={onPress}
          className={`relative z-10 w-44 h-44 rounded-full flex items-center justify-center shadow-2xl focus:outline-none transition-colors ${orbClass}`}
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: .94 }}
          animate={isIdle ? { y: [0, -8, 0] } : {}}
          transition={isIdle ? { duration: 3.5, repeat: Infinity, ease: 'easeInOut' } : {}}
        >
          {isSpeaking ? <Volume2 className="w-14 h-14 text-white" />
            : isListening ? <motion.div animate={{ scale: [1, 1.15, 1] }} transition={{ duration: .5, repeat: Infinity }}><Mic className="w-14 h-14 text-white" /></motion.div>
            : isProcessing ? <Sparkles className="w-14 h-14 text-white" />
            : <Mic className="w-14 h-14 text-white" />}
        </motion.button>
      </div>

      {/* State label */}
      <AnimatePresence mode="wait">
        {isIdle && <motion.p key="idle" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-sm text-slate-500 tracking-wide">Tap to speak</motion.p>}
        {isListening && <motion.p key="listen" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-sm text-teal-400 font-medium">Listening…</motion.p>}
        {isProcessing && <motion.p key="proc" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-sm text-indigo-400 font-medium">Thinking…</motion.p>}
        {isSpeaking && <motion.p key="speak" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-sm text-emerald-400 font-medium">YojVani Speaking…</motion.p>}
      </AnimatePresence>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Mobile FAB                                                          */
/* ------------------------------------------------------------------ */

function MobileFAB({ voiceState, onPress }) {
  const isListening = voiceState === 'LISTENING'
  const isProcessing = voiceState === 'PROCESSING'
  const isSpeaking = voiceState === 'SPEAKING'
  const isIdle = voiceState === 'IDLE'

  const orbClass = isListening
    ? 'bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/50'
    : isSpeaking
    ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/50'
    : isProcessing
    ? 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-indigo-500/50'
    : 'bg-gradient-to-br from-teal-500 to-emerald-600 shadow-teal-500/50'

  return (
    <div className="relative flex items-center justify-center w-16 h-16">
      {isListening && [0, 1].map(i => (
        <motion.div key={i} className="absolute rounded-full border border-red-400/40"
          initial={{ width: 64, height: 64, opacity: .9 }}
          animate={{ width: 110, height: 110, opacity: 0 }}
          transition={{ duration: 1.5, repeat: Infinity, delay: i * .5, ease: 'easeOut' }} />
      ))}
      {isProcessing && (
        <motion.div className="absolute inset-[-4px] rounded-full"
          style={{ background: 'conic-gradient(from 0deg,#14b8a6,#6366f1,#14b8a6)', WebkitMask: 'radial-gradient(farthest-side,transparent calc(100% - 4px),black calc(100% - 3px))' }}
          animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }} />
      )}
      <motion.button
        id="voice-fab-btn"
        onClick={onPress}
        className={`relative z-10 w-14 h-14 rounded-full flex items-center justify-center shadow-xl focus:outline-none transition-colors ${orbClass}`}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: .9 }}
        animate={isIdle ? { y: [0, -4, 0] } : {}}
        transition={isIdle ? { duration: 3, repeat: Infinity, ease: 'easeInOut' } : {}}
      >
        {isSpeaking ? <Volume2 className="w-6 h-6 text-white" />
          : isListening ? <motion.div animate={{ scale: [1, 1.15, 1] }} transition={{ duration: .5, repeat: Infinity }}><Mic className="w-6 h-6 text-white" /></motion.div>
          : isProcessing ? <Sparkles className="w-6 h-6 text-white" />
          : <Mic className="w-6 h-6 text-white" />}
      </motion.button>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Conversation Bubble                                                 */
/* ------------------------------------------------------------------ */

function ConvBubble({ role, text }) {
  const isUser = role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 18, scale: .96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -8, scale: .96 }}
      transition={{ duration: .35, ease: 'easeOut' }}
      className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-teal-500/25 mt-0.5">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
      )}
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 backdrop-blur-sm shadow-xl ${isUser ? 'bg-white/[0.06] border border-white/[0.08] rounded-br-sm' : 'bg-teal-500/[0.07] border border-teal-500/[0.18] rounded-bl-sm'}`}>
        <p className={`text-[11px] font-semibold uppercase tracking-wider mb-1.5 flex items-center gap-1.5 ${isUser ? 'text-slate-500' : 'text-teal-400/80'}`}>
          {isUser ? <><Mic className="w-3 h-3" /> You</> : <><Sparkles className="w-3 h-3 text-emerald-400" /> YojVani</>}
        </p>
        <p className="text-[14px] text-slate-200 leading-relaxed">{text}</p>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-white/[0.08] border border-white/[0.08] flex items-center justify-center flex-shrink-0 mt-0.5">
          <Mic className="w-4 h-4 text-slate-400" />
        </div>
      )}
    </motion.div>
  )
}

/* ------------------------------------------------------------------ */
/*  Inline Scheme Card (mobile feed)                                    */
/* ------------------------------------------------------------------ */

function InlineSchemeCard({ scheme, savedIds, onToggleSave }) {
  const isSaved = savedIds.has(scheme.id)
  return (
    <motion.div
      initial={{ opacity: 0, y: 14, scale: .97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: .32, ease: 'easeOut' }}
      className="ml-11 rounded-2xl border border-white/[0.08] bg-slate-900/80 backdrop-blur-sm overflow-hidden shadow-xl"
    >
      <div className={`h-1 bg-gradient-to-r ${scheme.gradient}`} />
      <div className="p-3 flex items-center gap-3">
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${scheme.gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
          <IndianRupee className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[13px] font-bold text-white leading-tight truncate">{scheme.title}</p>
          <p className="text-[11px] text-slate-500">{scheme.category}</p>
          <div className="mt-1 flex items-center gap-2 flex-wrap">
            <span className="text-[11px] font-semibold text-white bg-teal-500/15 border border-teal-500/25 px-2 py-0.5 rounded-full">{scheme.payout}</span>
            <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${scheme.status === 'Eligible' ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' : 'text-amber-400 bg-amber-400/10 border-amber-400/20'}`}>{scheme.status}</span>
          </div>
        </div>
        <motion.button
          id={`inline-scheme-save-${scheme.id}`}
          onClick={() => onToggleSave(scheme.id)}
          whileTap={{ scale: .85 }}
          className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center border transition-all ${isSaved ? 'bg-teal-500/20 border-teal-500/40 text-teal-400' : 'bg-slate-800/60 border-white/[0.07] text-slate-500 hover:text-teal-400'}`}
        >
          {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
        </motion.button>
      </div>
    </motion.div>
  )
}

/* ------------------------------------------------------------------ */
/*  Desktop Sidebar Scheme Card                                         */
/* ------------------------------------------------------------------ */

function SidebarSchemeCard({ scheme, savedIds, onToggleSave }) {
  const isSaved = savedIds.has(scheme.id)
  return (
    <motion.div
      initial={{ opacity: 0, y: 18, scale: .97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ duration: .32, ease: 'easeOut' }}
      className="w-full rounded-2xl border border-white/[0.08] bg-slate-900/80 backdrop-blur-sm overflow-hidden shadow-xl"
    >
      <div className={`h-1.5 bg-gradient-to-r ${scheme.gradient}`} />
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${scheme.gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
            <IndianRupee className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-white leading-tight truncate">{scheme.title}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">{scheme.category}</p>
              </div>
              <motion.button
                id={`scheme-save-${scheme.id}`}
                onClick={() => onToggleSave(scheme.id)}
                whileTap={{ scale: .85 }}
                className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center border transition-all ${isSaved ? 'bg-teal-500/20 border-teal-500/40 text-teal-400' : 'bg-slate-800/60 border-white/[0.07] text-slate-500 hover:text-teal-400'}`}
              >
                {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
              </motion.button>
            </div>
            <div className="mt-2">
              <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${scheme.status === 'Eligible' ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' : 'text-amber-400 bg-amber-400/10 border-amber-400/20'}`}>{scheme.status}</span>
            </div>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-white/[0.05] flex items-center justify-between gap-2">
          <span className="text-[12px] font-semibold text-white bg-teal-500/15 border border-teal-500/25 px-2.5 py-1 rounded-full">{scheme.payout}</span>
          <button className="text-[11px] text-teal-400 hover:text-teal-300 flex items-center gap-1 transition-colors">View Details <ArrowRight className="w-3 h-3" /></button>
        </div>
      </div>
    </motion.div>
  )
}

/* ------------------------------------------------------------------ */
/*  Main Page                                                           */
/* ------------------------------------------------------------------ */

export default function VoiceAssistantPage() {
  const navigate = useNavigate()
  const [voiceState, setVoiceState] = useState('IDLE')
  const [muted, setMuted] = useState(false)
  const [paused, setPaused] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [suggestedSchemes, setSuggestedSchemes] = useState([])
  const [savedIds, setSavedIds] = useState(new Set())
  const [langOpen, setLangOpen] = useState(false)
  const [selectedLang, setSelectedLang] = useState(LANGUAGES[0])
  const [demoIndex, setDemoIndex] = useState(0)
  const [turns, setTurns] = useState([])

  const timerRef = useRef(null)
  const streamRef = useRef(null)
  const feedRef = useRef(null)

  const statusMap = { IDLE: 'Ready', LISTENING: 'Listening…', PROCESSING: 'Processing…', SPEAKING: 'YojVani Speaking…' }
  const statusColors = { IDLE: 'text-slate-400', LISTENING: 'text-teal-400', PROCESSING: 'text-indigo-400', SPEAKING: 'text-emerald-400' }

  const handleToggleSave = id => setSavedIds(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })

  const scrollFeed = () => setTimeout(() => {
    if (feedRef.current) feedRef.current.scrollTo({ top: feedRef.current.scrollHeight, behavior: 'smooth' })
  }, 60)

  const runDemoTurn = () => {
    const turn = DEMO_TURNS[demoIndex % DEMO_TURNS.length]
    setDemoIndex(i => i + 1)
    setTranscript('')
    setAiResponse('')
    setVoiceState('LISTENING')

    let ci = 0
    const t1 = setInterval(() => {
      ci++
      setTranscript(turn.transcript.slice(0, ci))
      if (ci >= turn.transcript.length) {
        clearInterval(t1)
        setTurns(p => [...p, { role: 'user', text: turn.transcript, id: Date.now() }])
        scrollFeed()
        setTimeout(() => {
          setVoiceState('PROCESSING')
          setTimeout(() => {
            setVoiceState('SPEAKING')
            setSuggestedSchemes(p => p.some(s => s.id === turn.scheme.id) ? p : [...p, turn.scheme])
            let ri = 0
            streamRef.current = setInterval(() => {
              ri += 3
              setAiResponse(turn.response.slice(0, ri))
              if (ri >= turn.response.length) {
                clearInterval(streamRef.current)
                setTurns(p => [...p, { role: 'ai', text: turn.response, scheme: turn.scheme, id: Date.now() + 1 }])
                scrollFeed()
                setTimeout(() => setVoiceState('IDLE'), 800)
              }
            }, 30)
          }, 1800)
        }, 300)
      }
    }, 45)
    timerRef.current = t1
  }

  const handleOrbPress = () => {
    if (voiceState === 'IDLE') { runDemoTurn(); return }
    if (voiceState === 'LISTENING') { clearInterval(timerRef.current); setVoiceState('IDLE'); return }
    if (voiceState === 'SPEAKING') { clearInterval(streamRef.current); setVoiceState('IDLE') }
  }

  const handleReplay = () => { if (aiResponse) setVoiceState('SPEAKING') }

  useEffect(() => () => { clearInterval(timerRef.current); clearInterval(streamRef.current) }, [])

  return (
    <div className="min-h-screen bg-[#0B0F19] relative overflow-hidden flex flex-col" style={{ fontFamily: "'Inter',sans-serif" }}>

      {/* Ambient background */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-teal-600/[0.06] rounded-full blur-[130px]" />
        <div className="absolute bottom-0 right-0 w-[450px] h-[450px] bg-indigo-600/[0.06] rounded-full blur-[110px]" />
        <div className="absolute top-1/2 left-0 w-[320px] h-[320px] bg-emerald-600/[0.05] rounded-full blur-[95px]" />
      </div>

      {/* ── HEADER ── */}
      <header className="relative z-20 w-full flex items-center justify-between px-4 sm:px-6 py-3 border-b border-white/[0.06] bg-slate-950/60 backdrop-blur-xl">
        <button id="voice-back-btn" onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors group">
          <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
          <span className="text-sm font-medium hidden sm:inline">Back</span>
        </button>

        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/25">
            <AudioWaveform className="w-3.5 h-3.5 text-white absolute transform -translate-x-0.5" />
            <FileText className="w-3.5 h-3.5 text-white/70 absolute transform translate-x-1 translate-y-0.5 scale-75" />
          </div>
          <span className="text-base font-bold text-white tracking-tight">YojVani</span>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {/* Desktop status text */}
          <motion.span key={voiceState} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} className={`text-[12px] font-medium hidden sm:inline ${statusColors[voiceState]}`}>
            {statusMap[voiceState]}
          </motion.span>
          {/* Mobile status dot */}
          <motion.div key={voiceState + '-mob'} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="sm:hidden flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${voiceState === 'LISTENING' ? 'bg-teal-400 animate-pulse' : voiceState === 'PROCESSING' ? 'bg-indigo-400 animate-pulse' : voiceState === 'SPEAKING' ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
            <span className={`text-[11px] font-medium ${statusColors[voiceState]}`}>{statusMap[voiceState]}</span>
          </motion.div>

          {/* Language picker */}
          <div className="relative">
            <button id="voice-lang-btn" onClick={() => setLangOpen(o => !o)} className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border border-white/[0.10] bg-slate-900/80 text-slate-300 text-[12px] font-medium hover:border-teal-500/40 hover:text-white transition-all">
              <Globe className="w-3.5 h-3.5 text-teal-400" />
              <span className="hidden xs:inline">{selectedLang.label}</span>
            </button>
            <AnimatePresence>
              {langOpen && (
                <motion.div initial={{ opacity: 0, scale: .95, y: -4 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: .95, y: -4 }} transition={{ duration: .15 }}
                  className="absolute right-0 top-9 z-50 w-44 rounded-xl border border-white/[0.08] bg-slate-900/95 backdrop-blur-xl shadow-2xl overflow-hidden">
                  {LANGUAGES.map(lang => (
                    <button key={lang.code} id={`lang-opt-${lang.code}`} onClick={() => { setSelectedLang(lang); setLangOpen(false) }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 text-[13px] hover:bg-slate-800/80 transition-colors ${selectedLang.code === lang.code ? 'text-teal-400' : 'text-slate-300'}`}>
                      <span>{lang.label}</span><span className="text-slate-500">{lang.native}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="relative z-10 flex-1 flex overflow-hidden">

        {/* DESKTOP MAIN — orb center stage + history feed */}
        <main className="flex-1 hidden lg:flex flex-col overflow-hidden">
          {/* Orb stage */}
          <div className="flex-shrink-0 flex flex-col items-center justify-center py-10 px-6" style={{ minHeight: '58%' }}>
            <DesktopVoiceOrb voiceState={voiceState} onPress={handleOrbPress} />

            {/* Live bubbles while active */}
            <AnimatePresence>
              {transcript && voiceState === 'LISTENING' && (
                <motion.div key="lt" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="mt-6 max-w-md w-full rounded-2xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-sm px-4 py-3 flex gap-3 items-start">
                  <div className="w-7 h-7 rounded-lg bg-white/[0.08] border border-white/[0.08] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Mic className="w-3.5 h-3.5 text-slate-400" />
                  </div>
                  <p className="text-[14px] text-slate-200 leading-relaxed">{transcript}</p>
                </motion.div>
              )}
              {aiResponse && voiceState === 'SPEAKING' && (
                <motion.div key="lr" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="mt-4 max-w-md w-full rounded-2xl border border-teal-500/[0.18] bg-teal-500/[0.06] backdrop-blur-sm px-4 py-3">
                  <div className="mb-2"><AudioWaveBars count={16} /></div>
                  <p className="text-[14px] text-slate-200 leading-relaxed">{aiResponse}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Conversation history */}
          {turns.length > 0 && (
            <div ref={feedRef} className="flex-1 overflow-y-auto px-6 pb-4 space-y-3 border-t border-white/[0.04]">
              <p className="text-[11px] text-slate-600 uppercase tracking-wider font-medium pt-4 pb-1">Conversation History</p>
              <AnimatePresence initial={false}>
                {turns.map(t => <ConvBubble key={t.id} role={t.role} text={t.text} />)}
              </AnimatePresence>
            </div>
          )}
        </main>

        {/* MOBILE LAYOUT */}
        <div className="flex-1 lg:hidden flex flex-col overflow-hidden relative">
          <div ref={feedRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">

            {/* Empty state */}
            {turns.length === 0 && voiceState === 'IDLE' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center gap-5 py-20 text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-teal-500/20 to-emerald-600/20 border border-teal-500/20 flex items-center justify-center">
                  <Mic className="w-10 h-10 text-teal-400/60" />
                </div>
                <div className="space-y-1">
                  <p className="text-slate-300 font-semibold text-[15px]">Tap the mic to start</p>
                  <p className="text-slate-500 text-[13px] max-w-[220px] leading-relaxed">Ask about government schemes in Hindi or English</p>
                </div>
              </motion.div>
            )}

            {/* Live transcript */}
            <AnimatePresence>
              {transcript && voiceState === 'LISTENING' && (
                <motion.div key="mlt" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex justify-end gap-3">
                  <div className="max-w-[80%] rounded-2xl rounded-br-sm px-4 py-3 bg-white/[0.06] border border-white/[0.08]">
                    <p className="text-[11px] font-semibold uppercase tracking-wider mb-1.5 text-slate-500 flex items-center gap-1.5"><Mic className="w-3 h-3" /> You</p>
                    <p className="text-[14px] text-slate-200 leading-relaxed">{transcript}</p>
                  </div>
                  <div className="w-8 h-8 rounded-xl bg-white/[0.08] border border-white/[0.08] flex items-center justify-center flex-shrink-0 mt-0.5"><Mic className="w-4 h-4 text-slate-400" /></div>
                </motion.div>
              )}
              {/* Live AI response */}
              {aiResponse && voiceState === 'SPEAKING' && (
                <motion.div key="mlr" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex justify-start gap-3">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-lg shadow-teal-500/25"><Sparkles className="w-4 h-4 text-white" /></div>
                  <div className="max-w-[80%] rounded-2xl rounded-bl-sm px-4 py-3 bg-teal-500/[0.07] border border-teal-500/[0.18]">
                    <p className="text-[11px] font-semibold uppercase tracking-wider mb-1.5 text-teal-400/80 flex items-center gap-1.5"><Sparkles className="w-3 h-3" /> YojVani</p>
                    {!paused && <div className="mb-2"><AudioWaveBars count={12} /></div>}
                    <p className="text-[14px] text-slate-200 leading-relaxed">{aiResponse}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Historical turns + inline scheme cards */}
            <AnimatePresence initial={false}>
              {turns.map(t => (
                <React.Fragment key={t.id}>
                  <ConvBubble role={t.role} text={t.text} />
                  {t.role === 'ai' && t.scheme && (
                    <InlineSchemeCard scheme={t.scheme} savedIds={savedIds} onToggleSave={handleToggleSave} />
                  )}
                </React.Fragment>
              ))}
            </AnimatePresence>

            <div className="h-28" />
          </div>

          {/* FAB */}
          <div className="absolute bottom-20 right-5 z-20">
            <MobileFAB voiceState={voiceState} onPress={handleOrbPress} />
          </div>

          {/* Thinking label above FAB */}
          <AnimatePresence>
            {voiceState === 'PROCESSING' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute bottom-36 right-0 left-0 flex justify-center pointer-events-none">
                <span className="text-[12px] text-indigo-400 font-medium bg-slate-900/80 px-3 py-1.5 rounded-full border border-indigo-500/20 backdrop-blur-sm">Thinking…</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* DESKTOP SIDEBAR */}
        <aside className="hidden lg:flex w-[340px] xl:w-[380px] flex-shrink-0 flex-col border-l border-white/[0.06] bg-slate-950/50 backdrop-blur-md">
          <div className="px-5 pt-5 pb-3 flex-shrink-0 border-b border-white/[0.05]">
            <div className="flex items-center gap-2 mb-0.5">
              <div className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
              <h2 className="text-[13px] font-bold text-white tracking-tight">Suggested Schemes</h2>
            </div>
            <p className="text-[11px] text-slate-500">Based on your conversation</p>
          </div>
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
            <AnimatePresence initial={false}>
              {suggestedSchemes.length === 0 ? (
                <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center gap-4 py-20 text-center">
                  <div className="w-16 h-16 rounded-2xl border border-white/[0.06] bg-slate-800/40 flex items-center justify-center"><Bookmark className="w-7 h-7 text-slate-600" /></div>
                  <p className="text-[13px] text-slate-500 max-w-[180px] leading-relaxed">Speak to YojVani and relevant schemes will appear here.</p>
                </motion.div>
              ) : suggestedSchemes.map(s => <SidebarSchemeCard key={s.id} scheme={s} savedIds={savedIds} onToggleSave={handleToggleSave} />)}
            </AnimatePresence>
          </div>
          <AnimatePresence>
            {savedIds.size > 0 && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mx-5 mb-5 flex-shrink-0">
                <div className="rounded-xl border border-teal-500/20 bg-teal-500/[0.07] px-4 py-2.5 flex items-center gap-2">
                  <BookmarkCheck className="w-4 h-4 text-teal-400 flex-shrink-0" />
                  <span className="text-[12px] text-teal-300 font-medium">{savedIds.size} scheme{savedIds.size > 1 ? 's' : ''} saved</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </aside>
      </div>

      {/* ── DESKTOP FOOTER ── */}
      <footer className="relative z-20 hidden lg:block w-full px-4 sm:px-6 py-4 border-t border-white/[0.06] bg-slate-950/60 backdrop-blur-xl">
        <div className="max-w-md mx-auto flex items-center justify-center gap-6">
          <button id="voice-mute-btn" onClick={() => setMuted(m => !m)} className="flex flex-col items-center gap-1.5 group">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border transition-all ${muted ? 'bg-red-500/15 border-red-500/30 text-red-400' : 'bg-slate-800/80 border-white/[0.06] text-slate-400 group-hover:text-white group-hover:bg-slate-700/80'}`}>{muted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}</div>
            <span className="text-[10px] text-slate-600 group-hover:text-slate-400 transition-colors">{muted ? 'Unmute' : 'Mute'}</span>
          </button>
          <button id="voice-pause-btn" onClick={() => setPaused(p => !p)} className="flex flex-col items-center gap-1.5 group">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border transition-all ${paused ? 'bg-amber-500/15 border-amber-500/30 text-amber-400' : 'bg-slate-800/80 border-white/[0.06] text-slate-400 group-hover:text-white group-hover:bg-slate-700/80'}`}>{paused ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}</div>
            <span className="text-[10px] text-slate-600 group-hover:text-slate-400 transition-colors">{paused ? 'Resume' : 'Pause'}</span>
          </button>
          <button id="voice-replay-btn" onClick={handleReplay} disabled={!aiResponse} className="flex flex-col items-center gap-1.5 group disabled:opacity-40">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center border border-white/[0.06] bg-slate-800/80 text-slate-400 group-hover:text-white group-hover:bg-slate-700/80 transition-all"><RotateCcw className="w-5 h-5" /></div>
            <span className="text-[10px] text-slate-600 group-hover:text-slate-400 transition-colors">Replay</span>
          </button>
        </div>
      </footer>

      {/* ── MOBILE FOOTER ── */}
      <footer className="relative z-20 lg:hidden w-full px-4 py-3 border-t border-white/[0.06] bg-slate-950/80 backdrop-blur-xl flex items-center justify-between gap-3">
        <button id="voice-mute-mob-btn" onClick={() => setMuted(m => !m)} className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-[12px] font-medium transition-all ${muted ? 'bg-red-500/15 border-red-500/30 text-red-400' : 'bg-slate-800/80 border-white/[0.06] text-slate-400'}`}>
          {muted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}{muted ? 'Unmute' : 'Mute'}
        </button>
        <button id="voice-pause-mob-btn" onClick={() => setPaused(p => !p)} className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-[12px] font-medium transition-all ${paused ? 'bg-amber-500/15 border-amber-500/30 text-amber-400' : 'bg-slate-800/80 border-white/[0.06] text-slate-400'}`}>
          {paused ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}{paused ? 'Resume' : 'Pause'}
        </button>
        <button id="voice-replay-mob-btn" onClick={handleReplay} disabled={!aiResponse} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-white/[0.06] bg-slate-800/80 text-slate-400 text-[12px] font-medium disabled:opacity-40">
          <RotateCcw className="w-4 h-4" />Replay
        </button>
      </footer>

    </div>
  )
}
