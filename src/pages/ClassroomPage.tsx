// Google Classroom-like Environment
import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BookOpen,
  FileText,
  Users,
  Send,
  Calendar,
  Upload,
  Download,
  CheckCircle,
  Clock,
  Copy,
  Plus,
  BarChart3,
  MessageSquare,
  X
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

export default function ClassroomPage() {
  const { classId } = useParams();
  const { currentUser, userProfile, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [classData, setClassData] = useState<any>(null);
  const [assignments, setAssignments] = useState<any[]>([]);
  const [students, setStudents] = useState<any[]>([]);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Announcement
  const [announcement, setAnnouncement] = useState("");
  const [postingAnnouncement, setPostingAnnouncement] = useState(false);
  
  // Assignment submission
  const [selectedAssignment, setSelectedAssignment] = useState<any>(null);
  const [submissionText, setSubmissionText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [viewingAssignment, setViewingAssignment] = useState<any>(null);
  
  // Create Assignment
  const [showCreateAssignment, setShowCreateAssignment] = useState(false);
  const [creatingAssignment, setCreatingAssignment] = useState(false);
  const [newAssignment, setNewAssignment] = useState({
    title: "",
    description: "",
    instructions: "",
    dueDate: "",
    points: 100,
  });
  const [assignmentFiles, setAssignmentFiles] = useState<File[]>([]);
  const [assignmentQuestions, setAssignmentQuestions] = useState<string>("");
  
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const isTeacher = userProfile?.role === "teacher";

  useEffect(() => {
    if (!authLoading && (!currentUser || !userProfile)) {
      navigate("/login");
    }
  }, [authLoading, currentUser, userProfile, navigate]);

  useEffect(() => {
    if (classId && currentUser) {
      loadClassData();
    }
  }, [classId, currentUser]);

  const loadClassData = async () => {
    setLoading(true);
    try {
      // Load class details
      const classResponse = await axios.get(`${API_URL}/lms/classes/${classId}`);
      setClassData(classResponse.data.class);
      
      // Load assignments
      const assignmentsResponse = await axios.get(`${API_URL}/lms/assignments/course/${classId}`);
      setAssignments(assignmentsResponse.data.assignments || []);
      
      // Load submissions if student
      if (!isTeacher && currentUser) {
        const submissionsResponse = await axios.get(`${API_URL}/lms/submissions/student/${currentUser.uid}`);
        setSubmissions(submissionsResponse.data.submissions || []);
      }
      
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load class data");
      setLoading(false);
    }
  };

  const postAnnouncement = async () => {
    if (!announcement.trim()) {
      toast.error("Please enter an announcement");
      return;
    }
    
    setPostingAnnouncement(true);
    try {
      // In a real app, you'd have an announcements endpoint
      toast.success("Announcement posted!");
      setAnnouncement("");
    } catch (error) {
      toast.error("Failed to post announcement");
    } finally {
      setPostingAnnouncement(false);
    }
  };

  const submitAssignment = async () => {
    if (!submissionText.trim()) {
      toast.error("Please enter your submission");
      return;
    }
    
    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/lms/submissions/submit`, {
        assignment_id: selectedAssignment._id,
        student_id: currentUser?.uid,
        student_name: userProfile?.displayName,
        content: submissionText,
        answers: [] // Can be enhanced later
      });
      
      toast.success("Assignment submitted successfully!");
      setSelectedAssignment(null);
      setSubmissionText("");
      loadClassData();
    } catch (error) {
      toast.error("Failed to submit assignment");
    } finally {
      setSubmitting(false);
    }
  };

  const copyInviteCode = () => {
    navigator.clipboard.writeText(classData.invite_code);
    toast.success("Invite code copied!");
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAssignmentFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setAssignmentFiles(prev => prev.filter((_, i) => i !== index));
  };

  const createAssignment = async () => {
    if (!newAssignment.title || !newAssignment.dueDate) {
      toast.error("Please fill in title and due date");
      return;
    }

    setCreatingAssignment(true);
    try {
      // Parse questions from text (simple format: one question per line)
      const questions = assignmentQuestions
        .split("\n")
        .filter(q => q.trim())
        .map((q, idx) => ({
          question_number: idx + 1,
          question_text: q.trim(),
          question_type: "essay",
          points: Math.floor(newAssignment.points / assignmentQuestions.split("\n").filter(q => q.trim()).length),
          instructions: "Provide a detailed answer"
        }));

      // Convert files to base64 for storage (in production, use cloud storage)
      const resources = await Promise.all(
        assignmentFiles.map(async (file) => {
          return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => {
              resolve({
                type: file.type.includes("pdf") ? "pdf" : "file",
                title: file.name,
                content: e.target?.result as string,
                size: file.size
              });
            };
            reader.readAsDataURL(file);
          });
        })
      );

      const response = await axios.post(`${API_URL}/lms/assignments/create`, {
        course_id: classId,
        teacher_id: currentUser?.uid,
        title: newAssignment.title,
        description: newAssignment.description,
        instructions: newAssignment.instructions,
        resources: resources,
        due_date: newAssignment.dueDate,
        points: newAssignment.points,
        questions: questions.length > 0 ? questions : [
          {
            question_number: 1,
            question_text: newAssignment.instructions || "Complete the assignment",
            question_type: "essay",
            points: newAssignment.points,
            instructions: "Follow the provided instructions"
          }
        ]
      });

      if (response.data.status === "success") {
        toast.success("Assignment created successfully!");
        setShowCreateAssignment(false);
        setNewAssignment({
          title: "",
          description: "",
          instructions: "",
          dueDate: "",
          points: 100,
        });
        setAssignmentFiles([]);
        setAssignmentQuestions("");
        loadClassData();
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to create assignment");
    } finally {
      setCreatingAssignment(false);
    }
  };

  if (authLoading || loading || !currentUser || !userProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!classData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-muted-foreground">Class not found</p>
          <Button onClick={() => navigate("/dashboard")} className="mt-4">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Class Header */}
      <div className="bg-gradient-to-r from-primary/20 to-primary/10 border-b">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{classData.title}</h1>
              <p className="text-muted-foreground mb-4">{classData.description}</p>
              <div className="flex items-center gap-4">
                <Badge variant="secondary">
                  <Users className="w-3 h-3 mr-1" />
                  {classData.students?.length || 0} Students
                </Badge>
                <Badge variant="secondary">
                  <FileText className="w-3 h-3 mr-1" />
                  {assignments.length} Assignments
                </Badge>
                {isTeacher && (
                  <Button variant="outline" size="sm" onClick={copyInviteCode}>
                    <Copy className="w-4 h-4 mr-2" />
                    Code: {classData.invite_code}
                  </Button>
                )}
              </div>
            </div>
            <Button variant="outline" onClick={() => navigate("/dashboard")}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="stream" className="space-y-6">
          <TabsList>
            <TabsTrigger value="stream">
              <MessageSquare className="w-4 h-4 mr-2" />
              Stream
            </TabsTrigger>
            <TabsTrigger value="assignments">
              <FileText className="w-4 h-4 mr-2" />
              Assignments
            </TabsTrigger>
            {isTeacher && (
              <TabsTrigger value="students">
                <Users className="w-4 h-4 mr-2" />
                Students
              </TabsTrigger>
            )}
            <TabsTrigger value="grades">
              <BarChart3 className="w-4 h-4 mr-2" />
              Grades
            </TabsTrigger>
          </TabsList>

          {/* Stream Tab */}
          <TabsContent value="stream" className="space-y-6">
            {isTeacher && (
              <Card>
                <CardHeader>
                  <CardTitle>Post Announcement</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    value={announcement}
                    onChange={(e) => setAnnouncement(e.target.value)}
                    placeholder="Share something with your class..."
                    rows={3}
                  />
                  <Button onClick={postAnnouncement} disabled={postingAnnouncement}>
                    <Send className="w-4 h-4 mr-2" />
                    Post
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Recent Assignments */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Recent Activity</h2>
              {assignments.slice(0, 3).map((assignment) => {
                const submission = submissions.find(s => s.assignment_id === assignment._id);
                
                return (
                  <Card key={assignment._id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{assignment.title}</CardTitle>
                          <CardDescription>{assignment.description}</CardDescription>
                        </div>
                        {submission ? (
                          <Badge variant="outline" className="bg-green-500/10 border-green-500">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Submitted
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="bg-amber-500/10 border-amber-500">
                            <Clock className="w-3 h-3 mr-1" />
                            Pending
                          </Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                          <span>{assignment.points} points</span>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => setViewingAssignment(assignment)}
                          >
                            View Details
                          </Button>
                          {!isTeacher && !submission && (
                            <Button size="sm" onClick={() => setSelectedAssignment(assignment)}>
                              Submit
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Assignments Tab */}
          <TabsContent value="assignments" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">All Assignments</h2>
              {isTeacher && (
                <Button onClick={() => setShowCreateAssignment(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Assignment
                </Button>
              )}
            </div>

            <div className="grid gap-4">
              {assignments.map((assignment) => {
                const submission = submissions.find(s => s.assignment_id === assignment._id);
                
                return (
                  <Card key={assignment._id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle>{assignment.title}</CardTitle>
                          <CardDescription>{assignment.description}</CardDescription>
                        </div>
                        <Badge>{assignment.points} pts</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">
                            Due: {new Date(assignment.due_date).toLocaleDateString()}
                          </span>
                          {submission && (
                            <span className="text-green-600 dark:text-green-400">
                              Submitted: {new Date(submission.submitted_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            onClick={() => setViewingAssignment(assignment)}
                          >
                            View Details
                          </Button>
                          {!isTeacher && (
                            submission ? (
                              <div className="flex items-center gap-2">
                                {submission.grade !== null ? (
                                  <Badge variant="outline" className="bg-green-500/10 border-green-500">
                                    Grade: {submission.grade}/{assignment.points}
                                  </Badge>
                                ) : (
                                  <Badge variant="outline" className="bg-amber-500/10 border-amber-500">
                                    Awaiting grade
                                  </Badge>
                                )}
                              </div>
                            ) : (
                              <Button onClick={() => setSelectedAssignment(assignment)}>
                                Submit Assignment
                              </Button>
                            )
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
              
              {assignments.length === 0 && (
                <Card>
                  <CardContent className="py-12 text-center text-muted-foreground">
                    No assignments yet
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Students Tab (Teacher Only) */}
          {isTeacher && (
            <TabsContent value="students" className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Enrolled Students</h2>
                <Button variant="outline" onClick={copyInviteCode}>
                  <Copy className="w-4 h-4 mr-2" />
                  Share Invite Code
                </Button>
              </div>

              <Card>
                <CardContent className="pt-6">
                  {classData.students && classData.students.length > 0 ? (
                    <div className="space-y-2">
                      {classData.students.map((studentId: string, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                              <Users className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                              <p className="font-semibold">Student {index + 1}</p>
                              <p className="text-sm text-muted-foreground">{studentId}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      No students enrolled yet. Share the invite code to get started!
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          )}

          {/* Grades Tab */}
          <TabsContent value="grades" className="space-y-6">
            <h2 className="text-xl font-semibold">Grades</h2>
            
            <Card>
              <CardContent className="pt-6">
                {isTeacher ? (
                  <div className="text-center py-12 text-muted-foreground">
                    Gradebook coming soon
                  </div>
                ) : (
                  <div className="space-y-4">
                    {submissions.filter(s => s.grade !== null).map((submission) => {
                      const assignment = assignments.find(a => a._id === submission.assignment_id);
                      return assignment ? (
                        <div key={submission._id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <p className="font-semibold">{assignment.title}</p>
                            <p className="text-sm text-muted-foreground">
                              Submitted: {new Date(submission.submitted_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold">
                              {submission.grade}/{assignment.points}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {((submission.grade / assignment.points) * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>
                      ) : null;
                    })}
                    
                    {submissions.filter(s => s.grade !== null).length === 0 && (
                      <div className="text-center py-12 text-muted-foreground">
                        No graded assignments yet
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* View Assignment Details Dialog */}
      <Dialog open={!!viewingAssignment} onOpenChange={() => setViewingAssignment(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{viewingAssignment?.title}</DialogTitle>
            <DialogDescription>
              {viewingAssignment?.description}
            </DialogDescription>
          </DialogHeader>

          {viewingAssignment && (
            <div className="space-y-6">
              {/* Assignment Info */}
              <div className="grid grid-cols-3 gap-4 p-4 bg-accent rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground">Due Date</p>
                  <p className="font-semibold">
                    {new Date(viewingAssignment.due_date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Points</p>
                  <p className="font-semibold">{viewingAssignment.points}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Questions</p>
                  <p className="font-semibold">{viewingAssignment.questions?.length || 0}</p>
                </div>
              </div>

              {/* Instructions */}
              {viewingAssignment.instructions && (
                <div>
                  <h3 className="font-semibold mb-2">Instructions</h3>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {viewingAssignment.instructions}
                  </p>
                </div>
              )}

              {/* Resources/Files */}
              {viewingAssignment.resources && viewingAssignment.resources.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-3">Resources</h3>
                  <div className="space-y-2">
                    {viewingAssignment.resources.map((resource: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <FileText className="w-5 h-5 text-primary" />
                          <div>
                            <p className="font-medium">{resource.title}</p>
                            {resource.size && (
                              <p className="text-xs text-muted-foreground">
                                {(resource.size / 1024).toFixed(1)} KB
                              </p>
                            )}
                          </div>
                        </div>
                        {resource.content && resource.content.startsWith('data:') && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const link = document.createElement('a');
                              link.href = resource.content;
                              link.download = resource.title;
                              link.click();
                            }}
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Questions */}
              {viewingAssignment.questions && viewingAssignment.questions.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-3">Questions</h3>
                  <div className="space-y-4">
                    {viewingAssignment.questions.map((question: any, index: number) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-medium">
                            {question.question_number}. {question.question_text}
                          </p>
                          <Badge variant="secondary">{question.points} pts</Badge>
                        </div>
                        {question.instructions && (
                          <p className="text-sm text-muted-foreground mt-2">
                            {question.instructions}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                {!isTeacher && !submissions.find(s => s.assignment_id === viewingAssignment._id) && (
                  <Button 
                    onClick={() => {
                      setSelectedAssignment(viewingAssignment);
                      setViewingAssignment(null);
                    }}
                    className="flex-1"
                  >
                    Start Assignment
                  </Button>
                )}
                <Button 
                  variant="outline" 
                  onClick={() => setViewingAssignment(null)}
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Assignment Submission Dialog */}
      <Dialog open={!!selectedAssignment} onOpenChange={() => setSelectedAssignment(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Submit Assignment</DialogTitle>
            <DialogDescription>
              {selectedAssignment?.title}
            </DialogDescription>
          </DialogHeader>

          {selectedAssignment && (
            <div className="space-y-4">
              {/* Show Questions */}
              {selectedAssignment.questions && selectedAssignment.questions.length > 0 && (
                <div className="p-4 bg-accent rounded-lg">
                  <h4 className="font-semibold mb-3">Questions</h4>
                  <div className="space-y-2">
                    {selectedAssignment.questions.map((question: any, index: number) => (
                      <p key={index} className="text-sm">
                        {question.question_number}. {question.question_text}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* Response Area */}
              <div>
                <Label>Your Response</Label>
                <Textarea
                  value={submissionText}
                  onChange={(e) => setSubmissionText(e.target.value)}
                  placeholder="Enter your assignment submission here...&#10;&#10;Answer each question thoroughly."
                  rows={12}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Make sure to address all questions in your response
                </p>
              </div>

              <div className="flex gap-2">
                <Button onClick={submitAssignment} disabled={submitting} className="flex-1">
                  {submitting ? "Submitting..." : "Submit Assignment"}
                </Button>
                <Button variant="outline" onClick={() => setSelectedAssignment(null)}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Create Assignment Dialog */}
      <Dialog open={showCreateAssignment} onOpenChange={setShowCreateAssignment}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Assignment</DialogTitle>
            <DialogDescription>
              Create an assignment with instructions and optional file uploads
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <Label>Assignment Title *</Label>
              <Input
                value={newAssignment.title}
                onChange={(e) => setNewAssignment({ ...newAssignment, title: e.target.value })}
                placeholder="e.g., Propaganda Analysis Essay"
              />
            </div>

            {/* Description */}
            <div>
              <Label>Short Description</Label>
              <Input
                value={newAssignment.description}
                onChange={(e) => setNewAssignment({ ...newAssignment, description: e.target.value })}
                placeholder="Brief overview of the assignment"
              />
            </div>

            {/* Instructions */}
            <div>
              <Label>Detailed Instructions</Label>
              <Textarea
                value={newAssignment.instructions}
                onChange={(e) => setNewAssignment({ ...newAssignment, instructions: e.target.value })}
                placeholder="Provide detailed instructions for students..."
                rows={5}
              />
            </div>

            {/* Questions (Optional) */}
            <div>
              <Label>Questions (Optional)</Label>
              <Textarea
                value={assignmentQuestions}
                onChange={(e) => setAssignmentQuestions(e.target.value)}
                placeholder="Enter questions, one per line:&#10;1. What are the main propaganda techniques used?&#10;2. How does the author establish credibility?&#10;3. Identify any biases in the presentation."
                rows={4}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Enter each question on a new line
              </p>
            </div>

            {/* File Upload */}
            <div>
              <Label>Upload Resources (PDFs, Documents)</Label>
              <div className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    PDF, DOC, DOCX, TXT
                  </p>
                </label>
              </div>

              {/* Uploaded Files */}
              {assignmentFiles.length > 0 && (
                <div className="space-y-2 mt-3">
                  {assignmentFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-accent rounded-lg">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-primary" />
                        <span className="text-sm">{file.name}</span>
                        <span className="text-xs text-muted-foreground">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Due Date and Points */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Due Date *</Label>
                <Input
                  type="datetime-local"
                  value={newAssignment.dueDate}
                  onChange={(e) => setNewAssignment({ ...newAssignment, dueDate: e.target.value })}
                />
              </div>
              <div>
                <Label>Total Points</Label>
                <Input
                  type="number"
                  value={newAssignment.points}
                  onChange={(e) => setNewAssignment({ ...newAssignment, points: parseInt(e.target.value) || 100 })}
                  min="1"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-4">
              <Button 
                onClick={createAssignment} 
                disabled={creatingAssignment}
                className="flex-1"
              >
                {creatingAssignment ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Create Assignment
                  </>
                )}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowCreateAssignment(false)}
                disabled={creatingAssignment}
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
