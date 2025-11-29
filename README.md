# DataHalo - Media Literacy Education Platform

A comprehensive AI-powered platform for teaching journalism and media literacy, featuring
intelligent assignment generation, classroom management, and professional analysis tools.

## Overview

DataHalo is a modern educational platform designed specifically for journalism and media literacy
education. It combines an intelligent Learning Management System (LMS) with advanced AI-powered
tools to help educators teach critical media analysis skills and students develop fact-checking,
bias detection, and source verification capabilities.

## Key Features

### AI-Powered Assignment Generation

- **Intelligent Content Analysis**: Extracts and analyzes content from PDFs, articles, and YouTube
  videos
- **Journalism-Specific Questions**: Generates assignments focused on propaganda analysis, bias
  detection, fact-checking, and media ethics
- **Learning AI System**: Improves over time by learning from previous assignments and teacher
  feedback
- **Customizable Parameters**: Configure difficulty levels, question counts, target audiences, and
  learning goals
- **Resource Integration**: Automatically creates questions that reference specific provided
  materials

### Complete Learning Management System

- **Class Management**: Create and manage multiple classes with unique invite codes
- **Assignment Workflow**: Full lifecycle from creation to submission to grading
- **Role-Based Access**: Separate interfaces for teachers and students
- **Real-Time Updates**: Track assignment submissions and grades in real-time
- **File Management**: Upload and distribute PDFs and other educational resources

### Professional Analysis Tools

- **Journalist Credibility Analyzer**: Evaluate journalist backgrounds, bias history, and
  credibility
- **Narrative Tracker**: Monitor how stories evolve across different media outlets over time
- **Article Quality Assessment**: Analyze articles for journalistic standards and quality metrics
- **AI Tutor**: Interactive assistant for answering media literacy questions

### Authentication & Security

- Firebase authentication with email/password and Google sign-in
- Role-based access control (Teacher/Student)
- Secure user profile management
- Protected routes and data access

## Technology Stack

### Frontend

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Shadcn/ui components with Tailwind CSS
- **State Management**: React Query for server state
- **Routing**: React Router v6
- **Icons**: Lucide React
- **Notifications**: Sonner for toast notifications

### Backend

- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: Firebase Admin SDK
- **AI Integration**: NVIDIA NIM API (Llama 3.1 70B)
- **Content Extraction**: PyPDF, BeautifulSoup4, Requests

### Infrastructure

- **Hosting**: Configurable for cloud deployment
- **Database**: MongoDB Atlas recommended
- **File Storage**: Base64 encoding (upgradeable to cloud storage)
- **Environment Management**: Python dotenv, Vite environment variables

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- MongoDB instance (local or Atlas)
- Firebase project
- NVIDIA API key (for AI features)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/datahalo.git
cd datahalo
```

#### 2. Frontend Setup

```bash
cd datahalo
npm install
```

Create `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

#### 3. Backend Setup

```bash
cd Backend
pip install -r requirements.txt
```

Create `.env` file in the Backend directory:

```env
MONGODB_URI=mongodb://localhost:27017/
NVIDIA_API_KEY=your_nvidia_api_key
FIREBASE_CREDENTIALS_PATH=path/to/serviceAccountKey.json
```

#### 4. Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication (Email/Password and Google)
3. Enable Firestore Database
4. Download service account key for backend
5. Copy web app credentials for frontend

#### 5. MongoDB Setup

Option A - Local Installation:

```bash
# Install MongoDB Community Edition
# https://docs.mongodb.com/manual/installation/

# Start MongoDB service
mongod --dbpath /path/to/data/directory
```

Option B - MongoDB Atlas (Recommended):

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Update MONGODB_URI in backend .env

### Running the Application

#### Start Backend Server

```bash
cd Backend
python main.py
```

Server will start at `http://localhost:8000`

#### Start Frontend Development Server

```bash
cd datahalo
npm run dev
```

Application will be available at `http://localhost:5173`

## Usage Guide

### For Teachers

#### Creating a Class

1. Sign up with teacher role
2. Navigate to Dashboard
3. Click "My Classes" or use Quick Actions
4. Click "Create Class"
5. Enter class details and get invite code
6. Share invite code with students

#### Generating AI Assignments

1. Go to Dashboard
2. Click "AI Generator"
3. Add resources (PDFs, articles, videos)
4. Configure assignment parameters
5. Generate assignment
6. Review and publish to class

#### Managing Students

1. Open class from "My Classes"
2. Use "Students" tab to view enrolled students
3. Share invite code for new enrollments
4. Track student submissions in "Assignments" tab

### For Students

#### Joining a Class

1. Sign up with student role
2. Click "Enrolled Classes"
3. Click "Join Class"
4. Enter teacher-provided invite code

#### Submitting Assignments

1. Navigate to class
2. View assignment details
3. Click "Submit Assignment"
4. Write response addressing all questions
5. Submit before due date

#### Checking Grades

1. Open class
2. Go to "Grades" tab
3. View all graded assignments with scores and feedback

## API Documentation

### LMS Endpoints

#### Classes

- `POST /lms/courses/create` - Create a new class
- `GET /lms/courses/teacher/{teacher_id}` - Get teacher's classes
- `GET /lms/courses/student/{student_id}` - Get student's classes
- `POST /lms/enroll` - Enroll student in class
- `GET /lms/classes/{class_id}` - Get class details

#### Assignments

