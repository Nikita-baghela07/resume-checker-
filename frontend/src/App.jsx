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
          {/* Public routes */}
          <Route path="/auth" element={<ModernAuthPage />} />
          
          {/* Protected routes - require authentication */}
          <Route 
            path="/" 
            element={user ? <ModernHome /> : <Navigate to="/auth" replace />} 
          />
          <Route 
            path="/loading" 
            element={user ? <ModernLoadingPage /> : <Navigate to="/auth" replace />} 
          />
          <Route 
            path="/results" 
            element={user ? <ModernResultsPage /> : <Navigate to="/auth" replace />} 
          />
          
          {/* Redirect unknown routes to home or auth */}
          <Route path="*" element={<Navigate to={user ? "/" : "/auth"} replace />} />
        </Routes>
      </Router>
    </OptimizationProvider>
  )
}