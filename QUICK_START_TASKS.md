# 🎯 QUICK START - TASK PRIORITY LIST

## 🚀 START HERE: First 5 Tasks (Day 1)

### Priority 1: Backend Database Models (2 hours)
**File:** `backend/app/models/request_models.py`

```python
# Add these models:

class Question(BaseModel):
    id: str
    session_id: str
    question_text: str
    category: str  # "experience", "skills", "education", "projects"
    suggested_answer_length: int
    difficulty_level: str  # "easy", "medium", "hard"
    context: str  # Why this question is important
    order: int

class UserAnswer(BaseModel):
    id: str
    session_id: str
    question_id: str
    answer_text: str
    relevance_score: float  # 0-1, from SBERT/TF-IDF
    confidence: float
    timestamp: datetime
    section_type: str  # Which resume section this belongs to

class ChatSession(BaseModel):
    id: str
    user_id: str
    resume_text: str
    job_description: str
    questions: List[Question]
    answers: List[UserAnswer]
    status: str  # "active", "completed", "abandoned"
    created_at: datetime
    updated_at: datetime

class BulletPoint(BaseModel):
    text: str
    section: str
    confidence: float
    keywords_matched: List[str]
    original_answers: List[str]

class EnhancedResumeData(BaseModel):
    session_id: str
    original_resume: str
    enhanced_resume: str
    new_bullets: List[BulletPoint]
    total_keywords_added: int
    estimated_score_improvement: float
```

---

### Priority 2: Core Chatbot Service (3 hours)
**File:** `backend/app/services/chatbot_service.py` (NEW)

```python
from typing import List, Tuple
from sentence_transformers import util
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self, sbert_model=None):
        self.sbert_model = sbert_model
        self.vectorizer = TfidfVectorizer(max_features=500)
        
    def analyze_gaps(self, resume_text: str, job_description: str) -> dict:
        """
        Compare resume vs JD to find gaps.
        Returns: {
            'missing_keywords': [...],
            'missing_skills': [...],
            'gaps_by_category': {...}
        }
        """
        # Extract keywords from JD
        jd_keywords = self._extract_keywords(job_description)
        
        # Extract keywords from resume
        resume_keywords = self._extract_keywords(resume_text)
        
        # Find missing
        missing = set(jd_keywords) - set(resume_keywords)
        
        # Categorize by type
        gaps_by_category = self._categorize_gaps(missing, job_description)
        
        return {
            'missing_keywords': list(missing),
            'gaps_by_category': gaps_by_category,
            'total_gaps': len(missing)
        }
    
    def generate_questions(
        self, 
        resume_text: str, 
        job_description: str, 
        gaps: dict
    ) -> List[dict]:
        """
        Generate 10-12 targeted questions based on gaps.
        Uses SBERT for semantic understanding + TF-IDF for keyword matching.
        """
        questions = []
        
        # For each gap category, generate question
        for category, keywords in gaps['gaps_by_category'].items():
            for keyword in keywords[:3]:  # Top 3 per category
                question = self._generate_question(
                    keyword=keyword,
                    category=category,
                    job_description=job_description
                )
                questions.append(question)
        
        # Rank by importance (SBERT + TF-IDF combined score)
        questions = self._rank_questions(questions, job_description)
        
        # Return top 12
        return questions[:12]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple implementation - can be enhanced
        words = text.lower().split()
        # Filter by length and common words
        return [w for w in words if len(w) > 3]
    
    def _categorize_gaps(self, gaps: set, job_description: str) -> dict:
        """Categorize gaps into: skills, experience, education, projects."""
        return {
            'skills': list(gaps)[:5],
            'experience': list(gaps)[5:10],
            'education': list(gaps)[10:15],
            'projects': list(gaps)[15:]
        }
    
    def _generate_question(self, keyword: str, category: str, job_description: str) -> dict:
        """Generate natural language question for a keyword."""
        templates = {
            'skills': "Tell me about your experience with {keyword}. What projects or tasks have you used it for?",
            'experience': "Describe a project where you used {keyword}. What was the outcome?",
            'education': "Do you have any education or certification related to {keyword}?",
            'projects': "Have you worked on any projects involving {keyword}? Tell me about it."
        }
        
        template = templates.get(category, templates['skills'])
        question_text = template.format(keyword=keyword)
        
        return {
            'question_text': question_text,
            'keyword': keyword,
            'category': category,
            'difficulty': 'medium'
        }
    
    def _rank_questions(self, questions: List[dict], job_description: str) -> List[dict]:
        """Rank questions by importance using SBERT + TF-IDF."""
        for q in questions:
            if self.sbert_model:
                # SBERT similarity score (0-1)
                q_embedding = self.sbert_model.encode(q['question_text'])
                jd_embedding = self.sbert_model.encode(job_description)
                sbert_score = util.pytorch_cos_sim(q_embedding, jd_embedding)[0][0].item()
            else:
                sbert_score = 0.5
            
            # TF-IDF score
            try:
                tfidf_scores = self.vectorizer.fit_transform([q['question_text'], job_description])
                tfidf_score = (tfidf_scores[0] * tfidf_scores[1].T).toarray()[0][0]
            except:
                tfidf_score = 0.5
            
            # Combined score: 60% SBERT, 40% TF-IDF
            q['importance_score'] = (sbert_score * 0.6) + (tfidf_score * 0.4)
        
        # Sort by importance
        return sorted(questions, key=lambda x: x['importance_score'], reverse=True)
```

