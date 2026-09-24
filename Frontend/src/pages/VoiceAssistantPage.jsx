import React, { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Mic, MicOff, Volume2, VolumeX, RotateCcw,
  ChevronLeft, AudioWaveform, FileText, CheckCircle2,
  Sparkles, Globe, IndianRupee, ArrowRight,
} from 'lucide-react'

/* ------------------------------------------------------------------ */
/*  Constants & Mock data                                               */
/* ------------------------------------------------------------------ */

const LANGUAGES = [
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'en', label: 'English', native: 'English' },
]

/** Simulated conversation turns for demo purposes */
const DEMO_TURNS = [
  {
    transcript: 'मुझे किसानों के लिए सरकारी योजनाओं के बारे में जानकारी चाहिए।',
    response: 'PM किसान सम्मान निधि योजना के तहत पात्र किसानों को प्रति वर्ष ₹6,000 की आर्थिक सहायता प्रदान की जाती है। यह राशि ₹2,000 की तीन समान किश्तों में दी जाती है।',
    scheme: {
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
      title: 'PM Awas Yojana (Urban)',
      category: 'Housing',
      payout: '₹2.67 L subsidy',
      status: 'Check Eligibility',
      gradient: 'from-indigo-500 to-blue-600',
    },
  },
]

/* ------------------------------------------------------------------ */
/*  Voice state machine types                                           */
/* ------------------------------------------------------------------ */

// IDLE | LISTENING | PROCESSING | SPEAKING

/* ------------------------------------------------------------------ */
/*  Sub-components                                                      */
/* ------------------------------------------------------------------ */

/** Animated wave bars shown in SPEAKING state */
function AudioWaveBars({ count = 12 }) {
  return (
    <div className="flex items-center justify-center gap-[3px] h-12">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className="w-1.5 rounded-full bg-gradient-to-t from-teal-500 to-emerald-400"
          animate={{
            height: ['8px', `${20 + Math.random() * 28}px`, '8px'],
          }}
          transition={{
            duration: 0.5 + Math.random() * 0.4,
            repeat: Infinity,
            delay: i * 0.07,
            ease: 'easeInOut',
          }}
          style={{ height: '8px' }}
        />
      ))}
    </div>
  )
}

