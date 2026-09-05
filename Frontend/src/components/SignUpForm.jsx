import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Mail, Lock } from 'lucide-react'
import InputField from './InputField'
import Button from './Button'

/**
 * SignUpForm — Registration form with:
 *   - Full Name, Email, Password, Confirm Password
 *   - Animated password strength indicator
 *   - Terms & Privacy agreement checkbox
 *   - Inline validation
 *   - Loading state on submit
 *   - Mock handler (console.log)
 */
export default function SignUpForm() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  /* ── Password strength calculator ── */
  const getPasswordStrength = (pw) => {
    if (!pw) return { level: 0, label: '', color: '' }
    let score = 0
    if (pw.length >= 6) score++
    if (pw.length >= 10) score++
    if (/[A-Z]/.test(pw)) score++
    if (/[0-9]/.test(pw)) score++
    if (/[^A-Za-z0-9]/.test(pw)) score++

    if (score <= 1) return { level: 1, label: 'Weak', color: 'bg-red-500', textColor: 'text-red-400' }
    if (score <= 2) return { level: 2, label: 'Fair', color: 'bg-amber-500', textColor: 'text-amber-400' }
    if (score <= 3) return { level: 3, label: 'Good', color: 'bg-yellow-400', textColor: 'text-yellow-400' }
    if (score <= 4) return { level: 4, label: 'Strong', color: 'bg-emerald-400', textColor: 'text-emerald-400' }
    return { level: 5, label: 'Very Strong', color: 'bg-emerald-400', textColor: 'text-emerald-400' }
  }

  const strength = getPasswordStrength(form.password)

  /* ── Validation ── */
  const validate = () => {
    const errs = {}
    if (!form.name.trim()) errs.name = 'Full name is required'
    if (!form.email.trim()) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Please enter a valid email'
    if (!form.password) errs.password = 'Password is required'
    else if (form.password.length < 6) errs.password = 'Must be at least 6 characters'
    if (!form.confirmPassword) errs.confirmPassword = 'Please confirm your password'
    else if (form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match'
    if (!agreedToTerms) errs.terms = 'You must agree to the Terms of Service'
    return errs
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    // ──── Mock auth handler — redirect to login after delay ────
    console.log('🚀 Sign Up submitted:', { name: form.name, email: form.email })
    setTimeout(() => {
      setLoading(false)
      navigate('/login')
    }, 1500)
  }

  const update = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 animate-fade-in" noValidate>
      {/* Full Name */}
      <InputField
        id="signup-name"
        label="Full name"
        type="text"
        value={form.name}
        onChange={update('name')}
        icon={User}
        error={errors.name}
        autoComplete="name"
      />

      {/* Email */}
      <InputField
        id="signup-email"
        label="Email address"
        type="email"
        value={form.email}
        onChange={update('email')}
        icon={Mail}
        error={errors.email}
        autoComplete="email"
      />

      {/* Password + strength meter */}
      <div>
        <InputField
          id="signup-password"
          label="Password"
          type="password"
          value={form.password}
          onChange={update('password')}
          icon={Lock}
          error={errors.password}
          autoComplete="new-password"
        />

        {/* Strength indicator */}
        {form.password && (
          <div className="mt-2 space-y-1 animate-fade-in">
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className={`
                    h-[3px] flex-1 rounded-full transition-all duration-500 ease-out
                    ${i <= strength.level ? strength.color : 'bg-slate-700/60'}
                  `}
                />
              ))}
            </div>
            <p className={`text-[11px] font-medium tracking-wide ${strength.textColor} transition-colors`}>
              {strength.label}
            </p>
          </div>
        )}
      </div>

      {/* Confirm Password */}
      <InputField
        id="signup-confirm-password"
        label="Confirm password"
        type="password"
        value={form.confirmPassword}
        onChange={update('confirmPassword')}
        icon={Lock}
        error={errors.confirmPassword}
        autoComplete="new-password"
      />

      {/* Terms checkbox */}
      <div>
        <label className="flex items-start gap-2.5 cursor-pointer group select-none">
          <div className="relative mt-0.5">
            <input
              type="checkbox"
              checked={agreedToTerms}
              onChange={(e) => {
                setAgreedToTerms(e.target.checked)
                if (errors.terms) setErrors((prev) => ({ ...prev, terms: undefined }))
              }}
              className="
                peer appearance-none w-[18px] h-[18px] rounded-[5px]
                border border-slate-600 bg-slate-800/80
                checked:bg-indigo-500 checked:border-indigo-500
                transition-all duration-200 cursor-pointer
                hover:border-slate-500
              "
            />
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
          <span className="text-[13px] text-slate-400 group-hover:text-slate-300 transition-colors leading-5">
            I agree to the{' '}
            <button type="button" className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
              Terms of Service
            </button>{' '}
            and{' '}
            <button type="button" className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
              Privacy Policy
            </button>
          </span>
        </label>
        {errors.terms && (
          <p className="mt-1.5 text-xs text-red-400 pl-7 animate-fade-in">{errors.terms}</p>
        )}
      </div>

      {/* Submit */}
      <div className="pt-1">
        <Button type="submit" loading={loading} fullWidth id="signup-submit">
          Create Account
        </Button>
      </div>
    </form>
  )
}
