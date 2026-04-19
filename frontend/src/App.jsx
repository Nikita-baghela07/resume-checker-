import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import ModernHome from './pages/ModernHome.jsx'
import ModernLoadingPage from './pages/ModernLoadingPage.jsx'
import ModernResultsPage from './pages/ModernResultsPage.jsx'
import ModernAuthPage from './pages/ModernAuthPage.jsx'
import { useAuth } from './context/AuthContext.jsx'
import { OptimizationProvider } from './context/OptimizationContext.jsx'

export default function App() {
  const { user, loading: authLoading } = useAuth()

  if (authLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'var(--bg)'
      }}>
        <div style={{ fontSize: '18px', color: 'var(--text2)' }}>Loading...</div>
      </div>
    )
  }

  return (
    <OptimizationProvider>
      <Router>
        <Routes>
          <Route path="/auth" element={<ModernAuthPage />} />
          <Route path="/" element={<ModernHome />} />
          <Route path="/loading" element={<ModernLoadingPage />} />
          <Route path="/results" element={<ModernResultsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </OptimizationProvider>
  )
}