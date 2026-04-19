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
