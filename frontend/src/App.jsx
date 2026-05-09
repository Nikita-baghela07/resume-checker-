import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import ModernHome from './pages/ModernHome.jsx'
import ModernLoadingPage from './pages/ModernLoadingPage.jsx'
import ModernResultsPage from './pages/ModernResultsPage.jsx'
import ModernAuthPage from './pages/ModernAuthPage.jsx'
import ChatWidget from './components/ChatWidget.jsx'
import { useAuth } from './context/AuthContext.jsx'
import { OptimizationProvider } from './context/OptimizationContext.jsx'

export default function App() {
  const { user, loading: authLoading } = useAuth()

  // Allow guest access - test mode doesn't require login
  const isAuthenticated = user !== null

  if (authLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #1f4788 0%, #2d1b3d 100%)',
        color: '#ffffff'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚡</div>
          <div style={{ fontSize: '18px', fontWeight: '500', marginBottom: '8px' }}>OptiResume AI</div>
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>Loading your session...</div>
        </div>
      </div>
    )
  }

  return (
    <OptimizationProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/auth" element={<ModernAuthPage />} />
          
          {/* Routes that work with or without authentication (guest mode allowed) */}
          <Route path="/" element={<ModernHome />} />
          <Route path="/loading" element={<ModernLoadingPage />} />
          <Route path="/results" element={<ModernResultsPage />} />
          
          {/* Redirect unknown routes to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ChatWidget />
      </Router>
    </OptimizationProvider>
  )
}