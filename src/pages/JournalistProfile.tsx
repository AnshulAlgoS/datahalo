"use client";
import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ExternalLink,
  Award,
  AlertTriangle,
  Newspaper,
  Users,
  Target,
  TrendingUp,
  FileText,
  Link as LinkIcon,
  Calendar,
  CheckCircle,
  XCircle,
  BarChart3,
  PieChart,
} from "lucide-react";

interface AnalysisData {
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
    credibilityScore: {
      score: number;
      reasoning: string;
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

export default function JournalistProfile() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProfileData = async () => {
      if (!name) {
        navigate("/");
        return;
      }

      try {
        setLoading(true);
        
        // First, try to get data from sessionStorage
        const storedData = sessionStorage.getItem(`journalist_${name}`);
        if (storedData) {
          setData(JSON.parse(storedData));
          setLoading(false);
          return;
        }

        // If not in sessionStorage, fetch from API
        const API_URL = import.meta.env.VITE_API_URL || "https://datahalo.onrender.com" || "http://localhost:8000";
        const response = await fetch(`${API_URL}/journalist/${encodeURIComponent(name)}`);
        
        if (!response.ok) {
          throw new Error("Failed to fetch journalist data");
        }

        const apiData = await response.json();
        
        if (apiData.status === "success" && apiData.journalist) {
          // Transform API response to match expected format
          const profileData: AnalysisData = {
            status: "success",
            journalist: apiData.journalist.name,
            articlesAnalyzed: apiData.journalist.articlesAnalyzed,
            aiProfile: apiData.journalist.aiProfile
          };
          
          setData(profileData);
          
          // Store in sessionStorage for future use
          sessionStorage.setItem(`journalist_${name}`, JSON.stringify(profileData));
        } else {
          throw new Error("Invalid data received from server");
        }
      } catch (err) {
        console.error("Error fetching profile:", err);
        setError("Failed to load profile. The journalist may not be analyzed yet.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, [name, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-xl mb-4">
            <AlertTriangle className="w-16 h-16 text-destructive mx-auto" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Profile Not Found</h2>
          <p className="text-muted-foreground mb-6">
            {error || "This journalist hasn't been analyzed yet."}
          </p>
          <button
            onClick={() => navigate("/")}
            className="px-6 py-3 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg font-semibold transition-colors"
          >
            Go to Analyzer
          </button>
        </div>
      </div>
    );
  }

  const aiProfile = data.aiProfile;
  const credScore = aiProfile.credibilityScore?.score || 0;
  const recScore = aiProfile.recommendationScore?.overall || 0;

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-green-500";
    if (score >= 50) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 75) return "from-green-500/10 to-green-600/10 border-green-500/30";
    if (score >= 50) return "from-yellow-500/10 to-yellow-600/10 border-yellow-500/30";
    return "from-red-500/10 to-red-600/10 border-red-500/30";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-card/80 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <button
            onClick={() => {
              navigate('/');
              // Wait for navigation to complete, then scroll to analyzer
              setTimeout(() => {
                const analyzerElement = document.getElementById('analyzer');
                if (analyzerElement) {
                  analyzerElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              }, 100);
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 transition-all duration-300 text-foreground hover:text-primary"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Analyzer</span>
          </button>
          <h1 className="text-xl font-orbitron font-bold text-primary">
            DataHalo Profile
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card/90 rounded-2xl shadow-xl border border-border p-8"
        >
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {/* Profile Image */}
            <motion.img
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              src={aiProfile.digitalPresence?.profileImage || "/placeholder.jpg"}
              alt={aiProfile.name}
              className="w-40 h-40 rounded-full object-cover border-4 border-primary shadow-2xl"
              onError={(e) => {
                (e.target as HTMLImageElement).src = "/placeholder.jpg";
              }}
            />

            {/* Profile Info */}
            <div className="flex-1 text-center md:text-left space-y-4">
              <h2 className="text-4xl font-orbitron font-bold text-primary">
                {aiProfile.name}
              </h2>
              
              {/* Badges */}
              <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/30">
                  {aiProfile.writingTone}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-500 border border-blue-500/30">
                  {aiProfile.ideologicalBias}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-500 border border-purple-500/30">
                  {aiProfile.digitalPresence?.onlineReach} Reach
                </span>
              </div>

              {/* Bio */}
              <p className="text-muted-foreground leading-relaxed max-w-3xl">
                {aiProfile.biography}
              </p>

              {/* Social Links */}
              {aiProfile.digitalPresence?.verifiedLinks?.length > 0 && (
                <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                  {aiProfile.digitalPresence.verifiedLinks.map((link, i) => (
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
                <div className="pt-2">
                  <p className="text-sm text-muted-foreground">
                    <strong>Media Affiliations:</strong>{" "}
                    {aiProfile.digitalPresence.mediaAffiliations.join(", ")}
                  </p>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Score Dashboard */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Credibility Score */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className={`p-6 rounded-xl bg-gradient-to-br ${getScoreBgColor(credScore)} border shadow-lg`}
          >
            <div className="flex items-center justify-between mb-2">
              <Target size={24} className="text-blue-500" />
              <span className="text-xs font-semibold text-muted-foreground">CREDIBILITY</span>
            </div>
            <div className={`text-4xl font-bold ${getScoreColor(credScore)}`}>
              {credScore}/100
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {credScore >= 75 ? "Highly Credible" : credScore >= 50 ? "Moderately Credible" : "Low Credibility"}
            </p>
          </motion.div>

          {/* Recommendation Score */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className={`p-6 rounded-xl bg-gradient-to-br ${getScoreBgColor(recScore)} border shadow-lg`}
          >
            <div className="flex items-center justify-between mb-2">
              <TrendingUp size={24} className="text-green-500" />
              <span className="text-xs font-semibold text-muted-foreground">RECOMMENDATION</span>
            </div>
            <div className={`text-4xl font-bold ${getScoreColor(recScore)}`}>
              {recScore}/100
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {recScore >= 75 ? "Highly Recommended" : recScore >= 50 ? "Recommended" : "Use Caution"}
            </p>
          </motion.div>

          {/* Articles Analyzed */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-6 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/30 shadow-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <Newspaper size={24} className="text-purple-500" />
              <span className="text-xs font-semibold text-muted-foreground">ARTICLES</span>
            </div>
            <div className="text-4xl font-bold text-purple-500">
              {aiProfile.articlesAnalyzed?.total || data.articlesAnalyzed || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Analyzed & Verified
            </p>
          </motion.div>

          {/* Influence Level */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="p-6 rounded-xl bg-gradient-to-br from-orange-500/10 to-orange-600/10 border border-orange-500/30 shadow-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <Users size={24} className="text-orange-500" />
              <span className="text-xs font-semibold text-muted-foreground">INFLUENCE</span>
            </div>
            <div className="text-2xl font-bold text-orange-500">
              {aiProfile.engagementInsights?.influenceLevel || "Moderate"}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Overall Reach & Impact
            </p>
          </motion.div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Career Highlights */}
            {aiProfile.careerHighlights && aiProfile.careerHighlights.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
              >
                <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                  <Award size={20} />
                  Career Highlights
                </h3>
                <ul className="space-y-3">
                  {aiProfile.careerHighlights.map((highlight, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle size={16} className="text-green-500 mt-1 flex-shrink-0" />
                      <span className="text-sm text-foreground">{highlight}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}

            {/* Main Topics */}
            {aiProfile.mainTopics && aiProfile.mainTopics.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
              >
                <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                  <FileText size={20} />
                  Coverage Areas
                </h3>
                <div className="flex flex-wrap gap-2">
                  {aiProfile.mainTopics.map((topic, i) => (
                    <span
                      key={i}
                      className="px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-medium border border-primary/30"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Political Affiliation */}
            {aiProfile.politicalAffiliation && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
              >
                <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                  <Users size={20} />
                  Political Affiliation
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm font-semibold text-muted-foreground">Primary:</span>
                    <span className="text-sm font-bold text-foreground">{aiProfile.politicalAffiliation.primary}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm font-semibold text-muted-foreground">Confidence:</span>
                    <span className="text-sm font-bold text-foreground">{aiProfile.politicalAffiliation.confidence}</span>
                  </div>
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs font-semibold text-muted-foreground mb-1">Evidence:</p>
                    <p className="text-sm text-foreground">{aiProfile.politicalAffiliation.evidence}</p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Awards */}
            {aiProfile.awards && aiProfile.awards.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
              >
                <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                  <Award size={20} />
                  Awards & Recognition
                </h3>
                <ul className="space-y-2">
                  {aiProfile.awards.map((award, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-yellow-500 text-lg">🏆</span>
                      <span className="text-sm text-foreground">{award}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Credibility Assessment */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
            >
              <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                <Target size={20} />
                Credibility Assessment
              </h3>
              <p className="text-sm text-foreground mb-4">
                {aiProfile.credibilityScore?.reasoning}
              </p>
              
              {/* Strengths */}
              {aiProfile.recommendationScore?.strengths && aiProfile.recommendationScore.strengths.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-semibold text-green-600 mb-2">✓ Strengths:</p>
                  <ul className="space-y-1">
                    {aiProfile.recommendationScore.strengths.map((strength, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                        <span className="text-green-500">•</span>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Concerns */}
              {aiProfile.recommendationScore?.concerns && aiProfile.recommendationScore.concerns.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-orange-600 mb-2">⚠ Concerns:</p>
                  <ul className="space-y-1">
                    {aiProfile.recommendationScore.concerns.map((concern, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                        <span className="text-orange-500">•</span>
                        {concern}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>

            {/* Tone Analysis */}
            {aiProfile.toneAnalysis && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
              >
                <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                  <BarChart3 size={20} />
                  Tone Analysis
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">Emotional Tone</p>
                    <p className="text-sm font-semibold text-foreground">{aiProfile.toneAnalysis.emotionalTone}</p>
                  </div>
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">Bias</p>
                    <p className="text-sm font-semibold text-foreground">{aiProfile.toneAnalysis.bias}</p>
                  </div>
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">Objectivity</p>
                    <p className="text-sm font-semibold text-foreground">{aiProfile.toneAnalysis.objectivity}</p>
                  </div>
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">Consistency</p>
                    <p className="text-sm font-semibold text-foreground">{aiProfile.toneAnalysis.consistency}</p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Engagement Insights */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
            >
              <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                <PieChart size={20} />
                Engagement Insights
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm text-muted-foreground">Audience Sentiment:</span>
                  <span className="text-sm font-semibold text-foreground">{aiProfile.engagementInsights?.audienceSentiment}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm text-muted-foreground">Influence Level:</span>
                  <span className="text-sm font-semibold text-foreground">{aiProfile.engagementInsights?.influenceLevel}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm text-muted-foreground">Controversy Level:</span>
                  <span className="text-sm font-semibold text-foreground">{aiProfile.engagementInsights?.controversyLevel}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm text-muted-foreground">Trustworthiness:</span>
                  <span className="text-sm font-semibold text-foreground">{aiProfile.engagementInsights?.trustworthiness}</span>
                </div>
              </div>
            </motion.div>

            {/* Controversies */}
            {aiProfile.controversies && aiProfile.controversies.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
              >
                <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                  <AlertTriangle size={20} />
                  Controversies
                </h3>
                <ul className="space-y-3">
                  {aiProfile.controversies.map((controversy, i) => (
                    <li
                      key={i}
                      className="p-4 rounded-lg border border-orange-500/30 bg-orange-500/5"
                    >
                      <div className="flex items-start gap-3">
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            controversy.severity === "High"
                              ? "bg-red-500/20 text-red-500"
                              : controversy.severity === "Medium"
                              ? "bg-orange-500/20 text-orange-500"
                              : "bg-yellow-500/20 text-yellow-500"
                          }`}
                        >
                          {controversy.severity}
                        </span>
                        <div className="flex-1">
                          <p className="text-sm text-foreground mb-1">{controversy.description}</p>
                          <p className="text-xs text-muted-foreground">Source: {controversy.source}</p>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </div>
        </div>

        {/* Full Width Sections */}
        <div className="space-y-6">
          {/* Notable Works */}
          {aiProfile.notableWorks && aiProfile.notableWorks.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
            >
              <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                <Newspaper size={20} />
                Notable Works
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {aiProfile.notableWorks.map((work, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-lg border border-border bg-background/50 hover:bg-background/80 transition"
                  >
                    <a
                      href={work.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium hover:underline text-primary flex items-start gap-2"
                    >
                      <span className="flex-1">{work.title}</span>
                      <ExternalLink size={16} className="flex-shrink-0 mt-1" />
                    </a>
                    {work.year && (
                      <p className="text-xs text-muted-foreground mt-1">
                        <Calendar size={12} className="inline mr-1" />
                        {work.year}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground mt-2">{work.impact}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Key Articles */}
          {aiProfile.articlesAnalyzed?.keyArticles && aiProfile.articlesAnalyzed.keyArticles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
            >
              <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                <FileText size={20} />
                Key Articles Analyzed
              </h3>
              <div className="space-y-3">
                {aiProfile.articlesAnalyzed.keyArticles.map((article, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-lg border border-border bg-background/50 hover:bg-background/80 transition"
                  >
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium hover:underline text-primary flex items-start gap-2"
                    >
                      <span className="flex-1">{article.title}</span>
                      <ExternalLink size={16} className="flex-shrink-0 mt-1" />
                    </a>
                    <p className="text-xs text-muted-foreground mt-2">
                      {article.date && (
                        <>
                          <Calendar size={12} className="inline mr-1" />
                          {article.date} •{" "}
                        </>
                      )}
                      {article.significance}
                    </p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Ethical Assessment */}
          {aiProfile.ethicalAssessment && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-card/90 rounded-xl border border-border p-6 shadow-lg"
            >
              <h3 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                <Users size={20} />
                Ethical Assessment
              </h3>
              <p className="text-sm text-foreground leading-relaxed whitespace-pre-line">
                {aiProfile.ethicalAssessment}
              </p>
            </motion.div>
          )}

          {/* Final Recommendation */}
          {aiProfile.recommendationScore?.reasoning && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-xl border border-primary/30 p-6 shadow-lg"
            >
              <h3 className="text-xl font-semibold text-primary mb-4">
                Final Recommendation
              </h3>
              <p className="text-sm text-foreground">
                {aiProfile.recommendationScore.reasoning}
              </p>
            </motion.div>
          )}
        </div>

        {/* Metadata Footer */}
        {aiProfile._metadata && (
          <div className="bg-card/50 rounded-xl border border-border p-4 text-xs text-muted-foreground">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="font-semibold">Analysis Date:</span>
                <br />
                {new Date(aiProfile._metadata.analysis_timestamp).toLocaleDateString()}
              </div>
              <div>
                <span className="font-semibold">Data Sources:</span>
                <br />
                {aiProfile._metadata.data_sources} sources
              </div>
              <div>
                <span className="font-semibold">Verification Rate:</span>
                <br />
                {aiProfile._metadata.verification_rate}%
              </div>
              <div>
                <span className="font-semibold">Automated Scores:</span>
                <br />
                Tone: {aiProfile._metadata.automated_scores.tone}/10
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
