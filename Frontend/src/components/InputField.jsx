import React, { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

/**
 * InputField — Reusable input component with:
 *   - Optional leading icon (lucide-react)
 *   - Password show/hide toggle
 *   - Inline validation error message
 *   - Focus & error visual states via Tailwind
 */
export default function InputField({
  id,
  label,
  type = 'text',
  value,
  onChange,
  icon: Icon,
  error,
  autoComplete,
  required = false,
}) {
  const [focused, setFocused] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const isPassword = type === 'password'
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type

  return (
    <div>
      <div
        className={`
          relative flex items-center rounded-xl border transition-all duration-200
          ${error
            ? 'border-red-500/50 bg-red-500/[0.04]'
            : focused
              ? 'border-indigo-500/50 bg-white/[0.04] shadow-[0_0_0_3px_rgba(99,102,241,0.08)]'
              : 'border-white/[0.08] bg-white/[0.02] hover:border-white/[0.14]'
          }
        `}
      >
        {/* Leading icon */}
        {Icon && (
          <span
            className={`
              pl-4 flex-shrink-0 transition-colors duration-200
              ${error ? 'text-red-400' : focused ? 'text-indigo-400' : 'text-slate-500'}
            `}
          >
            <Icon size={18} strokeWidth={1.8} />
          </span>
        )}

        {/* Input */}
        <input
          id={id}
          type={inputType}
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={label}
          autoComplete={autoComplete}
          required={required}
          className="
            w-full bg-transparent px-4 py-3 text-[14px] text-gray-200
            placeholder:text-slate-500 outline-none
          "
        />

        {/* Password toggle */}
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword((s) => !s)}
            className="pr-4 flex-shrink-0 text-slate-500 hover:text-slate-300 transition-colors duration-150"
            tabIndex={-1}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff size={18} strokeWidth={1.8} /> : <Eye size={18} strokeWidth={1.8} />}
          </button>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="mt-1.5 text-xs text-red-400 pl-1 animate-fade-in">{error}</p>
      )}
    </div>
  )
}
