import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Mic, Keyboard, UploadCloud, Search, ArrowRight, MessageSquare, FileCheck, CheckCircle, Users, Activity, Star, Sparkles } from 'lucide-react'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1">
        {/* ── Hero Section ── */}
        <section className="relative px-4 pt-20 pb-24 overflow-hidden">
          {/* Background Elements */}
          <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
            <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-teal-600/[0.12] rounded-full blur-[120px] animate-pulse-slow" />
            <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-indigo-600/[0.08] rounded-full blur-[140px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
            <div
              className="absolute inset-0 opacity-[0.03]"
              style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px)',
                backgroundSize: '60px 60px',
              }}
            />
          </div>

          <div className="relative max-w-5xl mx-auto text-center animate-fade-in-up">
            
            {/* Floating Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4" />
              <span>India's #1 Multimodal AI Scheme Assistant</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight mb-6">
              Government Welfare Schemes, <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-500">Tailored to Your Voice.</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-12 leading-relaxed">
              Discover eligible government schemes, get instant answers, and analyze application forms using voice, text, or document upload in your local language.
            </p>

            {/* Central Interactive Gateway Preview Card */}
            <div className="max-w-3xl mx-auto bg-slate-900/60 backdrop-blur-xl border border-white/[0.08] p-8 rounded-3xl shadow-2xl shadow-black/50 flex flex-col gap-8">
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Voice Interaction */}
                <button 
                  onClick={() => navigate('/voice')}
                  className="group relative flex flex-col items-center gap-4 p-6 bg-slate-800/50 hover:bg-slate-800 border border-white/[0.05] hover:border-teal-500/50 rounded-2xl transition-all duration-300"
                >
                  <div className="relative w-16 h-16 flex items-center justify-center">
                    <div className="absolute inset-0 bg-teal-500/20 rounded-full animate-ping" />
                    <div className="absolute inset-0 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg shadow-teal-500/30">
                      <Mic className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="text-center">
                    <h3 className="text-white font-semibold mb-1">Speak</h3>
                    <p className="text-xs text-slate-400">Ask in your language</p>
                  </div>
                </button>

                {/* Text Interaction */}
                <button 
                  onClick={() => navigate('/chat')}
                  className="group relative flex flex-col items-center gap-4 p-6 bg-slate-800/50 hover:bg-slate-800 border border-white/[0.05] hover:border-indigo-500/50 rounded-2xl transition-all duration-300"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/30 group-hover:scale-105 transition-transform">
                    <Keyboard className="w-8 h-8 text-white" />
                  </div>
                  <div className="text-center">
                    <h3 className="text-white font-semibold mb-1">Type</h3>
                    <p className="text-xs text-slate-400">Chat with the assistant</p>
                  </div>
                </button>

                {/* Form Interaction */}
                <button 
                  onClick={() => navigate('/form-upload')}
                  className="group relative flex flex-col items-center gap-4 p-6 bg-slate-800/50 hover:bg-slate-800 border border-white/[0.05] hover:border-purple-500/50 rounded-2xl transition-all duration-300 border-dashed"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:-translate-y-1 transition-transform">
                    <UploadCloud className="w-8 h-8 text-white" />
                  </div>
                  <div className="text-center">
                    <h3 className="text-white font-semibold mb-1">Upload</h3>
                    <p className="text-xs text-slate-400">Analyze forms & docs</p>
                  </div>
                </button>

              </div>
              
              {/* Fallback Search Bar */}
              <div className="relative w-full max-w-xl mx-auto hidden md:block">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="E.g., 'What schemes are available for farmers in Karnataka?'" 
                  className="w-full bg-slate-950/50 border border-white/[0.1] text-white pl-12 pr-4 py-4 rounded-xl focus:outline-none focus:border-teal-500/50 focus:ring-1 focus:ring-teal-500/50 transition-all text-sm placeholder:text-slate-500"
                  readOnly
                  onClick={() => navigate('/chat')}
                />
              </div>
            </div>

            {/* Stats Banner */}
            <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto opacity-80">
              <div className="flex flex-col items-center p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <Users className="w-6 h-6 text-indigo-400 mb-2" />
                <span className="text-2xl font-bold text-white">50k+</span>
                <span className="text-xs text-slate-400">Citizens Assisted</span>
              </div>
              <div className="flex flex-col items-center p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <CheckCircle className="w-6 h-6 text-teal-400 mb-2" />
                <span className="text-2xl font-bold text-white">100+</span>
                <span className="text-xs text-slate-400">Schemes Covered</span>
              </div>
              <div className="flex flex-col items-center p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <Activity className="w-6 h-6 text-purple-400 mb-2" />
                <span className="text-2xl font-bold text-white">99%</span>
                <span className="text-xs text-slate-400">Accuracy Rate</span>
              </div>
              <div className="flex flex-col items-center p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <Star className="w-6 h-6 text-yellow-400 mb-2" />
                <span className="text-2xl font-bold text-white">4.9/5</span>
                <span className="text-xs text-slate-400">User Rating</span>
              </div>
            </div>

          </div>
        </section>

        {/* ── Multimodal Teaser Cards ── */}
        <section id="features" className="py-20 bg-slate-900 border-t border-white/[0.05]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Three Ways to Connect</h2>
              <p className="text-slate-400 max-w-2xl mx-auto">Interact with YojVani in the way that feels most natural to you. Our multimodal AI understands you seamlessly.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              
              {/* Card 1 */}
              <div className="bg-slate-950 border border-white/[0.08] rounded-3xl p-8 hover:-translate-y-2 hover:shadow-2xl hover:shadow-teal-500/10 transition-all duration-300">
                <div className="w-12 h-12 bg-teal-500/10 rounded-xl flex items-center justify-center mb-6">
                  <Mic className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Voice Assistant (Vani)</h3>
                <p className="text-sm text-slate-400 leading-relaxed mb-8">
                  Speak in your native dialect to find eligible schemes effortlessly. Natural, conversational AI that understands regional nuances.
                </p>
                <Link to="/voice" className="inline-flex items-center gap-2 text-teal-400 font-medium hover:text-teal-300 transition-colors text-sm">
                  Start Speaking <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

              {/* Card 2 */}
              <div className="bg-slate-950 border border-white/[0.08] rounded-3xl p-8 hover:-translate-y-2 hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300">
                <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center mb-6">
                  <MessageSquare className="w-6 h-6 text-indigo-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Text Assistant</h3>
                <p className="text-sm text-slate-400 leading-relaxed mb-8">
                  Type your queries or profile details for instant AI recommendations. Deep search across central and state schemes.
                </p>
                <Link to="/chat" className="inline-flex items-center gap-2 text-indigo-400 font-medium hover:text-indigo-300 transition-colors text-sm">
                  Open Chat <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

              {/* Card 3 */}
              <div className="bg-slate-950 border border-white/[0.08] rounded-3xl p-8 hover:-translate-y-2 hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-300">
                <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-6">
                  <FileCheck className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Form & Document Analyzer</h3>
                <p className="text-sm text-slate-400 leading-relaxed mb-8">
                  Upload PDF/JPG forms or IDs to check criteria and get completion steps. Auto-fill guidance based on your uploaded documents.
                </p>
                <Link to="/form-upload" className="inline-flex items-center gap-2 text-purple-400 font-medium hover:text-purple-300 transition-colors text-sm">
                  Upload Form <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

            </div>
          </div>
        </section>

        {/* ── How It Works ── */}
        <section id="how-it-works" className="py-24 bg-slate-950 relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            
            <div className="text-center mb-20">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">How YojVani Works</h2>
              <p className="text-slate-400 max-w-2xl mx-auto">Three simple steps to connect you with the government benefits you deserve.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
              
              {/* Step 1 */}
              <div className="relative">
                <div className="w-20 h-20 mx-auto bg-slate-900 border-2 border-slate-800 rounded-full flex items-center justify-center mb-6 relative z-10 shadow-xl">
                  <span className="text-2xl font-bold text-teal-400">1</span>
                </div>
                <div className="hidden md:block absolute top-10 left-[60%] w-full h-[2px] bg-gradient-to-r from-slate-800 to-transparent" />
                <h3 className="text-xl font-bold text-white mb-3">Input Your Need</h3>
                <p className="text-sm text-slate-400 leading-relaxed px-4">
                  Speak into your device, type your query, or upload your document/form to get started securely.
                </p>
              </div>

              {/* Step 2 */}
              <div className="relative">
                <div className="w-20 h-20 mx-auto bg-slate-900 border-2 border-slate-800 rounded-full flex items-center justify-center mb-6 relative z-10 shadow-xl">
                  <span className="text-2xl font-bold text-indigo-400">2</span>
                </div>
                <div className="hidden md:block absolute top-10 left-[60%] w-full h-[2px] bg-gradient-to-r from-slate-800 to-transparent" />
                <h3 className="text-xl font-bold text-white mb-3">Intelligent Matching</h3>
                <p className="text-sm text-slate-400 leading-relaxed px-4">
                  YojVani scans official central and state welfare databases to instantly match your criteria.
                </p>
              </div>

              {/* Step 3 */}
              <div className="relative">
                <div className="w-20 h-20 mx-auto bg-slate-900 border-2 border-slate-800 rounded-full flex items-center justify-center mb-6 relative z-10 shadow-xl">
                  <span className="text-2xl font-bold text-emerald-400">3</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Clear Guidance</h3>
                <p className="text-sm text-slate-400 leading-relaxed px-4">
                  Get audio explanations, translated summaries, or step-by-step form help right on your screen.
                </p>
              </div>

            </div>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  )
}
