import React from 'react'
import { Loader2 } from 'lucide-react'

/**
 * Button — Reusable CTA button with:
 *   - primary (gradient) / secondary (outline) variants
 *   - Loading spinner via lucide Loader2
 *   - Disabled state
 *   - Full-width option
 *   - Hover scale + glow micro-animation
 */
export default function Button({
  children,
  type = 'button',
  onClick,
  variant = 'primary',
  loading = false,
  disabled = false,
  fullWidth = false,
  id,
}) {
  const base = `
    relative py-3 px-6 rounded-xl font-semibold text-[14px] tracking-wide
    transition-all duration-300 flex items-center justify-center gap-2
    disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
    active:scale-[0.97]
  `

  const variants = {
    primary: `
      text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600
      hover:from-indigo-500 hover:via-indigo-400 hover:to-purple-500
      hover:shadow-xl hover:shadow-indigo-500/20 hover:scale-[1.02]
    `,
    secondary: `
      text-gray-300 border border-white/[0.08] bg-white/[0.02]
      hover:bg-white/[0.05] hover:border-white/[0.14] hover:text-white
      hover:scale-[1.01]
    `,
  }

  return (
    <button
      id={id}
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${base} ${variants[variant] || variants.primary} ${fullWidth ? 'w-full' : ''}`}
    >
      {loading && <Loader2 size={18} className="animate-spin" />}
      <span className={loading ? 'opacity-0' : ''}>{children}</span>
      {loading && (
        <span className="absolute inset-0 flex items-center justify-center gap-2 text-white">
          <Loader2 size={18} className="animate-spin" />
          {typeof children === 'string' && children.includes('Sign In')
            ? 'Signing in…'
            : typeof children === 'string' && children.includes('Create')
              ? 'Creating account…'
              : 'Loading…'
          }
        </span>
      )}
    </button>
  )
}
