// Classes Management - List all classes
import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  BookOpen,
  Plus,
  Users,
  FileText,
  LogIn,
  ArrowLeft
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

export default function ClassesPage() {
  const { currentUser, userProfile, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Create Class Dialog
  const [showCreateClass, setShowCreateClass] = useState(false);
  const [newClass, setNewClass] = useState({
    title: "",
    description: "",
    subject: "Media Literacy"
  });
  const [creating, setCreating] = useState(false);
  
  // Join Class Dialog
  const [showJoinClass, setShowJoinClass] = useState(false);
  const [inviteCode, setInviteCode] = useState("");
  const [joining, setJoining] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const isTeacher = userProfile?.role === "teacher";

  useEffect(() => {
    if (currentUser) {
      loadClasses();
    }
  }, [currentUser]);

  const loadClasses = async () => {
    setLoading(true);
    try {
      const endpoint = isTeacher 
        ? `/lms/courses/teacher/${currentUser?.uid}`
        : `/lms/courses/student/${currentUser?.uid}`;
      
      const response = await axios.get(`${API_URL}${endpoint}`);
      setClasses(response.data.courses || []);
    } catch (error) {
      toast.error("Failed to load classes");
    } finally {
      setLoading(false);
    }
  };

  const createClass = async () => {
    if (!newClass.title.trim()) {
      toast.error("Please enter a class title");
      return;
    }

    setCreating(true);
    try {
      const response = await axios.post(`${API_URL}/lms/courses/create`, {
        teacher_id: currentUser?.uid,
        title: newClass.title,
        description: newClass.description,
        subject: newClass.subject
      });

      toast.success(`Class created! Invite code: ${response.data.invite_code}`);
      setShowCreateClass(false);
      setNewClass({ title: "", description: "", subject: "Media Literacy" });
      loadClasses();
    } catch (error) {
      toast.error("Failed to create class");
    } finally {
      setCreating(false);
    }
  };

  const joinClass = async () => {
    if (!inviteCode.trim()) {
      toast.error("Please enter an invite code");
      return;
    }

    setJoining(true);
    try {
      await axios.post(`${API_URL}/lms/enroll`, {
        student_id: currentUser?.uid,
        invite_code: inviteCode.toUpperCase()
      });

      toast.success("Successfully enrolled in class!");
      setShowJoinClass(false);
      setInviteCode("");
      loadClasses();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to join class");
    } finally {
      setJoining(false);
    }
  };

  useEffect(() => {
    if (!authLoading && (!currentUser || !userProfile)) {
      navigate("/login");
    }
  }, [authLoading, currentUser, userProfile, navigate]);

  if (authLoading || !currentUser || !userProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary/20 to-primary/10 border-b">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <Link to="/dashboard" className="flex items-center text-sm text-muted-foreground hover:text-primary mb-2">
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to Dashboard
              </Link>
              <h1 className="text-3xl font-bold">
                {isTeacher ? "My Classes" : "Enrolled Classes"}
              </h1>
              <p className="text-muted-foreground mt-2">
                {isTeacher 
                  ? "Manage your classes and assignments" 
                  : "View your classes and complete assignments"}
              </p>
            </div>
            
            <Button 
              onClick={() => isTeacher ? setShowCreateClass(true) : setShowJoinClass(true)}
              size="lg"
            >
              {isTeacher ? (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Class
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4 mr-2" />
                  Join Class
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Classes Grid */}
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading classes...</p>
          </div>
        ) : classes.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {classes.map((classItem) => (
              <Card 
                key={classItem._id} 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/class/${classItem._id}`)}
              >
                <CardHeader className="bg-gradient-to-br from-primary/10 to-transparent">
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-primary" />
                    {classItem.title}
                  </CardTitle>
                  <CardDescription>{classItem.description}</CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {classItem.student_count || classItem.students?.length || 0} Students
                      </span>
                      <span className="text-muted-foreground flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        {classItem.assignment_count || 0} Assignments
                      </span>
                    </div>
                    
                    {isTeacher && classItem.invite_code && (
                      <div className="p-2 bg-accent rounded text-center">
                        <p className="text-xs text-muted-foreground">Invite Code</p>
                        <p className="font-mono font-bold text-primary">{classItem.invite_code}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <BookOpen className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-xl font-semibold mb-2">
                {isTeacher ? "No classes yet" : "Not enrolled in any classes"}
              </h3>
              <p className="text-muted-foreground mb-6">
                {isTeacher 
                  ? "Create your first class to get started with teaching" 
                  : "Join a class using an invite code to access assignments"}
              </p>
              <Button onClick={() => isTeacher ? setShowCreateClass(true) : setShowJoinClass(true)}>
                {isTeacher ? "Create First Class" : "Join a Class"}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Create Class Dialog */}
      <Dialog open={showCreateClass} onOpenChange={setShowCreateClass}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Class</DialogTitle>
            <DialogDescription>
              Set up a new class for your students
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Class Name</Label>
              <Input
                value={newClass.title}
                onChange={(e) => setNewClass({ ...newClass, title: e.target.value })}
                placeholder="e.g., Media Literacy 101"
              />
            </div>

            <div>
              <Label>Description</Label>
              <Textarea
                value={newClass.description}
                onChange={(e) => setNewClass({ ...newClass, description: e.target.value })}
                placeholder="Brief description of the class..."
                rows={3}
              />
            </div>

            <div>
              <Label>Subject</Label>
              <Input
                value={newClass.subject}
                onChange={(e) => setNewClass({ ...newClass, subject: e.target.value })}
                placeholder="e.g., Media Literacy, Journalism"
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={createClass} disabled={creating} className="flex-1">
                {creating ? "Creating..." : "Create Class"}
              </Button>
              <Button variant="outline" onClick={() => setShowCreateClass(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Join Class Dialog */}
      <Dialog open={showJoinClass} onOpenChange={setShowJoinClass}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Join Class</DialogTitle>
            <DialogDescription>
              Enter the invite code provided by your teacher
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Invite Code</Label>
              <Input
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                placeholder="e.g., ABC123"
                maxLength={6}
                className="font-mono text-lg text-center"
              />
              <p className="text-xs text-muted-foreground mt-1">
                6-character code from your teacher
              </p>
            </div>

            <div className="flex gap-2">
              <Button onClick={joinClass} disabled={joining} className="flex-1">
                {joining ? "Joining..." : "Join Class"}
              </Button>
              <Button variant="outline" onClick={() => setShowJoinClass(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
