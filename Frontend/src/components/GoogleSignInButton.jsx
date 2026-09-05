import React from 'react'
import { useGoogleLogin } from '@react-oauth/google'

/**
 * GoogleSignInButton — Styled "Continue with Google" button.
 *
 * Uses the useGoogleLogin hook from @react-oauth/google.
 * Configure a valid VITE_GOOGLE_CLIENT_ID in your .env for real OAuth.
 * Without a valid client ID, clicking the button will log a Google error
 * to the console — the rest of the app remains fully functional.
 */
export default function GoogleSignInButton() {
  const login = useGoogleLogin({
    onSuccess: (tokenResponse) => {
      console.log('✅ Google OAuth Success — Access Token:', tokenResponse.access_token)
      console.log('Full token response:', tokenResponse)
    },
    onError: (errorResponse) => {
      console.error('❌ Google OAuth Error:', errorResponse)
    },
  })

  return (
    <button
      type="button"
      onClick={() => login()}
      id="google-signin-btn"
      className="
        w-full py-3 px-4 rounded-xl
        border border-white/[0.08] bg-white/[0.02]
        hover:bg-white/[0.06] hover:border-white/[0.14]
        transition-all duration-200
        flex items-center justify-center gap-3
        text-[14px] font-medium text-gray-300 hover:text-white
        active:scale-[0.98]
      "
    >
      {/* Google "G" logo — official colors */}
      <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
          fill="#4285F4"
        />
        <path
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          fill="#34A853"
        />
        <path
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          fill="#FBBC05"
        />
        <path
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          fill="#EA4335"
        />
      </svg>
      Continue with Google
    </button>
  )
}
