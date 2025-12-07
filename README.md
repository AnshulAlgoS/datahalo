# 🎓 DataHalo - AI-Powered Media Literacy Education Platform

<div align="center">

![DataHalo](https://img.shields.io/badge/Version-2.2-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

**Empowering the next generation of critical thinkers with AI-powered journalism education**

[Features](#-key-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API](#-api-reference)

</div>

---

## 📖 Overview

DataHalo is a comprehensive, AI-powered platform designed specifically for journalism and media
literacy education. It combines an intelligent Learning Management System (LMS) with advanced
analysis tools to help educators teach critical media analysis skills and students develop
fact-checking, bias detection, and source verification capabilities.

**Perfect for:**

- 📚 Journalism schools and media literacy courses
- 🎓 Educational institutions teaching critical thinking
- 👨‍🏫 Teachers creating engaging assignments
- 👩‍🎓 Students learning to navigate the information landscape
- 📰 Professional development for aspiring journalists

---

## 🧩 Problem Statement

- Journalism programs lack an integrated, hands‑on platform combining LMS workflows with newsroom‑grade analysis tools; current solutions are fragmented and generic.
- Teachers spend hours converting real‑world materials (articles, PDFs, videos) into standards‑aligned assignments with rubrics and citations, slowing course delivery and reducing time for feedback.
- Students lack immediate, professional feedback against recognized newsroom standards (AP Style, SPJ Ethics, Reuters handbook), delaying skill development and making grading subjective.
- Courses struggle to teach bias, propaganda, source quality, and evolving narratives at scale because there is no live, multi‑outlet tracking with timelines, source clustering, and key phrase analysis.
- Civic journalism training lacks district/state context and exportable briefs tailored to real stakeholders (administrators, policing, economic), so outputs remain theoretical rather than actionable.

## ✨ Key Features

### 🤖 AI-Powered Assignment Generator

Transform any content into comprehensive journalism assignments with our intelligent generator:

- **Smart Content Extraction**: Automatically processes PDFs, articles, YouTube videos, and text
- **Journalism-Specific Questions**: Generates assignments focused on:
    - Propaganda analysis & manipulation techniques
    - Bias detection & objectivity evaluation
    - Fact-checking & source verification
    - Media ethics & SPJ standards
    - Investigative thinking & critical analysis
- **Self-Learning System**: Improves over time by learning from previous assignments
- **Resource-Based Questions**: Every question directly references provided materials
- **Comprehensive Rubrics**: Detailed grading criteria based on professional journalism standards
- **Customizable Parameters**:
    - Difficulty levels (Easy, Medium, Hard)
    - Question count (1-20)
    - Topic focus areas
    - Learning objectives

**Example Topics:**

- "Analyze propaganda techniques in political coverage"
- "Fact-check claims using triangulation method"
- "Compare bias across different news outlets"
- "Evaluate source credibility and transparency"

### 🎯 Complete Learning Management System (LMS)

Full-featured classroom management built for media literacy education:

#### For Teachers:

- **Class Management**
    - Create unlimited classes with unique invite codes
    - Manage student enrollments
    - Track class performance and engagement
    - Organize by subject (Media Literacy, Journalism, Fact-Checking)

- **Assignment Lifecycle**
    - AI-generated or manually created assignments
    - Rich resource integration (PDFs, URLs, videos)
    - Due date management
    - Point allocation and grading rubrics
    - Bulk operations and templates

- **Grading & Feedback**
    - Detailed submission review interface
    - Rubric-based grading
    - Personalized feedback for each student
    - Grade analytics and insights
    - Export options for record-keeping

#### For Students:

- **Easy Enrollment**
    - Join classes with 6-character invite codes
    - View all enrolled classes in dashboard
    - Track upcoming assignments and deadlines

- **Assignment Submission**
    - Rich text editor with markdown support
    - Question-by-question response format
    - Save drafts and edit before submission
    - File attachments and citations
    - Submission confirmation and receipts

- **Progress Tracking**
    - View grades and feedback instantly
    - Track learning progress over time
    - Access resources and past assignments
    - Performance analytics per class

### 📊 Professional Analysis Tools

#### 1. **AI Article Analyzer** (Dual Mode)

**Rule-Based Analysis** (Fast - Instant Results)

- ✅ Instant analysis (< 2 seconds)
- ✅ Based on AP Style, Reuters, SPJ Ethics standards
- ✅ Advanced garbage detection (spam/nonsense filtering)
- ✅ 8-criteria professional scoring:
    - **Objectivity**: Bias-free reporting
    - **Source Quality**: Credibility and attribution
    - **Factual Accuracy**: Verification and evidence
    - **Writing Clarity**: Readability and structure
    - **Ethical Standards**: SPJ Code compliance
    - **Context Completeness**: Background and balance
    - **Structure & Flow**: Inverted pyramid, organization
    - **Headline Quality**: Accuracy and clickbait detection
- ✅ ~75-80% correlation with expert grading
- ✅ Detailed feedback with specific improvement actions
- ✅ Learning resources personalized to weaknesses

**AI-Powered Analysis** (Deep - 5-15 seconds)

- ✅ Qwen3 480B AI model for contextual understanding
- ✅ Nuanced feedback with specific examples
- ✅ ATS-like scoring against journalism standards
- ✅ Professional-grade evaluation
- ✅ Industry-standard insights

**Analysis Output:**

```json
{
  "overall_score": 82,
  "letter_grade": "B+",
  "score_breakdown": {
    "objectivity": 85,
    "source_quality": 78,
    "factual_accuracy": 88,
    "writing_clarity": 80,
    "ethical_standards": 82,
    "context_completeness": 75,
    "structure_flow": 84,
    "headline_quality": 88
  },
  "strengths": ["Well-sourced", "Clear structure"],
  "critical_issues": ["Lacks diverse perspectives", "Missing context"],
  "improvement_actions": ["Add opposing viewpoints", "Cite primary sources"],
  "learning_recommendations": []
}
```

#### 2. **Journalist Case Study Generator**

Generate comprehensive educational case studies for any journalist:

- **Data Collection**: Uses DuckDuckGo scraping (no API keys needed)
- **AI Analysis**: Deep profile analysis using Qwen3 480B
- **Comprehensive Profile**:
    - Biography and career timeline
    - Notable works and major stories
    - Credibility score and verification rate
    - Writing style and tone analysis
    - Ideological bias assessment
    - Awards and recognition
    - Controversies and ethical issues
    - Regional expertise and beat coverage
    - Impact and influence metrics
    - Lessons for students

- **Gallery View**: Browse 50+ pre-analyzed journalists
- **Educational Use**: Perfect for case study discussions and comparative analysis

**Example Journalists Analyzed:**

- Barkha Dutt, Ravish Kumar, Rana Ayyub (India)
- Glenn Greenwald, Matt Taibbi (USA)
- And many more...

#### 3. **Narrative Tracker**

Monitor how stories evolve across media outlets over time:

- **Timeline Analysis**: Track narrative changes day-by-day
- **Source Clustering**: Identify coordinated coverage patterns
- **Manipulation Detection**:
    - Coordinated timing across outlets
    - Sudden spikes in coverage
    - Sentiment uniformity
    - Framing patterns
- **Key Phrases Extraction**: Identify repeated talking points
- **Major Events Mapping**: Connect narratives to real-world triggers
- **Google News Integration**: Fresh data via SERP API
- **Multi-Source Comparison**: Analyze coverage differences

**Use Cases:**

- "Track election coverage bias across outlets"
- "Analyze propaganda patterns in conflict reporting"
- "Study narrative framing in climate change news"

#### 4. **URL-Based Narrative Analysis**

Analyze narratives around any specific article:

- Paste any article URL
- Get comprehensive analysis of how that story is covered elsewhere
- Compare framing across different outlets
- Detect narrative manipulation
- Identify missing perspectives

#### 5. **News Intelligence Dashboard**

Smart news feed with AI-powered analysis:

- **Primary Actions**: Three big buttons — `Top Developments`, `Govt Exam Prep`, `District Insights`
- **District/State Insights**: Dropdowns for state and district to focus analysis locally
- **Judge Perspectives**: Women Commission, Economist, IAS Officer, Assistant Commissioner of Police, Social Worker, Block President
- **Smart Feed AI**: Personalized perspectives including all above, plus General Public, Finance Analyst, Tech Student, Business Student
- **Fresh Region Fetch**: Google News (SERP) and NewsData queries enriched with POV-specific keywords for relevant local stories
- **Article Selection**: `Government Exam Aspirant` POV analyzes up to 50 recent, relevant articles (excludes entertainment/sports)
- **Accurate Counts**: Frontend displays `articlesAnalyzed` returned by backend for transparency
- **PDF Export**: One‑click export of the analysis view to PDF using `html2canvas`
- **Multi-Category Support**: General, Tech, Business, Sports, Science, Health, Entertainment
- **Database Optimization**: Fast loading from MongoDB cache
- **Duplicate Detection**: Intelligent content deduplication
- **Source Diversity**: Multiple credible sources

### 🧠 AI Tutor with RAG

Interactive AI tutor for media literacy learning:

- **Multi-Turn Conversations**: Maintains context across chat sessions
- **RAG-Powered**: Real-time web search for current information
- **Expertise Areas**:
    - Media bias & objectivity
    - Propaganda techniques
    - Fact-checking methodologies
    - Deepfake detection
    - Narrative analysis
    - Source evaluation (CRAAP test)
    - Social media algorithms
    - Journalism ethics (SPJ Code)

- **Teaching Approach**:
    - Socratic method for deep learning
    - Real-world examples and case studies
    - Interactive exercises
    - Multi-level difficulty adjustment
    - Thought-provoking questions

- **Multi-Chat Support**:
    - Save and manage multiple conversations
    - Smart conversation titles
    - Full chat history
    - Delete and organize chats
    - User-specific chat sessions

**Example Questions:**

- "What is the SIFT method for fact-checking?"
- "Teach me about confirmation bias in news consumption"
- "How do I identify deepfakes?"
- "What are common propaganda techniques?"

### 🔐 Authentication & Security

Robust user management powered by Firebase:

- **Multiple Sign-In Methods**:
    - Email/Password authentication
    - Google Sign-In (one-click)
    - Secure password reset

- **Role-Based Access Control**:
    - Teacher role: Full LMS access, create classes, grade assignments
    - Student role: Join classes, submit assignments, track progress

- **Protected Routes**: Automatic redirection for unauthorized access
- **User Profiles**: Customizable profiles with institution info
- **Session Management**: Secure token-based authentication

---

## 🛠️ Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18** | Modern UI framework with hooks |
| **TypeScript** | Type-safe development |
| **Vite** | Lightning-fast build tool |
| **Shadcn/ui** | Beautiful, accessible components |
| **Tailwind CSS** | Utility-first styling |
| **React Query** | Server state management |
| **React Router v6** | Client-side routing |
| **Framer Motion** | Smooth animations |
| **Recharts** | Data visualization |
| **Lucide React** | Modern icon library |
| **Sonner** | Toast notifications |
| **React Markdown** | Rich content rendering |

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python framework |
| **MongoDB** | NoSQL database |
| **Firebase Admin SDK** | Authentication & user management |
| **NVIDIA NIM API** | Qwen3 Coder 480B AI model |
| **BeautifulSoup4** | Web scraping |
| **PyPDF** | PDF text extraction |
| **SERP API** | Google News integration |
| **News API** | Article aggregation |
| **Uvicorn** | ASGI server |

### Infrastructure

- **Database**: MongoDB Atlas (cloud) or local MongoDB
- **Hosting**: Vercel (frontend), Render/Railway (backend)
- **CDN**: Vercel Edge Network
- **Environment**: Python 3.9+, Node.js 18+

---

## 🚀 Quick Start

### Prerequisites

```bash
# Check versions
node --version  # v18.0.0 or higher
python --version  # 3.9.0 or higher
```

**Required Accounts:**

- Firebase project (free tier)
- MongoDB Atlas (free tier) or local MongoDB
- NVIDIA API key (free tier available)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/datahalo.git
cd datahalo
```

### 2. Frontend Setup

```bash
cd datahalo
npm install
```

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### 3. Backend Setup

```bash
cd Backend
pip install -r requirements.txt
```

Create `.env` file:

```env
MONGO_URI=mongodb://localhost:27017/
NVIDIA_API_KEY=your_nvidia_api_key
SERP_API_KEY=your_serp_api_key  # Optional but recommended
NEWS_API_KEY=your_news_api_key  # Optional
FIREBASE_CREDENTIALS_PATH=path/to/serviceAccountKey.json
```

### 4. Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Enable Authentication:
    - Email/Password
    - Google Sign-In
4. Enable Firestore Database
5. Download service account key (Settings → Service Accounts → Generate New Private Key)
6. Place in `Backend/` directory
7. Copy web app credentials to frontend `.env`

### 5. MongoDB Setup

**Option A: MongoDB Atlas (Recommended)**

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Get connection string
4. Update `MONGO_URI` in backend `.env`

**Option B: Local MongoDB**

```bash
# Install MongoDB Community Edition
# macOS
brew tap mongodb/brew
brew install mongodb-community

# Ubuntu
sudo apt-get install mongodb

# Start MongoDB
mongod --dbpath /path/to/data
```

### 6. Get API Keys

**NVIDIA API Key** (Required for AI features)

1. Sign up at [NVIDIA NIM](https://build.nvidia.com/)
2. Navigate to API Keys
3. Generate new key
4. Add to backend `.env`

**SERP API Key** (Optional - for Google News)

1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get free tier API key (100 searches/month)
3. Add to backend `.env`

### 7. Run the Application

**Start Backend:**

```bash
cd Backend
python main.py
```

Server starts at `http://localhost:8000`

**Start Frontend:**

```bash
cd datahalo
npm run dev
```

App available at `http://localhost:5173`

---

## 📚 Usage Guide

### For Teachers

#### Creating Your First Class

1. **Sign Up** as Teacher
    - Navigate to `/signup`
    - Choose "Teacher" role
    - Complete registration

2. **Create Class**
    - Go to Dashboard
    - Click "My Classes" → "Create Class"
    - Fill in details:
        - Title: "Media Literacy 101"
        - Subject: "Journalism"
        - Description: Course overview
    - Get unique **invite code** (e.g., "ABC123")

3. **Share Invite Code** with students

#### Generating AI Assignments

1. **Navigate to AI Generator**
    - Dashboard → "Generate Assignment"

2. **Add Resources** (Multiple types supported)
    - **URL**: Paste article link
    - **PDF**: Upload document
    - **YouTube**: Paste video URL
    - **Text**: Copy-paste content

3. **Configure Parameters**
   ```
   Topic: "Propaganda in Political Coverage"
   Difficulty: Medium
   Question Count: 5
   ```

4. **Generate & Review**
    - AI creates journalism-specific questions
    - Each question references specific resources
    - Includes detailed rubrics

5. **Publish to Class**
    - Select class from dropdown
    - Set due date
    - Assign points
    - Click "Create Assignment"

#### Grading Submissions

1. **View Submissions**
    - Class → "Assignments" tab
    - Click on assignment
    - See all student submissions

2. **Grade Each Submission**
    - Use provided rubric
    - Enter score (0-100)
    - Write detailed feedback
    - Submit grade

### For Students

#### Joining a Class

1. **Sign Up** as Student
2. **Join Class**
    - Dashboard → "Enrolled Classes"
    - Click "Join Class"
    - Enter invite code from teacher
    - Confirm enrollment

#### Completing Assignments

1. **View Assignment**
    - Go to class
    - Click on assignment
    - Read instructions and resources

2. **Submit Response**
    - Answer each question thoroughly
    - Reference provided resources
    - Use markdown for formatting
    - Submit before due date

3. **Check Grades**
    - Class → "Grades" tab
    - View score and feedback
    - Learn from teacher comments

### Using Analysis Tools

#### Article Analyzer

1. **Navigate to Tool**
    - Dashboard → "Article Analyzer"

2. **Input Article**
    - Paste article text
    - Choose analysis mode:
        - **AI Mode**: Deep analysis (5-15s)
        - **Rule-Based**: Instant analysis (<2s)

3. **Review Results**
    - Overall score and grade
    - 8-criteria breakdown
    - Strengths and issues
    - Improvement suggestions
    - Learning resources

#### Journalist Case Study

1. **Generate Case Study**
    - Dashboard → "Journalist Analyzer"
    - Enter journalist name
    - Click "Generate Case Study"

2. **Review Analysis**
    - Biography and background
    - Credibility assessment
    - Notable works
    - Bias analysis
    - Writing style
    - Ethical record

3. **Browse Gallery**
    - View pre-analyzed journalists
    - Filter by region/category
    - Compare profiles

#### Narrative Tracker

1. **Start Analysis**
    - Dashboard → "Narrative Tracker"
    - Enter topic (e.g., "Climate Change")
    - Select timeframe (7-90 days)

2. **Review Results**
    - Timeline of coverage
    - Key narratives and phrases
    - Manipulation indicators
    - Source clustering
    - Major events mapping

### AI Tutor Usage

1. **Start Conversation**
    - Dashboard → "AI Tutor"
    - Ask any media literacy question

2. **Multi-Turn Learning**
    - AI maintains context
    - Asks follow-up questions
    - Provides examples
    - Suggests exercises

3. **Manage Chats**
    - Save important conversations
    - Rename chat titles
    - Delete old chats
    - Resume previous discussions

---

## 📡 API Reference

### Base URL

```
Local: http://localhost:8000
Production: https://your-api.com
```

### Authentication

All LMS endpoints require Firebase authentication token:

```javascript
headers: {
  'Authorization': 'Bearer <firebase_token>',
  'Content-Type': 'application/json'
}
```

### Endpoints

#### LMS - Classes

**Create Class**

```http
POST /lms/courses/create
Content-Type: application/json

{
  "teacher_id": "string",
  "title": "string",
  "description": "string",
  "subject": "Media Literacy"
}

Response: {
  "status": "success",
  "course": {...},
  "invite_code": "ABC123"
}
```

**Get Teacher's Classes**

```http
GET /lms/courses/teacher/{teacher_id}

Response: {
  "status": "success",
  "courses": [...],
  "count": 5
}
```

**Get Student's Classes**

```http
GET /lms/courses/student/{student_id}
```

**Enroll Student**

```http
POST /lms/enroll
Content-Type: application/json

{
  "student_id": "string",
  "invite_code": "ABC123"
}
```

#### LMS - Assignments

**Generate AI Assignment**

```http
POST /lms/generate-assignment
Content-Type: application/json

{
  "resources": [
    {
      "type": "url|pdf|youtube|text",
      "content": "string",
      "title": "string"
    }
  ],
  "topic": "string",
  "difficulty": "easy|medium|hard",
  "question_count": 5
}

Response: {
  "status": "success",
  "assignment": {
    "title": "string",
    "questions": [...],
    "rubric": {...},
    "total_points": 50
  }
}
```

**Create Assignment**

```http
POST /lms/assignments/create
Content-Type: application/json

{
  "course_id": "string",
  "teacher_id": "string",
  "title": "string",
  "description": "string",
  "instructions": "string",
  "questions": [...],
  "due_date": "ISO8601",
  "points": 100
}
```

**Get Course Assignments**

```http
GET /lms/assignments/course/{course_id}
```

#### LMS - Submissions

**Submit Assignment**

```http
POST /lms/submissions/submit
Content-Type: application/json

{
  "assignment_id": "string",
  "student_id": "string",
  "student_name": "string",
  "content": "string",
  "answers": [...]
}
```

**Grade Submission**

```http
POST /lms/submissions/grade
Content-Type: application/json

{
  "submission_id": "string",
  "grade": 85,
  "feedback": "string"
}
```

**Get Student Submissions**

```http
GET /lms/submissions/student/{student_id}
```

#### Analysis Tools

**Analyze Article**

```http
POST /analyze-article?use_ai=true
Content-Type: application/json

{
  "article": "string (article text)"
}

Response: {
  "status": "success",
  "analysis": {
    "overall_score": 82,
    "letter_grade": "B+",
    "score_breakdown": {...},
    "strengths": [...],
    "issues": [...],
    "improvement_actions": [...],
    "learning_recommendations": [...]
  }
}
```

**Generate Journalist Case Study**

```http
POST /generate-case-study
Content-Type: application/json

{
  "journalist_name": "string"
}

Response: {
  "status": "success",
  "case_study": {
    "profile": {...},
    "analysis": {...},
    "credibility_score": 85
  }
}
```

**Analyze Narrative**

```http
POST /analyze-narrative
Content-Type: application/json

{
  "topic": "string",
  "days": 30
}

Response: {
  "status": "success",
  "analysis": {
    "timeline": [...],
    "key_narratives": [...],
    "manipulation_indicators": {...}
  }
}
```

**AI Tutor**

```http
POST /ai-tutor
Content-Type: application/json

{
  "message": "string",
  "conversation_history": [...],
  "user_id": "string",
  "chat_id": "string"  // Optional, creates new if not provided
}

Response: {
  "status": "success",
  "response": "string",
  "context_used": true,
  "sources": [...],
  "chat_id": "string"
}
```

**Get User Chats**

```http
GET /ai-tutor/chats/{user_id}?limit=20
```

**Get Chat Messages**

```http
GET /ai-tutor/chat/{chat_id}/messages
```

#### News Intelligence

**Get News**

```http
GET /news?category=general

Categories: general, technology, business, sports, science, health, entertainment

Response: {
  "status": "success",
  "articles": [...],
  "count": 50
}
```

**Refresh News**

```http
GET /refresh-news?category=general

Response: {
  "status": "success",
  "new_articles_count": 30,
  "total_articles": 80
}
```

**Smart Feed Analysis**

```http
POST /smart-feed?pov={pov}&days={7-30}&state={optional}&district={optional}

POV Options:
  general public, finance analyst, tech student, business student,
  government exam aspirant, women commission, economist, ias officer,
  assistant commissioner of police, social worker, block president

Response: {
  "status": "success",
  "perspective": "string",
  "articlesAnalyzed": 30,
  "summary": "AI-generated analysis with headings and bullet points"
}
```

Notes:
- When `state`/`district` are provided, backend performs region-targeted fetching via SERP/NewsData and filters by POV relevance.
- Analysis output uses big section headings and concise bullet points suitable for quick review and PDF export.

---

## 🗂️ Project Structure

```
datahalo/
├── Backend/
│   ├── main.py                          # FastAPI application & core endpoints
│   ├── lms_endpoints.py                 # LMS API routes
│   ├── requirements.txt                 # Python dependencies
│   ├── .env                            # Backend environment variables
│   └── utils/
│       ├── ai_article_analyzer.py      # AI-powered article analysis (Qwen3 480B)
│       ├── article_analyzer_v2.py      # Rule-based article analyzer
│       ├── ai_analysis.py              # Journalist AI analysis
│       ├── serp_scraper.py             # Case study data collection
│       ├── news_fetcher.py             # News aggregation
│       ├── smart_analysis.py           # Smart feed AI
│       └── url_narrative_analyzer.py   # URL-based narrative analysis
│
├── src/
│   ├── components/
│   │   ├── ui/                         # Shadcn UI components
│   │   ├── AITutorV2.tsx              # Multi-chat AI tutor
│   │   ├── ProtectedRoute.tsx         # Route protection
│   │   ├── SideNav.tsx                # Navigation
│   │   └── ...                        # Other components
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx              # Main teacher/student dashboard
│   │   ├── ClassesPage.tsx            # Classes list view
│   │   ├── ClassroomPage.tsx          # Individual classroom
│   │   ├── ArticleAnalyzer.tsx        # Article analysis tool
│   │   ├── JournalistsGallery.tsx     # Journalist case studies gallery
│   │   ├── NarrativeAnalyzer.tsx      # Narrative tracking tool
│   │   ├── SourceVerifier.tsx         # Source verification tool
│   │   ├── Login.tsx                  # Authentication
│   │   └── Signup.tsx                 # Registration
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx            # Authentication context
│   │
│   ├── lib/
│   │   ├── firebase.ts                # Firebase configuration
│   │   └── utils.ts                   # Utility functions
│   │
│   └── App.tsx                        # Main application
│
├── public/                             # Static assets
├── package.json                        # Frontend dependencies
├── vite.config.ts                     # Vite configuration
├── tailwind.config.ts                 # Tailwind configuration
└── README.md                          # This file
```

---

## 💾 Database Schema

### Collections

#### users (Firebase Firestore)

```javascript
{
  uid: "firebase_uid",
  email: "user@example.com",
  displayName: "John Doe",
  role: "student" | "teacher",
  institution: "University Name",
  photoURL: "https://...",
  createdAt: Timestamp,
  lastLogin: Timestamp
}
```

#### courses (MongoDB)

```javascript
{
  _id: ObjectId,
  teacher_id: "firebase_uid",
  title: "Media Literacy 101",
  description: "Course description",
  subject: "Media Literacy",
  invite_code: "ABC123",
  students: ["student_uid_1", "student_uid_2"],
  created_at: ISODate,
  updated_at: ISODate,
  assignment_count: 5,
  student_count: 25
}
```

#### assignments (MongoDB)

```javascript
{
  _id: ObjectId,
  course_id: "course_id",
  teacher_id: "teacher_uid",
  title: "Assignment Title",
  description: "Assignment description",
  instructions: "Detailed instructions",
  questions: [
    {
      question_number: 1,
      question_text: "Question text",
      question_type: "essay",
      points: 10,
      rubric: {
        excellent: "Criteria",
        good: "Criteria",
        fair: "Criteria",
        poor: "Criteria"
      }
    }
  ],
  resources: [
    {
      type: "url",
      content: "https://...",
      title: "Resource Title"
    }
  ],
  due_date: ISODate,
  points: 50,
  created_at: ISODate,
  submission_count: 20
}
```

#### submissions (MongoDB)

```javascript
{
  _id: ObjectId,
  assignment_id: "assignment_id",
  student_id: "student_uid",
  student_name: "Student Name",
  content: "Response text",
  answers: [
    {
      question_number: 1,
      answer: "Student answer"
    }
  ],
  submitted_at: ISODate,
  grade: 85,
  feedback: "Teacher feedback",
  graded_at: ISODate,
  status: "graded"
}
```

#### journalists (MongoDB)

```javascript
{
  _id: ObjectId,
  name: "Journalist Name",
  analysis_timestamp: ISODate,
  articlesAnalyzed: 50,
  aiProfile: {
    biography: "Bio text",
    credibilityScore: 85,
    notableWorks: [],
    mainTopics: [],
    ideologicalBias: "Center",
    writingTone: "Professional",
    ethicalAssessment: "High standards",
    awards: []
  },
  scrapedData: {
    articles_count: 50,
    verification_rate: 0.85,
    data_sources: []
  }
}
```

#### news (MongoDB)

```javascript
{
  _id: ObjectId,
  title: "Article Title",
  description: "Article description",
  url: "https://...",
  image: "https://...",
  source: "News Source",
  category: "general",
  publishedAt: ISODate,
  fetchedAt: ISODate
}
```

#### ai_tutor_chat_sessions (MongoDB)

```javascript
{
  _id: ObjectId,
  user_id: "user_uid",
  title: "Conversation Title",
  created_at: ISODate,
  updated_at: ISODate,
  message_count: 10,
  first_message: "Initial question"
}
```

#### ai_tutor_messages (MongoDB)

```javascript
{
  _id: ObjectId,
  chat_id: "chat_id",
  user_id: "user_uid",
  role: "user" | "assistant",
  content: "Message content",
  timestamp: ISODate,
  web_search_used: true,
  sources: [
    {
      title: "Source Title",
      url: "https://..."
    }
  ]
}
```

#### ai_learning_dataset (MongoDB)

```javascript
{
  _id: ObjectId,
  topic: "Assignment topic",
  difficulty: "medium",
  question_count: 5,
  resources_summary: [],
  sample_question: "Question text",
  learning_objectives: [],
  created_at: ISODate,
  quality_score: 85,
  feedback: "Teacher feedback",
  used_count: 10,
  journalism_focus: true
}
```

---

## ⚙️ Configuration

### Environment Variables

#### Frontend (.env)

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Firebase Configuration
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

#### Backend (.env)

```env
# Database Configuration
MONGO_URI=mongodb://localhost:27017/
# or MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/datahalo

# AI Configuration
NVIDIA_API_KEY=your_nvidia_api_key

# News & Search APIs (Optional)
SERP_API_KEY=your_serp_api_key
NEWS_API_KEY=your_news_api_key

# Firebase Admin
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
```

### Firebase Setup Steps

1. **Create Firebase Project**
   ```
   → Go to https://console.firebase.google.com
   → Create new project
   → Name: "DataHalo"
   ```

2. **Enable Authentication**
   ```
   → Authentication → Sign-in method
   → Enable "Email/Password"
   → Enable "Google"
   ```

3. **Enable Firestore**
   ```
   → Firestore Database → Create database
   → Start in production mode
   → Choose region
   ```

4. **Get Web Credentials**
   ```
   → Project Settings → General
   → Your apps → Web app
   → Copy configuration
   → Add to frontend .env
   ```

5. **Get Service Account**
   ```
   → Project Settings → Service Accounts
   → Generate new private key
   → Save as serviceAccountKey.json
   → Place in Backend/ directory
   ```

### MongoDB Atlas Setup

1. **Create Account**
   ```
   → Go to mongodb.com/cloud/atlas
   → Sign up (free tier)
   ```

2. **Create Cluster**
   ```
   → Create new cluster
   → Choose free tier (M0)
   → Select region
   → Name: "DataHalo"
   ```

3. **Configure Access**
   ```
   → Database Access → Add user
   → Username: datahalo
   → Password: secure_password
   → Role: Read & Write
   
   → Network Access → Add IP
   → Allow access from anywhere (0.0.0.0/0)
   ```

4. **Get Connection String**
   ```
   → Connect → Connect your application
   → Copy connection string
   → Replace <password> with your password
   → Add to backend .env as MONGO_URI
   ```

---

## 🚀 Deployment

### Frontend (Vercel)

1. **Build Application**
   ```bash
   npm run build
   ```

2. **Deploy to Vercel**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel
   ```

3. **Configure Environment Variables**
   ```
   → Vercel Dashboard
   → Project Settings → Environment Variables
   → Add all VITE_* variables
   ```

4. **Custom Domain** (Optional)
   ```
   → Domains → Add domain
   → Follow DNS configuration steps
   ```

### Backend (Render/Railway)

#### Using Render

1. **Create Web Service**
   ```
   → Dashboard → New → Web Service
   → Connect GitHub repository
   → Root Directory: Backend
   → Build Command: pip install -r requirements.txt
   → Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Environment Variables**
   ```
   → Environment
   → Add all backend .env variables
   → Upload serviceAccountKey.json as secret file
   ```

3. **Deploy**
   ```
   → Click "Create Web Service"
   → Wait for deployment
   → Copy service URL
   ```

#### Using Railway

1. **Create Project**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Initialize
   cd Backend
   railway init
   ```

2. **Configure**
   ```bash
   # Add environment variables
   railway variables set MONGO_URI="your_mongodb_uri"
   railway variables set NVIDIA_API_KEY="your_key"
   
   # Deploy
   railway up
   ```

3. **Get URL**
   ```bash
   railway domain
   ```

### Update Frontend to Use Production Backend

Update `VITE_API_URL` in frontend `.env`:

```env
VITE_API_URL=https://your-backend.railway.app
```

Redeploy frontend:

```bash
vercel --prod
```

---

## 🔒 Security Best Practices

### API Keys

- ✅ Never commit `.env` files to version control
- ✅ Use environment variables for all sensitive data
- ✅ Rotate API keys regularly
- ✅ Use different keys for development and production

### Authentication

- ✅ Implement HTTPS in production
- ✅ Use Firebase security rules
- ✅ Validate user roles on backend
- ✅ Implement rate limiting

### Database

- ✅ Use strong passwords
- ✅ Restrict IP access in MongoDB Atlas
- ✅ Enable authentication
- ✅ Regular backups
- ✅ Implement indexes for performance

### CORS Configuration

Backend CORS is configured for:

```python
allow_origins = [
    "http://localhost:5173",      # Local development
    "https://datahalo.vercel.app", # Production
    # Add your custom domain
]
```

---

## 🧪 Testing

### Frontend Testing

```bash
# Run linter
npm run lint

# Type check
npx tsc --noEmit

# Build test
npm run build
```

### Backend Testing

```bash
# Test API health
curl http://localhost:8000/health

# Test endpoints with httpie
pip install httpie

http POST localhost:8000/analyze-article article="Your article text"
```

### Manual Testing Checklist

- [ ] User registration (student & teacher)
- [ ] Class creation and invite code generation
- [ ] Student enrollment
- [ ] AI assignment generation with different resources
- [ ] Assignment submission
- [ ] Grading workflow
- [ ] Article analyzer (both modes)
- [ ] Journalist case study generation
- [ ] Narrative tracking
- [ ] AI tutor conversation
- [ ] News feed and refresh

---

## 📈 Performance Optimization

### Frontend

- ✅ Code splitting with React.lazy()
- ✅ Image optimization (WebP, lazy loading)
- ✅ Bundle size optimization
- ✅ React Query caching
- ✅ Memoization for expensive computations
- ✅ Virtual scrolling for large lists

### Backend

- ✅ MongoDB indexes on frequently queried fields
- ✅ Response caching with TTL
- ✅ Async/await for concurrent operations
- ✅ Connection pooling
- ✅ Pagination for large datasets
- ✅ Gzip compression

### Database Indexes

```javascript
// Recommended indexes
db.courses.createIndex({ "teacher_id": 1 })
db.courses.createIndex({ "invite_code": 1 }, { unique: true })
db.assignments.createIndex({ "course_id": 1 })
db.submissions.createIndex({ "assignment_id": 1 })
db.submissions.createIndex({ "student_id": 1 })
db.journalists.createIndex({ "name": 1 })
db.news.createIndex({ "category": 1, "fetchedAt": -1 })
```

---

## 🐛 Troubleshooting

### Common Issues

**Frontend not connecting to backend**

```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in Backend/main.py
# Ensure VITE_API_URL matches backend URL

# Check browser console for errors
```

**MongoDB connection failed**

```bash
# Check MongoDB is running (local)
mongod --dbpath /path/to/data

# Check connection string format
mongodb://username:password@host:port/database

# For Atlas, verify IP whitelist
# Network Access → IP Access List
```

**Firebase authentication errors**

```bash
# Verify Firebase credentials in .env
# Check Firebase console for enabled auth methods
# Ensure service account key is valid

# Test Firebase connection
firebase login
```

**AI generation not working**

```bash
# Verify NVIDIA_API_KEY is set
echo $NVIDIA_API_KEY

# Check API quota/limits
# Review backend logs for detailed errors

# Try with smaller content first
```

**CORS errors**

```bash
# Add your frontend URL to backend CORS
# Backend/main.py → allow_origins list

# For production, use your deployed URL
```

**PDF extraction failing**

```bash
# Install required dependencies
pip install pypdf

# Check PDF is not encrypted/password-protected
# Try with smaller PDF first
```

### Debug Mode

Enable verbose logging:

**Backend:**

```python
# Backend/main.py
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**

```javascript
// Add to .env
VITE_DEBUG=true
```

---

## 🛣️ Roadmap

## 🛣️ Roadmap

### Version 2.3 (Q1 2025)

- [ ] **Rich Text Editor** for assignments
    - Markdown support
    - Citation management
    - Image embedding
    - Code block formatting

- [ ] **Real-Time Collaboration**
    - Live document editing
    - Comment threads on submissions
    - Peer review system

- [ ] **Advanced Analytics Dashboard**
    - Student progress tracking
    - Class performance metrics
    - Learning outcome analysis
    - Export to CSV/PDF

- [ ] **Mobile Responsiveness**
    - Optimize for tablet/mobile
    - Touch-friendly UI
    - Progressive Web App (PWA)

### Version 2.4 (Q2 2025)

- [ ] **Video Integration**
    - Record video submissions
    - Embed YouTube playlists
    - Video annotation tools

- [ ] **Gamification**
    - Achievement badges
    - Leaderboards
    - Streaks and rewards
    - Points system

- [ ] **Email Notifications**
    - Assignment reminders
    - Grade notifications
    - Class updates

- [ ] **Advanced Search**
    - Search across all content
    - Filters and facets
    - Save search queries

### Version 3.0 (Q3 2025)

- [ ] **Plagiarism Detection**
    - Copyscape integration
    - Similarity checking
    - Citation verification

- [ ] **Automated Grading**
    - AI-powered rubric evaluation
    - Partial credit assignment
    - Feedback generation

- [ ] **Discussion Forums**
    - Class discussions
    - Topic threads
    - Moderation tools

- [ ] **Calendar Integration**
    - Google Calendar sync
    - Deadline reminders
    - Class schedule

- [ ] **Mobile Apps**
    - React Native iOS/Android apps
    - Push notifications
    - Offline mode

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Process

1. **Fork the Repository**
   ```bash
   git fork https://github.com/yourusername/datahalo.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Make Changes**
    - Follow code style guidelines
    - Add tests for new features
    - Update documentation

4. **Commit Changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

5. **Push to Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```

6. **Open Pull Request**
    - Describe changes clearly
    - Reference related issues
    - Wait for review

### Code Style

**TypeScript/React:**

- Use TypeScript strict mode
- Follow ESLint rules
- Use functional components and hooks
- Write descriptive component names

**Python:**

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions
- Keep functions focused and small

### Commit Messages

Follow conventional commits:

```
feat: Add new article analyzer feature
fix: Fix grading calculation bug
docs: Update API documentation
style: Format code with prettier
refactor: Restructure assignment service
test: Add tests for LMS endpoints
chore: Update dependencies
```

---

## 📄 License

This project is licensed under the **MIT License**:

```
MIT License

Copyright (c) 2025 DataHalo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

### Technology Partners

- **NVIDIA NIM**: Qwen3 Coder 480B AI model for intelligent analysis
- **Firebase**: Authentication and user management
- **MongoDB**: Flexible, scalable database
- **Vercel**: Fast, reliable frontend hosting
- **Shadcn/ui**: Beautiful, accessible component library

### Open Source Libraries

- **React**: UI framework
- **FastAPI**: High-performance Python framework
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Modern icon library
- **React Query**: Server state management
- **BeautifulSoup4**: Web scraping
- **PyPDF**: PDF text extraction

### Journalism Standards

- **SPJ Code of Ethics**: Professional journalism guidelines
- **AP Stylebook**: Writing and editing standards
- **Reuters Handbook**: Editorial guidelines
- **Poynter Institute**: Media literacy education

### Inspiration

Built with ❤️ for educators, students, and journalists who believe in the power of media literacy to
strengthen democracy and critical thinking.

---

## 📞 Support

### Getting Help

**Documentation:**

- Read this README
- Check API reference
- Review code examples

**Community:**

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and ideas
- Email: support@datahalo.com

**Professional Support:**

- Enterprise setup assistance
- Custom feature development
- Training and onboarding

### Reporting Issues

When reporting bugs, include:

- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment (OS, browser, versions)
- Error logs

**Example:**

```
Title: Assignment generation fails with PDF files

Description:
When trying to generate an assignment with a PDF resource,
the AI generator returns an error after 30 seconds.

Steps to Reproduce:
1. Go to Dashboard → Generate Assignment
2. Add PDF resource (file: sample.pdf, 5MB)
3. Set topic: "Media Bias"
4. Click "Generate"
5. Error appears after 30s

Expected: Assignment with questions based on PDF
Actual: Error "PDF extraction failed"

Environment:
- OS: macOS 14.1
- Browser: Chrome 120
- Backend: Local (Python 3.11)
- PDF: Not encrypted, 50 pages

Logs:
[Attach relevant logs]
```

---

## 📊 Stats & Metrics

- **Lines of Code**: ~15,000+
- **Components**: 50+
- **API Endpoints**: 40+
- **Database Collections**: 9
- **Supported File Types**: PDF, URL, YouTube, Text
- **AI Models**: Qwen3 Coder 480B
- **Analysis Criteria**: 8 journalism standards
- **Learning Resources**: 100+ curated links

---

## 🎯 Use Cases

### Educational Institutions

1. **Journalism Schools**
    - Teach media literacy fundamentals
    - Analyze real-world case studies
    - Grade student assignments efficiently

2. **High Schools**
    - Critical thinking curriculum
    - Fact-checking exercises
    - Source evaluation skills

3. **Universities**
    - Advanced journalism courses
    - Research projects
    - Thesis preparation

### Professional Development

1. **Newsrooms**
    - Training new journalists
    - Ethics refreshers
    - Bias awareness workshops

2. **Corporate Communications**
    - Media relations training
    - Crisis communication prep
    - Press release evaluation

### Individual Learning

1. **Students**
    - Self-paced learning
    - Assignment practice
    - Skill development

2. **Aspiring Journalists**
    - Portfolio building
    - Case study analysis
    - Professional standards mastery

---

## 🌟 Why DataHalo?

### For Teachers

- ⚡ **Save Time**: AI generates assignments in seconds
- 📚 **Rich Resources**: Integrate any content type
- 📊 **Track Progress**: Comprehensive analytics
- 🎯 **Focused Learning**: Journalism-specific curriculum

### For Students

- 🧠 **Learn Critically**: Develop essential media literacy skills
- 💡 **Real Examples**: Analyze actual news and journalists
- 🎓 **Personalized**: AI tutor adapts to your needs
- 🚀 **Engaging**: Interactive tools and instant feedback

### For Institutions

- 💰 **Cost-Effective**: Open-source, self-hostable
- 🔒 **Secure**: Firebase authentication, role-based access
- 📈 **Scalable**: MongoDB handles growth
- 🛠️ **Customizable**: Adapt to your needs

---

## 📚 Additional Resources

### Learning Materials

- [SPJ Code of Ethics](https://www.spj.org/ethicscode.asp)
- [AP Stylebook](https://www.apstylebook.com/)
- [Poynter Institute](https://www.poynter.org/)
- [Media Literacy Now](https://medialiteracynow.org/)
- [Fact-Check.org](https://www.factcheck.org/)

### Technical Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Manual](https://docs.mongodb.com/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Tailwind CSS](https://tailwindcss.com/)

### Community

- [GitHub Repository](https://github.com/yourusername/datahalo)
- [Issue Tracker](https://github.com/yourusername/datahalo/issues)
- [Discussions](https://github.com/yourusername/datahalo/discussions)

---

<div align="center">

**Built with ❤️ for media literacy education**

[⬆ Back to Top](#-datahalo---ai-powered-media-literacy-education-platform)

---

**Version 2.2** | Last Updated: January 2025 | Status: Production Ready

Made by DataHalo Team | [Website](#) | [Twitter](#) | [LinkedIn](#)

</div>
