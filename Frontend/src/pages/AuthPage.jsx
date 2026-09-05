import React from 'react'
import { Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import SignInForm from '../components/SignInForm'
import SignUpForm from '../components/SignUpForm'
import GoogleSignInButton from '../components/GoogleSignInButton'

/**
 * AuthPage — Centered glassmorphic card with route-driven mode.
 *
 * Props:
 *   mode — "signin" | "signup"  (set by App.jsx routes)
 *
 * /login  → mode="signin"  → shows SignInForm
 * /signup → mode="signup"  → shows SignUpForm
 */
export default function AuthPage({ mode = 'signin' }) {
  const isSignIn = mode === 'signin'

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4 py-6 relative overflow-hidden">

      {/* ── Background decoration ── */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-indigo-600/[0.12] rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute -bottom-48 -left-48 w-[600px] h-[600px] bg-purple-600/[0.08] rounded-full blur-[140px] animate-pulse-slow animation-delay-2000" />
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[400px] h-[400px] bg-teal-500/[0.04] rounded-full blur-[100px] animate-pulse-slow animation-delay-4000" />

        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* ── Auth Card ── */}
      <div className="relative w-full max-w-[440px] animate-fade-in-up">
        <div className="bg-slate-900/70 backdrop-blur-2xl border border-white/[0.06] rounded-2xl shadow-2xl shadow-black/50">

          {/* ── Header / Brand ── */}
          <div className="text-center pt-6 pb-1 px-8">
            <div className="inline-flex items-center gap-2.5 mb-2">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
                <Sparkles className="w-[18px] h-[18px] text-white" />
              </div>
              <h1 className="text-xl font-bold text-white tracking-tight">
                YojVani
              </h1>
            </div>
            <p className="text-[13px] text-slate-400">
              Your AI-powered Government Scheme Companion
            </p>
          </div>

          {/* ── Tab Bar (route-based) ── */}
          <div className="mx-8 mt-4 flex bg-slate-800/50 rounded-xl p-1 border border-white/[0.04]">
            <Link
              to="/login"
              className={`
                flex-1 py-2.5 text-[13px] font-semibold rounded-lg text-center
                transition-all duration-300 tracking-wide
                ${isSignIn
                  ? 'bg-indigo-500/[0.15] text-indigo-300 shadow-sm shadow-indigo-500/10'
                  : 'text-slate-500 hover:text-slate-300'
                }
              `}
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className={`
                flex-1 py-2.5 text-[13px] font-semibold rounded-lg text-center
                transition-all duration-300 tracking-wide
                ${!isSignIn
                  ? 'bg-indigo-500/[0.15] text-indigo-300 shadow-sm shadow-indigo-500/10'
                  : 'text-slate-500 hover:text-slate-300'
                }
              `}
            >
              Sign Up
            </Link>
          </div>

          {/* ── Form Content ── */}
          <div className="px-8 pt-4 pb-6">
            {/* Google OAuth */}
            <GoogleSignInButton />

            {/* Divider */}
            <div className="flex items-center gap-3 my-4">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent" />
              <span className="text-[11px] text-slate-500 uppercase tracking-[0.12em] font-medium whitespace-nowrap">
                or continue with email
              </span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent" />
            </div>

            {/* Active Form */}
            <div key={mode}>
              {isSignIn ? <SignInForm /> : <SignUpForm />}
            </div>

            {/* Footer switch (route links) */}
            <p className="text-center text-[13px] text-slate-500 mt-5">
              {isSignIn ? (
                <>
                  Don&apos;t have an account?{' '}
                  <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
                    Sign Up
                  </Link>
                </>
              ) : (
                <>
                  Already have an account?{' '}
                  <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
                    Sign In
                  </Link>
                </>
              )}
            </p>
          </div>
        </div>

        {/* Subtle bottom glow */}
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-3/4 h-16 bg-indigo-500/[0.06] blur-2xl rounded-full pointer-events-none" />
      </div>
    </div>
  )
}
