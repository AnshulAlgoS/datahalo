"use client";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { getApiBaseUrl } from "../config/api";
import {
  Search,
  Loader2,
  GraduationCap,
  BookOpen,
  Lightbulb,
  Users,
  AlertTriangle,
  CheckCircle,
  Brain,
  ExternalLink,
} from "lucide-react";

// Sample journalists for quick testing
const SAMPLE_JOURNALISTS = [
  { name: "Anderson Cooper", beat: "News Anchor, CNN" },
  { name: "Christiane Amanpour", beat: "International Correspondent" },
  { name: "Bob Woodward", beat: "Investigative Journalism" },
  { name: "Rachel Maddow", beat: "Political Commentary" },
  { name: "Ronan Farrow", beat: "Investigative Reporting" },
  { name: "Glenn Greenwald", beat: "Investigative Journalism" },
];

export default function JournalistAnalyzer() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState("");

  const addLog = (msg: string) =>
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const generateCaseStudy = async (targetName?: string) => {
    const journalistName = targetName || name;
    
    if (!journalistName.trim()) {
      setError("Please enter a journalist's name.");
      addLog("⚠️ No name entered.");
      return;
    }
    
    setError("");
    setLogs([]);
    setLoading(true);
    addLog(`SEARCH: Generating case study for "${journalistName}"...`);
    addLog("📚 This is an educational tool for journalism students");

    try {
      const apiUrl = `${getApiBaseUrl()}/generate-case-study`;
      addLog(`🔗 API URL: ${apiUrl}`);
      addLog("🌐 Scraping DuckDuckGo for comprehensive data...");
      addLog("NEWS: Searching for articles, awards, controversies...");
      
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ journalist_name: journalistName.trim() }),
        credentials: 'omit',
        mode: 'cors'
      });
      
      addLog(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        addLog(`❌ Error response: ${errorText}`);
        setError(`Case study generation failed (${response.status}): ${errorText}`);
        return;
      }
      
      const data = await response.json();
      addLog("CHECK: Case study generated successfully!");
      addLog(`STATS: Analyzed ${data.data_sources_count} data sources`);
      addLog("📝 Creating educational analysis...");
      
      // Store in sessionStorage and navigate
      sessionStorage.setItem(`case_study_${journalistName}`, JSON.stringify(data));
      addLog("🎓 Redirecting to case study...");
      
      setTimeout(() => {
        navigate(`/profile/${encodeURIComponent(journalistName)}`);
      }, 500);
      
    } catch (error: any) {
      console.error("Full error:", error);
      addLog(`❌ Network error: ${error.message}`);
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sampleName: string) => {
    setName(sampleName);
    generateCaseStudy(sampleName);
  };

  return (
    <div id="analyzer" className="max-w-6xl mx-auto mt-16 p-8 rounded-2xl shadow-xl bg-card/80 backdrop-blur-md border border-border space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center gap-3">
          <GraduationCap className="w-10 h-10 text-primary" />
          <h1 className="text-4xl font-orbitron font-bold text-primary">
            Journalist Case Study Generator
          </h1>
        </div>
        <p className="text-muted-foreground max-w-3xl mx-auto">
          Generate comprehensive educational case studies of journalists for students. 
          Like law students study landmark cases and famous lawyers, journalism students can study 
          real journalists' work, methods, ethics, and impact.
        </p>
      </motion.div>

      {/* Educational Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-primary/30"
      >
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary/20 rounded-xl flex-shrink-0">
            <BookOpen className="w-6 h-6 text-primary" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              What You'll Get
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Major works & investigative reporting analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Awards, recognition & career trajectory</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Ethical analysis & controversies</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Writing style & methodology breakdown</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Learning objectives & discussion questions</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Comparative analysis & practical applications</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Input Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            placeholder="Enter journalist name (e.g., Anderson Cooper)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && generateCaseStudy()}
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-md bg-background border border-border text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary transition-all duration-200 text-lg disabled:opacity-50"
          />
          <button
            onClick={() => generateCaseStudy()}
            disabled={loading || !name.trim()}
            className="px-8 py-3 rounded-md font-medium bg-primary text-primary-foreground hover:bg-primary/90 active:scale-95 transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2 min-w-[200px]"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <GraduationCap className="w-5 h-5" />
                Generate Case Study
              </>
            )}
          </button>
        </div>

        {/* Sample Journalists */}
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-primary" />
            Try these sample journalists for comprehensive case studies:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {SAMPLE_JOURNALISTS.map((journalist, idx) => (
              <button
                key={idx}
                onClick={() => loadSample(journalist.name)}
                disabled={loading}
                className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 border border-border/50 hover:border-primary/50 transition-all text-left group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-start gap-2">
                  <Users className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm group-hover:text-primary transition-colors truncate">
                      {journalist.name}
                    </div>
                    <div className="text-xs text-muted-foreground truncate">
                      {journalist.beat}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
          <div className="flex items-start gap-2">
            <Brain className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
            <p className="text-xs text-muted-foreground">
              <strong className="text-primary">How it works:</strong> Our AI-powered scraper searches
              DuckDuckGo for comprehensive information about the journalist, including articles, awards,
              controversies, interviews, and career background. Then, an AI journalism professor analyzes 
              this data to create an educational case study with learning objectives, discussion questions, 
              and practical applications - perfect for journalism courses and self-study.
            </p>
          </div>
        </div>
      </div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 rounded-xl bg-destructive/10 border border-destructive/30"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-destructive mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-destructive">Error</p>
                <p className="text-sm text-muted-foreground">{error}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading State */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50"
          >
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="relative">
                <Loader2 className="w-16 h-16 text-primary animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Search className="w-8 h-8 text-primary/50" />
                </div>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-2">Generating Case Study...</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  This may take 30-60 seconds as we:
                </p>
                <div className="space-y-2 text-xs text-muted-foreground max-w-md">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                    <span>Searching DuckDuckGo for articles and mentions</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '200ms' }} />
                    <span>Scraping major works and publications</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '400ms' }} />
                    <span>Finding awards, recognition, and controversies</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '600ms' }} />
                    <span>Analyzing writing style and methodology</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '800ms' }} />
                    <span>Generating comprehensive educational analysis</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Logs */}
      <div className="border border-border rounded-md p-4 max-h-64 overflow-y-auto font-mono text-xs bg-card/70 backdrop-blur-sm text-muted-foreground">
        <h3 className="font-semibold mb-2 text-primary text-sm font-orbitron border-b border-border pb-1 flex items-center gap-2">
          <ExternalLink className="w-4 h-4" />
          Live Progress Logs
        </h3>
        {logs.length > 0 ? (
          logs.map((log, idx) => (
            <div key={idx} className="whitespace-pre-wrap py-0.5">
              {log}
            </div>
          ))
        ) : (
          <p className="text-muted-foreground/50">No activity yet. Enter a journalist name to start.</p>
        )}
      </div>
    </div>
  );
}
