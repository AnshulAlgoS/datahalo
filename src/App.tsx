import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import JournalistProfile from "./pages/JournalistProfile";
import NotFound from "./pages/NotFound";
import JournalistsGallery from "./pages/JournalistsGallery";
import NarrativeAnalyzer from "./pages/NarrativeAnalyzer";
import ArticleAnalyzer from "./pages/ArticleAnalyzer";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import ClassesPage from "./pages/ClassesPage";
import ClassroomPage from "./pages/ClassroomPage";
import SourceVerifier from "./pages/SourceVerifier";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Index />} />
            <Route path="/profile/:name" element={<JournalistProfile />} />
            <Route path="/journalists" element={<JournalistsGallery />} />
            <Route path="/narrative-analyzer" element={<NarrativeAnalyzer />} />
            <Route path="/article-analyzer" element={<ArticleAnalyzer />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            
            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/classes"
              element={
                <ProtectedRoute>
                  <ClassesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/class/:classId"
              element={
                <ProtectedRoute>
                  <ClassroomPage />
                </ProtectedRoute>
              }
            />
            <Route path="/source-verifier" element={<SourceVerifier />} />
            
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
