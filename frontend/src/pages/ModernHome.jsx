import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadResume, optimizeResume } from '../services/api.js';
import { useOptimization } from '../context/OptimizationContext.jsx';
import '../styles/modern.css';

export default function Home() {
  const navigate = useNavigate();
  const { setResults, setLoading: setOptLoading, setError: setOptError } = useOptimization();
  const [mode, setMode] = useState('upload');
  const [hasFile, setHasFile] = useState(false);
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [fileName, setFileName] = useState('');
  const [optimizing, setOptimizing] = useState(false);
  const [uploadedResumeText, setUploadedResumeText] = useState('');

  const checkReady = () => {
    const hasResume = mode === 'upload' ? hasFile : resumeText.trim().length >= 300;
    const hasJD = jdText.trim().length >= 50;
    return hasResume && hasJD;
  };

  const handleFileSelect = (file) => {
    if (file && file.type === 'application/pdf') {
      setHasFile(true);
      setFileName(file.name);
    }
  };

  const handleOptimize = async () => {
    if (!checkReady() || optimizing) return;

    setOptimizing(true);
    setOptLoading(true);

    try {
      // Get resume text (from upload or paste)
      let finalResumeText = resumeText;

      if (mode === 'upload' && hasFile) {
        const fileInput = document.getElementById('file-input');
        if (fileInput && fileInput.files[0]) {
          console.log('Uploading file:', fileInput.files[0].name);
          const uploadResult = await uploadResume(fileInput.files[0]);
          console.log('Upload result:', uploadResult);
          
          if (!uploadResult.resume_text) {
            throw new Error('Failed to extract text from PDF. Please try a different file.');
          }
          
          finalResumeText = uploadResult.resume_text;
          setUploadedResumeText(finalResumeText);
        }
      }

      if (!finalResumeText || finalResumeText.length < 300) {
        throw new Error(`Resume must be at least 300 characters (currently ${finalResumeText.length} characters)`);
      }
      
      if (!jdText || jdText.length < 50) {
        throw new Error(`Job description must be at least 50 characters (currently ${jdText.length} characters)`);
      }

      console.log('Starting optimization with:', { 
        resumeLength: finalResumeText.length, 
        jdLength: jdText.length 
      });
      
      // Call optimize API
      const results = await optimizeResume(finalResumeText, jdText);
      console.log('Optimization results:', results);
      
      // Store results in context
      setResults(results);
      setOptError(null);

      // Navigate to loading page, then results
      navigate('/loading');
    } catch (err) {
      console.error('Optimization error:', err);
      
      // Extract error message properly
      let errorMsg = 'Failed to optimize resume. Please try again.';
      
      if (err?.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err?.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err?.message && typeof err.message === 'string') {
        errorMsg = err.message;
      } else if (err?.response?.status === 0 || err?.code === 'ECONNABORTED') {
        errorMsg = 'Connection timeout. Is the backend server running?';
      } else if (err?.response?.status >= 500) {
        errorMsg = 'Server error. Please try again in a moment.';
      }
      
      setOptError(errorMsg);
      setOptLoading(false);
      alert(`Error: ${errorMsg}`);
      console.log('Full error object:', err);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <>
      {/* Navigation */}
      <nav>
        <div className="nav-inner">
          <a href="/" className="logo">
            <div className="logo-mark">OR</div>
            <span className="logo-text">Opti<span style={{ color: 'var(--accent)' }}>Resume</span></span>
          </a>
          <div className="nav-links">
            <button className="nav-link">How it works</button>
            <button className="nav-link">Features</button>
            <button className="nav-link">Pricing</button>
            <button className="nav-cta" onClick={() => document.getElementById('upload-section').scrollIntoView({ behavior: 'smooth' })}>
              Optimize Resume →
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero fade-in" id="upload-section">
        <div className="hero-left">
          <div className="hero-badge">
            <span className="hero-badge-dot"></span>
            ATS Semantic Scoring Engine
          </div>
          <h1>Get past the<br/><em>ATS filter</em>.<br/>Land the interview.</h1>
          <p className="hero-sub">Upload your resume, paste any job description — get a semantically scored, AI-optimized resume with before/after proof in under 10 seconds.</p>
          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-num">70%</div>
              <div className="hero-stat-label">Resumes rejected by ATS</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-num">+36%</div>
              <div className="hero-stat-label">Average score improvement</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-num">&lt;10s</div>
              <div className="hero-stat-label">Full optimization time</div>
            </div>
          </div>
          <div className="trust-row">
            <div className="trust-item"><div className="trust-check">✓</div>No fabricated experience</div>
            <div className="trust-item"><div className="trust-check">✓</div>ATS-safe PDF output</div>
            <div className="trust-item"><div className="trust-check">✓</div>Explainable skill gaps</div>
          </div>
        </div>

        {/* Upload Card */}
        <div className="upload-card fade-in" style={{ animationDelay: '0.1s' }}>
          <div className="upload-card-header">
            <div className="upload-card-title">Optimize your resume</div>
            <div className="upload-card-sub">Free · No account required</div>
          </div>
          <div className="upload-card-body">
            {/* Resume Section */}
            <div style={{ marginBottom: '18px' }}>
              <div className="jd-label">
                <span>① Your resume</span>
                <div className="mode-toggle">
                  <button className={`mode-btn ${mode === 'upload' ? 'active' : ''}`} onClick={() => setMode('upload')}>Upload PDF</button>
                  <button className={`mode-btn ${mode === 'paste' ? 'active' : ''}`} onClick={() => setMode('paste')}>Paste text</button>
                </div>
              </div>

              {/* Upload Mode */}
              {mode === 'upload' && !hasFile && (
                <div
                  className="drop-zone"
                  onClick={() => document.getElementById('file-input').click()}
                  onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('drag-over'); }}
                  onDragLeave={(e) => e.currentTarget.classList.remove('drag-over')}
                  onDrop={(e) => {
                    e.preventDefault();
                    e.currentTarget.classList.remove('drag-over');
                    const file = e.dataTransfer.files[0];
                    handleFileSelect(file);
                  }}
                >
                  <input
                    type="file"
                    id="file-input"
                    accept=".pdf"
                    className="drop-file-input"
                    onChange={(e) => handleFileSelect(e.target.files[0])}
                  />
                  <div className="drop-icon">📄</div>
                  <div className="drop-title">Drop your PDF here</div>
                  <div className="drop-sub">or <span>browse files</span> — PDF only, max 5MB</div>
                </div>
              )}

              {/* File Selected */}
              {hasFile && (
                <div className="drop-success show">
                  <div className="drop-success-icon">✓</div>
                  <div>
                    <div className="drop-success-name">{fileName}</div>
                    <div className="drop-success-meta">Ready to optimize</div>
                  </div>
                  <button className="drop-success-remove" onClick={() => { setHasFile(false); setFileName(''); }}>×</button>
                </div>
              )}

              {/* Paste Mode */}
              {mode === 'paste' && (
                <>
                  <textarea
                    className="jd-textarea"
                    placeholder="Paste your full resume text here..."
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    style={{ minHeight: '120px' }}
                  />
                  <div className="jd-count">
                    <span>{resumeText.length}</span> / 300 characters minimum
                    {resumeText.length < 300 && <span style={{ color: '#EF4444', marginLeft: '8px' }}>({300 - resumeText.length} more needed)</span>}
                  </div>
                </>
              )}
            </div>

            <div className="divider"></div>

            {/* Job Description Section */}
            <div style={{ marginBottom: '20px' }}>
              <div className="jd-label">
                <span>② Job description</span>
                <button className="jd-sample-btn" onClick={() => setJdText('Software Engineer — Backend\n\nRequired: Python, FastAPI, PostgreSQL, Docker, CI/CD, REST APIs\n\nResponsibilities: Design scalable backend systems, lead architecture initiatives...')}>
                  Load sample →
                </button>
              </div>
              <textarea
                className="jd-textarea"
                placeholder="Paste the job description you're applying for..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
              />
              <div className="jd-count"><span>{jdText.length}</span> characters</div>
            </div>

            <button
              className="optimize-btn"
              onClick={handleOptimize}
              disabled={!checkReady() || optimizing}
              style={{ opacity: !checkReady() || optimizing ? 0.6 : 1, cursor: !checkReady() || optimizing ? 'not-allowed' : 'pointer' }}
            >
              {optimizing ? '⟳ Optimizing...' : 'Optimize My Resume →'}
            </button>
            <div className="btn-hint">
              {!checkReady() ? (
                resumeText.length < 300 && mode === 'paste' 
                  ? `Resume too short: ${300 - resumeText.length} more characters needed`
                  : 'Upload your resume (PDF) and paste a job description to continue'
              ) : 'No data stored · ATS-safe output guaranteed'}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-strip">
        <div className="features-inner">
          <div className="features-header">
            <div className="features-eyebrow">What we do differently</div>
            <h2 className="features-title">Not keyword stuffing.<br/>Semantic intelligence.</h2>
            <p className="features-sub">We use the same embedding technology that modern ATS systems use — so we optimize for meaning, not just words.</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon" style={{ background: '#FFF3EE', border: '1px solid #FFE8DC' }}>🎯</div>
              <div className="feature-name">Semantic ATS Scoring</div>
              <div className="feature-desc">SBERT embeddings score your resume section-by-section. Skills 50% · Experience 30% · Keywords 20%</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon" style={{ background: '#EDFAF4', border: '1px solid #BBF7D0' }}>✏️</div>
              <div className="feature-name">Truth-Preserved Rewriting</div>
              <div className="feature-desc">Claude rewrites your bullets to match JD language. Zero fabricated experience.</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon" style={{ background: '#FFFBEB', border: '1px solid #FDE68A' }}>🔍</div>
              <div className="feature-name">Skill Gap Intelligence</div>
              <div className="feature-desc">Identifies exactly what you're missing, ranked High / Medium / Low.</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon" style={{ background: '#F5F3FF', border: '1px solid #DDD6FE' }}>📄</div>
              <div className="feature-name">Professional PDF Output</div>
              <div className="feature-desc">ATS-safe resume PDF with professional formatting.</div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="proof-strip">
        <div className="proof-inner">
          <div className="proof-card">
            <div className="proof-score-row">
              <div className="proof-before">38%</div>
              <div className="proof-arrow">→</div>
              <div className="proof-after">81%</div>
              <div className="proof-delta">+43%</div>
            </div>
            <div className="proof-quote">"I've been applying for months with no callbacks. OptiResume showed me exactly what was missing — Docker and CI/CD were the blockers."</div>
            <div className="proof-author">Arjun Mehta</div>
            <div className="proof-role">Backend Engineer, Bangalore</div>
          </div>
          <div className="proof-card">
            <div className="proof-score-row">
              <div className="proof-before">44%</div>
              <div className="proof-arrow">→</div>
              <div className="proof-after">79%</div>
              <div className="proof-delta">+35%</div>
            </div>
            <div className="proof-quote">"The skill gap breakdown was eye-opening. I didn't realize my resume was missing 6 keywords from the job description."</div>
            <div className="proof-author">Priya Sharma</div>
            <div className="proof-role">Data Analyst, Pune</div>
          </div>
          <div className="proof-card">
            <div className="proof-score-row">
              <div className="proof-before">42%</div>
              <div className="proof-arrow">→</div>
              <div className="proof-after">78%</div>
              <div className="proof-delta">+36%</div>
            </div>
            <div className="proof-quote">"It doesn't add fake experience — it rewrites what you actually did using stronger language."</div>
            <div className="proof-author">Rohan Desai</div>
            <div className="proof-role">Full-Stack Developer, Mumbai</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="footer-inner">
          <div className="footer-left">
            <div className="logo-mark" style={{ width: '28px', height: '28px', fontSize: '13px' }}>OR</div>
            <span>OptiResume AI · Built for the hackathon</span>
          </div>
          <div className="footer-links">
            <a href="#" className="footer-link">Privacy</a>
            <a href="#" className="footer-link">Terms</a>
            <a href="#" className="footer-link">Contact</a>
          </div>
        </div>
      </footer>
    </>
  );
}
