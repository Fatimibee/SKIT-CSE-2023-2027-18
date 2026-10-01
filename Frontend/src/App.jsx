import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import ProfilePage from './pages/ProfilePage'
import VoiceAssistantPage from './pages/VoiceAssistantPage'
import SchemesPage from './pages/SchemesPage'
import ChatPage from './pages/ChatPage'
import DocumentUploadPage from './pages/DocumentUploadPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<AuthPage mode="signin" />} />
      <Route path="/signup" element={<AuthPage mode="signup" />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/voice" element={<VoiceAssistantPage />} />
      <Route path="/schemes" element={<SchemesPage />} />
      <Route path="/document-upload" element={<DocumentUploadPage />} />
      {/* Redirect all unknown routes to landing page */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