---

### Priority 3: Enhancement Service (3 hours)
**File:** `backend/app/services/enhancement_service.py` (NEW)

```python
import logging
from typing import List, Tuple
from ai_engine.rewriting.resume_rewriter import ResumeRewriter

logger = logging.getLogger(__name__)

class EnhancementService:
    def __init__(self, sbert_model=None):
        self.sbert_model = sbert_model
        self.rewriter = ResumeRewriter()
    
    def validate_answer(self, answer: str, job_description: str) -> Tuple[bool, float]:
        """
        Validate if answer is relevant to JD.
        Returns: (is_valid, relevance_score)
        """
        # Check minimum length
        if len(answer) < 50:
            return False, 0.3
        
        # Check semantic relevance
        if self.sbert_model:
            answer_embedding = self.sbert_model.encode(answer)
            jd_embedding = self.sbert_model.encode(job_description)
            relevance = (answer_embedding @ jd_embedding.T).item()
        else:
            relevance = 0.5
        
        return relevance > 0.4, relevance
    
    def aggregate_answers(
        self,
        answers: List[dict],
        resume_text: str,
        job_description: str
    ) -> dict:
        """
        Convert user answers into resume bullets.
        Returns: {
            'enhanced_resume': str,
            'new_bullets': List[BulletPoint],
            'summary': str
        }
        """
        # Group answers by resume section
        grouped = self._group_by_section(answers)
        
        # Generate bullets for each section
        new_bullets = []
        for section, group_answers in grouped.items():
            bullets = self._generate_bullets(group_answers, section, job_description)
            new_bullets.extend(bullets)
        
        # Insert bullets into resume
        enhanced_resume = self._insert_bullets(resume_text, new_bullets)
        
        return {
            'enhanced_resume': enhanced_resume,
            'new_bullets': new_bullets,
            'total_keywords_added': len(new_bullets)
        }
    
    def _group_by_section(self, answers: List[dict]) -> dict:
        """Group answers by resume section."""
        grouped = {
            'experience': [],
            'skills': [],
            'education': [],
            'projects': []
        }
        
        for answer in answers:
            section = answer.get('section', 'experience')
            grouped[section].append(answer)
        
        return grouped
    
    def _generate_bullets(
        self,
        answers: List[dict],
        section: str,
        job_description: str
    ) -> List[dict]:
        """Convert answers into professional resume bullets."""
        bullets = []
        
        for answer in answers:
            # Use LLM to convert answer to bullet
            prompt = f"""
            Convert this user answer into a professional resume bullet point.
            User Answer: {answer['text']}
            Resume Section: {section}
            Job Description Context: {job_description[:200]}
            
            Return ONLY the bullet point text, starting with a strong action verb.
            """
            
            bullet_text = self.rewriter._generate_with_groq(prompt)
            
            bullets.append({
                'text': bullet_text.strip(),
                'section': section,
                'confidence': answer.get('relevance_score', 0.8),
                'original_answer': answer['text']
            })
        
        return bullets
    
    def _insert_bullets(self, resume_text: str, new_bullets: List[dict]) -> str:
        """Insert new bullets into appropriate resume sections."""
        # Parse resume structure
        sections = self._parse_resume_sections(resume_text)
        
        # Add new bullets to appropriate sections
        for bullet in new_bullets:
            section = bullet['section']
            if section in sections:
                sections[section]['bullets'].append(bullet['text'])
        
        # Reconstruct resume
        enhanced = self._reconstruct_resume(sections)
        
        return enhanced
    
    def _parse_resume_sections(self, resume_text: str) -> dict:
        """Parse resume into sections."""
        # Simplified parser
        sections = {
            'experience': {'header': 'Experience', 'bullets': []},
            'skills': {'header': 'Skills', 'bullets': []},
            'education': {'header': 'Education', 'bullets': []},
            'projects': {'header': 'Projects', 'bullets': []}
        }
        
        # TODO: Implement proper parsing
        return sections
    
    def _reconstruct_resume(self, sections: dict) -> str:
        """Reconstruct resume from parsed sections."""
        # TODO: Implement reconstruction
        pass
```

