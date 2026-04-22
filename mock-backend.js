/**
 * Temporary Mock Backend - Node.js Express
 * Allows frontend testing while Python backend is set up
 * Run: node mock-backend.js
 */

const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 8000;

// Middleware
app.use(express.json());
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175', 'http://localhost:5176', 'http://localhost:5177'],
  credentials: true
}));

// Simple in-memory user store for testing
const users = {};
let tokenCounter = 1;

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 200,
    message: 'Mock backend running',
    mode: 'mock (Node.js)',
    version: '0.0.1'
  });
});

// Register endpoint
app.post('/api/v1/auth/register', (req, res) => {
  const { email, password, full_name } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({
      detail: 'Email and password required'
    });
  }
  
  if (users[email]) {
    return res.status(400).json({
      detail: 'Email already registered'
    });
  }
  
  const user = {
    email,
    password,
    full_name: full_name || 'User',
    id: Object.keys(users).length + 1
  };
  
  users[email] = user;
  const token = `mock-token-${tokenCounter++}`;
  
  res.status(201).json({
    access_token: token,
    token_type: 'bearer',
    user: { email: user.email, full_name: user.full_name, id: user.id }
  });
});

// Login endpoint
app.post('/api/v1/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({
      detail: 'Email and password required'
    });
  }
  
  const user = users[email];
  
  if (!user || user.password !== password) {
    return res.status(401).json({
      detail: 'Invalid email or password'
    });
  }
  
  const token = `mock-token-${tokenCounter++}`;
  
  res.json({
    access_token: token,
    token_type: 'bearer',
    user: { email: user.email, full_name: user.full_name, id: user.id }
  });
});

// Verify token endpoint
app.post('/api/v1/auth/verify', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({
      detail: 'No token provided'
    });
  }
  
  // Mock token verification
  res.json({
    valid: true,
    user: { email: 'test@example.com', full_name: 'Test User', id: 1 }
  });
});

// Current user endpoint (required by AuthContext)
app.get('/api/v1/auth/me', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token || !token.startsWith('mock-token-')) {
    return res.status(401).json({
      detail: 'Invalid token'
    });
  }
  
  // Return mock user data
  res.json({
    email: 'test@example.com',
    full_name: 'Test User',
    id: 1
  });
});

// Upload endpoint
app.post('/api/v1/upload', (req, res) => {
  res.json({
    resume_text: 'Mock resume text extracted from PDF',
    char_count: 150,
    sections_detected: ['experience', 'skills', 'education']
  });
});

// Optimize endpoint
app.post('/api/v1/optimize', (req, res) => {
  res.json({
    optimized_resume: 'Mock optimized resume content',
    score: 75,
    improvements: ['Added quantified metrics', 'Improved action verbs'],
    pdf_url: '/mock-optimized.pdf'
  });
});

app.listen(PORT, () => {
  console.log(`\n✅ MOCK BACKEND RUNNING`);
  console.log(`📍 http://localhost:${PORT}`);
  console.log(`📚 API Docs simulation`);
  console.log(`\n⚠️  NOTE: This is a temporary Node.js mock backend`);
  console.log(`💡 To use the real backend, please install Python 3.8+\n`);
});
