# 🏗️ CHATBOT ARCHITECTURE & DATA FLOW DIAGRAMS

## 📊 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OPTIRESUME AI - CHATBOT SYSTEM                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React + Vite)                             │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ ModernHome   │  │ ChatbotPage  │  │ Enhancement  │  │ Results Page │    │
│  │ (Upload)     │→ │ (Questions)  │→ │ (Bullets)    │→ │ (Download)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│        │                    │                 │                │              │
│        │                    ├─ Chatbot.jsx    ├─ Review.jsx    │             │
│        │                    ├─ Resume.jsx     ├─ Editor.jsx    │             │
│        │                    └─ Progress.jsx   └─ Preview.jsx   │             │
│        │                                                                     │
│        └────────────────────────────────────────────────────────────────────→ API
│
│  ┌─────────────────────────────────────────────────────────┐                │
│  │              CONTEXT & STATE MANAGEMENT                 │                │
│  │  ┌──────────────────┐  ┌──────────────────┐             │                │
│  │  │ OptimizationCtx  │  │ ChatContext (NEW)│             │                │
│  │  │                  │  │                  │             │                │
│  │  │ • resumeText     │  │ • sessionId      │             │                │
│  │  │ • jobDesc        │  │ • questions[]    │             │                │
│  │  │ • results        │  │ • answers{}      │             │                │
│  │  │ • loading        │  │ • progress       │             │                │
│  │  └──────────────────┘  └──────────────────┘             │                │
│  └─────────────────────────────────────────────────────────┘                │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │                    STYLES                               │                │
│  │  • styles/modern.css (existing)                         │                │
│  │  • styles/chatbot.css (new)                             │                │
│  └─────────────────────────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI + PostgreSQL)                          │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      ROUTES (chatbot.py)                             │    │
│  │                                                                      │    │
│  │  POST /chat/start-session          → Start new chat                │    │
│  │  POST /chat/submit-answer          → Process single answer         │    │
│  │  GET  /chat/questions/:session_id  → Get next questions            │    │
│  │  POST /chat/aggregate-answers      → Convert answers to bullets    │    │
│  │  POST /optimize/final              → Final optimization            │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                  SERVICES LAYER (services/)                          │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │    │
│  │  │ ChatbotService   │  │ EnhancementSvc   │  │ SemanticMatcher  │ │    │
│  │  │                  │  │                  │  │                  │ │    │
│  │  │ • analyze_gaps() │  │ • validate()     │  │ • extract_kw()   │ │    │
│  │  │ • gen_questions()│  │ • aggregate()    │  │ • match()        │ │    │
│  │  │ • rank_questions│  │ • gen_bullets()  │  │ • score()        │ │    │
│  │  │ • format_q()    │  │ • insert_bullets()│ │ • suggest()      │ │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐                       │    │
│  │  │ SectionEnhancer  │  │ RewriterService  │  (existing)           │    │
│  │  │                  │  │                  │                        │    │
│  │  │ • enhance_exp()  │  │ • rewrite()      │                        │    │
│  │  │ • enhance_skills │  │ • diff()         │                        │    │
│  │  │ • enhance_proj() │  │ • with_groq()    │                        │    │
│  │  │ • format()       │  │                  │                        │    │
│  │  └──────────────────┘  └──────────────────┘                       │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                   ML/AI MODELS                                       │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │    │
│  │  │   SBERT Model    │  │  TF-IDF Vector   │  │  Groq LLM API   │ │    │
│  │  │ (all-MiniLM)     │  │                  │  │ (llama-3.1-8b)  │ │    │
│  │  │                  │  │ • Keyword extract│  │                  │ │    │
│  │  │ • Embed text     │  │ • Similarity     │  │ • Generate Q's   │ │    │
│  │  │ • Semantic sim   │  │ • Ranking        │  │ • Rewrite bullets│ │    │
│  │  │ • Cosine dist    │  │ • Filtering      │  │ • LLM reasoning  │ │    │
│  │  │                  │  │                  │  │                  │ │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │               DATABASE MODELS (SQLAlchemy)                           │    │
│  │                                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    │
│  │  │ ChatSession  │  │ Question     │  │ UserAnswer   │             │    │
│  │  │              │  │              │  │              │             │    │
│  │  │ • id         │  │ • id         │  │ • id         │             │    │
│  │  │ • user_id   │  │ • session_id │  │ • question_id│             │    │
│  │  │ • resume    │  │ • text       │  │ • answer_text│             │    │
│  │  │ • jd        │  │ • category   │  │ • score      │             │    │
│  │  │ • status    │  │ • order      │  │ • timestamp  │             │    │
│  │  │ • created   │  │ • difficulty │  │ • section    │             │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │    │
│  │                                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐                               │    │
│  │  │ BulletPoint  │  │ EnhancedRsm  │                               │    │
│  │  │              │  │              │                               │    │
│  │  │ • text       │  │ • session_id │                               │    │
│  │  │ • section    │  │ • original   │                               │    │
│  │  │ • confidence │  │ • enhanced   │                               │    │
│  │  │ • keywords   │  │ • bullets[]  │                               │    │
│  │  └──────────────┘  └──────────────┘                               │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   ↓                                          │
│            ┌──────────────────────────────────────────────┐                 │
│            │        PostgreSQL Database                   │                 │
│            │  (on Render.com)                             │                 │
│            └──────────────────────────────────────────────┘                 │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                         │
│                                                                               │
│  • Groq API → LLM for question/bullet generation                            │
│  • Vercel → Frontend hosting                                                 │
│  • Render → Backend hosting                                                  │
│  • PostgreSQL → Database                                                     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW DIAGRAM

