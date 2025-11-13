"use client";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { buildApiUrl, API_ENDPOINTS } from "../config/api";
import {
  ChevronDown,
  ChevronUp,
  Link as LinkIcon,
  Newspaper,
  Award,
  AlertTriangle,
  TrendingUp,
  Users,
  FileText,
  Target,
  ExternalLink,
} from "lucide-react";

interface AnalysisResponse {
  status: string;
  journalist: string;
  articlesAnalyzed: number;
  aiProfile: {
    name: string;
    biography: string;
    careerHighlights: string[];
    mainTopics: string[];
    writingTone: string;
    ideologicalBias: string;
    politicalAffiliation?: {
      primary: string;
      confidence: string;
      evidence: string;
    };
    haloScore: {
      score: number;
      level: string;
      description: string;
    };
    notableWorks: Array<{
      title: string;
      url: string;
      impact: string;
      year?: string;
    }>;
    awards: string[];
    controversies: Array<{
      description: string;
      severity: string;
      source: string;
    }>;
    digitalPresence: {
      profileImage: string;
      verifiedLinks: Array<{
        platform: string;
        handle: string;
        url: string;
      }>;
      mediaAffiliations: string[];
      onlineReach: string;
    };
    engagementInsights: {
      audienceSentiment: string;
      influenceLevel: string;
      controversyLevel: string;
      trustworthiness: string;
    };
    ethicalAssessment: string;
    articlesAnalyzed: {
      total: number;
      verificationRate: string;
      topDomains: string[];
      dateRange: string;
      keyArticles: Array<{
        title: string;
        url: string;
        date: string;
        significance: string;
      }>;
    };
    toneAnalysis: {
      emotionalTone: string;
      bias: string;
      objectivity: string;
      consistency: string;
    };
    recommendationScore: {
      overall: number;
      reasoning: string;
      strengths: string[];
      concerns: string[];
    };
    _metadata?: {
      analysis_timestamp: string;
      data_sources: number;
      verification_rate: number;
      automated_scores: {
        tone: number;
        bias: string;
        controversy: number;
        credibility: number;
      };
    };
  };
}

