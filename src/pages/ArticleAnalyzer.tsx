import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  FileText,
  Zap,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Users,
  Target,
  BookOpen,
  Lightbulb,
  Award,
  BarChart3,
  Eye,
  Link as LinkIcon,
  Loader2,
  Download,
  Share2,
  PlayCircle,
  ExternalLink,
  GraduationCap,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getApiBaseUrl } from "@/config/api";

const API_URL = getApiBaseUrl();

interface ScoreBreakdown {
  objectivity: number;
  source_quality: number;
  factual_accuracy: number;
  writing_clarity: number;
  ethical_standards: number;
  bias_control: number;
  structure_flow: number;
  headline_quality: number;
}

interface DetailedIssue {
  category: string;
  severity: "high" | "medium" | "low";
  issue: string;
  location?: string;
  suggestion: string;
  example?: string;
}

interface ImprovementAction {
  priority: "high" | "medium" | "low";
  issue: string;
  how_to_fix: string;
  before?: string;
  after?: string;
}

interface LearningResource {
  type: "video" | "article" | "course" | "tool";
  title: string;
  url: string;
  platform: string;
}

interface LearningRecommendation {
  module: string;
  reason: string;
  link?: string;
  resources?: LearningResource[];
}

interface AnalysisResult {
  overall_score: number;
  letter_grade: string;
  confidence?: number;
  confidence_explanation?: string;
  warnings?: string[];
  score_breakdown: ScoreBreakdown;
  strengths: string[];
  critical_issues: string[];
  detailed_issues: DetailedIssue[];
  improvement_actions: ImprovementAction[];
  learning_recommendations: LearningRecommendation[];
  article_stats: {
    word_count: number;
    sentence_count: number;
    paragraph_count: number;
    avg_sentence_length: number;
    readability_score: number;
    syllables_per_word?: number;
  };
  methodology?: {
    scoring_system: string;
    weights: Record<string, string>;
    standards_based_on: string[];
    accuracy_note: string;
  };
  ai_insights?: {
    framing_analysis?: string;
    missing_perspectives?: string[];
    logical_issues?: string[];
    contextual_concerns?: string[];
    credibility_assessment?: string;
    improvement_priority?: string;
    grade_justification?: string;
  };
}

const SAMPLE_ARTICLES = [
  {
    title: "Campus Protest Coverage",
    text: `Students staged a shocking protest at the university yesterday, demanding immediate action on climate change. The outrageous demonstration blocked traffic for hours.

Over 500 angry protesters gathered at noon, waving signs and chanting slogans. Campus security struggled to control the massive crowd as tensions escalated dramatically.

According to student leader Sarah, "We need change now." The university administration has not responded to requests for comment.

The protest was organized by environmental activists who claim the university is not doing enough to combat climate change. Critics say the protesters are disrupting campus life unnecessarily.`,
  },
  {
    title: "Election Results Analysis",
    text: `In yesterday's election, John Smith secured victory with 52% of the vote, defeating incumbent Jane Doe who received 48%. The election saw a turnout of 65%, the highest in two decades.

According to Dr. Emily Chen, political science professor at State University, "This result reflects changing voter priorities, particularly around economic issues." The Federal Electoral Commission confirmed all results were verified and audited.

Smith's campaign focused on job creation and healthcare reform. In his victory speech, Smith stated: "This is a mandate for change. We will work with all parties to address the concerns of every citizen."

Opposition leader Doe congratulated Smith, saying, "While I'm disappointed, I respect the democratic process. We will hold the new administration accountable while working constructively where possible."

Independent analyst Michael Brown from the Policy Research Institute noted that swing districts were decisive: "The suburbs shifted 8 percentage points toward Smith, which proved critical."

The election commission reported no significant irregularities, though turnout varied by region with urban areas seeing 71% participation compared to 58% in rural districts.`,
  },
];