/** Central animated orb button */
function VoiceOrb({ voiceState, onPress }) {
  const isListening  = voiceState === 'LISTENING'
  const isProcessing = voiceState === 'PROCESSING'
  const isSpeaking   = voiceState === 'SPEAKING'
  const isIdle       = voiceState === 'IDLE'

  return (
    <div className="relative flex items-center justify-center w-52 h-52">

      {/* Idle subtle glow ring */}
      {isIdle && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(20,184,166,0.12) 0%, transparent 70%)' }}
          animate={{ scale: [1, 1.15, 1], opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}

      {/* Listening: multi-ring ripple */}
      {isListening && (
        <>
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="absolute rounded-full border border-teal-400/40"
              initial={{ width: 96, height: 96, opacity: 0.8 }}
              animate={{ width: 200, height: 200, opacity: 0 }}
              transition={{ duration: 1.6, repeat: Infinity, delay: i * 0.5, ease: 'easeOut' }}
            />
          ))}
        </>
      )}

      {/* Processing: spinning gradient ring */}
      {isProcessing && (
        <motion.div
          className="absolute inset-[-6px] rounded-full"
          style={{
            background: 'conic-gradient(from 0deg, #14b8a6, #6366f1, #14b8a6)',
            WebkitMask: 'radial-gradient(farthest-side, transparent calc(100% - 6px), black calc(100% - 5px))',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
        />
      )}

      {/* Speaking: pulsating border */}
      {isSpeaking && (
        <motion.div
          className="absolute inset-[-4px] rounded-full border-2 border-emerald-400/60"
          animate={{ scale: [1, 1.06, 1], opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}

      {/* Orb button */}
      <motion.button
        id="voice-orb-btn"
        onClick={onPress}
        className={`relative z-10 w-24 h-24 rounded-full flex items-center justify-center shadow-2xl transition-colors focus:outline-none ${
          isListening
            ? 'bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/40'
            : isSpeaking
            ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/40'
            : isProcessing
            ? 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-indigo-500/40'
            : 'bg-gradient-to-br from-teal-500 to-emerald-600 shadow-teal-500/40'
        }`}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.93 }}
        animate={isIdle ? { y: [0, -6, 0] } : {}}
        transition={isIdle ? { duration: 3, repeat: Infinity, ease: 'easeInOut' } : {}}
      >
        {isSpeaking ? (
          <Volume2 className="w-9 h-9 text-white" />
        ) : isListening ? (
          <motion.div
            animate={{ scale: [1, 1.15, 1] }}
            transition={{ duration: 0.5, repeat: Infinity }}
          >
            <Mic className="w-9 h-9 text-white" />
          </motion.div>
        ) : isProcessing ? (
          <Sparkles className="w-9 h-9 text-white" />
        ) : (
          <Mic className="w-9 h-9 text-white" />
        )}
      </motion.button>
    </div>
  )
}

/** Scheme card preview */
function SchemePreviewCard({ scheme }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 16, scale: 0.95 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="w-full max-w-md mx-auto mt-4 rounded-2xl border border-white/[0.08] bg-slate-900/80 backdrop-blur-sm overflow-hidden shadow-xl"
    >
      <div className={`h-1.5 bg-gradient-to-r ${scheme.gradient}`} />
      <div className="p-4 flex items-start gap-4">
        <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${scheme.gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
          <IndianRupee className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <p className="text-[13px] font-bold text-white leading-tight">{scheme.title}</p>
              <p className="text-[11px] text-slate-500 mt-0.5">{scheme.category}</p>
            </div>
            <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border flex-shrink-0 ${
              scheme.status === 'Eligible'
                ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
                : 'text-amber-400 bg-amber-400/10 border-amber-400/20'
            }`}>
              {scheme.status}
            </span>
          </div>
          <div className="mt-2.5 flex items-center gap-2">
            <span className="text-[12px] font-semibold text-white bg-teal-500/15 border border-teal-500/25 px-2.5 py-1 rounded-full">
              {scheme.payout}
            </span>
            <button className="text-[11px] text-teal-400 hover:text-teal-300 flex items-center gap-1 transition-colors">
              View Details <ArrowRight className="w-3 h-3" />
            </button>
          </div>
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
  const [voiceState, setVoiceState]     = useState('IDLE')   // IDLE | LISTENING | PROCESSING | SPEAKING
  const [muted, setMuted]               = useState(false)
  const [paused, setPaused]             = useState(false)
  const [transcript, setTranscript]     = useState('')
  const [aiResponse, setAiResponse]     = useState('')
  const [matchedScheme, setMatchedScheme] = useState(null)
  const [langOpen, setLangOpen]         = useState(false)
  const [selectedLang, setSelectedLang] = useState(LANGUAGES[0])
  const [demoIndex, setDemoIndex]       = useState(0)


  const timerRef   = useRef(null)
  const streamRef  = useRef(null)

  const statusMap = {
    IDLE:       'Ready',
    LISTENING:  'Listening\u2026',
    PROCESSING: 'Processing\u2026',
    SPEAKING:   'YojVani Speaking\u2026',
  }

  const statusColors = {
    IDLE:       'text-slate-400',
    LISTENING:  'text-teal-400',
    PROCESSING: 'text-indigo-400',
    SPEAKING:   'text-emerald-400',
  }

  /** Simulate a full voice turn for demo */
  const runDemoTurn = () => {
    const turn = DEMO_TURNS[demoIndex % DEMO_TURNS.length]
    setDemoIndex((i) => i + 1)
    setTranscript('')
    setAiResponse('')
    setMatchedScheme(null)

    // — LISTENING —
    setVoiceState('LISTENING')
    let charIdx = 0
    const typeTranscript = setInterval(() => {
      charIdx++
      setTranscript(turn.transcript.slice(0, charIdx))
      if (charIdx >= turn.transcript.length) {
        clearInterval(typeTranscript)
        // — PROCESSING —
        setTimeout(() => {
          setVoiceState('PROCESSING')
          // — SPEAKING —
          setTimeout(() => {
            setVoiceState('SPEAKING')
            setMatchedScheme(turn.scheme)
            let rIdx = 0
            streamRef.current = setInterval(() => {
              rIdx += 3
              setAiResponse(turn.response.slice(0, rIdx))
              if (rIdx >= turn.response.length) {
                clearInterval(streamRef.current)
                setTimeout(() => setVoiceState('IDLE'), 800)
              }
            }, 30)
          }, 1800)
        }, 300)
      }
    }, 45)
    timerRef.current = typeTranscript
  }

  const handleOrbPress = () => {
    if (voiceState === 'IDLE')      { runDemoTurn(); return }
    if (voiceState === 'LISTENING') {
      clearInterval(timerRef.current)
      setVoiceState('IDLE')
      return
    }
    if (voiceState === 'SPEAKING') {
      clearInterval(streamRef.current)
      setVoiceState('IDLE')
    }
  }

  const handleReplay = () => {
    if (aiResponse) setVoiceState('SPEAKING')
  }


  useEffect(() => {
    return () => {
      clearInterval(timerRef.current)
      clearInterval(streamRef.current)
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#0B0F19] relative overflow-hidden flex flex-col">

      {/* Ambient orbs */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-teal-600/[0.06] rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-indigo-600/[0.06] rounded-full blur-[100px]" />
        <div className="absolute top-1/2 left-0 w-[300px] h-[300px] bg-emerald-600/[0.05] rounded-full blur-[90px]" />
      </div>

      {/* ── Top bar ── */}
      <header className="relative z-20 w-full flex items-center justify-between px-4 sm:px-6 py-4 border-b border-white/[0.06] bg-slate-950/60 backdrop-blur-xl">

        {/* Back button */}
        <button
          id="voice-back-btn"
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors group"
        >
          <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
          <span className="text-sm font-medium hidden sm:inline">Back</span>
        </button>

        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/25">
            <AudioWaveform className="w-3.5 h-3.5 text-white absolute transform -translate-x-0.5" />
            <FileText className="w-3.5 h-3.5 text-white/70 absolute transform translate-x-1 translate-y-0.5 scale-75" />
          </div>
          <span className="text-base font-bold text-white tracking-tight">YojVani</span>
        </div>

        {/* Right: language picker + status */}
        <div className="flex items-center gap-3">
          {/* Status badge */}
          <motion.span
            key={voiceState}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className={`text-[12px] font-medium hidden sm:inline ${statusColors[voiceState]}`}
          >
            {statusMap[voiceState]}
          </motion.span>

          {/* Language selector */}
          <div className="relative">
            <button
              id="voice-lang-btn"
              onClick={() => setLangOpen((o) => !o)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/[0.10] bg-slate-900/80 text-slate-300 text-[12px] font-medium hover:border-teal-500/40 hover:text-white transition-all"
            >
              <Globe className="w-3.5 h-3.5 text-teal-400" />
              {selectedLang.label}
            </button>
            <AnimatePresence>
              {langOpen && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -4 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-9 z-50 w-44 rounded-xl border border-white/[0.08] bg-slate-900/95 backdrop-blur-xl shadow-2xl overflow-hidden"
                >
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.code}
                      id={`lang-opt-${lang.code}`}
                      onClick={() => { setSelectedLang(lang); setLangOpen(false) }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 text-[13px] hover:bg-slate-800/80 transition-colors ${selectedLang.code === lang.code ? 'text-teal-400' : 'text-slate-300'}`}
                    >
                      <span>{lang.label}</span>
                      <span className="text-slate-500">{lang.native}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-start px-4 sm:px-6 py-6 overflow-y-auto">
        <div className="w-full max-w-lg flex flex-col items-center gap-5">

          {/* Status text (mobile) */}
          <motion.div
            key={voiceState + '-mobile'}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="sm:hidden"
          >
            <span className={`text-[13px] font-medium ${statusColors[voiceState]}`}>{statusMap[voiceState]}</span>
          </motion.div>

          {/* Central orb */}
          <VoiceOrb voiceState={voiceState} onPress={handleOrbPress} />

          {/* Tap to speak prompt */}
          <AnimatePresence>
            {voiceState === 'IDLE' && (
              <motion.p
                key="tap-hint"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="text-sm text-slate-500 -mt-3"
              >
                Tap to speak
              </motion.p>
            )}
            {voiceState === 'PROCESSING' && (
              <motion.p
                key="thinking-hint"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-sm text-indigo-400 font-medium -mt-3"
              >
                Thinking&hellip;
              </motion.p>
            )}
          </AnimatePresence>

          {/* ── Transcript box ── */}
          <AnimatePresence>
            {transcript && (
              <motion.div
                key="transcript"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="w-full rounded-2xl border border-white/[0.07] bg-white/[0.03] backdrop-blur-sm p-4"
              >
                <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-2 font-medium flex items-center gap-1.5">
                  <Mic className="w-3 h-3 text-teal-400" /> You
                </p>
                <p className="text-[14px] text-slate-200 leading-relaxed">{transcript}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── AI response box ── */}
          <AnimatePresence>
            {aiResponse && (
              <motion.div
                key="ai-response"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="w-full rounded-2xl border border-teal-500/[0.15] bg-teal-500/[0.04] backdrop-blur-sm p-4"
              >
                <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-2 font-medium flex items-center gap-1.5">
                  <Sparkles className="w-3 h-3 text-emerald-400" /> YojVani
                </p>

                {/* Waveform when speaking */}
                {voiceState === 'SPEAKING' && !paused && (
                  <div className="mb-3">
                    <AudioWaveBars count={16} />
                  </div>
                )}

                <p className="text-[14px] text-slate-200 leading-relaxed">{aiResponse}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Matched scheme preview ── */}
          <AnimatePresence>
            {matchedScheme && (
              <SchemePreviewCard key="scheme-card" scheme={matchedScheme} />
            )}
          </AnimatePresence>


        </div>
      </main>

      {/* ── Bottom action toolbar ── */}
      <footer className="relative z-20 w-full px-4 sm:px-6 py-4 border-t border-white/[0.06] bg-slate-950/60 backdrop-blur-xl">
        <div className="max-w-lg mx-auto flex items-center justify-center gap-3">

          {/* Mute/Unmute */}
          <button
            id="voice-mute-btn"
            onClick={() => setMuted((m) => !m)}
            title={muted ? 'Unmute' : 'Mute'}
            className={`flex flex-col items-center gap-1 group`}
          >
            <div className={`w-11 h-11 rounded-2xl flex items-center justify-center border transition-all ${muted ? 'bg-red-500/15 border-red-500/30 text-red-400' : 'bg-slate-800/80 border-white/[0.06] text-slate-400 hover:text-white hover:bg-slate-700/80'}`}>
              {muted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </div>
            <span className="text-[10px] text-slate-600">{muted ? 'Unmute' : 'Mute'}</span>
          </button>

          {/* Pause / Resume audio */}
          <button
            id="voice-pause-btn"
            onClick={() => setPaused((p) => !p)}
            title={paused ? 'Resume' : 'Pause'}
            className="flex flex-col items-center gap-1"
          >
            <div className={`w-11 h-11 rounded-2xl flex items-center justify-center border transition-all ${paused ? 'bg-amber-500/15 border-amber-500/30 text-amber-400' : 'bg-slate-800/80 border-white/[0.06] text-slate-400 hover:text-white hover:bg-slate-700/80'}`}>
              {paused ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
            </div>
            <span className="text-[10px] text-slate-600">{paused ? 'Resume' : 'Pause'}</span>
          </button>

          {/* Replay */}
          <button
            id="voice-replay-btn"
            onClick={handleReplay}
            title="Replay last response"
            disabled={!aiResponse}
            className="flex flex-col items-center gap-1 disabled:opacity-40"
          >
            <div className="w-11 h-11 rounded-2xl flex items-center justify-center border border-white/[0.06] bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700/80 transition-all">
              <RotateCcw className="w-5 h-5" />
            </div>
            <span className="text-[10px] text-slate-600">Replay</span>
          </button>


        </div>
      </footer>
    </div>
  )
}