### Phase 1: Upload & Gap Analysis

```
User Upload
    ↓
Resume PDF + Job Description
    ↓
[Frontend: ModernHome]
    ↓
POST /upload
    ↓
[Backend: Parser Service]
    ├─ Extract resume text
    ├─ Extract resume structure
    ├─ Parse JD keywords
    └─ Store in OptimizationContext
    ↓
Store in database
    ↓
Navigate to /chat
```

### Phase 2: Question Generation

```
Resume + JD Ready
    ↓
[Frontend: ChatbotPage.jsx loaded]
    ↓
POST /chat/start-session
    ↓
[Backend: ChatbotService]
    ├─ analyze_gaps()
    │  ├─ Extract resume keywords
    │  ├─ Extract JD keywords
    │  ├─ Find missing keywords
    │  └─ Categorize gaps by type
    │
    ├─ generate_questions()
    │  ├─ For each gap:
    │  │  ├─ Create natural question template
    │  │  ├─ SBERT encode question
    │  │  ├─ TF-IDF score question
    │  │  └─ Combine scores (60% SBERT + 40% TF-IDF)
    │  │
    │  └─ Rank questions by importance
    │
    └─ Return top 12 questions
    ↓
Store in ChatSession (database)
    ↓
Return: session_id + first 3 questions
    ↓
[Frontend: Display questions in Chatbot]
```

### Phase 3: Answer Collection & Validation

```
User Types Answer
    ↓
POST /chat/submit-answer
    ↓
[Backend: EnhancementService]
    ├─ validate_answer()
    │  ├─ Check length > 50 chars
    │  ├─ SBERT encode answer
    │  ├─ SBERT encode JD
    │  ├─ Calculate cosine similarity
    │  └─ Calculate relevance score (0-1)
    │
    ├─ Score must be > 0.4 to accept
    │
    └─ Return relevance_score + feedback
    ↓
[Frontend: Show feedback]
    ├─ If valid: "Great answer! ✓"
    ├─ If weak: "Try to be more specific"
    └─ If bad: "This doesn't match the job"
    ↓
Store answer in database
    ↓
Move to next question or finish
```

### Phase 4: Answer Aggregation

```
All Questions Answered
    ↓
POST /chat/aggregate-answers
    ↓
[Backend: EnhancementService]
    ├─ aggregate_answers()
    │  ├─ Group answers by resume section
    │  │  ├─ Experience
    │  │  ├─ Skills
    │  │  ├─ Education
    │  │  └─ Projects
    │  │
    │  ├─ For each group:
    │  │  ├─ Combine similar answers
    │  │  ├─ Generate resume bullets
    │  │  ├─ Check keyword match
    │  │  └─ Score confidence
    │  │
    │  └─ Return new_bullets[]
    │
    ├─ For each bullet: call Groq API
    │  ├─ Prompt: "Convert answer to resume bullet"
    │  ├─ Input: user answer
    │  ├─ Output: Professional bullet point
    │  └─ Include action verb + metrics
    │
    ├─ Validate bullets
    │  ├─ Check keywords from JD
    │  ├─ Check formatting
    │  └─ Ensure ATS-friendly
    │
    └─ Return enhanced_resume + new_bullets[]
    ↓
Store enhanced resume in database
    ↓
[Frontend: EnhancementPage]
    ├─ Display new bullets
    ├─ Show before/after comparison
    ├─ Allow edit/delete bullets
    └─ Option to proceed or re-answer
```

