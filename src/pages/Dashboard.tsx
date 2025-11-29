// Dashboard Page (Student & Teacher with AI Assignment Generator)
import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  LogOut,
  GraduationCap,
  BookOpen,
  FileText,
  TrendingUp,
  Award,
  Search,
  BarChart3,
  Users,
  Calendar,
  Home,
  Sparkles,
  Loader2,
  Plus,
  X,
  Link as LinkIcon,
  Youtube,
  FileUp,
  CheckCircle2,
  Brain,
  Send,
  ExternalLink,
  Eye
} from "lucide-react";
import AITutorV2, { AITutorButton } from "@/components/AITutorV2";
import { toast } from "sonner";
import axios from "axios";

interface Resource {
  type: "url" | "youtube" | "text" | "pdf";
  content: string;
  title: string;
}

export default function Dashboard() {
  const { currentUser, userProfile, logout, loading } = useAuth();
  const navigate = useNavigate();
  const [aiTutorOpen, setAiTutorOpen] = useState(false);
  
  // AI Assignment Generator State
  const [showAIGenerator, setShowAIGenerator] = useState(false);
  const [resources, setResources] = useState<Resource[]>([]);
  const [currentResource, setCurrentResource] = useState<Resource>({
    type: "url",
    content: "",
    title: ""
  });
  const [aiTopic, setAiTopic] = useState("");
  const [aiDifficulty, setAiDifficulty] = useState("medium");
  const [aiQuestionCount, setAiQuestionCount] = useState(5);
  const [generatedAssignment, setGeneratedAssignment] = useState<any>(null);
  const [generating, setGenerating] = useState(false);
  const [datasetSize, setDatasetSize] = useState(0);
  
  // Additional teacher inputs for better AI generation
  const [targetAudience, setTargetAudience] = useState("");
  const [learningGoal, setLearningGoal] = useState("");
  const [assignmentContext, setAssignmentContext] = useState("");
  
  // Publish Assignment
  const [showPublish, setShowPublish] = useState(false);
  const [publishData, setPublishData] = useState({
    classId: "",
    dueDate: "",
  });
  const [classes, setClasses] = useState<any[]>([]);
  const [publishing, setPublishing] = useState(false);

  // News Integration
  const [topStories, setTopStories] = useState<any[]>([]);
  const [loadingNews, setLoadingNews] = useState(false);

  // Case Studies
  const [caseStudies, setCaseStudies] = useState<any[]>([]);
  const [loadingCaseStudies, setLoadingCaseStudies] = useState(false);

  // Teacher: Student Article Submissions
  const [submittedArticles, setSubmittedArticles] = useState<any[]>([]);
  const [loadingArticles, setLoadingArticles] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // Define role checks early (before useEffect)
  const isStudent = userProfile?.role === "student";
  const isTeacher = userProfile?.role === "teacher";

  // Handle authentication redirect (only after auth is loaded)
  useEffect(() => {
    if (!loading && (!currentUser || !userProfile)) {
      navigate("/login");
    }
  }, [currentUser, userProfile, navigate, loading]);

  useEffect(() => {
    if (isTeacher && currentUser) {
      loadTeacherClasses();
      loadSubmittedArticles();
    }
  }, [isTeacher, currentUser]);

  useEffect(() => {
    if (isStudent && currentUser) {
      loadTopStories();
      loadCaseStudies();
    }
  }, [isStudent, currentUser]);

  const loadTopStories = async () => {
    setLoadingNews(true);
    try {
      // Check if we have cached stories from today
      const cacheKey = 'datahalo_daily_news';
      const cacheTimestampKey = 'datahalo_daily_news_timestamp';
      const cachedStories = localStorage.getItem(cacheKey);
      const cachedTimestamp = localStorage.getItem(cacheTimestampKey);
      
      // Get today's date as string
      const today = new Date().toDateString();
      
      // Use cached stories if they're from today
      if (cachedStories && cachedTimestamp === today) {
        console.log("Using cached daily news stories");
        setTopStories(JSON.parse(cachedStories));
        setLoadingNews(false);
        return;
      }
      
      // Otherwise, fetch fresh stories
      console.log("Fetching fresh daily news stories");
      const response = await axios.get(`${API_URL}/lms/news/top-stories`);
      if (response.data.status === "success") {
        const stories = response.data.stories.slice(0, 3); // Top 3 stories
        setTopStories(stories);
        
        // Cache the stories for the whole day
        localStorage.setItem(cacheKey, JSON.stringify(stories));
        localStorage.setItem(cacheTimestampKey, today);
        
        console.log("Cached daily news stories for", today);
      }
    } catch (error) {
      console.error("Failed to load news:", error);
      // Fallback to placeholder if API fails
      setTopStories([
        { 
          title: "Loading real news stories...",
          source: "Fetching from multiple sources",
          category: "Loading",
          url: "#"
        }
      ]);
    } finally {
      setLoadingNews(false);
    }
  };

  const loadCaseStudies = async () => {
    setLoadingCaseStudies(true);
    try {
      const response = await axios.get(`${API_URL}/lms/case-studies/published`);
      if (response.data.status === "success") {
        setCaseStudies(response.data.case_studies.slice(0, 5)); // Latest 5
      }
    } catch (error) {
      console.error("Failed to load case studies");
    } finally {
      setLoadingCaseStudies(false);
    }
  };

  const loadTeacherClasses = async () => {
    try {
      const response = await axios.get(`${API_URL}/lms/courses/teacher/${currentUser?.uid}`);
      setClasses(response.data.courses || []);
    } catch (error) {
      console.error("Failed to load classes");
    }
  };

  const loadSubmittedArticles = async () => {
    setLoadingArticles(true);
    try {
      const response = await axios.get(`${API_URL}/lms/case-studies/teacher/${currentUser?.uid}`);
      if (response.data.status === "success") {
        setSubmittedArticles(response.data.case_studies || []);
      }
    } catch (error) {
      console.error("Failed to load submitted articles");
    } finally {
      setLoadingArticles(false);
    }
  };

  const gradeArticle = async (studyId: string, grade: number, feedback: string) => {
    try {
      await axios.post(`${API_URL}/lms/case-studies/grade/${studyId}`, null, {
        params: { grade, feedback, publish: false }
      });
      toast.success("Article graded successfully!");
      loadSubmittedArticles(); // Reload
    } catch (error) {
      toast.error("Failed to grade article");
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Logged out successfully");
      navigate("/login");
    } catch (error) {
      toast.error("Failed to log out");
    }
  };

  const addResource = () => {
    if (!currentResource.title || !currentResource.content) {
      toast.error("Please fill resource details");
      return;
    }
    setResources([...resources, currentResource]);
    setCurrentResource({ type: "url", content: "", title: "" });
    toast.success("Resource added!");
  };

  const removeResource = (index: number) => {
    setResources(resources.filter((_, i) => i !== index));
  };

  const generateAssignment = async () => {
    if (resources.length === 0) {
      toast.error("Please add at least one resource");
      return;
    }
    if (!aiTopic) {
      toast.error("Please enter a topic");
      return;
    }

    setGenerating(true);
    try {
      // Build enhanced topic with context
      let enhancedTopic = aiTopic;
      if (targetAudience) {
        enhancedTopic += ` | Target Audience: ${targetAudience}`;
      }
      if (learningGoal) {
        enhancedTopic += ` | Learning Goal: ${learningGoal}`;
      }
      if (assignmentContext) {
        enhancedTopic += ` | Context: ${assignmentContext}`;
      }

      const response = await axios.post(`${API_URL}/lms/generate-assignment`, {
        resources,
        topic: enhancedTopic,
        difficulty: aiDifficulty,
        question_count: aiQuestionCount
      });

      if (response.data.status === "success") {
        setGeneratedAssignment(response.data.assignment);
        setDatasetSize(response.data.learning_dataset_size || 0);
        
        // Show extraction info
        if (response.data.extraction_info && response.data.extraction_info.length > 0) {
          console.log("Content Extraction Info:", response.data.extraction_info);
          console.log("Total content chars:", response.data.total_content_chars);
        }
        
        toast.success(`Assignment generated! ${response.data.total_content_chars} chars extracted from resources`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to generate assignment");
    } finally {
      setGenerating(false);
    }
  };

  const publishAssignment = async () => {
    if (!publishData.classId) {
      toast.error("Please select a class");
      return;
    }
    if (!publishData.dueDate) {
      toast.error("Please set a due date");
      return;
    }

    setPublishing(true);
    try {
      await axios.post(`${API_URL}/lms/assignments/create`, {
        course_id: publishData.classId,
        teacher_id: currentUser?.uid,
        title: generatedAssignment.title,
        description: generatedAssignment.description,
        instructions: generatedAssignment.instructions,
        resources: generatedAssignment.resources_used || [],
        due_date: publishData.dueDate,
        points: generatedAssignment.total_points,
        questions: generatedAssignment.questions || []
      });

      toast.success("Assignment published successfully!");
      setShowPublish(false);
      setShowAIGenerator(false);
      setGeneratedAssignment(null);
      setResources([]);
      setAiTopic("");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to publish assignment");
    } finally {
      setPublishing(false);
    }
  };

  // Show loading state while authentication is being checked
  if (loading || !currentUser || !userProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_hsl(191_100%_50%_/_0.05),_transparent_70%)] animate-glow-pulse" />
      
      {/* Header */}
      <header className="relative z-10 bg-card/50 backdrop-blur-md border-b border-border/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/" className="text-2xl font-bold text-primary drop-shadow-[0_0_10px_hsl(191_100%_50%_/_0.3)]">
                DataHalo
              </Link>
              <span className="text-sm text-muted-foreground">
                {isStudent ? "Student" : "Teacher"} Dashboard
              </span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="outline">
                  Back to Tools
                </Button>
              </Link>
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarImage src={userProfile.photoURL} />
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    {userProfile.displayName.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden md:block text-right">
                  <p className="text-sm font-semibold">{userProfile.displayName}</p>
                  <p className="text-xs text-muted-foreground">{userProfile.email}</p>
                </div>
              </div>
              <Button variant="outline" size="icon" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Welcome back, {userProfile.displayName}!
          </h1>
          <p className="text-muted-foreground">
            {isStudent
              ? "Continue your media literacy learning journey"
              : "Manage your courses and students"}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {isStudent ? (
            <>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Courses Enrolled</CardTitle>
                    <BookOpen className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">3</div>
                  <p className="text-xs text-muted-foreground mt-1">2 in progress</p>
                </CardContent>
              </Card>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Assignments</CardTitle>
                    <FileText className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">5</div>
                  <p className="text-xs text-muted-foreground mt-1">2 due this week</p>
                </CardContent>
              </Card>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Progress</CardTitle>
                    <TrendingUp className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">68%</div>
                  <p className="text-xs text-muted-foreground mt-1">+12% this month</p>
                </CardContent>
              </Card>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Certificates</CardTitle>
                    <Award className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">2</div>
                  <p className="text-xs text-muted-foreground mt-1">1 in progress</p>
                </CardContent>
              </Card>
            </>
          ) : (
            <>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Courses Teaching</CardTitle>
                    <BookOpen className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">4</div>
                  <p className="text-xs text-muted-foreground mt-1">2 active this semester</p>
                </CardContent>
              </Card>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Students</CardTitle>
                    <Users className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">87</div>
                  <p className="text-xs text-muted-foreground mt-1">Across all courses</p>
                </CardContent>
              </Card>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Pending Grades</CardTitle>
                    <FileText className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">23</div>
                  <p className="text-xs text-muted-foreground mt-1">Assignments to grade</p>
                </CardContent>
              </Card>
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Class Average</CardTitle>
                    <BarChart3 className="w-4 h-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">82%</div>
                  <p className="text-xs text-muted-foreground mt-1">+5% from last term</p>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Course/Tools */}
          <div className="lg:col-span-2 space-y-6">
            {isStudent ? (
              <>
                {/* TODAY'S NEWSROOM - The Core Workflow */}
                <Card className="shadow-[0_0_30px_hsl(191_100%_50%_/_0.3)] border-primary/50 backdrop-blur-md bg-gradient-to-br from-primary/10 to-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-2xl flex items-center gap-2">
                          <Sparkles className="w-6 h-6 text-primary" />
                          Today's Newsroom
                        </CardTitle>
                        <CardDescription>Your Daily Journalism Investigation Workspace</CardDescription>
                      </div>
                      <Badge variant="outline" className="bg-primary/20">
                        {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* The Workflow Steps */}
                    <div className="grid md:grid-cols-3 gap-3 mb-6">
                      <div className="p-3 bg-background/60 rounded-lg border border-primary/20">
                        <div className="text-center">
                          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mx-auto mb-2">
                            <span className="text-primary font-bold">1</span>
                          </div>
                          <p className="text-xs font-semibold">Select Story</p>
                        </div>
                      </div>
                      <div className="p-3 bg-background/60 rounded-lg border border-primary/20">
                        <div className="text-center">
                          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mx-auto mb-2">
                            <span className="text-primary font-bold">2</span>
                          </div>
                          <p className="text-xs font-semibold">Investigate & Analyze</p>
                        </div>
                      </div>
                      <div className="p-3 bg-background/60 rounded-lg border border-primary/20">
                        <div className="text-center">
                          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mx-auto mb-2">
                            <span className="text-primary font-bold">3</span>
                          </div>
                          <p className="text-xs font-semibold">Write & Submit</p>
                        </div>
                      </div>
                    </div>

                    {/* Top Stories Today - Real News from API */}
                    <div className="border-t pt-4">
                      <h3 className="font-semibold mb-3 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Top Stories to Investigate Today
                        {loadingNews && <Loader2 className="w-3 h-3 animate-spin" />}
                      </h3>
                      <div className="space-y-2">
                        {topStories.length > 0 ? topStories.map((story, idx) => (
                          <div key={idx} className="p-3 bg-background hover:bg-accent rounded-lg border cursor-pointer transition-colors group">
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex-1">
                                <h4 className="font-medium text-sm group-hover:text-primary transition-colors">{story.title}</h4>
                                <div className="flex items-center gap-2 mt-1 flex-wrap">
                                  <Badge variant="secondary" className="text-xs capitalize">{story.category || 'News'}</Badge>
                                  <span className="text-xs text-muted-foreground">Source: {story.source}</span>
                                </div>
                                {story.description && (
                                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{story.description}</p>
                                )}
                                {/* Action Buttons */}
                                <div className="flex gap-2 mt-2">
                                  {story.url && story.url !== "#" && story.url !== "https://www.example.com" && (
                                    <a 
                                      href={story.url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <Button size="sm" variant="outline" className="h-7 text-xs">
                                        <ExternalLink className="w-3 h-3 mr-1" />
                                        Read Article
                                      </Button>
                                    </a>
                                  )}
                                  <Link 
                                    to="/article-analyzer" 
                                    state={{ story: story }}
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    <Button size="sm" variant="default" className="h-7 text-xs">
                                      <FileText className="w-3 h-3 mr-1" />
                                      Analyze
                                    </Button>
                                  </Link>
                                </div>
                              </div>
                            </div>
                          </div>
                        )) : (
                          <div className="p-6 text-center text-muted-foreground">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                            <p className="text-sm">Fetching today's top stories...</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Investigation Tools */}
                    <div className="border-t pt-4">
                      <h3 className="font-semibold mb-3">Your Investigation Toolkit</h3>
                      <div className="grid grid-cols-2 gap-2">
                        <Link to="/article-analyzer">
                          <Button variant="outline" className="w-full justify-start" size="sm">
                            <FileText className="w-4 h-4 mr-2" />
                            Write Analysis
                          </Button>
                        </Link>
                        <Link to="/narrative-analyzer">
                          <Button variant="outline" className="w-full justify-start" size="sm">
                            <TrendingUp className="w-4 h-4 mr-2" />
                            Track Narrative
                          </Button>
                        </Link>
                        <Link to="/source-verifier">
                          <Button variant="outline" className="w-full justify-start" size="sm">
                            <Search className="w-4 h-4 mr-2" />
                            Verify Sources
                          </Button>
                        </Link>
                        <Button variant="outline" className="w-full justify-start" size="sm" onClick={() => setAiTutorOpen(true)}>
                          <Brain className="w-4 h-4 mr-2" />
                          Ask AI Tutor
                        </Button>
                        <Link to="/journalists">
                          <Button variant="outline" className="w-full justify-start col-span-2" size="sm">
                            <Users className="w-4 h-4 mr-2" />
                            Learn from Masters
                          </Button>
                        </Link>
                      </div>
                    </div>

                    {/* Start Investigation */}
                    <Button className="w-full" size="lg">
                      <Sparkles className="w-4 h-4 mr-2" />
                      Start Today's Investigation
                    </Button>
                  </CardContent>
                </Card>

                {/* Case Studies Section */}
                <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                  <CardHeader>
                    <CardTitle>Case Studies from Past Investigations</CardTitle>
                    <CardDescription>Learn from other students' analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      {
                        title: "How I Fact-Checked Trump's Rally Claims",
                        student: "Anonymous Student",
                        grade: "95%",
                        topic: "Politics"
                      },
                      {
                        title: "Comparing Ukraine War Coverage Across 5 Sources",
                        student: "Anonymous Student",
                        grade: "92%",
                        topic: "International"
                      },
                      {
                        title: "Identifying Propaganda in Climate Change Articles",
                        student: "Anonymous Student",
                        grade: "88%",
                        topic: "Climate"
                      }
                    ].map((study, idx) => (
                      <div key={idx} className="p-3 border rounded-lg hover:shadow-md transition-shadow cursor-pointer">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-sm mb-1">{study.title}</h4>
                            <div className="flex items-center gap-2">
                              <Badge variant="secondary" className="text-xs">{study.topic}</Badge>
                              <span className="text-xs text-muted-foreground">by {study.student}</span>
                            </div>
                          </div>
                          <Badge variant="outline" className="bg-green-500/10 border-green-500">
                            {study.grade}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </>
            ) : (
              <>
                {/* Teacher: Student Article Submissions */}
                <Card className="shadow-[0_0_30px_hsl(191_100%_50%_/_0.3)] border-primary/50 backdrop-blur-md bg-gradient-to-br from-primary/10 to-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-2xl flex items-center gap-2">
                          <FileText className="w-6 h-6 text-primary" />
                          Student Article Submissions
                        </CardTitle>
                        <CardDescription>Review and grade student article analyses</CardDescription>
                      </div>
                      <Badge variant="outline" className="bg-primary/20">
                        {submittedArticles.length} Pending
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {loadingArticles ? (
                      <div className="py-8 text-center">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-primary" />
                        <p className="text-sm text-muted-foreground">Loading submissions...</p>
                      </div>
                    ) : submittedArticles.length > 0 ? (
                      <div className="space-y-3">
                        {submittedArticles.slice(0, 5).map((submission, idx) => (
                          <div key={idx} className="p-4 border rounded-lg hover:shadow-md transition-shadow bg-background">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <h4 className="font-semibold text-sm">{submission.story_title || "Article Analysis"}</h4>
                                  {submission.status === "pending_review" && (
                                    <Badge variant="outline" className="bg-yellow-500/10 border-yellow-500 text-yellow-700">
                                      Pending Review
                                    </Badge>
                                  )}
                                  {submission.status === "graded" && (
                                    <Badge variant="outline" className="bg-green-500/10 border-green-500 text-green-700">
                                      Graded: {submission.grade}%
                                    </Badge>
                                  )}
                                </div>
                                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                                  <span className="flex items-center gap-1">
                                    <Users className="w-3 h-3" />
                                    {submission.student_name}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    {new Date(submission.submitted_at).toLocaleDateString()}
                                  </span>
                                  <Badge variant="secondary" className="text-xs">{submission.topic || "General"}</Badge>
                                </div>
                                {submission.story_url && (
                                  <a 
                                    href={submission.story_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-xs text-primary hover:underline flex items-center gap-1 mb-2"
                                  >
                                    <ExternalLink className="w-3 h-3" />
                                    View Original Article
                                  </a>
                                )}
                                <p className="text-xs text-muted-foreground line-clamp-2">
                                  {submission.analysis_content?.substring(0, 150)}...
                                </p>
                              </div>
                              <div className="flex flex-col gap-2 ml-4">
                                <Dialog>
                                  <DialogTrigger asChild>
                                    <Button size="sm" variant="outline">
                                      <Eye className="w-4 h-4 mr-1" />
                                      Review
                                    </Button>
                                  </DialogTrigger>
                                  <DialogContent className="max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
                                    <DialogHeader className="border-b pb-4">
                                      <DialogTitle className="text-2xl">{submission.story_title}</DialogTitle>
                                      <DialogDescription className="flex items-center gap-4 text-base mt-2">
                                        <span className="flex items-center gap-2">
                                          <Users className="w-4 h-4" />
                                          {submission.student_name}
                                        </span>
                                        <span className="flex items-center gap-2">
                                          <Calendar className="w-4 h-4" />
                                          {new Date(submission.submitted_at).toLocaleDateString('en-US', { 
                                            month: 'long', 
                                            day: 'numeric', 
                                            year: 'numeric' 
                                          })}
                                        </span>
                                      </DialogDescription>
                                    </DialogHeader>
                                    
                                    <div className="flex-1 overflow-y-auto py-6 space-y-6">
                                      {/* Parse and display original article separately */}
                                      {(() => {
                                        const content = submission.analysis_content || "";
                                        const parts = content.split("---\nOriginal Article Text:\n");
                                        const analysisReport = parts[0];
                                        const originalArticle = parts[1] || "";
                                        
                                        return (
                                          <>
                                            {originalArticle && (
                                              <div className="space-y-3">
                                                <div className="flex items-center justify-between">
                                                  <h3 className="text-lg font-bold flex items-center gap-2 text-primary">
                                                    <FileText className="w-5 h-5" />
                                                    Student's Original Article
                                                  </h3>
                                                  <Badge variant="outline" className="text-xs">
                                                    {originalArticle.trim().split(/\s+/).filter(Boolean).length} words
                                                  </Badge>
                                                </div>
                                                <div className="relative">
                                                  <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-blue-500 to-blue-600 rounded-full"></div>
                                                  <div className="ml-4 p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/40 dark:to-blue-900/20 rounded-xl border-2 border-blue-200 dark:border-blue-800 shadow-sm">
                                                    <div className="prose prose-sm dark:prose-invert max-w-none">
                                                      <div className="text-[15px] leading-[1.8] whitespace-pre-wrap text-gray-800 dark:text-gray-200 max-h-[400px] overflow-y-auto custom-scrollbar">
                                                        {originalArticle.trim()}
                                                      </div>
                                                    </div>
                                                  </div>
                                                </div>
                                              </div>
                                            )}
                                            
                                            <div className="space-y-3">
                                              <h3 className="text-lg font-bold flex items-center gap-2 text-primary">
                                                <BarChart3 className="w-5 h-5" />
                                                Automated Analysis Report
                                              </h3>
                                              <div className="relative">
                                                <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-500 to-purple-600 rounded-full"></div>
                                                <div className="ml-4 p-5 bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/40 dark:to-purple-900/20 rounded-xl border-2 border-purple-200 dark:border-purple-800 shadow-sm">
                                                  <div className="text-[14px] leading-[1.7] whitespace-pre-wrap font-mono text-gray-700 dark:text-gray-300 max-h-[500px] overflow-y-auto custom-scrollbar">
                                                    {analysisReport.trim()}
                                                  </div>
                                                </div>
                                              </div>
                                            </div>
                                          </>
                                        );
                                      })()}
                                      
                                      {submission.story_url && submission.story_url !== "N/A - Student Written Article" && (
                                        <div className="pt-4 border-t">
                                          <Label className="text-sm font-semibold mb-2 block">External Reference:</Label>
                                          <a 
                                            href={submission.story_url} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 hover:underline bg-primary/5 px-3 py-2 rounded-lg border border-primary/20 transition-colors"
                                          >
                                            <ExternalLink className="w-4 h-4" />
                                            {submission.story_url}
                                          </a>
                                        </div>
                                      )}
                                      
                                      {/* Grading Section */}
                                      {submission.status === "pending_review" && (
                                        <div className="pt-6 border-t-2 border-dashed space-y-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 p-6 rounded-xl">
                                          <h3 className="text-lg font-bold flex items-center gap-2 text-green-700 dark:text-green-400">
                                            <CheckCircle2 className="w-5 h-5" />
                                            Grade This Submission
                                          </h3>
                                          <div className="space-y-4">
                                            <div>
                                              <Label className="text-sm font-semibold mb-2 block">Grade (0-100):</Label>
                                              <Input 
                                                type="number" 
                                                min="0" 
                                                max="100" 
                                                placeholder="Enter grade (e.g., 85)"
                                                id={`grade-${submission._id}`}
                                                className="text-lg font-semibold"
                                              />
                                            </div>
                                            <div>
                                              <Label className="text-sm font-semibold mb-2 block">Your Feedback:</Label>
                                              <Textarea 
                                                placeholder="Provide constructive feedback on the student's article and analysis...

Example: 'Excellent analysis of bias and sourcing. Your identification of loaded language was particularly strong. Consider exploring the framing techniques more deeply and comparing this coverage with other outlets.'"
                                                rows={6}
                                                id={`feedback-${submission._id}`}
                                                className="text-sm leading-relaxed"
                                              />
                                            </div>
                                            <Button 
                                              onClick={() => {
                                                const gradeInput = document.getElementById(`grade-${submission._id}`) as HTMLInputElement;
                                                const feedbackInput = document.getElementById(`feedback-${submission._id}`) as HTMLTextAreaElement;
                                                const grade = parseInt(gradeInput?.value || "0");
                                                const feedback = feedbackInput?.value || "";
                                                
                                                if (grade < 0 || grade > 100) {
                                                  toast.error("Grade must be between 0 and 100");
                                                  return;
                                                }
                                                if (!feedback) {
                                                  toast.error("Please provide feedback");
                                                  return;
                                                }
                                                
                                                gradeArticle(submission._id, grade, feedback);
                                              }}
                                              className="w-full h-12 text-base font-semibold bg-green-600 hover:bg-green-700"
                                            >
                                              <CheckCircle2 className="w-5 h-5 mr-2" />
                                              Submit Grade & Feedback
                                            </Button>
                                          </div>
                                        </div>
                                      )}
                                      
                                      {submission.status === "graded" && (
                                        <div className="pt-6 border-t-2 border-dashed space-y-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 p-6 rounded-xl">
                                          <h3 className="text-lg font-bold flex items-center gap-2 text-blue-700 dark:text-blue-400">
                                            <Award className="w-5 h-5" />
                                            Grading Complete
                                          </h3>
                                          <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-900 rounded-lg border-2 border-blue-200 dark:border-blue-800">
                                            <Label className="text-base font-semibold">Final Grade:</Label>
                                            <Badge variant="outline" className="bg-green-500/10 border-green-500 text-green-700 text-lg px-4 py-1">
                                              {submission.grade}%
                                            </Badge>
                                          </div>
                                          <div className="p-4 bg-white dark:bg-gray-900 rounded-lg border-2 border-blue-200 dark:border-blue-800">
                                            <Label className="text-sm font-semibold mb-2 block">Your Feedback:</Label>
                                            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                                              {submission.feedback}
                                            </p>
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </DialogContent>
                                </Dialog>
                                {submission.status === "pending_review" && (
                                  <Badge variant="outline" className="text-xs text-center">
                                    New
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="py-8 text-center text-muted-foreground">
                        <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p className="font-semibold mb-1">No Submissions Yet</p>
                        <p className="text-sm">Student article analyses will appear here when submitted</p>
                      </div>
                    )}
                    {submittedArticles.length > 5 && (
                      <Button variant="outline" className="w-full mt-4">
                        View All {submittedArticles.length} Submissions
                      </Button>
                    )}
                  </CardContent>
                </Card>

                {/* My Courses */}
                <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                  <CardHeader>
                    <CardTitle>My Courses</CardTitle>
                    <CardDescription>Manage your teaching assignments</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {[
                      { title: "Media Literacy 101", students: 35, pending: 8 },
                      { title: "Advanced Journalism", students: 28, pending: 12 },
                      { title: "Fact-Checking Workshop", students: 24, pending: 3 }
                    ].map((course, index) => (
                      <div key={index} className="p-4 border rounded-lg hover:shadow-md transition-shadow border-border/50">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-semibold mb-1">{course.title}</h3>
                            <p className="text-sm text-muted-foreground">
                              {course.students} students · {course.pending} pending submissions
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">View</Button>
                            <Button size="sm">Grade</Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </>
            )}

            {/* Quick Actions */}
            <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Access your classes and tools</CardDescription>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 gap-4">
                <Link to="/classes" className="block">
                  <div className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer border-border/50">
                    <BookOpen className="w-8 h-8 mb-2 text-primary" />
                    <h3 className="font-semibold mb-1">
                      {isTeacher ? "My Classes" : "Enrolled Classes"}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {isTeacher ? "Manage your classes" : "View your classes"}
                    </p>
                  </div>
                </Link>
                {isTeacher && (
                  <div
                    className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer border-primary/30 bg-gradient-to-br from-primary/5 to-transparent"
                    onClick={() => setShowAIGenerator(true)}
                  >
                    <Sparkles className="w-8 h-8 mb-2 text-primary" />
                    <h3 className="font-semibold mb-1">AI Generator</h3>
                    <p className="text-sm text-muted-foreground">
                      Create assignments with AI
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Journalist Gallery - Learn from Pros */}
            {isStudent && (
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader>
                  <CardTitle>Learn from Professional Journalists</CardTitle>
                  <CardDescription>Study how experts cover today's stories</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-4">
                  <Link to="/journalists" className="block">
                    <div className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer border-border/50">
                      <Users className="w-8 h-8 mb-2 text-primary" />
                      <h3 className="font-semibold mb-1">Journalist Gallery</h3>
                      <p className="text-sm text-muted-foreground">
                        Explore journalist profiles & track records
                      </p>
                    </div>
                  </Link>
                  <Link to="/" className="block">
                    <div className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer border-border/50">
                      <Search className="w-8 h-8 mb-2 text-primary" />
                      <h3 className="font-semibold mb-1">Source Verification</h3>
                      <p className="text-sm text-muted-foreground">
                        Check journalist credibility & history
                      </p>
                    </div>
                  </Link>
                </CardContent>
              </Card>
            )}

            {/* Teacher Tools */}
            {isTeacher && (
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader>
                  <CardTitle>Teaching Tools</CardTitle>
                  <CardDescription>Manage assignments and review submissions</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-4">
                  <div
                    className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer border-primary/30 bg-gradient-to-br from-primary/5 to-transparent"
                    onClick={() => setShowAIGenerator(true)}
                  >
                    <Sparkles className="w-8 h-8 mb-2 text-primary" />
                    <h3 className="font-semibold mb-1">AI Generator</h3>
                    <p className="text-sm text-muted-foreground">
                      Create assignments from news stories
                    </p>
                  </div>
                  <Link to="/classes" className="block">
                    <div className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer border-border/50">
                      <Users className="w-8 h-8 mb-2 text-primary" />
                      <h3 className="font-semibold mb-1">Review Submissions</h3>
                      <p className="text-sm text-muted-foreground">
                        Grade student investigations
                      </p>
                    </div>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Activity/Upcoming */}
          <div className="space-y-6">
            {isStudent && (
              <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Upcoming Deadlines
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { title: "Bias Analysis Essay", course: "Media Literacy 101", due: "Tomorrow", urgent: true },
                    { title: "Propaganda Quiz", course: "Advanced Course", due: "In 3 days", urgent: false },
                    { title: "Narrative Project", course: "Fact-Checking", due: "Next week", urgent: false }
                  ].map((assignment, index) => (
                    <div
                      key={index}
                      className={`p-3 border-l-4 ${
                        assignment.urgent ? "border-red-500 bg-red-500/10" : "border-primary"
                      } rounded`}
                    >
                      <h4 className="font-semibold text-sm">{assignment.title}</h4>
                      <p className="text-xs text-muted-foreground">{assignment.course}</p>
                      <p className={`text-xs mt-1 ${assignment.urgent ? "text-red-600 font-semibold" : "text-muted-foreground"}`}>
                        Due: {assignment.due}
                      </p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            <Card className="shadow-[0_0_20px_hsl(191_100%_50%_/_0.1)] border-border/50 backdrop-blur-md bg-card/80">
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {isStudent ? (
                  <>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Completed</p>
                      <p className="font-semibold">Module 3: Propaganda Techniques</p>
                      <p className="text-xs text-muted-foreground">2 hours ago</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Submitted</p>
                      <p className="font-semibold">Journalist Analysis Assignment</p>
                      <p className="text-xs text-muted-foreground">Yesterday</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Earned</p>
                      <p className="font-semibold">Bias Detection Badge</p>
                      <p className="text-xs text-muted-foreground">3 days ago</p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Graded</p>
                      <p className="font-semibold">15 assignments</p>
                      <p className="text-xs text-muted-foreground">Today</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Created</p>
                      <p className="font-semibold">New quiz: Propaganda Techniques</p>
                      <p className="text-xs text-muted-foreground">Yesterday</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Announcement</p>
                      <p className="font-semibold">Posted to Media Literacy 101</p>
                      <p className="text-xs text-muted-foreground">2 days ago</p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* AI Tutor */}
      {!aiTutorOpen && <AITutorButton onClick={() => setAiTutorOpen(true)} />}
      <AITutorV2 isOpen={aiTutorOpen} onClose={() => setAiTutorOpen(false)} />

      {/* AI Assignment Generator Dialog */}
      <Dialog open={showAIGenerator} onOpenChange={setShowAIGenerator}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Journalism AI Assignment Generator
            </DialogTitle>
            <DialogDescription className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Add resources → AI generates professional journalism assignments · Learning from {datasetSize} past assignments
            </DialogDescription>
          </DialogHeader>

          {!generatedAssignment ? (
            <div className="space-y-6">
              {/* Add Resources */}
              <div className="border rounded-lg p-4 space-y-4 border-primary/20 bg-primary/5">
                <h3 className="font-semibold flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Add Learning Resources
                </h3>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Resource Type</Label>
                    <Select
                      value={currentResource.type}
                      onValueChange={(value: any) =>
                        setCurrentResource({ ...currentResource, type: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="url">Article URL</SelectItem>
                        <SelectItem value="youtube">YouTube Video</SelectItem>
                        <SelectItem value="text">Text Content</SelectItem>
                        <SelectItem value="pdf">PDF Document</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Resource Title</Label>
                    <Input
                      value={currentResource.title}
                      onChange={(e) =>
                        setCurrentResource({ ...currentResource, title: e.target.value })
                      }
                      placeholder="e.g., Fact-Checking Masterclass"
                    />
                  </div>
                </div>

                <div>
                  <Label>
                    {currentResource.type === "text" ? "Content" : "URL"}
                  </Label>
                  {currentResource.type === "text" ? (
                    <Textarea
                      value={currentResource.content}
                      onChange={(e) =>
                        setCurrentResource({ ...currentResource, content: e.target.value })
                      }
                      placeholder="Paste article text, PDF content, or lesson material..."
                      rows={4}
                    />
                  ) : (
                    <>
                      <Input
                        value={currentResource.content}
                        onChange={(e) =>
                          setCurrentResource({ ...currentResource, content: e.target.value })
                        }
                        placeholder="https://..."
                      />
                      {currentResource.type === "pdf" && (
                        <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                          ⚠️ PDF extraction may not always work. For best results, copy the PDF text and use "Text Content" type instead.
                        </p>
                      )}
                    </>
                  )}
                </div>

                <Button onClick={addResource} variant="outline" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Resource
                </Button>

                {/* Resource List */}
                {resources.length > 0 && (
                  <div className="space-y-2 mt-4">
                    <p className="text-sm font-semibold">Resources ({resources.length}):</p>
                    {resources.map((resource, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 bg-background rounded-lg border"
                      >
                        <div className="flex items-center gap-2">
                          {resource.type === "url" && <LinkIcon className="w-4 h-4 text-primary" />}
                          {resource.type === "youtube" && <Youtube className="w-4 h-4 text-red-500" />}
                          {resource.type === "pdf" && <FileUp className="w-4 h-4 text-blue-500" />}
                          {resource.type === "text" && <FileText className="w-4 h-4 text-green-500" />}
                          <span className="text-sm font-medium">{resource.title}</span>
                        </div>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7"
                          onClick={() => removeResource(index)}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Assignment Parameters */}
              <div className="space-y-4">
                <div>
                  <Label>Assignment Topic</Label>
                  <Input
                    value={aiTopic}
                    onChange={(e) => setAiTopic(e.target.value)}
                    placeholder="e.g., Propaganda Techniques in Modern Media"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Target Audience</Label>
                    <Input
                      value={targetAudience}
                      onChange={(e) => setTargetAudience(e.target.value)}
                      placeholder="e.g., Undergraduate journalism students, Year 2"
                    />
                  </div>
                  <div>
                    <Label>Learning Goal</Label>
                    <Input
                      value={learningGoal}
                      onChange={(e) => setLearningGoal(e.target.value)}
                      placeholder="e.g., Students will identify 5 propaganda techniques"
                    />
                  </div>
                </div>

                <div>
                  <Label>Assignment Context (Optional)</Label>
                  <Textarea
                    value={assignmentContext}
                    onChange={(e) => setAssignmentContext(e.target.value)}
                    placeholder="e.g., This is part of a unit on media manipulation. Students have already learned about bias. They will use this assignment to prepare for a group project on analyzing campaign ads."
                    rows={3}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Difficulty Level</Label>
                    <Select value={aiDifficulty} onValueChange={setAiDifficulty}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="easy">Easy (Beginner)</SelectItem>
                        <SelectItem value="medium">Medium (Intermediate)</SelectItem>
                        <SelectItem value="hard">Hard (Advanced)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Number of Questions</Label>
                    <Select
                      value={aiQuestionCount.toString()}
                      onValueChange={(value) => setAiQuestionCount(parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="3">3 Questions</SelectItem>
                        <SelectItem value="5">5 Questions</SelectItem>
                        <SelectItem value="7">7 Questions</SelectItem>
                        <SelectItem value="10">10 Questions</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                <p className="text-sm">
                  <strong className="text-primary">🎓 AI Learning Status:</strong> This AI has learned from{" "}
                  <strong>{datasetSize}</strong> past assignments and improves with every generation.
                  Your input helps train better journalism education!
                </p>
              </div>

              <Button
                onClick={generateAssignment}
                disabled={generating}
                className="w-full"
                size="lg"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Generating Assignment...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate Journalism Assignment with AI
                  </>
                )}
              </Button>
            </div>
          ) : (
            /* Generated Assignment Preview */
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold">{generatedAssignment.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {generatedAssignment.description}
                  </p>
                </div>
                <Badge variant="outline" className="bg-green-500/10 border-green-500">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  AI Generated
                </Badge>
              </div>

              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div className="p-3 bg-accent rounded-lg">
                  <span className="text-muted-foreground">Points:</span>
                  <span className="ml-2 font-bold text-lg">{generatedAssignment.total_points}</span>
                </div>
                <div className="p-3 bg-accent rounded-lg">
                  <span className="text-muted-foreground">Time:</span>
                  <span className="ml-2 font-semibold">{generatedAssignment.estimated_time}</span>
                </div>
                <div className="p-3 bg-accent rounded-lg">
                  <span className="text-muted-foreground">Questions:</span>
                  <span className="ml-2 font-bold text-lg">{generatedAssignment.questions?.length}</span>
                </div>
              </div>

              {/* Resources Used */}
              {generatedAssignment.resources_used && generatedAssignment.resources_used.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">Resources Referenced:</h4>
                  <div className="space-y-2">
                    {generatedAssignment.resources_used.map((resource: any, i: number) => (
                      <div key={i} className="p-2 bg-accent/50 rounded text-xs">
                        <p className="font-semibold">{resource.title}</p>
                        <p className="text-muted-foreground">Type: {resource.type}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Instructions:</h4>
                <p className="text-sm text-muted-foreground">{generatedAssignment.instructions}</p>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Learning Objectives:</h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {generatedAssignment.learning_objectives?.map((obj: string, i: number) => (
                    <li key={i}>{obj}</li>
                  ))}
                </ul>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3">Questions:</h4>
                <div className="space-y-3 max-h-60 overflow-y-auto">
                  {generatedAssignment.questions?.map((q: any, i: number) => (
                    <Card key={i} className="border-primary/20">
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-sm">Q{q.question_number}: {q.question_type}</span>
                          <Badge>{q.points} pts</Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm">{q.question_text}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setGeneratedAssignment(null);
                    setResources([]);
                    setAiTopic("");
                    setTargetAudience("");
                    setLearningGoal("");
                    setAssignmentContext("");
                  }}
                  className="flex-1"
                >
                  Generate New
                </Button>
                <Button
                  onClick={() => {
                    // Export as PDF
                    const printWindow = window.open('', '', 'height=800,width=800');
                    if (printWindow) {
                      printWindow.document.write('<html><head><title>Assignment</title>');
                      printWindow.document.write('<style>body{font-family:Arial,sans-serif;padding:40px;line-height:1.6;}h1{color:#0ea5e9;}h2{color:#333;margin-top:20px;}p{margin:10px 0;}.question{margin:20px 0;padding:15px;border-left:3px solid #0ea5e9;background:#f8f9fa;}.rubric{margin:10px 0;font-size:0.9em;}.points{float:right;font-weight:bold;}</style>');
                      printWindow.document.write('</head><body>');
                      printWindow.document.write(`<h1>${generatedAssignment.title}</h1>`);
                      printWindow.document.write(`<p><strong>Time:</strong> ${generatedAssignment.estimated_time} | <strong>Points:</strong> ${generatedAssignment.total_points}</p>`);
                      printWindow.document.write(`<p>${generatedAssignment.description}</p>`);
                      printWindow.document.write(`<h2>Instructions</h2><p>${generatedAssignment.instructions}</p>`);
                      printWindow.document.write(`<h2>Learning Objectives</h2><ul>${generatedAssignment.learning_objectives?.map((obj: string) => `<li>${obj}</li>`).join('')}</ul>`);
                      printWindow.document.write('<h2>Questions</h2>');
                      generatedAssignment.questions?.forEach((q: any) => {
                        printWindow.document.write(`<div class="question"><p><strong>Question ${q.question_number}</strong> <span class="points">${q.points} points</span></p><p>${q.question_text}</p><p><em>${q.instructions}</em></p></div>`);
                      });
                      printWindow.document.write('</body></html>');
                      printWindow.document.close();
                      printWindow.print();
                    }
                    toast.success("Opening print dialog for PDF export");
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Export as PDF
                </Button>
                <Button onClick={() => setShowPublish(true)} className="flex-1">
                  <Send className="w-4 h-4 mr-2" />
                  Publish to Class
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Publish Assignment Dialog */}
      <Dialog open={showPublish} onOpenChange={setShowPublish}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Publish Assignment to Class</DialogTitle>
            <DialogDescription>
              Select a class and set a due date
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Select Class</Label>
              <Select 
                value={publishData.classId} 
                onValueChange={(value) => setPublishData({ ...publishData, classId: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Choose a class" />
                </SelectTrigger>
                <SelectContent>
                  {classes.map((cls) => (
                    <SelectItem key={cls._id} value={cls._id}>
                      {cls.title} ({cls.student_count || 0} students)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {classes.length === 0 && (
                <p className="text-xs text-amber-600 mt-1">
                  You haven't created any classes yet. Create a class first!
                </p>
              )}
            </div>

            <div>
              <Label>Due Date</Label>
              <Input
                type="datetime-local"
                value={publishData.dueDate}
                onChange={(e) => setPublishData({ ...publishData, dueDate: e.target.value })}
              />
            </div>

            <div className="bg-accent p-3 rounded-lg text-sm">
              <p className="font-semibold mb-1">{generatedAssignment?.title}</p>
              <p className="text-muted-foreground">
                {generatedAssignment?.questions?.length} questions · {generatedAssignment?.total_points} points
              </p>
            </div>

            <div className="flex gap-2">
              <Button onClick={publishAssignment} disabled={publishing} className="flex-1">
                {publishing ? "Publishing..." : "Publish Assignment"}
              </Button>
              <Button variant="outline" onClick={() => setShowPublish(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
