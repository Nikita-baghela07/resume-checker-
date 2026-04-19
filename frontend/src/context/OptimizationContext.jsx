import React, { createContext, useContext, useState } from 'react';

const OptimizationContext = createContext();

export function OptimizationProvider({ children }) {
  const [optimizationData, setOptimizationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const setResults = (data) => {
    setOptimizationData(data);
    setError(null);
  };

  const clearResults = () => {
    setOptimizationData(null);
    setError(null);
  };

  const value = {
    optimizationData,
    setResults,
    clearResults,
    loading,
    setLoading,
    error,
    setError,
  };

  return (
    <OptimizationContext.Provider value={value}>
      {children}
    </OptimizationContext.Provider>
  );
}

export function useOptimization() {
  const context = useContext(OptimizationContext);
  if (!context) {
    throw new Error('useOptimization must be used within OptimizationProvider');
  }
  return context;
}