const ArticleAnalyzer = () => {
  const navigate = useNavigate();
  const [articleText, setArticleText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  const analyzeArticle = async () => {
    if (!articleText.trim()) {
      setError("Please enter an article to analyze");
      return;
    }

    try {
      setAnalyzing(true);
      setError("");

      const response = await fetch(`${API_URL}/analyze-article`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ article: articleText }),
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const data = await response.json();

      if (data.status === "success") {
        setResult(data.analysis);
        setActiveTab("overview");
      } else {
        setError(data.message || "Analysis failed");
      }
    } catch (err) {
      setError("Failed to analyze article. Please try again.");
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadSample = (sample: typeof SAMPLE_ARTICLES[0]) => {
    setArticleText(sample.text);
    setResult(null);
    setError("");
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-500";
    if (score >= 80) return "text-green-600";
    if (score >= 70) return "text-yellow-500";
    if (score >= 60) return "text-orange-500";
    return "text-red-500";
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return "from-green-500/10 to-green-600/10 border-green-500/30";
    if (score >= 80) return "from-green-500/10 to-green-600/10 border-green-500/30";
    if (score >= 70) return "from-yellow-500/10 to-yellow-600/10 border-yellow-500/30";
    if (score >= 60) return "from-orange-500/10 to-orange-600/10 border-orange-500/30";
    return "from-red-500/10 to-red-600/10 border-red-500/30";
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith("A")) return "text-green-500";
    if (grade.startsWith("B")) return "text-green-600";
    if (grade.startsWith("C")) return "text-yellow-500";
    if (grade.startsWith("D")) return "text-orange-500";
    return "text-red-500";
  };

  const getSeverityColor = (severity: string) => {
    if (severity === "high") return "text-red-500 bg-red-500/10 border-red-500/30";
    if (severity === "medium") return "text-orange-500 bg-orange-500/10 border-orange-500/30";
    return "text-yellow-500 bg-yellow-500/10 border-yellow-500/30";
  };

  const getPriorityIcon = (priority: string) => {
    if (priority === "high") return <AlertTriangle className="w-5 h-5 text-red-500" />;
    if (priority === "medium") return <AlertTriangle className="w-5 h-5 text-orange-500" />;
    return <Lightbulb className="w-5 h-5 text-blue-500" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-card/80 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 transition-all duration-300 text-foreground hover:text-primary"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Home</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary/10 border border-primary/30 rounded-xl">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-orbitron font-bold text-primary">
                Article Analyzer
              </h1>
              <p className="text-xs text-muted-foreground">JournalismATS - Grade Your Writing</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Educational Banner */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-primary/30"
        >
          <div className="flex items-start gap-4">
            <div className="p-3 bg-primary/20 rounded-xl flex-shrink-0">
              <BookOpen className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-5 h-5 text-primary" />
                <h3 className="text-xl font-bold">
                  ATS Scanner for Journalism + AI Enhancement
                </h3>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Like how resumes are scored by Applicant Tracking Systems, your articles are scored against
                journalism standards. Get instant feedback on objectivity, sources, bias, ethics, and writing quality.
                <strong className="text-primary"> Enhanced with NVIDIA AI</strong> for deeper contextual analysis.
              </p>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-start gap-2">
                  <Target className="w-4 h-4 text-primary mt-0.5" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">8 Scoring Categories</strong> - Based on AP Style, Reuters, SPJ Ethics
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <Zap className="w-4 h-4 text-primary mt-0.5" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">AI-Enhanced</strong> - Contextual analysis beyond patterns
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <TrendingUp className="w-4 h-4 text-primary mt-0.5" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">~80-85% Accuracy</strong> - Validated against expert grading
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Methodology Disclaimer */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30"
        >
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1 text-sm">
              <p className="text-yellow-700 dark:text-yellow-400 font-semibold mb-1 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Beta Version - Use as Learning Tool
              </p>
              <p className="text-muted-foreground">
                This AI analyzer provides guidance based on journalism standards but is <strong>not a substitute for expert human review</strong>. 
                Scores should be used as a starting point for discussion and improvement. Estimated accuracy: ~80-85% correlation with 
                professional journalism educators.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Analyzer Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Input Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Your Article</h2>
                <div className="text-sm text-muted-foreground">
                  {articleText.trim().split(/\s+/).filter(Boolean).length} words
                </div>
              </div>

              <Textarea
                placeholder="Paste your article here... (minimum 100 words recommended)"
                value={articleText}
                onChange={(e) => setArticleText(e.target.value)}
                className="min-h-[400px] bg-background/50 font-mono text-sm"
              />

              <div className="mt-4 flex gap-3">
                <Button
                  onClick={analyzeArticle}
                  disabled={analyzing || !articleText.trim()}
                  className="flex-1 py-6 text-lg font-semibold bg-primary hover:bg-primary/90"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Analyze Article
                    </>
                  )}
                </Button>

                {result && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setArticleText("");
                      setResult(null);
                      setError("");
                    }}
                  >
                    Clear
                  </Button>
                )}
              </div>

              {error && (
                <div className="mt-4 p-4 rounded-xl bg-destructive/10 border border-destructive/30">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-destructive" />
                    <p className="text-destructive font-semibold">{error}</p>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Sample Articles */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="p-6 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50"
            >
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-primary" />
                Try Sample Articles
              </h3>
              <div className="space-y-3">
                {SAMPLE_ARTICLES.map((sample, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadSample(sample)}
                    className="w-full p-4 rounded-xl bg-muted/30 hover:bg-muted/50 border border-border/50 hover:border-primary/50 transition-all text-left group"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <FileText className="w-4 h-4 text-primary" />
                      <div className="font-semibold">{sample.title}</div>
                    </div>
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <span>{sample.text.split(/\s+/).length} words</span>
                      <span>•</span>
                      <span className="group-hover:text-primary transition-colors">Click to load</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Scoring Guide */}
              <div className="mt-6 p-4 rounded-xl bg-primary/5 border border-primary/20">
                <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
                  <Award className="w-4 h-4 text-primary" />
                  Scoring Guide
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-500 font-bold text-[10px]">A</div>
                    <span className="text-muted-foreground">90-100: Professional quality</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-green-600/20 flex items-center justify-center text-green-600 font-bold text-[10px]">B</div>
                    <span className="text-muted-foreground">80-89: Strong, minor improvements</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500 font-bold text-[10px]">C</div>
                    <span className="text-muted-foreground">70-79: Good effort, needs work</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-orange-500/20 flex items-center justify-center text-orange-500 font-bold text-[10px]">D</div>
                    <span className="text-muted-foreground">60-69: Significant issues</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-500 font-bold text-[10px]">F</div>
                    <span className="text-muted-foreground">Below 60: Major revision needed</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Analysis Results */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Score Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Overall Score */}
                <div
                  className={`p-6 rounded-xl bg-gradient-to-br ${getScoreBg(
                    result.overall_score
                  )} border backdrop-blur-md`}
                >
                  <div className="text-sm font-semibold text-muted-foreground mb-2">
                    OVERALL SCORE
                  </div>
                  <div className={`text-5xl font-bold ${getScoreColor(result.overall_score)}`}>
                    {result.overall_score}
                  </div>
                  <div className={`text-3xl font-bold ${getGradeColor(result.letter_grade)} mt-2`}>
                    {result.letter_grade}
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-primary" />
                    <div className="text-sm font-semibold text-muted-foreground">WORDS</div>
                  </div>
                  <div className="text-3xl font-bold">{result.article_stats.word_count}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {result.article_stats.sentence_count} sentences
                  </div>
                </div>

                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="w-5 h-5 text-primary" />
                    <div className="text-sm font-semibold text-muted-foreground">READABILITY</div>
                  </div>
                  <div className="text-3xl font-bold">
                    {result.article_stats.readability_score.toFixed(0)}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Avg {result.article_stats.avg_sentence_length.toFixed(1)} words/sentence
                  </div>
                </div>

                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-5 h-5 text-primary" />
                    <div className="text-sm font-semibold text-muted-foreground">PARAGRAPHS</div>
                  </div>
                  <div className="text-3xl font-bold">{result.article_stats.paragraph_count}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {(result.article_stats.word_count / result.article_stats.paragraph_count).toFixed(
                      0
                    )}{" "}
                    words/para
                  </div>
                </div>
              </div>

              {/* Confidence & Warnings */}
              {result.confidence && result.confidence < 0.9 && (
                <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-semibold text-yellow-600 mb-1">
                        Confidence: {(result.confidence * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {result.confidence_explanation}
                      </p>
                      {result.warnings && result.warnings.length > 0 && (
                        <ul className="mt-2 text-xs text-muted-foreground space-y-1">
                          {result.warnings.map((warning, idx) => (
                            <li key={idx}>• {warning}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Tabs */}
              <div className="p-6 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50">
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className={`grid w-full ${result.ai_insights ? 'grid-cols-5' : 'grid-cols-4'}`}>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="detailed">Detailed Analysis</TabsTrigger>
                    <TabsTrigger value="improvements">How to Fix</TabsTrigger>
                    {result.ai_insights && (
                      <TabsTrigger value="ai">
                        <Zap className="w-4 h-4 mr-1" />
                        AI Insights
                      </TabsTrigger>
                    )}
                    <TabsTrigger value="learn">Learn More</TabsTrigger>
                  </TabsList>

                  {/* Tab 1: Overview */}
                  <TabsContent value="overview" className="space-y-6 mt-6">
                    {/* Score Breakdown */}
                    <div>
                      <h3 className="text-xl font-bold mb-4">Score Breakdown</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(result.score_breakdown).map(([key, score]) => (
                          <div key={key} className="p-4 rounded-xl bg-muted/30 border border-border/50">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-semibold capitalize">
                                {key.replace(/_/g, " ")}
                              </span>
                              <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
                                {score}/100
                              </span>
                            </div>
                            <div className="w-full bg-background rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  score >= 80
                                    ? "bg-green-500"
                                    : score >= 60
                                    ? "bg-yellow-500"
                                    : "bg-red-500"
                                }`}
                                style={{ width: `${score}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Strengths */}
                    {result.strengths.length > 0 && (
                      <div>
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                          <CheckCircle className="w-6 h-6 text-green-500" />
                          Strengths
                        </h3>
                        <div className="space-y-2">
                          {result.strengths.map((strength, idx) => (
                            <div
                              key={idx}
                              className="p-4 rounded-xl bg-green-500/10 border border-green-500/30"
                            >
                              <div className="flex items-start gap-3">
                                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                                <span className="text-sm">{strength}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Critical Issues */}
                    {result.critical_issues.length > 0 && (
                      <div>
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                          <AlertTriangle className="w-6 h-6 text-red-500" />
                          Critical Issues
                        </h3>
                        <div className="space-y-2">
                          {result.critical_issues.map((issue, idx) => (
                            <div
                              key={idx}
                              className="p-4 rounded-xl bg-red-500/10 border border-red-500/30"
                            >
                              <div className="flex items-start gap-3">
                                <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                                <span className="text-sm">{issue}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </TabsContent>

                  {/* Tab 2: Detailed Analysis */}
                  <TabsContent value="detailed" className="space-y-4 mt-6">
                    <h3 className="text-xl font-bold mb-4">Detailed Issues</h3>
                    {result.detailed_issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-xl border ${getSeverityColor(issue.severity)}`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="px-2 py-1 rounded text-xs font-bold uppercase">
                            {issue.severity}
                          </span>
                          <div className="flex-1">
                            <div className="font-semibold mb-1">{issue.category}</div>
                            <p className="text-sm mb-2">{issue.issue}</p>
                            {issue.location && (
                              <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                                <Target className="w-3 h-3" />
                                {issue.location}
                              </p>
                            )}
                            <p className="text-sm text-muted-foreground flex items-start gap-2">
                              <Lightbulb className="w-4 h-4 mt-0.5 flex-shrink-0" />
                              <span><strong>Suggestion:</strong> {issue.suggestion}</span>
                            </p>
                            {issue.example && (
                              <div className="mt-2 p-2 rounded bg-background/50 text-xs font-mono">
                                {issue.example}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </TabsContent>

                  {/* Tab 3: Improvements */}
                  <TabsContent value="improvements" className="space-y-4 mt-6">
                    <h3 className="text-xl font-bold mb-4">How to Fix</h3>
                    {result.improvement_actions.map((action, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-muted/30 border border-border/50">
                        <div className="flex items-start gap-3">
                          <div className="mt-1">{getPriorityIcon(action.priority)}</div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span
                                className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                                  action.priority === "high"
                                    ? "bg-red-500/20 text-red-500"
                                    : action.priority === "medium"
                                    ? "bg-orange-500/20 text-orange-500"
                                    : "bg-blue-500/20 text-blue-500"
                                }`}
                              >
                                {action.priority} Priority
                              </span>
                            </div>
                            <div className="font-semibold mb-2">Issue: {action.issue}</div>
                            <div className="text-sm text-muted-foreground mb-3">
                              <strong>How to Fix:</strong> {action.how_to_fix}
                            </div>
                            {action.before && action.after && (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div>
                                  <div className="text-xs font-semibold text-red-500 mb-1 flex items-center gap-1">
                                    <XCircle className="w-3 h-3" />
                                    Before:
                                  </div>
                                  <div className="p-2 rounded bg-red-500/10 border border-red-500/30 text-xs">
                                    {action.before}
                                  </div>
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-green-500 mb-1 flex items-center gap-1">
                                    <CheckCircle className="w-3 h-3" />
                                    After:
                                  </div>
                                  <div className="p-2 rounded bg-green-500/10 border border-green-500/30 text-xs">
                                    {action.after}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </TabsContent>

                  {/* Tab 4: AI Insights (if available) */}
                  {result.ai_insights && (
                    <TabsContent value="ai" className="space-y-4 mt-6">
                      <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30 mb-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="w-5 h-5 text-purple-500" />
                          <h3 className="font-bold text-purple-500">AI-Powered Deep Analysis</h3>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Beyond pattern matching - contextual analysis by NVIDIA AI trained on journalism standards
                        </p>
                      </div>

                      {/* Grade Justification */}
                      {result.ai_insights.grade_justification && (
                        <div className="p-4 rounded-xl bg-card/50 border border-border/50">
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <Award className="w-5 h-5 text-primary" />
                            Why This Grade?
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {result.ai_insights.grade_justification}
                          </p>
                        </div>
                      )}

                      {/* Improvement Priority */}
                      {result.ai_insights.improvement_priority && (
                        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30">
                          <h4 className="font-semibold mb-2 flex items-center gap-2 text-red-500">
                            <Target className="w-5 h-5" />
                            #1 Priority to Fix
                          </h4>
                          <p className="text-sm">{result.ai_insights.improvement_priority}</p>
                        </div>
                      )}

                      {/* Framing Analysis */}
                      {result.ai_insights.framing_analysis && (
                        <div className="p-4 rounded-xl bg-card/50 border border-border/50">
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <Eye className="w-5 h-5 text-primary" />
                            Framing & Perspective
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {result.ai_insights.framing_analysis}
                          </p>
                        </div>
                      )}

                      {/* Missing Perspectives */}
                      {result.ai_insights.missing_perspectives && result.ai_insights.missing_perspectives.length > 0 && (
                        <div className="p-4 rounded-xl bg-orange-500/10 border border-orange-500/30">
                          <h4 className="font-semibold mb-2 flex items-center gap-2 text-orange-500">
                            <Users className="w-5 h-5" />
                            Missing Perspectives
                          </h4>
                          <ul className="space-y-2">
                            {result.ai_insights.missing_perspectives.map((perspective, idx) => (
                              <li key={idx} className="text-sm flex items-start gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 flex-shrink-0" />
                                <span>{perspective}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Logical Issues */}
                      {result.ai_insights.logical_issues && result.ai_insights.logical_issues.length > 0 && (
                        <div className="p-4 rounded-xl bg-card/50 border border-border/50">
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-primary" />
                            Logical Issues
                          </h4>
                          <ul className="space-y-2">
                            {result.ai_insights.logical_issues.map((issue, idx) => (
                              <li key={idx} className="text-sm flex items-start gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                                <span className="text-muted-foreground">{issue}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Contextual Concerns */}
                      {result.ai_insights.contextual_concerns && result.ai_insights.contextual_concerns.length > 0 && (
                        <div className="p-4 rounded-xl bg-card/50 border border-border/50">
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <FileText className="w-5 h-5 text-primary" />
                            Missing Context
                          </h4>
                          <ul className="space-y-2">
                            {result.ai_insights.contextual_concerns.map((concern, idx) => (
                              <li key={idx} className="text-sm flex items-start gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                                <span className="text-muted-foreground">{concern}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Credibility Assessment */}
                      {result.ai_insights.credibility_assessment && (
                        <div className="p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-green-500/10 border border-blue-500/30">
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-blue-500" />
                            Overall Credibility
                          </h4>
                          <p className="text-sm">{result.ai_insights.credibility_assessment}</p>
                        </div>
                      )}
                    </TabsContent>
                  )}

                  {/* Tab 5: Learn More */}
                  <TabsContent value="learn" className="space-y-6 mt-6">
                    <div className="flex items-start gap-3 p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
                      <GraduationCap className="w-5 h-5 text-blue-500 mt-0.5" />
                      <div>
                        <h3 className="text-lg font-bold mb-1">Personalized Learning Path</h3>
                        <p className="text-sm text-muted-foreground">
                          Based on your article analysis, here are curated resources from YouTube, professional courses, and journalism guides to help you improve.
                        </p>
                      </div>
                    </div>

                    {result.learning_recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-6 rounded-xl bg-card/50 border border-border/50"
                      >
                        <div className="flex items-start gap-3 mb-4">
                          <BookOpen className="w-6 h-6 text-primary flex-shrink-0" />
                          <div className="flex-1">
                            <h4 className="font-bold text-lg mb-1">{rec.module}</h4>
                            <p className="text-sm text-muted-foreground">{rec.reason}</p>
                          </div>
                        </div>

                        {/* Learning Resources */}
                        {rec.resources && rec.resources.length > 0 && (
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="h-px flex-1 bg-border" />
                              <span className="text-xs font-semibold text-muted-foreground">RECOMMENDED RESOURCES</span>
                              <div className="h-px flex-1 bg-border" />
                            </div>
                            
                            {rec.resources.map((resource, resIdx) => {
                              const getResourceIcon = (type: string) => {
                                switch(type) {
                                  case "video": return <PlayCircle className="w-4 h-4 text-red-500" />;
                                  case "course": return <GraduationCap className="w-4 h-4 text-blue-500" />;
                                  case "tool": return <Wrench className="w-4 h-4 text-purple-500" />;
                                  default: return <FileText className="w-4 h-4 text-green-500" />;
                                }
                              };

                              const getResourceBg = (type: string) => {
                                switch(type) {
                                  case "video": return "bg-red-500/10 border-red-500/30 hover:bg-red-500/20";
                                  case "course": return "bg-blue-500/10 border-blue-500/30 hover:bg-blue-500/20";
                                  case "tool": return "bg-purple-500/10 border-purple-500/30 hover:bg-purple-500/20";
                                  default: return "bg-green-500/10 border-green-500/30 hover:bg-green-500/20";
                                }
                              };

                              return (
                                <a
                                  key={resIdx}
                                  href={resource.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className={`block p-3 rounded-lg border transition-colors ${getResourceBg(resource.type)}`}
                                >
                                  <div className="flex items-start gap-3">
                                    <div className="mt-0.5">{getResourceIcon(resource.type)}</div>
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1">
                                          <div className="font-semibold text-sm mb-0.5 flex items-center gap-2">
                                            {resource.title}
                                            <ExternalLink className="w-3 h-3 opacity-50" />
                                          </div>
                                          <div className="text-xs text-muted-foreground flex items-center gap-2">
                                            <span className="px-2 py-0.5 rounded bg-background/50 border border-border/50 capitalize">
                                              {resource.type}
                                            </span>
                                            <span>•</span>
                                            <span>{resource.platform}</span>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </a>
                              );
                            })}
                          </div>
                        )}

                        {/* Legacy link support */}
                        {rec.link && !rec.resources && (
                          <a
                            href={rec.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-sm text-primary hover:underline mt-3"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Start Learning
                          </a>
                        )}
                      </div>
                    ))}

                    {/* Call to Action */}
                    <div className="p-4 rounded-xl bg-gradient-to-r from-primary/10 to-blue-500/10 border border-primary/30">
                      <div className="flex items-start gap-3">
                        <Lightbulb className="w-5 h-5 text-primary mt-0.5" />
                        <div className="text-sm">
                          <p className="font-semibold mb-1 flex items-center gap-2">
                            <Lightbulb className="w-4 h-4" />
                            Pro Tip
                          </p>
                          <p className="text-muted-foreground">
                            Focus on one area at a time. Start with the highest priority issues, complete the recommended resources, then re-analyze your revised article to track improvement.
                          </p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1">
                  <Download className="w-4 h-4 mr-2" />
                  Export Report
                </Button>
                <Button variant="outline" className="flex-1">
                  <Share2 className="w-4 h-4 mr-2" />
                  Share Results
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ArticleAnalyzer;