- `POST /lms/generate-assignment` - Generate AI assignment
- `POST /lms/assignments/create` - Create assignment manually
- `GET /lms/assignments/course/{course_id}` - Get class assignments

#### Submissions

- `POST /lms/submissions/submit` - Submit assignment
- `GET /lms/submissions/student/{student_id}` - Get student submissions
- `POST /lms/submissions/grade` - Grade submission

### Analysis Tools Endpoints

- `POST /analyze_journalist` - Analyze journalist credibility
- `POST /track_narrative` - Track narrative evolution
- `POST /analyze_article` - Analyze article quality

## Project Structure

```
datahalo/
├── Backend/
│   ├── main.py                 # FastAPI application
│   ├── lms_endpoints.py        # LMS API routes
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Backend environment variables
├── src/
│   ├── components/
│   │   ├── ui/                 # Shadcn UI components
│   │   ├── AITutorV2.tsx      # AI tutor component
│   │   └── ProtectedRoute.tsx # Route protection
│   ├── contexts/
│   │   └── AuthContext.tsx    # Authentication context
│   ├── pages/
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   ├── ClassesPage.tsx    # Classes list
│   │   ├── ClassroomPage.tsx  # Individual classroom
│   │   ├── Login.tsx          # Authentication
│   │   └── Signup.tsx         # Registration
│   ├── lib/
│   │   └── firebase.ts        # Firebase configuration
│   └── App.tsx                # Main application
├── public/                    # Static assets
└── package.json              # Frontend dependencies
```

## Database Schema

### MongoDB Collections

#### users (Firebase Firestore)

```javascript
{
  uid: string,
  email: string,
  displayName: string,
  role: "student" | "teacher",
  institution: string,
  createdAt: timestamp
}
```

#### courses

```javascript
{
  _id: ObjectId,
  teacher_id: string,
  title: string,
  description: string,
  subject: string,
  invite_code: string,
  students: [string],
  created_at: timestamp
}
```

#### assignments

```javascript
{
  _id: ObjectId,
  course_id: string,
  teacher_id: string,
  title: string,
  description: string,
  instructions: string,
  questions: [Question],
  resources: [Resource],
  due_date: timestamp,
  points: number
}
```

#### submissions

```javascript
{
  _id: ObjectId,
  assignment_id: string,
  student_id: string,
  student_name: string,
  content: string,
  submitted_at: timestamp,
  grade: number | null,
  feedback: string | null
}
```

#### ai_learning_dataset

```javascript
{
  topic: string,
  difficulty: string,
  resources_summary: [Resource],
  learning_objectives: [string],
  created_at: timestamp,
  quality_score: number | null
}
```

## Configuration

### Environment Variables

#### Frontend (.env)

- `VITE_API_URL` - Backend API base URL
- `VITE_FIREBASE_*` - Firebase configuration

#### Backend (.env)

- `MONGODB_URI` - MongoDB connection string
- `NVIDIA_API_KEY` - NVIDIA NIM API key for AI features
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase service account key

## Deployment

### Frontend (Vercel/Netlify)

1. Build the application:

```bash
npm run build
```

2. Deploy the `dist` folder to your hosting provider

3. Configure environment variables in hosting dashboard

### Backend (Railway/Heroku/AWS)

1. Install production dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables

3. Deploy using platform-specific commands

4. Ensure MongoDB is accessible from deployment

## Best Practices

### Security

- Never commit `.env` files to version control
- Use environment variables for all sensitive data
- Implement rate limiting on API endpoints
- Regularly update dependencies
- Use HTTPS in production

### Performance

- Implement caching for frequently accessed data
- Use MongoDB indexes for common queries
- Optimize image and file sizes
- Implement lazy loading for large components
- Use pagination for large data sets

### Code Quality

- Follow TypeScript strict mode
- Use ESLint and Prettier for code formatting
- Write comprehensive error handling
- Add loading states for async operations
- Include proper TypeScript types

## Troubleshooting

### Common Issues

**Frontend not connecting to backend**

- Check VITE_API_URL in frontend .env
- Verify backend is running on correct port
- Check CORS settings in FastAPI

**MongoDB connection failed**

- Verify MongoDB is running
- Check MONGODB_URI format
- Ensure network access for Atlas

**Firebase authentication errors**

- Verify Firebase credentials are correct
- Check Firebase console for enabled auth methods
- Ensure service account key is valid

**AI generation not working**

- Verify NVIDIA_API_KEY is valid
- Check API rate limits
- Review backend logs for errors

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Use TypeScript for frontend
- Follow PEP 8 for Python backend
- Write descriptive commit messages
- Add comments for complex logic
- Update documentation for new features

## Roadmap

### Version 2.0 (Planned)

- Multi-chat AI tutor with saved conversations
- Real-time fact-checking API integration
- Rich text editor with citation support
- Peer review system for assignments
- Advanced analytics dashboard

### Version 2.1

- Mobile application (React Native)
- Video lesson integration
- Discussion forums
- Gamification with badges and achievements
- Live collaboration tools

### Version 3.0

- Plagiarism detection
- Automated grading suggestions
- Email notification system
- Calendar integration
- Advanced reporting and analytics

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:

- Open an issue on GitHub
- Contact the development team
- Check documentation for common solutions

## Acknowledgments

- Built with React and FastAPI
- UI components from Shadcn/ui
- AI powered by NVIDIA NIM
- Icons from Lucide React
- Inspired by modern LMS platforms and journalism education needs

## Authors

DataHalo Development Team

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready
