
# DataHalo LMS Endpoints - Media Literacy Assignment Management
# Focus: Teacher-Student management with AI Assignment Generator

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import string
import requests
import os
import logging

# Setup logger
logger = logging.getLogger("DataHalo")

router = APIRouter(prefix="/lms", tags=["LMS"])

# These will be initialized by main.py
db = None
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Collections (will be initialized after db is set)
courses_collection = None
assignments_collection = None
submissions_collection = None
ai_learning_dataset = None
case_studies_collection = None

def init_lms(database):
    """Initialize LMS with database connection from main.py"""
    global db, courses_collection, assignments_collection, submissions_collection, ai_learning_dataset, case_studies_collection
    db = database
    courses_collection = db["courses"]
    assignments_collection = db["assignments"]
    submissions_collection = db["submissions"]
    ai_learning_dataset = db["ai_learning_dataset"]
    case_studies_collection = db["case_studies"]
    logger.info("LMS: Initialized with shared database connection")

# ==================== MODELS ==================== #

class Resource(BaseModel):
    type: str  # url, text, youtube, pdf
    content: str  # URL or text content
    title: str

class GenerateAssignmentRequest(BaseModel):
    resources: List[Resource]
    topic: str
    difficulty: str  # easy, medium, hard
    question_count: int = 5
    
class CreateCourseRequest(BaseModel):
    teacher_id: str
    title: str
    description: str
    subject: str  # Media Literacy, Journalism, Fact-Checking
    
class EnrollRequest(BaseModel):
    student_id: str
    invite_code: str
    
class CreateAssignmentRequest(BaseModel):
    course_id: str
    teacher_id: str
    title: str
    description: str
    instructions: str
    resources: List[dict]
    due_date: str
    points: int
    questions: List[dict]  # From AI generator or manual
    
class SubmitAssignmentRequest(BaseModel):
    assignment_id: str
    student_id: str
    student_name: str
    content: str
    answers: List[dict]
    
class GradeSubmissionRequest(BaseModel):
    submission_id: str
    grade: int
    feedback: str

# ==================== HELPER FUNCTIONS ==================== #

def generate_invite_code() -> str:
    """Generate a unique 6-character invite code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def extract_content_from_url(url: str) -> str:
    """Extract text content from URL"""
    try:
        # For YouTube, return video metadata
        if "youtube.com" in url or "youtu.be" in url:
            return f"YouTube Video: {url}"
        
        # For PDF files
        if url.lower().endswith('.pdf') or 'pdf' in url.lower():
            try:
                import io
                from pypdf import PdfReader
                
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    pdf_file = io.BytesIO(response.content)
                    reader = PdfReader(pdf_file)
                    
                    # Extract text from all pages (limit to first 20 pages)
                    text = ""
                    for page_num in range(min(20, len(reader.pages))):
                        page = reader.pages[page_num]
                        text += page.extract_text() + "\n\n"
                    
                    # Limit to 10000 characters
                    return text[:10000] if text.strip() else f"PDF: {url} (Could not extract text)"
            except Exception as pdf_error:
                logger.warning(f"PDF extraction failed: {pdf_error}")
                return f"PDF: {url} (Please paste the text content directly)"
        
        # For regular URLs, try to fetch content
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            # Try to extract clean text from HTML
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text from article/main content
                article = soup.find('article') or soup.find('main') or soup.find('body')
                if article:
                    text = article.get_text(separator='\n', strip=True)
                    # Clean up extra whitespace
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    text = '\n'.join(lines)
                    return text[:8000]  # Limit to 8000 chars
            except:
                pass
            
            # Fallback to raw HTML (limited)
            return response.text[:5000]
        
        return f"URL: {url}"
    except Exception as e:
        logger.error(f"URL extraction failed: {e}")
        return f"URL: {url}"

# ==================== AI ASSIGNMENT GENERATOR ==================== #

@router.post("/generate-assignment")
async def generate_assignment(request: GenerateAssignmentRequest):
    """
    🤖 JOURNALISM-SPECIFIC AI ASSIGNMENT GENERATOR WITH LEARNING
    
    Takes resources and generates assignments specifically for journalism education.
    Stores all inputs/outputs to build a learning dataset and improve over time.
    """
    try:
        if not NVIDIA_API_KEY:
            raise HTTPException(status_code=503, detail="AI service not configured")
        
        # STEP 0: Learn from past assignments (RAG approach)
        past_examples = list(ai_learning_dataset.find().sort("created_at", -1).limit(5))
        learning_context = ""
        
        if past_examples:
            learning_context = "\n\nLEARNING FROM PAST SUCCESSFUL ASSIGNMENTS:\n"
            for idx, example in enumerate(past_examples, 1):
                learning_context += f"\nExample {idx}:\n"
                learning_context += f"Topic: {example.get('topic', 'N/A')}\n"
                learning_context += f"Question Style: {example.get('sample_question', 'N/A')}\n"
                learning_context += f"Teacher Feedback: {example.get('teacher_notes', 'Effective')}\n"
        
        # Step 1: Process resources and extract content
        resource_summaries = []
        extraction_logs = []  # For debugging
        
        for idx, resource in enumerate(request.resources, 1):
            logger.info(f"Processing resource {idx}: {resource.title} (type: {resource.type})")
            
            if resource.type == "url":
                content = await extract_content_from_url(resource.content)
                logger.info(f"Extracted {len(content)} chars from URL: {resource.content[:100]}")
                extraction_logs.append(f"Resource {idx}: Extracted {len(content)} characters")
                
                # Use MORE content for better AI understanding (up to 3000 chars)
                resource_summaries.append(
                    f"===== RESOURCE {idx}: {resource.title} =====\n"
                    f"Type: Article/URL\n"
                    f"Source: {resource.content}\n"
                    f"CONTENT TO ANALYZE:\n{content[:3000]}\n"
                    f"===== END RESOURCE {idx} ====="
                )
                
            elif resource.type == "youtube":
                logger.info(f"YouTube video: {resource.content}")
                extraction_logs.append(f"Resource {idx}: YouTube video added")
                resource_summaries.append(
                    f"===== RESOURCE {idx}: {resource.title} =====\n"
                    f"Type: YouTube Video\n"
                    f"URL: {resource.content}\n"
                    f"INSTRUCTIONS: Create questions that ask students to watch this video and analyze its content.\n"
                    f"===== END RESOURCE {idx} ====="
                )
                
            elif resource.type == "text":
                logger.info(f"Text content: {len(resource.content)} chars")
                extraction_logs.append(f"Resource {idx}: {len(resource.content)} characters of text")
                resource_summaries.append(
                    f"===== RESOURCE {idx}: {resource.title} =====\n"
                    f"Type: Text Content\n"
                    f"CONTENT TO ANALYZE:\n{resource.content[:3000]}\n"
                    f"===== END RESOURCE {idx} ====="
                )
                
            elif resource.type == "pdf":
                content = await extract_content_from_url(resource.content)
                logger.info(f"Extracted {len(content)} chars from PDF: {resource.content[:100]}")
                extraction_logs.append(f"Resource {idx}: Extracted {len(content)} characters from PDF")
                
                resource_summaries.append(
                    f"===== RESOURCE {idx}: {resource.title} =====\n"
                    f"Type: PDF Document\n"
                    f"Source: {resource.content}\n"
                    f"CONTENT TO ANALYZE:\n{content[:3000]}\n"
                    f"===== END RESOURCE {idx} ====="
                )
        
        resources_text = "\n\n".join(resource_summaries)
        logger.info(f"Total resources processed: {len(resource_summaries)}")
        logger.info(f"Total text for AI: {len(resources_text)} characters")
        
        # Step 2: Build JOURNALISM-SPECIFIC AI prompt with STRONG resource emphasis
        prompt = f"""You are an EXPERT JOURNALISM EDUCATOR specializing in:
- Investigative Reporting
- Media Ethics & Standards
- Source Verification & Fact-Checking
- Bias Detection & Objectivity
- Narrative Construction
- Propaganda Analysis
- Digital Media Literacy

{learning_context}

🔴 CRITICAL INSTRUCTION: You MUST create questions that DIRECTLY reference and analyze the SPECIFIC content provided in the resources below. DO NOT create generic questions about the topic. Every question MUST require students to engage with the actual resource content.

RESOURCES PROVIDED (READ THESE CAREFULLY):
{resources_text}

ASSIGNMENT REQUIREMENTS:
- Topic: {request.topic}
- Difficulty Level: {request.difficulty}
- Number of Questions: {request.question_count}
- Subject: Journalism & Media Literacy

🔴 MANDATORY: Every question you create MUST:
1. Quote or reference specific content from the resources above
2. Ask students to analyze, evaluate, or apply concepts FROM the provided resources
3. Include phrases like "In Resource 1...", "According to the article...", "In the video..."
4. Test comprehension of the ACTUAL resource content, not generic knowledge

JOURNALISM-FOCUSED ASSIGNMENT STRUCTURE:
Create {request.question_count} questions that test PROFESSIONAL JOURNALISM SKILLS:
1. **Source Verification**: Can students identify credible sources and verify claims?
2. **Bias Detection**: Can they spot and analyze media bias, framing, and agenda?
3. **Fact-Checking**: Can they fact-check claims using multiple sources?
4. **Ethical Analysis**: Do they understand SPJ Code of Ethics and journalism standards?
5. **Investigative Thinking**: Can they ask probing questions and connect dots?
6. **Narrative Deconstruction**: Can they identify how stories are constructed and who benefits?
7. **Propaganda Analysis**: Can they spot manipulation techniques?
8. **Practical Application**: Real-world journalism scenarios

QUESTION TYPES TO USE:
- Analysis Questions: Analyze content from provided resources
- Essay Questions: Deep exploration of concepts
- Case Study: Apply concepts to real scenarios
- Critical Evaluation: Evaluate sources/claims
- Practical Exercise: Hands-on media literacy tasks

For each question, provide:
- Clear question text
- Expected response type (essay, analysis, short answer)
- Point value
- Detailed rubric (Excellent/Good/Fair/Poor criteria)
- Connection to specific resources

OUTPUT FORMAT (MUST BE VALID JSON):
{{
  "title": "Engaging assignment title related to {request.topic}",
  "description": "Brief overview of what students will learn",
  "instructions": "Clear step-by-step instructions for students including how to use the resources",
  "estimated_time": "Realistic time estimate (e.g., '45-60 minutes')",
  "learning_objectives": [
    "Specific objective 1",
    "Specific objective 2",
    "Specific objective 3"
  ],
  "questions": [
    {{
      "question_number": 1,
      "question_text": "Detailed question referencing specific resource",
      "question_type": "analysis|essay|short_answer|evaluation",
      "points": 10,
      "instructions": "Specific guidance for this question",
      "resource_reference": "Resource 1: [title]",
      "rubric": {{
        "excellent": "Criteria for 90-100% (specific expectations)",
        "good": "Criteria for 75-89% (specific expectations)",
        "fair": "Criteria for 60-74% (specific expectations)",
        "poor": "Criteria for below 60% (specific expectations)"
      }},
      "sample_answer_framework": "Guide for what a good answer should include"
    }}
  ],
  "total_points": {request.question_count * 10},
  "teacher_notes": "Tips for grading and common student misconceptions",
  "extension_activities": [
    "Optional advanced activity 1",
    "Optional advanced activity 2"
  ]
}}

JOURNALISM-SPECIFIC REQUIREMENTS:
- Reference REAL journalists, news outlets, and current events when applicable
- Use SPJ Code of Ethics as framework
- Include practical verification exercises (use Google, fact-checking sites)
- Ask students to compare coverage across different outlets (bias analysis)
- Include questions about SOURCE TRIANGULATION (verify with 3+ sources)
- Reference fact-checking organizations: Alt News, Boom Live, Snopes, FactCheck.org
- Use Indian journalism context when relevant
- Make rubrics based on professional journalism standards
- Include "Why does this matter?" context for each question
- Questions should build investigative thinking skills

🔴 RESOURCE-BASED QUESTION EXAMPLES (FOLLOW THIS PATTERN):
- BAD: "What is propaganda?" (Generic, not using resources)
- GOOD: "In Resource 1, the author states '[quote from resource]'. Analyze this statement and identify which propaganda technique is being used."

- BAD: "Explain fact-checking methods" (Generic)
- GOOD: "Using the fact-checking method described in Resource 2, verify the claim '[specific claim from resource]' using at least 3 sources."

- BAD: "What is media bias?" (Generic)
- GOOD: "Compare how Resource 1 and Resource 2 frame the same event differently. What specific language choices reveal bias?"

🔴 EVERY SINGLE QUESTION MUST:
- Start with "In Resource X..." or "According to [specific source]..." or "The article states..."
- Quote or paraphrase ACTUAL content from the resources
- Require students to READ the resources to answer
- Be IMPOSSIBLE to answer without accessing the provided resources

LEARNING OBJECTIVE:
Students should be able to work as fact-checkers, identify propaganda, verify sources, 
and understand how narratives are constructed in real journalism BY ANALYZING THE PROVIDED RESOURCES.

Generate the assignment now. Return ONLY valid JSON, no markdown, no explanations.

REMEMBER: If you create generic questions not tied to the specific resource content, the assignment will FAIL."""

        # Step 3: Call AI
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert assignment generator. Return ONLY valid JSON. No markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        # AI call with retry logic and increased timeout
        max_retries = 2
        for attempt in range(max_retries):
            try:
                logger.info(f"AI: Attempt {attempt + 1}/{max_retries} for assignment generation")
                response = requests.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120  # Increased to 120 seconds
                )
                response.raise_for_status()
                break
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"AI: Timeout, retrying in 5s...")
                    import time
                    time.sleep(5)
                else:
                    raise
        response.raise_for_status()
        
        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]
        
        # Step 4: Parse JSON response
        import json
        import re
        
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group(0)
            assignment_data = json.loads(json_str)
        else:
            assignment_data = json.loads(content)
        
        # Step 5: Add metadata
        assignment_data["resources_used"] = [
            {"title": r.title, "type": r.type, "content": r.content}
            for r in request.resources
        ]
        assignment_data["generated_at"] = datetime.utcnow().isoformat()
        assignment_data["generation_params"] = {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "question_count": request.question_count
        }
        
        # STEP 6: Store in LEARNING DATASET for continuous improvement
        learning_entry = {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "question_count": request.question_count,
            "resources_summary": [
                {"title": r.title, "type": r.type} for r in request.resources
            ],
            "sample_question": assignment_data["questions"][0]["question_text"] if assignment_data.get("questions") else "",
            "learning_objectives": assignment_data.get("learning_objectives", []),
            "teacher_notes": assignment_data.get("teacher_notes", ""),
            "created_at": datetime.utcnow(),
            "ai_model": "meta/llama-3.1-70b-instruct",
            "quality_score": None,  # Teacher can rate later
            "feedback": None,  # Teacher feedback for improvement
            "used_count": 0,  # Track how many times this pattern is used
            "journalism_focus": True
        }
        
        try:
            ai_learning_dataset.insert_one(learning_entry)
            logger.info(f"✅ Stored assignment in learning dataset. Total entries: {ai_learning_dataset.count_documents({})}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to store in learning dataset: {e}")
        
        return {
            "status": "success",
            "assignment": assignment_data,
            "message": f"Generated {len(assignment_data['questions'])} questions",
            "learning_dataset_size": ai_learning_dataset.count_documents({}),
            "ai_improving": True,
            "extraction_info": extraction_logs,  # Show what was extracted
            "total_content_chars": len(resources_text)
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment generation failed: {str(e)}")

# ==================== COURSE MANAGEMENT ==================== #

@router.post("/courses/create")
async def create_course(request: CreateCourseRequest):
    """Teacher creates a new course (class)"""
    try:
        invite_code = generate_invite_code()
        
        course = {
            "teacher_id": request.teacher_id,
            "title": request.title,
            "description": request.description,
            "subject": request.subject,
            "invite_code": invite_code,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "students": [],
            "resources": [],
            "assignment_count": 0,
            "student_count": 0
        }
        
        result = courses_collection.insert_one(course)
        course["_id"] = str(result.inserted_id)
        
        return {
            "status": "success",
            "course": course,
            "invite_code": invite_code,
            "message": f"Course created! Share invite code: {invite_code}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/courses/teacher/{teacher_id}")
async def get_teacher_courses(teacher_id: str):
    """Get all courses for a teacher"""
    try:
        courses = list(courses_collection.find({"teacher_id": teacher_id}).sort("updated_at", -1))
        
        for course in courses:
            course["_id"] = str(course["_id"])
            # Add stats
            course["assignment_count"] = assignments_collection.count_documents({"course_id": str(course["_id"])})
            course["student_count"] = len(course.get("students", []))
        
        return {
            "status": "success",
            "courses": courses,
            "count": len(courses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/classes/{class_id}")
async def get_class(class_id: str):
    """Get specific class details"""
    try:
        from bson import ObjectId
        
        course = courses_collection.find_one({"_id": ObjectId(class_id)})
        
        if not course:
            raise HTTPException(status_code=404, detail="Class not found")
        
        course["_id"] = str(course["_id"])
        course["assignment_count"] = assignments_collection.count_documents({"course_id": class_id})
        course["student_count"] = len(course.get("students", []))
        
        return {
            "status": "success",
            "class": course
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/courses/student/{student_id}")
async def get_student_courses(student_id: str):
    """Get all enrolled courses for a student"""
    try:
        courses = list(courses_collection.find({"students": student_id}).sort("updated_at", -1))
        
        for course in courses:
            course["_id"] = str(course["_id"])
        
        return {
            "status": "success",
            "courses": courses,
            "count": len(courses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enroll")
async def enroll_student(request: EnrollRequest):
    """Student enrolls in a course using invite code"""
    try:
        course = courses_collection.find_one({"invite_code": request.invite_code})
        
        if not course:
            raise HTTPException(status_code=404, detail="Invalid invite code")
        
        # Check if already enrolled
        if request.student_id in course.get("students", []):
            return {
                "status": "already_enrolled",
                "message": "You are already enrolled in this course"
            }
        
        # Add student to course
        courses_collection.update_one(
            {"invite_code": request.invite_code},
            {
                "$push": {"students": request.student_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "status": "success",
            "course_title": course["title"],
            "message": "Successfully enrolled!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ASSIGNMENT MANAGEMENT ==================== #

@router.post("/assignments/create")
async def create_assignment(request: CreateAssignmentRequest):
    """Teacher creates an assignment (manual or AI-generated)"""
    try:
        from bson import ObjectId
        
        assignment = {
            "course_id": request.course_id,
            "teacher_id": request.teacher_id,
            "title": request.title,
            "description": request.description,
            "instructions": request.instructions,
            "resources": request.resources,
            "questions": request.questions,
            "due_date": request.due_date,
            "points": request.points,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "submission_count": 0,
            "graded_count": 0
        }
        
        result = assignments_collection.insert_one(assignment)
        assignment["_id"] = str(result.inserted_id)
        
        # Update course assignment count (convert to ObjectId if it's a string)
        try:
            course_id_obj = ObjectId(request.course_id) if isinstance(request.course_id, str) else request.course_id
            courses_collection.update_one(
                {"_id": course_id_obj},
                {"$inc": {"assignment_count": 1}}
            )
        except Exception as e:
            logger.warning(f"Failed to update course assignment count: {e}")
        
        return {
            "status": "success",
            "assignment": assignment,
            "message": "Assignment created successfully!"
        }
    except Exception as e:
        logger.error(f"Assignment creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/course/{course_id}")
async def get_course_assignments(course_id: str):
    """Get all assignments for a course"""
    try:
        assignments = list(assignments_collection.find({"course_id": course_id}).sort("created_at", -1))
        
        for assignment in assignments:
            assignment["_id"] = str(assignment["_id"])
            assignment["submission_count"] = submissions_collection.count_documents({"assignment_id": str(assignment["_id"])})
        
        return {
            "status": "success",
            "assignments": assignments,
            "count": len(assignments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SUBMISSION MANAGEMENT ==================== #

@router.post("/submissions/submit")
async def submit_assignment(request: SubmitAssignmentRequest):
    """Student submits an assignment"""
    try:
        submission = {
            "assignment_id": request.assignment_id,
            "student_id": request.student_id,
            "student_name": request.student_name,
            "content": request.content,
            "answers": request.answers,
            "submitted_at": datetime.utcnow(),
            "grade": None,
            "feedback": None,
            "graded_at": None,
            "status": "submitted"
        }
        
        result = submissions_collection.insert_one(submission)
        submission["_id"] = str(result.inserted_id)
        
        return {
            "status": "success",
            "submission": submission,
            "message": "Assignment submitted successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submissions/grade")
async def grade_submission(request: GradeSubmissionRequest):
    """Teacher grades a submission"""
    try:
        from bson import ObjectId
        
        result = submissions_collection.update_one(
            {"_id": ObjectId(request.submission_id)},
            {
                "$set": {
                    "grade": request.grade,
                    "feedback": request.feedback,
                    "graded_at": datetime.utcnow(),
                    "status": "graded"
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return {
            "status": "success",
            "message": "Submission graded successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submissions/assignment/{assignment_id}")
async def get_assignment_submissions(assignment_id: str):
    """Get all submissions for an assignment (teacher view)"""
    try:
        submissions = list(submissions_collection.find({"assignment_id": assignment_id}).sort("submitted_at", -1))
        
        for submission in submissions:
            submission["_id"] = str(submission["_id"])
        
        return {
            "status": "success",
            "submissions": submissions,
            "count": len(submissions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submissions/student/{student_id}")
async def get_student_submissions(student_id: str):
    """Get all submissions for a student"""
    try:
        submissions = list(submissions_collection.find({"student_id": student_id}).sort("submitted_at", -1))
        
        for submission in submissions:
            submission["_id"] = str(submission["_id"])
        
        return {
            "status": "success",
            "submissions": submissions,
            "count": len(submissions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== NEWS API INTEGRATION ==================== #

@router.get("/news/top-stories")
async def get_top_stories():
    """
    Fetch top news stories for student investigation.
    Focuses on educational, credible sources with full article URLs.
    """
    try:
        # CURATED EDUCATIONAL NEWS - Always available as fallback
        curated_stories = [
            {
                "title": "How Fact-Checkers Verify Breaking News in Real-Time",
                "description": "An inside look at the methods professional fact-checkers use to verify breaking news stories, including cross-referencing sources and identifying manipulated images.",
                "source": "Poynter Institute",
                "url": "https://www.poynter.org/fact-checking/",
                "category": "media-literacy",
                "keywords": ["fact-checking", "verification", "journalism"]
            },
            {
                "title": "The Rise of AI-Generated News: Opportunities and Ethical Concerns",
                "description": "Exploring how AI is transforming journalism, from automated reporting to personalized news feeds, and the ethical questions this raises.",
                "source": "Columbia Journalism Review",
                "url": "https://www.cjr.org/",
                "category": "technology",
                "keywords": ["AI", "journalism", "ethics"]
            },
            {
                "title": "Identifying Propaganda Techniques in Modern Media Coverage",
                "description": "A comprehensive guide to recognizing propaganda methods used in news coverage, including loaded language, bandwagon appeals, and selective reporting.",
                "source": "Media Literacy Now",
                "url": "https://medialiteracynow.org/",
                "category": "media-analysis",
                "keywords": ["propaganda", "bias", "media-literacy"]
            },
            {
                "title": "Climate Change Reporting: Balancing Urgency with Accuracy",
                "description": "How journalists navigate the challenge of reporting on climate change while maintaining objectivity and avoiding both alarmism and denialism.",
                "source": "NPR",
                "url": "https://www.npr.org/sections/science/",
                "category": "environment",
                "keywords": ["climate", "science-reporting", "journalism-ethics"]
            },
            {
                "title": "The Economics of News: Why Local Journalism is Disappearing",
                "description": "Investigating the business model crisis affecting local news outlets and what it means for democracy and community accountability.",
                "source": "ProPublica",
                "url": "https://www.propublica.org/",
                "category": "business",
                "keywords": ["local-news", "journalism-economics", "democracy"]
            }
        ]
        
        # FOR EDUCATIONAL PURPOSES: Use curated journalism-focused stories
        # This ensures students always get relevant, educational content
        stories = curated_stories
        logger.info("Using curated educational journalism stories")
        
        # Ensure all stories have required fields
        for story in stories:
            if not story.get("url"):
                story["url"] = "https://www.example.com"  # Fallback
            if not story.get("description"):
                story["description"] = "Click to read the full article."
            if not story.get("source"):
                story["source"] = "News Source"
        
        return {
            "status": "success",
            "stories": stories[:5],  # Return exactly 5 stories
            "count": len(stories[:5]),
            "fetched_at": datetime.utcnow().isoformat(),
            "source_type": "api" if NEWS_API_KEY and len(stories) > 3 else "curated"
        }
    except Exception as e:
        logger.error(f"News fetch error: {str(e)}")
        # Return curated stories as ultimate fallback
        return {
            "status": "success",
            "stories": curated_stories[:5],
            "count": 5,
            "fetched_at": datetime.utcnow().isoformat(),
            "source_type": "curated_fallback"
        }

# ==================== CASE STUDIES ARCHIVE ==================== #

class CaseStudySubmission(BaseModel):
    student_id: str
    student_name: str
    story_title: str
    story_url: str
    analysis_content: str
    topic: str
    class_id: Optional[str] = None
    teacher_id: Optional[str] = None

@router.post("/case-studies/submit")
async def submit_case_study(submission: CaseStudySubmission):
    """Submit student analysis as a case study"""
    try:
        case_study = {
            "student_id": submission.student_id,
            "student_name": submission.student_name,
            "story_title": submission.story_title,
            "story_url": submission.story_url,
            "analysis_content": submission.analysis_content,
            "topic": submission.topic,
            "class_id": submission.class_id,
            "teacher_id": submission.teacher_id,
            "submitted_at": datetime.utcnow(),
            "grade": None,
            "feedback": None,
            "published": False,  # Teacher can publish to make it visible to all
            "views": 0,
            "status": "pending_review"
        }
        
        result = case_studies_collection.insert_one(case_study)
        case_study["_id"] = str(result.inserted_id)
        
        return {
            "status": "success",
            "case_study": case_study,
            "message": "Analysis submitted successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journalists/all")
async def get_all_journalists():
    """Get all analyzed journalists with their full case study data"""
    try:
        # Fetch from journalists collection (created from homepage case study generator)
        journalists_raw = list(db["journalists"].find().sort("analysis_timestamp", -1).limit(50))
        
        journalists = []
        for journalist in journalists_raw:
            journalist["_id"] = str(journalist["_id"])
            
            # Extract aiProfile which contains all the case study data
            ai_profile = journalist.get("aiProfile", {})
            
            # Extract biography/bio
            bio = (ai_profile.get("biography") or 
                   ai_profile.get("summary") or 
                   ai_profile.get("overview") or
                   "Journalist profile")
            
            # Extract notable works/major stories
            notable_works_raw = (ai_profile.get("notableWorks") or
                                ai_profile.get("major_stories") or
                                ai_profile.get("notable_works") or
                                [])
            
            # Convert notable works to simple strings if they're objects
            notable_works = []
            for work in notable_works_raw:
                if isinstance(work, dict):
                    notable_works.append(work.get("title", str(work)))
                else:
                    notable_works.append(str(work))
            
            # Extract main topics as specializations
            main_topics = ai_profile.get("mainTopics", [])
            if not main_topics:
                main_topics = [ai_profile.get("category", "General Journalism")]
            
            # Extract credibility score safely
            cred_score_obj = ai_profile.get("credibilityScore", {})
            if isinstance(cred_score_obj, dict):
                cred_score = cred_score_obj.get("overall", cred_score_obj.get("score", 85))
            elif isinstance(cred_score_obj, (int, float)):
                cred_score = cred_score_obj
            else:
                cred_score = 85
            
            # Extract lessons from different fields
            lessons = []
            ethical_assessment = ai_profile.get("ethicalAssessment", "")
            if ethical_assessment and len(ethical_assessment) > 10:
                lessons.append(f"Ethics: {ethical_assessment[:70]}...")
            if ai_profile.get("writingTone"):
                lessons.append(f"Style: {ai_profile.get('writingTone')}")
            if ai_profile.get("ideologicalBias"):
                lessons.append(f"Bias: {ai_profile.get('ideologicalBias')}")
            
            if not lessons:
                lessons = ["Professional journalism", "Ethical reporting", "Source verification"]
            

            # Extract profile image from various sources
            profile_image = None
            scraped_data = journalist.get("scrapedData", {})
            if isinstance(scraped_data, dict):
                profile_image = scraped_data.get("imageUrl") or scraped_data.get("image")
            if not profile_image:
                profile_image = ai_profile.get("profileImage") or ai_profile.get("image")
            
            journalist_data = {
                "_id": journalist["_id"],
                "name": journalist.get("name", "Unknown Journalist"),
                "bio": bio[:200] + "..." if len(bio) > 200 else bio,  # Truncate for gallery
                "analysis": ai_profile,  # Full AI profile for detailed view
                "credibility_score": cred_score,
                "article_count": journalist.get("articlesAnalyzed", 0),
                "awards": len(ai_profile.get("awards", [])),
                "region": (ai_profile.get("region") or 
                          ai_profile.get("country") or 
                          "International"),
                "country": ai_profile.get("country", "International"),
                "verified": True,  # All analyzed journalists are verified
                "category": main_topics[0] if main_topics else "General Journalism",
                "specializations": main_topics[:3],  # Top 3 topics
                "key_work": (notable_works[0] if notable_works else "Various investigations"),
                "lessons": lessons[:3],  # Top 3 lessons
                "major_stories": notable_works[:5],  # Top 5 stories
                "impact": ai_profile.get("influence", ""),
                "writing_style": ai_profile.get("writingTone", ""),
                "ethical_approach": ai_profile.get("ethicalAssessment", "")[:150] if ai_profile.get("ethicalAssessment") else "",
                "ideology": ai_profile.get("ideologicalBias", ""),
                "controversies": ai_profile.get("controversies", []),
                "created_at": journalist.get("analysis_timestamp"),
                "image": profile_image,  # Add profile image URL
            }
            journalists.append(journalist_data)
        
        logger.info(f"SUCCESS: Fetched {len(journalists)} journalists with case study data")
        
        return {
            "status": "success",
            "journalists": journalists,
            "count": len(journalists)
        }
    except Exception as e:
        logger.error(f"ERROR: Failed to fetch journalists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journalists/{journalist_name}")
async def get_journalist_case_study(journalist_name: str):
    """Get full case study for a specific journalist"""
    try:
        # Find journalist by name in the journalists collection
        journalist = db["journalists"].find_one({"name": {"$regex": journalist_name, "$options": "i"}})
        
        if not journalist:
            raise HTTPException(status_code=404, detail="Journalist not found")
        
        journalist["_id"] = str(journalist["_id"])
        
        return {
            "status": "success",
            "journalist": journalist
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Failed to fetch journalist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case-studies/published")
async def get_published_case_studies():
    """Get published case studies for learning"""
    try:
        # Get top 20 published case studies with highest grades
        case_studies = list(
            case_studies_collection.find(
                {"published": True, "grade": {"$ne": None}}
            ).sort([("grade", -1), ("views", -1)]).limit(20)
        )
        
        for study in case_studies:
            study["_id"] = str(study["_id"])
            # Anonymize student info
            study["student_name"] = "Anonymous Student"
            study["student_id"] = "***"
        
        return {
            "status": "success",
            "case_studies": case_studies,
            "count": len(case_studies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case-studies/teacher/{teacher_id}")
async def get_teacher_case_studies(teacher_id: str):
    """Get case studies submitted to teacher for review"""
    try:
        case_studies = list(
            case_studies_collection.find(
                {"teacher_id": teacher_id}
            ).sort("submitted_at", -1)
        )
        
        for study in case_studies:
            study["_id"] = str(study["_id"])
        
        return {
            "status": "success",
            "case_studies": case_studies,
            "count": len(case_studies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/case-studies/grade/{study_id}")
async def grade_case_study(study_id: str, grade: int, feedback: str, publish: bool = False):
    """Teacher grades and optionally publishes case study"""
    try:
        from bson import ObjectId
        
        update_data = {
            "grade": grade,
            "feedback": feedback,
            "graded_at": datetime.utcnow(),
            "status": "graded"
        }
        
        if publish:
            update_data["published"] = True
        
        result = case_studies_collection.update_one(
            {"_id": ObjectId(study_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Case study not found")
        
        return {
            "status": "success",
            "message": "Case study graded successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
