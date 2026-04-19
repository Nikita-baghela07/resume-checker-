import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOptimization } from '../context/OptimizationContext.jsx';
import '../styles/modern.css';

export default function ModernLoadingPage() {
  const navigate = useNavigate();
  const { optimizationData } = useOptimization();
  const [progress, setProgress] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);

  const steps = [
    'Parsing resume structure',
    'Analyzing job description',
    'Computing semantic match',
    'Detecting skill gaps',
    'Rewriting bullets with AI',
    'Scoring optimized resume',
    'Generating results'
  ];

  useEffect(() => {
    // If results are already available, navigate immediately
    if (optimizationData) {
      setProgress(100);
      setCompletedSteps(Array.from({ length: steps.length }, (_, i) => i));
      setTimeout(() => navigate('/results'), 300);
      return;
    }

    const durations = [900, 1000, 1200, 800, 2000, 900, 700];
    let currentStep = 0;

    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 0.6, 94));
    }, 80);

    const stepInterval = setInterval(() => {
      if (currentStep > 0) {
        setCompletedSteps(prev => [...prev, currentStep - 1]);
      }

      if (currentStep < steps.length) {
        setActiveStep(currentStep);
        currentStep++;
      } else {
        clearInterval(stepInterval);
        clearInterval(progressInterval);
        setProgress(100);
        setCompletedSteps(prev => [...prev, steps.length - 1]);
        setTimeout(() => navigate('/results'), 500);
      }
    }, durations[currentStep] || 1000);

    return () => {
      clearInterval(progressInterval);
      clearInterval(stepInterval);
    };
  }, [navigate, steps.length, optimizationData]);

  return (
    <div className="loading-screen">
      <div className="loading-card fade-in">
        <div className="loading-spinner-wrap">
          <div className="loading-ring"></div>
          <div className="loading-ring2"></div>
        </div>
        <div className="loading-title">Optimizing your resume</div>
        <div className="loading-sub">AI is analyzing and rewriting for maximum ATS impact</div>
        <div className="loading-progress-track">
          <div className="loading-progress-bar" style={{ width: `${progress}%` }}></div>
        </div>
        <div className="loading-pct">{Math.floor(progress)}%</div>
        <div className="loading-steps">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`loading-step ${
                completedSteps.includes(index) ? 'done' : activeStep === index ? 'active' : ''
              }`}
            >
              <div className="step-icon">
                {completedSteps.includes(index) ? '✓' : index + 1}
              </div>
              {step}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