---

### Priority 4: API Endpoints (3 hours)
**File:** `backend/app/routes/chatbot.py` (NEW)

```python
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.request_models import Question, UserAnswer, ChatSession
from app.services.chatbot_service import ChatbotService
from app.services.enhancement_service import EnhancementService
from app.routes.auth import get_current_user
from app.models.user import User as UserModel
import uuid
import logging

router = APIRouter(prefix="/chat", tags=["chatbot"])
logger = logging.getLogger(__name__)

@router.post("/start-session")
async def start_session(
    resume_text: str,
    job_description: str,
    request: Request,
    current_user: UserModel = Depends(get_current_user)
):
    """Start a new chat session and get initial questions."""
    try:
        session_id = str(uuid.uuid4())
        sbert_model = request.app.state.sbert_model
        
        # Initialize services
        chatbot_service = ChatbotService(sbert_model)
        
        # Analyze gaps
        gaps = chatbot_service.analyze_gaps(resume_text, job_description)
        logger.info(f"Found {gaps['total_gaps']} gaps")
        
        # Generate questions
        questions = chatbot_service.generate_questions(
            resume_text,
            job_description,
            gaps
        )
        logger.info(f"Generated {len(questions)} questions")
        
        # TODO: Store session in database
        
        return {
            'session_id': session_id,
            'total_questions': len(questions),
            'questions': questions[:3]  # Return first 3
        }
    
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-answer")
async def submit_answer(
    session_id: str,
    question_id: str,
    answer_text: str,
    job_description: str,
    request: Request,
    current_user: UserModel = Depends(get_current_user)
):
    """Submit an answer and get relevance score."""
    try:
        enhancement_service = EnhancementService(request.app.state.sbert_model)
        
        # Validate answer
        is_valid, relevance_score = enhancement_service.validate_answer(
            answer_text,
            job_description
        )
        
        # TODO: Store answer in database
        
        return {
            'is_valid': is_valid,
            'relevance_score': relevance_score,
            'feedback': 'Great answer!' if is_valid else 'Try to be more specific.'
        }
    
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aggregate-answers")
async def aggregate_answers(
    session_id: str,
    resume_text: str,
    job_description: str,
    answers: list,
    request: Request,
    current_user: UserModel = Depends(get_current_user)
):
    """Aggregate user answers into enhanced resume."""
    try:
        enhancement_service = EnhancementService(request.app.state.sbert_model)
        
        # Generate bullets from answers
        result = enhancement_service.aggregate_answers(
            answers,
            resume_text,
            job_description
        )
        
        logger.info(f"Generated {result['total_keywords_added']} new bullets")
        
        return result
    
    except Exception as e:
        logger.error(f"Error aggregating answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Priority 5: Frontend ChatbotPage (4 hours)
**File:** `frontend/src/pages/ChatbotPage.jsx` (NEW)

```jsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useOptimization } from '../context/OptimizationContext'
import Chatbot from '../components/Chatbot'
import ResumeBuilder from '../components/ResumeBuilder'
import { startChatSession, submitAnswer, aggregateAnswers } from '../services/chatbotApi'
import '../styles/chatbot.css'