export default function JournalistAnalyzer() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState(false);

  const addLog = (msg: string) =>
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const analyzeJournalist = async () => {
    if (!name.trim()) {
      setError("Please enter a journalist's name.");
      addLog("⚠️ No name entered.");
      return;
    }
    setError("");
    setAnalysis(null);
    setLogs([]);
    setExpanded(false);
    setLoading(true);
    addLog(`🚀 Analyzing "${name}"...`);

    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.ANALYZE);
      addLog(`🔗 API URL: ${apiUrl}`);
      
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ name: name.trim() }),
        credentials: 'omit', // Don't send cookies for CORS
        mode: 'cors' // Explicit CORS mode
      });
      
      addLog(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        addLog(`❌ Error response: ${errorText}`);
        setError(`Analysis failed (${response.status}): ${errorText}`);
        return;
      }
      
      const data = await response.json();
      addLog("✅ Analysis received successfully!");
      setAnalysis(data);
      
    } catch (error: any) {
      console.error("Full error:", error);
      addLog(`❌ Network error: ${error.message}`);
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const viewDetailedProfile = () => {
    if (analysis && analysis.aiProfile) {
      // Store analysis data in sessionStorage
      sessionStorage.setItem(`journalist_${analysis.aiProfile.name}`, JSON.stringify(analysis));
      // Navigate to profile page
      navigate(`/profile/${encodeURIComponent(analysis.aiProfile.name)}`);
    }
  };

  // Extract data from AI profile
  const aiProfile = analysis?.aiProfile;
  const journalistName = aiProfile?.name || analysis?.journalist || name;
  const biography = aiProfile?.biography || "No biography available.";
  const profileImage =
    aiProfile?.digitalPresence?.profileImage || "/placeholder.jpg";
  const socialLinks = aiProfile?.digitalPresence?.verifiedLinks || [];
  const articles = aiProfile?.articlesAnalyzed?.keyArticles || [];
  const haloScore = aiProfile?.haloScore?.score || 0;
  const haloLevel = aiProfile?.haloScore?.level || "Unknown";
  const haloDescription = aiProfile?.haloScore?.description || "";
  const recScore = aiProfile?.recommendationScore?.overall || 0;

  return (
    <div id="analyzer" className="max-w-6xl mx-auto mt-16 p-8 rounded-2xl shadow-xl bg-card/80 backdrop-blur-md border border-border space-y-8">
      {/* Header */}
      <motion.h1
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-orbitron font-bold text-primary mb-2 text-center"
      >
        Journalist Profile Analyzer
      </motion.h1>
      <p className="text-center text-muted-foreground mb-6">
        Enter a journalist's name to fetch profile, articles, and AI-based transparency analysis.
      </p>

      {/* Input Section */}
      <div className="flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Enter journalist name (e.g., Barkha Dutt)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && analyzeJournalist()}
          className="flex-1 px-4 py-3 rounded-md bg-background border border-border text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary transition-all duration-200"
        />
        <button
          onClick={analyzeJournalist}
          disabled={loading}
          className="px-6 py-3 rounded-md font-medium bg-primary text-primary-foreground hover:bg-primary/90 active:scale-95 transition-all duration-200 disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 rounded-md bg-destructive/20 border border-destructive text-destructive text-sm text-center">
          {error}
        </div>
      )}

      {/* Analysis Result */}
      {analysis && aiProfile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-border bg-card/90 shadow-md p-6 space-y-6"
        >
          {/* Profile Header */}
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            <motion.img
              src={profileImage}
              alt={journalistName}
              className="w-32 h-32 rounded-full object-cover border-2 border-primary shadow-lg"
              onError={(e) => {
                (e.target as HTMLImageElement).src = "/placeholder.jpg";
              }}
            />
            <div className="flex-1 space-y-3">
              <h2 className="text-3xl font-semibold text-primary border-b border-border pb-2">
                {journalistName}
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                {biography}
              </p>

              {/* Social Links */}
              {socialLinks.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {socialLinks.map((link, i) => (
                    <a
                      key={i}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-md bg-muted hover:bg-muted/60 border border-border transition-colors"
                    >
                      <LinkIcon size={12} />
                      {link.platform}: @{link.handle}
                    </a>
                  ))}
                </div>
              )}

              {/* Media Affiliations */}
              {aiProfile.digitalPresence?.mediaAffiliations?.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm text-muted-foreground">
                    <strong>Media Affiliations:</strong>{" "}
                    {aiProfile.digitalPresence.mediaAffiliations.join(", ")}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Score Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Halo Score
                  </p>
                  <p className="text-3xl font-bold text-blue-500">
                    {haloScore}/100
                  </p>
                  <p className="text-xs text-blue-400 font-medium">
                    {haloLevel}
                  </p>
                </div>
                <Target size={32} className="text-blue-500/50" />
              </div>
              {haloDescription && (
                <p className="text-xs text-muted-foreground mt-2">
                  {haloDescription}
                </p>
              )}
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Recommendation
                  </p>
                  <p className="text-3xl font-bold text-green-500">
                    {recScore}/100
                  </p>
                </div>
                <TrendingUp size={32} className="text-green-500/50" />
              </div>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Articles Analyzed
                  </p>
                  <p className="text-3xl font-bold text-purple-500">
                    {aiProfile.articlesAnalyzed?.total || analysis.articlesAnalyzed || 0}
                  </p>
                </div>
                <Newspaper size={32} className="text-purple-500/50" />
              </div>
            </div>
          </div>

          {/* Quick Insights */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t border-border pt-4">
            <div>
              <h3 className="text-sm font-semibold text-primary mb-2">
                Writing Style
              </h3>
              <p className="text-sm text-muted-foreground">
                <strong>Tone:</strong> {aiProfile.writingTone || "N/A"}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Bias:</strong> {aiProfile.ideologicalBias || "N/A"}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-primary mb-2">
                Digital Presence
              </h3>
              <p className="text-sm text-muted-foreground">
                <strong>Reach:</strong>{" "}
                {aiProfile.digitalPresence?.onlineReach || "N/A"}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Influence:</strong>{" "}
                {aiProfile.engagementInsights?.influenceLevel || "N/A"}
              </p>
            </div>
          </div>

          {/* View Detailed Profile Button */}
          <div className="border-t border-border pt-4">
            <button
              onClick={viewDetailedProfile}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-md font-medium bg-primary text-primary-foreground hover:bg-primary/90 active:scale-95 transition-all duration-200"
            >
              <ExternalLink size={16} />
              View Detailed Profile
            </button>
          </div>
        </motion.div>
      )}

      {/* Logs */}
      <div className="mt-10 border border-border rounded-md p-4 max-h-64 overflow-y-auto font-mono text-xs bg-card/70 backdrop-blur-sm text-muted-foreground">
        <h3 className="font-semibold mb-2 text-primary text-sm font-orbitron border-b border-border pb-1">
          Live Logs
        </h3>
        {logs.length > 0 ? (
          logs.map((log, idx) => (
            <div key={idx} className="whitespace-pre-wrap">
              {log}
            </div>
          ))
        ) : (
          <p>No logs yet.</p>
        )}
      </div>
    </div>
  );
}
