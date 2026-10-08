import React, { useState } from 'react'
import { GoogleLogin } from '@react-oauth/google'

export default function GoogleSignInButton() {
  const [error, setError] = useState(null)

  const handleSuccess = async (credentialResponse) => {
    try {
      console.log('✅ Google OAuth Success, sending to backend...')
      
      const res = await fetch('http://localhost:8080/api/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          credential: credentialResponse.credential,
        }),
      })

      if (!res.ok) {
        throw new Error('Backend authentication failed')
      }

      const data = await res.json()
      console.log('🎉 Backend returned token:', data.token)
      // TODO: Save this token to localStorage or your global state
      // localStorage.setItem('token', data.token)

    } catch (err) {
      console.error('❌ Error during backend auth:', err)
      setError(err.message)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center w-full">
      <GoogleLogin
        onSuccess={(e)=>{console.log(e)}}
        onError={(e) => {
          console.error('❌ Google Login UI Failed',e)
          setError('Google Login failed.')
        }}
        theme="filled_black"
        shape="pill"
        size="large"
        width="100%"
      />
      {error && <p className="text-red-400 mt-2 text-sm">{error}</p>}
    </div>
  )
}