export default function ChatbotPage() {
  const navigate = useNavigate()
  const { results } = useOptimization()
  
  const [sessionId, setSessionId] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState(0)

  // Get resume and JD from results
  const resumeText = results?.resume_text
  const jobDescription = results?.job_description

  useEffect(() => {
    if (!resumeText || !jobDescription) {
      navigate('/')
      return
    }

    // Start chat session
    const startChat = async () => {
      try {
        setLoading(true)
        const data = await startChatSession(resumeText, jobDescription)
        setSessionId(data.session_id)
        setQuestions(data.questions)
        setProgress(0)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    startChat()
  }, [resumeText, jobDescription])

  const handleAnswerSubmit = async (answer) => {
    try {
      const question = questions[currentIndex]
      
      // Submit answer
      const response = await submitAnswer(
        sessionId,
        question.id,
        answer,
        jobDescription
      )

      // Store answer
      setAnswers({
        ...answers,
        [currentIndex]: {
          question: question.question_text,
          answer,
          relevanceScore: response.relevance_score
        }
      })

      // Update progress
      const newProgress = ((currentIndex + 1) / questions.length) * 100
      setProgress(newProgress)

      // Move to next question or finish
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1)
      } else {
        handleFinishChat()
      }
    } catch (err) {
      setError(err.message)
    }
  }

  const handleFinishChat = async () => {
    try {
      setLoading(true)
      
      // Convert answers to API format
      const answersArray = Object.entries(answers).map(([idx, data]) => ({
        text: data.answer,
        section: 'experience' // TODO: Determine section
      }))

      // Aggregate answers
      const result = await aggregateAnswers(
        sessionId,
        resumeText,
        jobDescription,
        answersArray
      )

      // Store enhanced resume in context
      // TODO: Navigate to enhancement page or results
      navigate('/results', { state: { enhanced: result } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading chatbot...</div>
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  return (
    <div className="chatbot-page">
      <div className="chatbot-container">
        <div className="chatbot-left">
          <Chatbot
            questions={questions}
            currentIndex={currentIndex}
            progress={progress}
            onSubmit={handleAnswerSubmit}
            total={questions.length}
          />
        </div>

        <div className="chatbot-right">
          <ResumeBuilder
            resumeText={resumeText}
            answers={answers}
            currentQuestion={questions[currentIndex]}
          />
        </div>
      </div>
    </div>
  )
}
```

---

## 📋 NEXT 10 TASKS (Week 1)

After completing Priority 1-5:

6. **Chatbot Component** (Frontend) - UI for asking questions
7. **ResumeBuilder Component** (Frontend) - Show resume with live preview
8. **ChatContext** (Frontend State) - Manage chat state globally
9. **Chatbot CSS Styling** (Frontend) - Modern design for chatbot
10. **Update ModernHome** - Add navigation to chatbot after upload
11. **API Service Layer** (Frontend) - API calls to new endpoints
12. **Error Handling** (Both) - Graceful error fallbacks
13. **Session Management** (Backend) - Store/retrieve sessions
14. **Testing** - Unit tests for all new services
15. **Integration** - Connect all pieces together

---

## 🔗 FILE DEPENDENCIES

```
Backend:
models/request_models.py → services/chatbot_service.py → routes/chatbot.py
models/user.py ← services/chatbot_service.py
services/enhancement_service.py → routes/chatbot.py
services/rewriter_service.py → services/enhancement_service.py

Frontend:
pages/ChatbotPage.jsx → context/ChatContext.jsx
pages/ChatbotPage.jsx → components/Chatbot.jsx
pages/ChatbotPage.jsx → components/ResumeBuilder.jsx
components/Chatbot.jsx → services/chatbotApi.js
components/ResumeBuilder.jsx → services/chatbotApi.js
styles/chatbot.css ← all new components
```

---

## 🎯 END OF FIRST 5 TASKS

After completing these 5 tasks:
- ✅ Database ready to store sessions
- ✅ Backend can analyze gaps and generate questions
- ✅ Backend can validate answers and aggregate them
- ✅ API endpoints ready to receive requests
- ✅ Frontend page ready to display chat UI

**Estimated Time:** 12-14 hours
**Next:** Build frontend UI components
