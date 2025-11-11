"use client";
import React, { useState } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
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

export default function JournalistAnalyzer() {
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
    addLog(`🚀 Sending "${name}" to backend...`);

    try {
      const response = await axios.post<AnalysisResponse>(
        "http://localhost:8000/analyze",
        { name: name.trim() },
        { timeout: 90000, headers: { "Content-Type": "application/json" } }
      );
      addLog("✅ Analysis received.");
      setAnalysis(response.data);
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message;
      setError(`Analysis failed: ${message}`);
      addLog(`❌ Error: ${message}`);
    } finally {
      setLoading(false);
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
  const credScore = aiProfile?.credibilityScore?.score || 0;
  const recScore = aiProfile?.recommendationScore?.overall || 0;

  return (
    <div className="max-w-6xl mx-auto mt-16 p-8 rounded-2xl shadow-xl bg-card/80 backdrop-blur-md border border-border space-y-8">
      {/* Header */}
      <motion.h1
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-orbitron font-bold text-primary mb-2 text-center"
      >
        Journalist Credibility Analyzer
      </motion.h1>
      <p className="text-center text-muted-foreground mb-6">
        Enter a journalist's name to fetch profile, articles, and AI-based
        credibility analysis.
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
              <h2 className="text-3xl font-semibold text-primary font-orbitron border-b border-border pb-2">
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
                    Credibility Score
                  </p>
                  <p className="text-3xl font-bold text-blue-500">
                    {credScore}/100
                  </p>
                </div>
                <Target size={32} className="text-blue-500/50" />
              </div>
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

          {/* Expandable Detailed Analysis */}
          <div className="border-t border-border pt-4">
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-2 text-primary font-medium hover:underline mb-3"
            >
              {expanded ? (
                <>
                  <ChevronUp size={16} /> Hide Detailed Analysis
                </>
              ) : (
                <>
                  <ChevronDown size={16} /> View Detailed Analysis
                </>
              )}
            </button>

            <AnimatePresence>
              {expanded && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="space-y-6"
                >
                  {/* Career Highlights */}
                  {aiProfile.careerHighlights &&
                    aiProfile.careerHighlights.length > 0 && (
                      <div className="p-4 bg-muted/30 rounded-lg border border-border">
                        <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                          <Award size={18} /> Career Highlights
                        </h4>
                        <ul className="space-y-2">
                          {aiProfile.careerHighlights.map((highlight, i) => (
                            <li
                              key={i}
                              className="text-sm text-foreground flex items-start gap-2"
                            >
                              <span className="text-primary mt-1">•</span>
                              {highlight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Main Topics */}
                  {aiProfile.mainTopics && aiProfile.mainTopics.length > 0 && (
                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                      <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                        <FileText size={18} /> Main Topics Covered
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {aiProfile.mainTopics.map((topic, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm border border-primary/30"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Credibility Assessment */}
                  <div className="p-4 bg-muted/30 rounded-lg border border-border">
                    <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                      <Target size={18} /> Credibility Assessment
                    </h4>
                    <p className="text-sm text-foreground mb-3">
                      {aiProfile.credibilityScore?.reasoning}
                    </p>
                    {aiProfile.recommendationScore?.strengths &&
                      aiProfile.recommendationScore.strengths.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs font-semibold text-green-600 mb-1">
                            Strengths:
                          </p>
                          <ul className="space-y-1">
                            {aiProfile.recommendationScore.strengths.map(
                              (strength, i) => (
                                <li
                                  key={i}
                                  className="text-xs text-foreground flex items-start gap-2"
                                >
                                  <span className="text-green-500">✓</span>
                                  {strength}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    {aiProfile.recommendationScore?.concerns &&
                      aiProfile.recommendationScore.concerns.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs font-semibold text-orange-600 mb-1">
                            Concerns:
                          </p>
                          <ul className="space-y-1">
                            {aiProfile.recommendationScore.concerns.map(
                              (concern, i) => (
                                <li
                                  key={i}
                                  className="text-xs text-foreground flex items-start gap-2"
                                >
                                  <span className="text-orange-500">⚠</span>
                                  {concern}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                  </div>

                  {/* Political Affiliation */}
                  {aiProfile.politicalAffiliation && (
                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                      <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                        <Users size={18} /> Political Affiliation
                      </h4>
                      <p className="text-sm text-foreground leading-relaxed">
                        <strong>Primary Affiliation:</strong>{" "}
                        {aiProfile.politicalAffiliation.primary}
                      </p>
                      <p className="text-sm text-foreground leading-relaxed">
                        <strong>Confidence:</strong>{" "}
                        {aiProfile.politicalAffiliation.confidence}
                      </p>
                      <p className="text-sm text-foreground leading-relaxed">
                        <strong>Evidence:</strong> {aiProfile.politicalAffiliation.evidence}
                      </p>
                    </div>
                  )}

                  {/* Notable Works */}
                  {aiProfile.notableWorks &&
                    aiProfile.notableWorks.length > 0 && (
                      <div className="p-4 bg-muted/30 rounded-lg border border-border">
                        <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                          <Newspaper size={18} /> Notable Works
                        </h4>
                        <ul className="space-y-3">
                          {aiProfile.notableWorks.map((work, i) => (
                            <li
                              key={i}
                              className="p-3 rounded-md border border-border bg-background/50 hover:bg-background/80 transition"
                            >
                              <a
                                href={work.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-medium hover:underline text-primary"
                              >
                                {work.title}
                              </a>
                              {work.year && (
                                <span className="text-xs text-muted-foreground ml-2">
                                  ({work.year})
                                </span>
                              )}
                              <p className="text-xs text-muted-foreground mt-1">
                                {work.impact}
                              </p>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Awards */}
                  {aiProfile.awards && aiProfile.awards.length > 0 && (
                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                      <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                        <Award size={18} /> Awards & Recognition
                      </h4>
                      <ul className="space-y-1">
                        {aiProfile.awards.map((award, i) => (
                          <li
                            key={i}
                            className="text-sm text-foreground flex items-start gap-2"
                          >
                            <span className="text-yellow-500">🏆</span>
                            {award}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Controversies */}
                  {aiProfile.controversies &&
                    aiProfile.controversies.length > 0 && (
                      <div className="p-4 bg-muted/30 rounded-lg border border-border">
                        <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                          <AlertTriangle size={18} /> Controversies
                        </h4>
                        <ul className="space-y-3">
                          {aiProfile.controversies.map((controversy, i) => (
                            <li
                              key={i}
                              className="p-3 rounded-md border border-orange-500/30 bg-orange-500/5"
                            >
                              <div className="flex items-start gap-2">
                                <span
                                  className={`text-xs font-semibold px-2 py-0.5 rounded ${
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
                                  <p className="text-sm text-foreground">
                                    {controversy.description}
                                  </p>
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Source: {controversy.source}
                                  </p>
                                </div>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Ethical Assessment */}
                  {aiProfile.ethicalAssessment && (
                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                      <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                        <Users size={18} /> Ethical Assessment
                      </h4>
                      <p className="text-sm text-foreground leading-relaxed whitespace-pre-line">
                        {aiProfile.ethicalAssessment}
                      </p>
                    </div>
                  )}

                  {/* Tone Analysis */}
                  {aiProfile.toneAnalysis && (
                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                      <h4 className="font-semibold text-primary mb-3">
                        Tone Analysis
                      </h4>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <p className="text-muted-foreground">
                            <strong>Emotional Tone:</strong>{" "}
                            {aiProfile.toneAnalysis.emotionalTone}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">
                            <strong>Bias:</strong>{" "}
                            {aiProfile.toneAnalysis.bias}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">
                            <strong>Objectivity:</strong>{" "}
                            {aiProfile.toneAnalysis.objectivity}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">
                            <strong>Consistency:</strong>{" "}
                            {aiProfile.toneAnalysis.consistency}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Key Articles */}
                  {articles.length > 0 && (
                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                      <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
                        <Newspaper size={18} /> Key Articles
                      </h4>
                      <ul className="space-y-3">
                        {articles.map((article, i) => (
                          <li
                            key={i}
                            className="p-3 rounded-md border border-border bg-background/50 hover:bg-background/80 transition"
                          >
                            <a
                              href={article.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-medium hover:underline text-primary"
                            >
                              {article.title}
                            </a>
                            <p className="text-xs text-muted-foreground mt-1">
                              {article.date && `Published: ${article.date} • `}
                              {article.significance}
                            </p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Final Recommendation */}
                  {aiProfile.recommendationScore?.reasoning && (
                    <div className="p-4 bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg border border-primary/30">
                      <h4 className="font-semibold text-primary mb-2">
                        Final Recommendation
                      </h4>
                      <p className="text-sm text-foreground">
                        {aiProfile.recommendationScore.reasoning}
                      </p>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
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