### Phase 5: Final Optimization

```
User Approves Bullets
    ↓
POST /optimize/final
    ↓
Input: enhanced_resume + job_description
    ↓
[Backend: Optimize Pipeline]
    ├─ Scoring Service
    │  ├─ Score enhanced resume
    │  ├─ Compare to JD
    │  └─ Calculate improvement
    │
    ├─ Skill Gap Service
    │  ├─ Detect remaining gaps
    │  └─ Show unfilled keywords
    │
    ├─ Rewriter Service
    │  ├─ Further optimize bullets
    │  ├─ Add metrics/numbers
    │  └─ Check formatting
    │
    ├─ Generate Diffs
    │  ├─ Compare original vs enhanced
    │  └─ Show all changes
    │
    └─ Return OptimizeResponse
       ├─ initial_score
       ├─ optimized_score
       ├─ improvement %
       ├─ new_bullets[]
       ├─ optimized_resume
       └─ diff[]
    ↓
[Frontend: ResultsPage]
    ├─ Show scores
    ├─ Show improvements
    ├─ Tab: Overview
    ├─ Tab: Improvements
    ├─ Tab: Resume Preview
    ├─ Download PDF
    └─ Share results
```

---

## 🎯 SBERT + TF-IDF SYNC ALGORITHM

```
┌────────────────────────────────────────────────────────────┐
│         HYBRID SIMILARITY SCORING (SBERT + TF-IDF)        │
└────────────────────────────────────────────────────────────┘

INPUT: Question, Job Description, User Answer

STEP 1: ENCODE WITH SBERT
├─ question_embedding = sbert_model.encode(question)
├─ jd_embedding = sbert_model.encode(job_description)
├─ answer_embedding = sbert_model.encode(user_answer)
│
└─ Calculate cosine similarities:
   ├─ sbert_q_jd = cosine_similarity(question_embedding, jd_embedding)
   ├─ sbert_a_jd = cosine_similarity(answer_embedding, jd_embedding)
   └─ sbert_score = max(sbert_q_jd, sbert_a_jd)  // [0.0, 1.0]

STEP 2: CALCULATE WITH TF-IDF
├─ Vectorize question + JD + answer
├─ tfidf_matrix = vectorizer.fit_transform([question, jd, answer])
│
└─ Calculate dot products:
   ├─ tfidf_q_jd = tfidf_matrix[0] · tfidf_matrix[1]
   ├─ tfidf_a_jd = tfidf_matrix[2] · tfidf_matrix[1]
   └─ tfidf_score = max(tfidf_q_jd, tfidf_a_jd)  // [0.0, 1.0]

STEP 3: COMBINE SCORES
├─ final_score = (sbert_score × 0.6) + (tfidf_score × 0.4)
│  └─ 60% weight on semantic meaning (SBERT)
│  └─ 40% weight on keyword matching (TF-IDF)
│
└─ RESULT: Combined score [0.0, 1.0]

STEP 4: INTERPRET RESULT
├─ score > 0.7: EXCELLENT - Use answer as-is
├─ score 0.5-0.7: GOOD - Accept with minor edits
├─ score 0.4-0.5: OK - Ask for clarification
└─ score < 0.4: POOR - Reject and ask again

PERFORMANCE:
├─ With SBERT: ~200ms per question
├─ With TF-IDF only: ~50ms per question
└─ Fallback if SBERT unavailable: TF-IDF only mode
```

---

## 📱 FRONTEND COMPONENT HIERARCHY

