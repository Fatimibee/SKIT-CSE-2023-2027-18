import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock } from 'lucide-react'
import InputField from './InputField'
import Button from './Button'

/**
 * SignInForm — Email + Password sign-in with:
 *   - Inline validation
 *   - "Remember me" checkbox
 *   - "Forgot password?" link
 *   - Loading state on submit
 *   - Mock handler (console.log)
 */
export default function SignInForm() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [remember, setRemember] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const validate = () => {
    const errs = {}
    if (!form.email.trim()) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Please enter a valid email'
    if (!form.password) errs.password = 'Password is required'
    else if (form.password.length < 6) errs.password = 'Must be at least 6 characters'
    return errs
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    // ──── Mock auth handler — redirect to dashboard after delay ────
    console.log('🔐 Sign In submitted:', { email: form.email, remember })
    setTimeout(() => {
      setLoading(false)
      navigate('/dashboard')
    }, 1500)
  }

  const update = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 animate-fade-in" noValidate>
      <InputField
        id="signin-email"
        label="Email address"
        type="email"
        value={form.email}
        onChange={update('email')}
        icon={Mail}
        error={errors.email}
        autoComplete="email"
      />

      <InputField
        id="signin-password"
        label="Password"
        type="password"
        value={form.password}
        onChange={update('password')}
        icon={Lock}
        error={errors.password}
        autoComplete="current-password"
      />

      {/* Remember me + Forgot password */}
      <div className="flex items-center justify-between pt-0.5">
        <label className="flex items-center gap-2.5 cursor-pointer group select-none">
          <div className="relative">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              className="
                peer appearance-none w-[18px] h-[18px] rounded-[5px]
                border border-slate-600 bg-slate-800/80
                checked:bg-indigo-500 checked:border-indigo-500
                transition-all duration-200 cursor-pointer
                hover:border-slate-500
              "
            />
            {/* Checkmark icon */}
            <svg
              className="
                absolute top-[3px] left-[3px] w-3 h-3
                text-white opacity-0 peer-checked:opacity-100
                transition-opacity duration-200 pointer-events-none
              "
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M2 6l3 3 5-5" />
            </svg>
          </div>
          <span className="text-[13px] text-slate-400 group-hover:text-slate-300 transition-colors">
            Remember me
          </span>
        </label>

        <button
          type="button"
          className="text-[13px] text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
        >
          Forgot password?
        </button>
      </div>

      {/* Submit */}
      <div className="pt-1">
        <Button type="submit" loading={loading} fullWidth id="signin-submit">
          Sign In
        </Button>
      </div>
    </form>
  )
}
