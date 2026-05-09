import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import '../styles/modern.css';

export default function ModernProfilePage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  if (!user) {
    navigate('/auth');
    return null;
  }

  return (
    <>
      <nav>
        <div className="nav-inner">
          <a href="/" className="logo">
            <div className="logo-mark">OR</div>
            <span className="logo-text">Opti<span style={{ color: 'var(--accent)' }}>Resume</span></span>
          </a>
          <div className="nav-links">
            <button className="nav-link" onClick={() => navigate('/')}>Home</button>
            <button className="nav-link" onClick={logout}>Logout</button>
          </div>
        </div>
      </nav>

      <div className="results-body" style={{ maxWidth: '800px', marginTop: '40px' }}>
        <div className="score-card fade-in">
          <div className="score-card-header">
            <div className="score-card-title">User Profile</div>
            <div className="score-card-badge">Account Settings</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '20px 0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%', 
                background: 'var(--accent)', 
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '32px',
                fontWeight: '700'
              }}>
                {user.full_name?.charAt(0) || user.email?.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 style={{ fontSize: '24px', color: 'var(--text)' }}>{user.full_name || 'User'}</h2>
                <p style={{ color: 'var(--text2)' }}>{user.email}</p>
              </div>
            </div>

            <div className="divider"></div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div className="feature-card">
                <div className="feature-name">Account Type</div>
                <div className="feature-desc">Free Plan</div>
              </div>
              <div className="feature-card">
                <div className="feature-name">Optimization Count</div>
                <div className="feature-desc">Unlimted Access</div>
              </div>
            </div>

            <button 
              className="btn-outline" 
              style={{ width: 'fit-content', marginTop: '20px', color: 'var(--red)', borderColor: 'var(--red)' }}
              onClick={logout}
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
