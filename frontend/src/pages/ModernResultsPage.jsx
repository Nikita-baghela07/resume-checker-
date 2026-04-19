import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { downloadPDF } from '../services/api.js';
import { useOptimization } from '../context/OptimizationContext.jsx';
import '../styles/modern.css';

export default function ModernResultsPage() {
  const navigate = useNavigate();
  const { optimizationData } = useOptimization();
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedDiff, setExpandedDiff] = useState(0);
  const [diffFilter, setDiffFilter] = useState('all');
  const [downloading, setDownloading] = useState(false);

  if (!optimizationData) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'var(--bg)',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{ fontSize: '18px', color: 'var(--text2)' }}>No results found</div>
        <button 
          onClick={() => navigate('/')}
          style={{
            padding: '10px 20px',
            background: 'var(--accent)',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          ← Go back to home
        </button>
      </div>
    );
  }

  const {
    scores = { initial: {}, optimized: {} },
    skill_gaps = [],
    optimized_resume = '',
    diff = []
  } = optimizationData;

  const initialScore = Math.round(scores.initial?.overall || 0);
  const optimizedScore = Math.round(scores.optimized?.overall || 0);
  const improvement = optimizedScore - initialScore;
  const changedCount = diff.filter(d => d.changed).length;
  
  const filteredDiffs = diffFilter === 'all' 
    ? diff 
    : diffFilter === 'changed' 
      ? diff.filter(d => d.changed) 
      : diff.filter(d => !d.changed);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await downloadPDF(optimized_resume, 'Candidate');
    } catch (err) {
      alert('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const getDiffItem = (diffItem, index) => (
    <div key={index} className={`diff-item ${expandedDiff === index ? 'open' : ''}`}>
      <div className="diff-item-header" onClick={() => setExpandedDiff(expandedDiff === index ? -1 : index)}>
        <span className={`diff-status ${diffItem.changed ? 'changed' : 'unchanged'}`}></span>
        <span className="diff-item-text">{diffItem.original.length > 75 ? diffItem.original.slice(0, 75) + '…' : diffItem.original}</span>
        <span className={`diff-item-badge ${diffItem.changed ? 'improved' : 'unchanged'}`}>
          {diffItem.changed ? 'Improved' : 'Unchanged'}
        </span>
        <span className="diff-chevron">▼</span>
      </div>
      {expandedDiff === index && (
        <div className="diff-body">
          <div className="diff-cols">
            <div className="diff-col before">
              <div className="diff-col-label">Original</div>
              <div className="diff-col-text">{diffItem.original}</div>
            </div>
            <div className="diff-col after">
              <div className="diff-col-label">Optimized</div>
              <div className="diff-col-text">{diffItem.optimized}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Categorize skill gaps
  const highSkills = skill_gaps.filter(s => s.priority === 'high');
  const mediumSkills = skill_gaps.filter(s => s.priority === 'medium');
  const lowSkills = skill_gaps.filter(s => s.priority === 'low');

  return (
    <>
      <nav>
        <div className="nav-inner">
          <a href="/" className="logo">
            <div className="logo-mark">OR</div>
            <span className="logo-text">Opti<span style={{ color: 'var(--accent)' }}>Resume</span></span>
          </a>
        </div>
      </nav>

      {/* Results nav */}
      <div className="results-nav">
        <div className="results-nav-inner">
          <div className="results-tabs">
            <button className={`results-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
              Score Overview
            </button>
            <button className={`results-tab ${activeTab === 'improvements' ? 'active' : ''}`} onClick={() => setActiveTab('improvements')}>
              Improvements ({changedCount})
            </button>
            <button className={`results-tab ${activeTab === 'resume' ? 'active' : ''}`} onClick={() => setActiveTab('resume')}>
              Full Resume
            </button>
          </div>
          <div className="results-actions">
            <button className="btn-outline" onClick={() => navigate('/')}>← Optimize Another</button>
            <button 
              className="btn-accent" 
              onClick={handleDownload}
              disabled={downloading}
            >
              {downloading ? '⟳ Downloading...' : '⬇ Download Resume'}
            </button>
          </div>
        </div>
      </div>

      {/* Win banner */}
      <div className="win-banner">
        <div className="win-banner-inner">
          <div className="win-badge">🎯</div>
          <div className="win-text">
            <h3>ATS Score improved by +{improvement} points</h3>
            <p>{changedCount} bullets rewritten · {skill_gaps.length} skill gaps identified · {initialScore}% → {optimizedScore}% overall match</p>
          </div>
          <div className="win-meta">
            <div className="win-meta-item">
              <div className="win-meta-num green" style={{ color: 'var(--green)' }}>{optimizedScore}%</div>
              <div className="win-meta-label">Optimized score</div>
            </div>
            <div className="win-meta-item">
              <div className="win-meta-num">{changedCount}</div>
              <div className="win-meta-label">Bullets improved</div>
            </div>
            <div className="win-meta-item">
              <div className="win-meta-num">{skill_gaps.length}</div>
              <div className="win-meta-label">Skills missing</div>
            </div>
            <div className="win-meta-item">
              <div className="win-meta-num green" style={{ color: 'var(--green)' }}>ATS ✓</div>
              <div className="win-meta-label">Format status</div>
            </div>
          </div>
        </div>
      </div>

      {/* Results body */}
      <div className="results-body">
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="overview-grid">
            <div className="overview-left">
              {/* Score card */}
              <div className="score-card fade-in">
                <div className="score-card-header">
                  <div className="score-card-title">ATS Score Analysis</div>
                  <div className="score-card-badge">Semantic Match</div>
                </div>
                <div className="score-big-row">
                  <div className="score-big">
                    <div className="score-big-label">Before</div>
                    <div className="score-number before">{initialScore}%</div>
                  </div>
                  <div className="score-arrow-wrap">
                    <div className="score-arrow">→</div>
                    <div className="score-delta-pill">+{improvement}%</div>
                  </div>
                  <div className="score-big">
                    <div className="score-big-label">After</div>
                    <div className="score-number after" style={{ color: 'var(--green)' }}>{optimizedScore}%</div>
                  </div>
                </div>
                <div className="score-bars">
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">🎯 Skills match</span>
                      <span className="score-bar-vals">{Math.round(scores.initial?.skills_match || 0)}% → <strong style={{ color: 'var(--green)' }}>{Math.round(scores.optimized?.skills_match || 0)}%</strong></span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill green" style={{ width: `${scores.optimized?.skills_match || 0}%` }}></div>
                    </div>
                  </div>
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">💼 Experience match</span>
                      <span className="score-bar-vals">{Math.round(scores.initial?.experience_match || 0)}% → <strong style={{ color: 'var(--amber)' }}>{Math.round(scores.optimized?.experience_match || 0)}%</strong></span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill amber" style={{ width: `${scores.optimized?.experience_match || 0}%`, background: 'var(--amber)' }}></div>
                    </div>
                  </div>
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">🔑 Keyword coverage</span>
                      <span className="score-bar-vals">{Math.round(scores.initial?.keyword_coverage || 0)}% → <strong style={{ color: 'var(--accent)' }}>{Math.round(scores.optimized?.keyword_coverage || 0)}%</strong></span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill accent" style={{ width: `${scores.optimized?.keyword_coverage || 0}%`, background: 'var(--accent)' }}></div>
                    </div>
                  </div>
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">📄 Formatting</span>
                      <span className="score-bar-vals" style={{ color: 'var(--green)', fontWeight: '600' }}>ATS Safe ✓</span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill green" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Skill gaps */}
            <div className="fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="skill-gap-card">
                <div className="sg-header">
                  <div className="sg-title">Skill Gap Analysis</div>
                  <div className="sg-count">{skill_gaps.length} skills missing</div>
                </div>
                <div className="sg-summary">
                  <div className="sg-summary-box high" style={{ background: 'var(--redbg)', border: '1px solid #FECACA' }}>
                    <div className="sg-summary-num" style={{ color: 'var(--red)' }}>{highSkills.length}</div>
                    <div className="sg-summary-label">High priority</div>
                  </div>
                  <div className="sg-summary-box medium" style={{ background: 'var(--amberbg)', border: '1px solid #FDE68A' }}>
                    <div className="sg-summary-num" style={{ color: 'var(--amber)' }}>{mediumSkills.length}</div>
                    <div className="sg-summary-label">Medium</div>
                  </div>
                  <div className="sg-summary-box low" style={{ background: 'var(--greenbg)', border: '1px solid #BBF7D0' }}>
                    <div className="sg-summary-num" style={{ color: 'var(--green)' }}>{lowSkills.length}</div>
                    <div className="sg-summary-label">Low</div>
                  </div>
                </div>
                <div className="sg-tags">
                  {skill_gaps.map((gap, idx) => (
                    <div key={idx} className={`sg-tag ${gap.priority}`} style={{
                      background: gap.priority === 'high' ? 'var(--redbg)' : gap.priority === 'medium' ? 'var(--amberbg)' : 'var(--greenbg)',
                      color: gap.priority === 'high' ? 'var(--red)' : gap.priority === 'medium' ? 'var(--amber)' : 'var(--green)',
                      border: gap.priority === 'high' ? '1px solid #FECACA' : gap.priority === 'medium' ? '1px solid #FDE68A' : '1px solid #BBF7D0'
                    }}>
                      <span className="sg-tag-dot" style={{
                        background: gap.priority === 'high' ? 'var(--red)' : gap.priority === 'medium' ? 'var(--amber)' : 'var(--green)'
                      }}></span>
                      {gap.skill}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* IMPROVEMENTS TAB */}
        {activeTab === 'improvements' && (
          <div className="diff-card fade-in">
            <div className="diff-card-header">
              <div className="diff-card-title">Resume Improvements</div>
              <div className="diff-filters">
                <button className={`diff-filter ${diffFilter === 'all' ? 'active' : ''}`} onClick={() => setDiffFilter('all')} style={{
                  background: diffFilter === 'all' ? 'var(--text)' : 'transparent',
                  color: diffFilter === 'all' ? '#fff' : 'var(--text2)',
                  borderColor: diffFilter === 'all' ? 'var(--text)' : 'var(--border)'
                }}>All ({diff.length})</button>
                <button className={`diff-filter ${diffFilter === 'changed' ? 'active' : ''}`} onClick={() => setDiffFilter('changed')} style={{
                  background: diffFilter === 'changed' ? 'var(--text)' : 'transparent',
                  color: diffFilter === 'changed' ? '#fff' : 'var(--text2)',
                  borderColor: diffFilter === 'changed' ? 'var(--text)' : 'var(--border)'
                }}>Improved ({changedCount})</button>
                <button className={`diff-filter ${diffFilter === 'unchanged' ? 'active' : ''}`} onClick={() => setDiffFilter('unchanged')} style={{
                  background: diffFilter === 'unchanged' ? 'var(--text)' : 'transparent',
                  color: diffFilter === 'unchanged' ? '#fff' : 'var(--text2)',
                  borderColor: diffFilter === 'unchanged' ? 'var(--text)' : 'var(--border)'
                }}>Unchanged ({diff.length - changedCount})</button>
              </div>
            </div>
            <div className="diff-list">
              {filteredDiffs.length > 0 ? (
                filteredDiffs.map((diffItem, idx) => getDiffItem(diffItem, idx))
              ) : (
                <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text2)' }}>
                  No items to show
                </div>
              )}
            </div>
          </div>
        )}

        {/* RESUME TAB */}
        {activeTab === 'resume' && (
          <div className="resume-compare fade-in">
            <div className="resume-panel">
              <div className="resume-panel-header">
                <div className="resume-panel-title">Original Resume</div>
                <span className="resume-panel-badge" style={{ background: 'var(--redbg)', color: 'var(--red)' }}>{initialScore}% ATS score</span>
              </div>
              <div className="resume-panel-body mono" style={{ fontFamily: "'DM Mono', monospace", fontSize: '12px', color: 'var(--text2)', whiteSpace: 'pre-wrap', overflow: 'auto', maxHeight: '500px' }}>
                {/* Show original from diffs or reconstructed */}
                {diff.map(d => d.original).join('\n\n')}
              </div>
            </div>
            <div className="resume-panel optimized">
              <div className="resume-panel-header">
                <div className="resume-panel-title">Optimized Resume</div>
                <span className="resume-panel-badge" style={{ background: 'var(--greenbg)', color: 'var(--green)' }}>{optimizedScore}% ATS score</span>
              </div>
              <div className="resume-panel-body mono" style={{ fontFamily: "'DM Mono', monospace", fontSize: '12px', color: 'var(--text2)', whiteSpace: 'pre-wrap', overflow: 'auto', maxHeight: '500px' }}>
                {optimized_resume}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default function ModernResultsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedDiff, setExpandedDiff] = useState(0);
  const [diffFilter, setDiffFilter] = useState('all');

  const sampleDiffs = [
    { original: "Worked on the backend of a web application", optimized: "Engineered RESTful backend services using Python and FastAPI, handling 50K+ daily API requests", changed: true },
    { original: "Did some coding in Python", optimized: "Developed and maintained SQL queries against PostgreSQL database, improving query performance by 25%", changed: true },
    { original: "Helped fix bugs in the existing codebase", optimized: "Resolved critical bugs in production codebase, reducing incident response time by 40%", changed: true },
    { original: "Worked with the database team", optimized: "Collaborated with cross-functional teams to deliver features in 2-week Agile sprints", changed: true },
    { original: "Did testing for some features", optimized: "Conducted integration testing and documented API endpoints using Swagger", changed: true },
    { original: "Built some features for the company website", optimized: "Built and deployed RESTful API endpoints using Python and FastAPI, serving 10K+ daily users", changed: true },
    { original: "Made a small API", optimized: "Developed a lightweight REST API for internal tooling, reducing manual workflows by 60%", changed: true },
    { original: "Wrote code using Python and JavaScript", optimized: "Implemented backend logic using Python and JavaScript with Git version control best practices", changed: true },
    { original: "Worked on database stuff", optimized: "Optimized PostgreSQL database queries, improving page load times by 35%", changed: true },
    { original: "I am a software developer with some experience in coding", optimized: "I am a software developer with some experience in coding", changed: false },
    { original: "Languages: Python, JavaScript, Java", optimized: "Languages: Python, JavaScript, Java", changed: false },
  ];

  const skillGaps = [
    { skill: 'Docker', priority: 'high' },
    { skill: 'CI/CD', priority: 'high' },
    { skill: 'GitHub Actions', priority: 'high' },
    { skill: 'Kubernetes', priority: 'medium' },
    { skill: 'Redis', priority: 'medium' },
    { skill: 'AWS', priority: 'low' },
  ];

  const filteredDiffs = diffFilter === 'all' ? sampleDiffs : diffFilter === 'changed' ? sampleDiffs.filter(d => d.changed) : sampleDiffs.filter(d => !d.changed);

  const getDiffItem = (diff, index) => (
    <div key={index} className={`diff-item ${expandedDiff === index ? 'open' : ''}`}>
      <div className="diff-item-header" onClick={() => setExpandedDiff(expandedDiff === index ? -1 : index)}>
        <span className={`diff-status ${diff.changed ? 'changed' : 'unchanged'}`}></span>
        <span className="diff-item-text">{diff.original.length > 75 ? diff.original.slice(0, 75) + '…' : diff.original}</span>
        <span className={`diff-item-badge ${diff.changed ? 'improved' : 'unchanged'}`}>
          {diff.changed ? 'Improved' : 'Unchanged'}
        </span>
        <span className="diff-chevron">▼</span>
      </div>
      {expandedDiff === index && (
        <div className="diff-body">
          <div className="diff-cols">
            <div className="diff-col before">
              <div className="diff-col-label">Original</div>
              <div className="diff-col-text">{diff.original}</div>
            </div>
            <div className="diff-col after">
              <div className="diff-col-label">Optimized</div>
              <div className="diff-col-text">{diff.optimized}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      <nav>
        <div className="nav-inner">
          <a href="/" className="logo">
            <div className="logo-mark">OR</div>
            <span className="logo-text">Opti<span style={{ color: 'var(--accent)' }}>Resume</span></span>
          </a>
        </div>
      </nav>

      {/* Results nav */}
      <div className="results-nav">
        <div className="results-nav-inner">
          <div className="results-tabs">
            <button className={`results-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
              Score Overview
            </button>
            <button className={`results-tab ${activeTab === 'improvements' ? 'active' : ''}`} onClick={() => setActiveTab('improvements')}>
              Improvements (11)
            </button>
            <button className={`results-tab ${activeTab === 'resume' ? 'active' : ''}`} onClick={() => setActiveTab('resume')}>
              Full Resume
            </button>
          </div>
          <div className="results-actions">
            <button className="btn-outline" onClick={() => navigate('/')}>← Optimize Another</button>
            <button className="btn-accent" onClick={() => alert('Downloading optimized resume PDF...')}>
              ⬇ Download Resume
            </button>
          </div>
        </div>
      </div>

      {/* Win banner */}
      <div className="win-banner">
        <div className="win-banner-inner">
          <div className="win-badge">🎯</div>
          <div className="win-text">
            <h3>ATS Score improved by +36 points</h3>
            <p>11 bullets rewritten · 3 high-priority skill gaps identified · 42% → 78% overall match</p>
          </div>
          <div className="win-meta">
            <div className="win-meta-item">
              <div className="win-meta-num green" style={{ color: 'var(--green)' }}>78%</div>
              <div className="win-meta-label">Optimized score</div>
            </div>
            <div className="win-meta-item">
              <div className="win-meta-num">11</div>
              <div className="win-meta-label">Bullets rewritten</div>
            </div>
            <div className="win-meta-item">
              <div className="win-meta-num">3</div>
              <div className="win-meta-label">Skills missing</div>
            </div>
            <div className="win-meta-item">
              <div className="win-meta-num green" style={{ color: 'var(--green)' }}>ATS ✓</div>
              <div className="win-meta-label">Format status</div>
            </div>
          </div>
        </div>
      </div>

      {/* Results body */}
      <div className="results-body">
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="overview-grid">
            <div className="overview-left">
              {/* Score card */}
              <div className="score-card fade-in">
                <div className="score-card-header">
                  <div className="score-card-title">ATS Score Analysis</div>
                  <div className="score-card-badge">Semantic Match</div>
                </div>
                <div className="score-big-row">
                  <div className="score-big">
                    <div className="score-big-label">Before</div>
                    <div className="score-number before">42%</div>
                  </div>
                  <div className="score-arrow-wrap">
                    <div className="score-arrow">→</div>
                    <div className="score-delta-pill">+36%</div>
                  </div>
                  <div className="score-big">
                    <div className="score-big-label">After</div>
                    <div className="score-number after" style={{ color: 'var(--green)' }}>78%</div>
                  </div>
                </div>
                <div className="score-bars">
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">🎯 Skills match</span>
                      <span className="score-bar-vals">38% → <strong style={{ color: 'var(--green)' }}>88%</strong></span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill green" style={{ width: '88%' }}></div>
                    </div>
                  </div>
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">💼 Experience match</span>
                      <span className="score-bar-vals">45% → <strong style={{ color: 'var(--amber)' }}>74%</strong></span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill amber" style={{ width: '74%', background: 'var(--amber)' }}></div>
                    </div>
                  </div>
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">🔑 Keyword coverage</span>
                      <span className="score-bar-vals">44% → <strong style={{ color: 'var(--accent)' }}>80%</strong></span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill accent" style={{ width: '80%', background: 'var(--accent)' }}></div>
                    </div>
                  </div>
                  <div className="score-bar-row">
                    <div className="score-bar-meta">
                      <span className="score-bar-name">📄 Formatting</span>
                      <span className="score-bar-vals" style={{ color: 'var(--green)', fontWeight: '600' }}>ATS Safe ✓</span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill green" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Skill gaps */}
            <div className="fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="skill-gap-card">
                <div className="sg-header">
                  <div className="sg-title">Skill Gap Analysis</div>
                  <div className="sg-count">6 skills missing</div>
                </div>
                <div className="sg-summary">
                  <div className="sg-summary-box high" style={{ background: 'var(--redbg)', border: '1px solid #FECACA' }}>
                    <div className="sg-summary-num" style={{ color: 'var(--red)' }}>3</div>
                    <div className="sg-summary-label">High priority</div>
                  </div>
                  <div className="sg-summary-box medium" style={{ background: 'var(--amberbg)', border: '1px solid #FDE68A' }}>
                    <div className="sg-summary-num" style={{ color: 'var(--amber)' }}>2</div>
                    <div className="sg-summary-label">Medium</div>
                  </div>
                  <div className="sg-summary-box low" style={{ background: 'var(--greenbg)', border: '1px solid #BBF7D0' }}>
                    <div className="sg-summary-num" style={{ color: 'var(--green)' }}>1</div>
                    <div className="sg-summary-label">Low</div>
                  </div>
                </div>
                <div className="sg-tags">
                  {skillGaps.map((gap, idx) => (
                    <div key={idx} className={`sg-tag ${gap.priority}`} style={{
                      background: gap.priority === 'high' ? 'var(--redbg)' : gap.priority === 'medium' ? 'var(--amberbg)' : 'var(--greenbg)',
                      color: gap.priority === 'high' ? 'var(--red)' : gap.priority === 'medium' ? 'var(--amber)' : 'var(--green)',
                      border: gap.priority === 'high' ? '1px solid #FECACA' : gap.priority === 'medium' ? '1px solid #FDE68A' : '1px solid #BBF7D0'
                    }}>
                      <span className="sg-tag-dot" style={{
                        background: gap.priority === 'high' ? 'var(--red)' : gap.priority === 'medium' ? 'var(--amber)' : 'var(--green)'
                      }}></span>
                      {gap.skill}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* IMPROVEMENTS TAB */}
        {activeTab === 'improvements' && (
          <div className="diff-card fade-in">
            <div className="diff-card-header">
              <div className="diff-card-title">Resume Improvements</div>
              <div className="diff-filters">
                <button className={`diff-filter ${diffFilter === 'all' ? 'active' : ''}`} onClick={() => setDiffFilter('all')} style={{
                  background: diffFilter === 'all' ? 'var(--text)' : 'transparent',
                  color: diffFilter === 'all' ? '#fff' : 'var(--text2)',
                  borderColor: diffFilter === 'all' ? 'var(--text)' : 'var(--border)'
                }}>All (11)</button>
                <button className={`diff-filter ${diffFilter === 'changed' ? 'active' : ''}`} onClick={() => setDiffFilter('changed')} style={{
                  background: diffFilter === 'changed' ? 'var(--text)' : 'transparent',
                  color: diffFilter === 'changed' ? '#fff' : 'var(--text2)',
                  borderColor: diffFilter === 'changed' ? 'var(--text)' : 'var(--border)'
                }}>Improved (9)</button>
                <button className={`diff-filter ${diffFilter === 'unchanged' ? 'active' : ''}`} onClick={() => setDiffFilter('unchanged')} style={{
                  background: diffFilter === 'unchanged' ? 'var(--text)' : 'transparent',
                  color: diffFilter === 'unchanged' ? '#fff' : 'var(--text2)',
                  borderColor: diffFilter === 'unchanged' ? 'var(--text)' : 'var(--border)'
                }}>Unchanged (2)</button>
              </div>
            </div>
            <div className="diff-list">
              {filteredDiffs.map((diff, idx) => getDiffItem(diff, idx))}
            </div>
          </div>
        )}

        {/* RESUME TAB */}
        {activeTab === 'resume' && (
          <div className="resume-compare fade-in">
            <div className="resume-panel">
              <div className="resume-panel-header">
                <div className="resume-panel-title">Original Resume</div>
                <span className="resume-panel-badge" style={{ background: 'var(--redbg)', color: 'var(--red)' }}>42% ATS score</span>
              </div>
              <div className="resume-panel-body mono" style={{ fontFamily: "'DM Mono', monospace", fontSize: '12px', color: 'var(--text2)' }}>
                JOHN DOE
                johndoe@email.com | +91 9876543210

                EXPERIENCE
                Software Developer Intern - XYZ Tech Pvt. Ltd.
                - Worked on the backend of a web application
                - Did some coding in Python
                - Worked with the database team
              </div>
            </div>
            <div className="resume-panel optimized">
              <div className="resume-panel-header">
                <div className="resume-panel-title">Optimized Resume</div>
                <span className="resume-panel-badge" style={{ background: 'var(--greenbg)', color: 'var(--green)' }}>78% ATS score</span>
              </div>
              <div className="resume-panel-body mono" style={{ fontFamily: "'DM Mono', monospace", fontSize: '12px', color: 'var(--text2)' }}>
                JOHN DOE
                johndoe@email.com | +91 9876543210

                EXPERIENCE
                Software Developer Intern - XYZ Tech Pvt. Ltd.
                - Engineered RESTful backend services using Python and FastAPI, handling 50K+ daily API requests
                - Developed and maintained SQL queries against PostgreSQL database
                - Collaborated with cross-functional teams to deliver features
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
