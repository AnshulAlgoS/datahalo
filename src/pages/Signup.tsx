// Signup Page
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, UserRole } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Loader2, GraduationCap, BookOpen } from "lucide-react";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [institution, setInstitution] = useState("");
  const [department, setDepartment] = useState("");
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<UserRole>("student");
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    try {
      setLoading(true);
      
      const additionalInfo = activeTab === "student" 
        ? { institution, studentId }
        : { institution, department };

      await signup(email, password, displayName, activeTab, additionalInfo);
      toast.success("Account created successfully!");
      navigate("/dashboard");
    } catch (error: any) {
      toast.error(error.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 relative overflow-hidden">
      {/* Animated background glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_hsl(191_100%_50%_/_0.1),_transparent_70%)] animate-glow-pulse" />
      
      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2 drop-shadow-[0_0_10px_hsl(191_100%_50%_/_0.5)]">
            DataHalo
          </h1>
          <p className="text-muted-foreground">
            Media Literacy Education Platform
          </p>
        </div>

        <Card className="shadow-[0_0_40px_hsl(191_100%_50%_/_0.2)] border-border/50 backdrop-blur-md bg-card/80">
          <CardHeader>
            <CardTitle className="text-2xl">Create Account</CardTitle>
            <CardDescription>
              Join thousands of students and teachers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as UserRole)} className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="student" className="flex items-center gap-2">
                  <GraduationCap className="w-4 h-4" />
                  Student
                </TabsTrigger>
                <TabsTrigger value="teacher" className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Teacher
                </TabsTrigger>
              </TabsList>

              <TabsContent value="student">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name-student">Full Name</Label>
                    <Input
                      id="name-student"
                      type="text"
                      placeholder="John Doe"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email-student">Email</Label>
                    <Input
                      id="email-student"
                      type="email"
                      placeholder="student@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="institution-student">Institution</Label>
                    <Input
                      id="institution-student"
                      type="text"
                      placeholder="Your college/university"
                      value={institution}
                      onChange={(e) => setInstitution(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="student-id">Student ID (Optional)</Label>
                    <Input
                      id="student-id"
                      type="text"
                      placeholder="Your student ID"
                      value={studentId}
                      onChange={(e) => setStudentId(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password-student">Password</Label>
                    <Input
                      id="password-student"
                      type="password"
                      placeholder="At least 6 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_20px_hsl(191_100%_50%_/_0.3)] hover:shadow-[0_0_30px_hsl(191_100%_50%_/_0.5)] transition-all" 
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Account...
                      </>
                    ) : (
                      "Create Student Account"
                    )}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="teacher">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name-teacher">Full Name</Label>
                    <Input
                      id="name-teacher"
                      type="text"
                      placeholder="Dr. Jane Smith"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email-teacher">Email</Label>
                    <Input
                      id="email-teacher"
                      type="email"
                      placeholder="teacher@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="institution-teacher">Institution</Label>
                    <Input
                      id="institution-teacher"
                      type="text"
                      placeholder="Your college/university"
                      value={institution}
                      onChange={(e) => setInstitution(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Input
                      id="department"
                      type="text"
                      placeholder="e.g., Mass Communication"
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password-teacher">Password</Label>
                    <Input
                      id="password-teacher"
                      type="password"
                      placeholder="At least 6 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_20px_hsl(191_100%_50%_/_0.3)] hover:shadow-[0_0_30px_hsl(191_100%_50%_/_0.5)] transition-all" 
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Account...
                      </>
                    ) : (
                      "Create Teacher Account"
                    )}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            <div className="mt-6 text-center text-sm">
              <p className="text-muted-foreground">
                Already have an account?{" "}
                <Link to="/login" className="text-primary hover:text-primary/80 font-semibold transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