```
App
├── Router
│   ├── / (ModernHome)
│   │   └── Upload Resume + JD
│   │       └── Navigate to /chat
│   │
│   ├── /chat (ChatbotPage) ← NEW
│   │   ├── Left: Chatbot.jsx
│   │   │   ├── QuestionCard.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── InputField.jsx
│   │   │   └── ActionButtons.jsx
│   │   │
│   │   └── Right: ResumeBuilder.jsx
│   │       ├── SectionSelector.jsx
│   │       ├── PreviewPane.jsx
│   │       ├── BulletPoint.jsx
│   │       └── KeywordHighlight.jsx
│   │
│   ├── /enhance (EnhancementPage) ← NEW
│   │   ├── BulletReview.jsx
│   │   ├── BulletEditor.jsx
│   │   ├── SectionSummary.jsx
│   │   ├── ComparisonView.jsx
│   │   ├── AtsScorePreview.jsx
│   │   └── ActionButtons.jsx
│   │
│   ├── /loading (ModernLoadingPage)
│   │   └── 7-step progress animation
│   │
│   └── /results (ModernResultsPage)
│       ├── ScoreCard.jsx
│       ├── ImprovementTab.jsx
│       ├── ResumePreview.jsx
│       ├── DownloadButton.jsx
│       └── ShareButton.jsx
│
├── Context Providers
│   ├── AuthProvider
│   ├── OptimizationProvider
│   └── ChatProvider ← NEW
│
└── Global Styles
    ├── modern.css
    └── chatbot.css ← NEW
```

---

## 🗄️ DATABASE SCHEMA CHANGES

```sql
-- NEW TABLE: chat_sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    resume_text TEXT,
    job_description TEXT,
    status VARCHAR(20),  -- "active", "completed", "abandoned"
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- NEW TABLE: questions
CREATE TABLE questions (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    question_text TEXT,
    category VARCHAR(50),  -- "experience", "skills", "education", "projects"
    difficulty_level VARCHAR(20),  -- "easy", "medium", "hard"
    importance_score FLOAT,  -- 0-1
    suggested_answer_length INT,
    context TEXT,
    question_order INT,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- NEW TABLE: user_answers
CREATE TABLE user_answers (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    question_id UUID NOT NULL,
    answer_text TEXT,
    relevance_score FLOAT,  -- 0-1
    confidence FLOAT,  -- 0-1
    section_type VARCHAR(50),
    submitted_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- NEW TABLE: bullet_points
CREATE TABLE bullet_points (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    section_type VARCHAR(50),  -- "experience", "skills", etc.
    bullet_text TEXT,
    confidence FLOAT,  -- 0-1
    keywords_matched TEXT[],  -- Array of matched keywords
    original_answers TEXT[],  -- Array of user answers
    is_included BOOLEAN DEFAULT TRUE,  -- User can exclude
    order_position INT,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- NEW TABLE: enhanced_resumes
CREATE TABLE enhanced_resumes (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    original_resume TEXT,
    enhanced_resume TEXT,
    total_keywords_added INT,
    estimated_improvement FLOAT,  -- 0-100%
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- ALTER: users table (if needed)
ALTER TABLE users ADD COLUMN IF NOT EXISTS 
    chatbot_preference JSON;  -- Store user settings
```

---

## 🔌 API REQUEST/RESPONSE EXAMPLES

### 1. Start Session
```
POST /chat/start-session
{
  "resume_text": "...",
  "job_description": "..."
}

Response:
{
  "session_id": "uuid-123",
  "total_questions": 12,
  "questions": [
    {
      "id": "q-1",
      "question_text": "Tell me about your experience with Python",
      "category": "skills",
      "difficulty_level": "medium",
      "context": "Python is critical for this role"
    },
    ...
  ]
}
```

### 2. Submit Answer
```
POST /chat/submit-answer
{
  "session_id": "uuid-123",
  "question_id": "q-1",
  "answer_text": "I have 5 years of Python experience...",
  "job_description": "..."
}

Response:
{
  "is_valid": true,
  "relevance_score": 0.85,
  "confidence": 0.92,
  "feedback": "Excellent answer! Very relevant.",
  "next_question_id": "q-2"
}
```

### 3. Aggregate Answers
```
POST /chat/aggregate-answers
{
  "session_id": "uuid-123",
  "resume_text": "...",
  "job_description": "...",
  "answers": [
    { "text": "...", "section": "experience" },
    ...
  ]
}

Response:
{
  "enhanced_resume": "...",
  "new_bullets": [
    {
      "text": "Developed Python APIs using FastAPI",
      "section": "experience",
      "confidence": 0.92,
      "keywords_matched": ["Python", "FastAPI", "APIs"]
    }
  ],
  "total_keywords_added": 8
}
```

---

This completes the comprehensive architecture documentation!
