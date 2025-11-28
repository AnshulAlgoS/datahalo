import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  TrendingUp,
  ArrowLeft,
  Calendar,
  Newspaper,
  Target,
  AlertCircle,
  Loader2,
  BarChart3,
  LineChart,
  Eye,
  Clock,
  Zap,
  Filter,
  Download,
  BookOpen,
  Users,
  GraduationCap,
  Share2,
  Copy,
  Check,
  Search,
  Link,
  FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getApiBaseUrl } from "@/config/api";

const API_URL = getApiBaseUrl();

interface NarrativeAnalysis {
  topic: string;
  timeframe: string;
  totalArticles: number;
  media_feeding_you?: {
    main_narrative: string;
    emotional_angle: string;
    key_phrases: string[];
    twisted_reality: string;
    coverage_level: string;
  };
  manipulation_tactics?: {
    emotional_manipulation: string;
    distraction_technique: string;
    loaded_language: string[];
    timing_game: string;
    source_coordination: string;
    omission_tactic: string;
  };
  government_actions?: {
    what_govt_doing: string;
    policies_laws: string;
    enforcement: string;
    govt_silence: string;
    political_angle: string;
  };
  whats_hidden?: {
    buried_facts: string[];
    missing_voices: string[];
    overshadowing_stories: string[];
    censored_angles: string[];
    financial_interests: string[];
  };
  who_benefits?: {
    power_beneficiary: string;
    financial_beneficiary: string;
    cui_bono: string;
  };
  reality_check?: {
    media_says: string;
    they_hide: string;
    real_story: string;
    why_the_spin: string;
  };
  articles_analyzed?: Array<{
    number: number;
    title: string;
    source: string;
    date: string;
  }>;
  // Keep old structure for backwards compatibility
  narrativePattern?: {
    rising: boolean;
    trend: string;
    sentiment: string;
    intensity: number;
  };
  timeline?: Array<{
    date: string;
    count: number;
    sentiment: string;
    keyEvents: string[];
  }>;
  keyNarratives?: Array<{
    narrative: string;
    frequency: number;
    sources: string[];
    firstAppeared: string;
    peakDate: string;
  }>;
  manipulation_indicators?: {
    coordinated_timing: boolean;
    source_clustering: boolean;
    sentiment_uniformity: boolean;
    sudden_spike: boolean;
    explanation: string;
  };
  context?: {
    majorEvents: string[];
    relatedTopics: string[];
    potentialTriggers: string[];
  };
}

const NarrativeAnalyzer = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'topic' | 'url'>('topic');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [topic, setTopic] = useState("");
  const [url, setUrl] = useState("");
  const [timeframe, setTimeframe] = useState("30");
  const [analysis, setAnalysis] = useState<NarrativeAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const [showEducational, setShowEducational] = useState(true);

  const suggestedTopics = [
    "Elections 2024",
    "Farmer Protests",
    "Economic Reforms",
    "Foreign Policy",
    "Climate Change",
    "Healthcare Policy",
    "Education Reforms",
    "Technology Regulation"
  ];

  const analyzeNarrative = async () => {
    if (mode === 'topic' && !topic.trim()) {
      setError("Please enter a topic to analyze");
      return;
    }

    if (mode === 'url' && !url.trim()) {
      setError("Please enter a URL to analyze");
      return;
    }

    try {
      setAnalyzing(true);
      setError("");
      setShowEducational(false);
      
      // Use different endpoints based on mode
      const endpoint = mode === 'url' ? '/analyze-url-narrative' : '/analyze-narrative';
      const requestBody = mode === 'url' 
        ? { url: url }
        : { topic: topic, days: parseInt(timeframe) };
      
      console.log(' Mode:', mode);
      console.log(' Endpoint:', endpoint);
      console.log(' Request Body:', requestBody);
      console.log(' Full URL:', `${API_URL}${endpoint}`);
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      
      console.log('STATS: Response Status:', response.status);
      console.log('DATA: Response Data:', data);

      if (response.ok && data.status === "success") {
        console.log('CHECK: Analysis received:', data.analysis);
        console.log('📋 Analysis keys:', Object.keys(data.analysis));
        
        // Validate critical fields
        if (!data.analysis || typeof data.analysis !== 'object') {
          console.error('❌ Invalid analysis object');
          setError("Received invalid data from server");
          return;
        }
        
        setAnalysis(data.analysis);
        console.log('CHECK: Analysis state updated successfully');
      } else if (response.status === 404 && data.detail) {
        const detail = typeof data.detail === 'string' ? { message: data.detail } : data.detail;
        setError(detail.message || data.detail);
        if (detail.suggestions) {
          setSuggestions(detail.suggestions);
        }
      } else {
        setError(data.message || data.detail || data.error || "Failed to analyze narrative");
      }
    } catch (err) {
      setError("Failed to connect to server. Please check your connection.");
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const exportData = () => {
    if (!analysis) return;
    
    const exportObject = {
      metadata: {
        exportDate: new Date().toISOString(),
        platform: "DataHalo Narrative Analyzer",
        citation: `DataHalo. (${new Date().getFullYear()}). Narrative Analysis: ${analysis.topic}. Retrieved from https://datahalo.vercel.app/narrative-analyzer`,
      },
      analysis: analysis,
    };
    
    const blob = new Blob([JSON.stringify(exportObject, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `narrative-analysis-${analysis.topic.replace(/\s+/g, '-')}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const copyAnalysis = () => {
    if (!analysis) return;
    
    // Build text based on available structure (new or old)
    let text = `
NARRATIVE ANALYSIS: ${analysis.topic}
Generated by DataHalo | ${new Date().toLocaleDateString()}

OVERVIEW
- Articles Analyzed: ${analysis.totalArticles}
- Timeframe: ${analysis.timeframe}
`;

    // Add investigative sections if available (new structure)
    if (analysis.media_feeding_you) {
      text += `\nWHAT MEDIA IS FEEDING YOU\n`;
      text += `Main Narrative: ${analysis.media_feeding_you.main_narrative}\n`;
      text += `Emotional Angle: ${analysis.media_feeding_you.emotional_angle}\n`;
      
      if (analysis.manipulation_tactics) {
        text += `\nMANIPULATION TACTICS DETECTED\n`;
        Object.entries(analysis.manipulation_tactics).forEach(([key, value]) => {
          if (value && typeof value === 'string') {
            text += `- ${key.replace(/_/g, ' ').toUpperCase()}: ${value}\n`;
          }
        });
      }
      
      if (analysis.government_actions) {
        text += `\nGOVERNMENT ACTIONS\n`;
        Object.entries(analysis.government_actions).forEach(([key, value]) => {
          if (value && typeof value === 'string') {
            text += `- ${key.replace(/_/g, ' ').toUpperCase()}: ${value}\n`;
          }
        });
      }
    }
    
    // Add old structure if available
    if (analysis.narrativePattern) {
      text += `\nPATTERN\n`;
      text += `- Trend: ${analysis.narrativePattern.trend}\n`;
      text += `- Sentiment: ${analysis.narrativePattern.sentiment}\n`;
      text += `- Intensity: ${analysis.narrativePattern.intensity}%\n`;
    }
    
    if (analysis.keyNarratives && analysis.keyNarratives.length > 0) {
      text += `\nKEY NARRATIVES\n`;
      analysis.keyNarratives.forEach((n, i) => {
        text += `${i + 1}. ${n.narrative} (${n.frequency} mentions)\n`;
      });
    }
    
    if (analysis.manipulation_indicators && (
      analysis.manipulation_indicators.coordinated_timing || 
      analysis.manipulation_indicators.source_clustering
    )) {
      text += `\n⚠️ MANIPULATION DETECTED\n${analysis.manipulation_indicators.explanation}\n`;
    }

    text += `\nCitation: DataHalo. (${new Date().getFullYear()}). Narrative Analysis: ${analysis.topic}. https://datahalo.vercel.app/narrative-analyzer`;
    
    navigator.clipboard.writeText(text.trim());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const shareAnalysis = () => {
    if (!analysis) return;
    
    // Build share text based on available structure
    let shareText = `Analyzed ${analysis.totalArticles} articles about "${analysis.topic}".`;
    
    if (analysis.narrativePattern) {
      shareText += ` Trend: ${analysis.narrativePattern.trend}, Sentiment: ${analysis.narrativePattern.sentiment}`;
    } else if (analysis.media_feeding_you) {
      shareText += ` Main narrative: ${analysis.media_feeding_you.main_narrative.substring(0, 100)}...`;
    }
    
    const shareData = {
      title: `Media Narrative Analysis: ${analysis.topic}`,
      text: shareText,
      url: window.location.href
    };
    
    if (navigator.share) {
      navigator.share(shareData);
    } else {
      copyAnalysis();
    }
  };

  const getSentimentColor = (sentiment: string) => {
    if (!sentiment) return "text-yellow-500";
    const sentimentLower = sentiment.toLowerCase();
    if (sentimentLower.includes("positive")) return "text-green-500";
    if (sentimentLower.includes("negative")) return "text-red-500";
    return "text-yellow-500";
  };

  const getSentimentBg = (sentiment: string) => {
    if (!sentiment) return "bg-yellow-500/10 border-yellow-500/30";
    const sentimentLower = sentiment.toLowerCase();
    if (sentimentLower.includes("positive")) return "bg-green-500/10 border-green-500/30";
    if (sentimentLower.includes("negative")) return "bg-red-500/10 border-red-500/30";
    return "bg-yellow-500/10 border-yellow-500/30";
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background" />
      
      {/* Animated background blobs */}
      <motion.div
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 8, repeat: Infinity }}
        className="absolute top-20 right-20 w-96 h-96 bg-primary/20 rounded-full blur-[120px]"
      />
      <motion.div
        animate={{ 
          scale: [1.2, 1, 1.2],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 10, repeat: Infinity }}
        className="absolute bottom-20 left-20 w-96 h-96 bg-accent/20 rounded-full blur-[120px]"
      />

      {/* Content */}
      <div className="relative z-10 min-h-screen">
        {/* Header */}
        <div className="border-b border-border/50 backdrop-blur-md bg-card/30 sticky top-0 z-30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  onClick={() => navigate("/")}
                  className="group px-4 py-2 bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 rounded-xl transition-all"
                >
                  <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
                  Back to Home
                </Button>
                
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary/10 border border-primary/30 rounded-xl">
                    <GraduationCap className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h1 className="font-orbitron text-2xl md:text-3xl font-bold">
                      Media <span className="text-primary">Literacy</span> Analyzer
                    </h1>
                    <p className="text-sm text-muted-foreground">
                      Learn how news articles push ideologies · For students & critical thinkers
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Educational Banner - Learn How Media Manipulates */}
          {showEducational && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-primary/30"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/20 rounded-xl flex-shrink-0">
                  <GraduationCap className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3">
                    Learn How News Articles Push Ideologies
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    This tool teaches you to **decode media manipulation** by analyzing how journalists frame stories to influence public opinion. 
                    Perfect for journalism students, media literacy education, and anyone wanting to think critically about news.
                  </p>
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                      <div className="flex items-center gap-2 mb-2">
                        <Search className="w-4 h-4 text-primary" />
                        <p className="font-semibold text-foreground">Step 1: Data Collection</p>
                      </div>
                      <p className="text-muted-foreground">We analyze multiple articles about your topic from different sources</p>
                    </div>
                    <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                      <div className="flex items-center gap-2 mb-2">
                        <Eye className="w-4 h-4 text-primary" />
                        <p className="font-semibold text-foreground">Step 2: Pattern Detection</p>
                      </div>
                      <p className="text-muted-foreground">We identify how outlets frame the same story differently</p>
                    </div>
                    <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                      <div className="flex items-center gap-2 mb-2">
                        <BookOpen className="w-4 h-4 text-primary" />
                        <p className="font-semibold text-foreground">Step 3: Learn Techniques</p>
                      </div>
                      <p className="text-muted-foreground">Understand the specific manipulation tactics being used</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Analyzer Interface */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <div className="p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50">
              {/* Info Banner */}
              <div className="mb-6 p-4 rounded-xl bg-primary/10 border border-primary/30">
                <div className="flex items-start gap-3">
                  <GraduationCap className="w-5 h-5 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-primary mb-1">
                      Educational Tool: Decode Media Manipulation
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Enter any topic or news URL to see how journalists frame stories to influence public opinion. We'll show you the specific 
                      techniques used - word choice, timing, source selection - and teach you to spot propaganda. Perfect for journalism students, 
                      media literacy classes, and anyone wanting to think critically about news.
                    </p>
                  </div>
                </div>
              </div>

              {/* Search Interface */}
              <div className="space-y-4">
                {/* Mode Selection - Make it more prominent */}
                <div className="p-4 rounded-xl bg-muted/30 border border-border/50">
                  <label className="block text-sm font-semibold mb-3">Analysis Mode</label>
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setMode('topic');
                        setError("");
                        setSuggestions([]);
                      }}
                      className={`flex-1 py-6 text-base font-semibold transition-all ${
                        mode === 'topic' 
                          ? 'bg-primary text-primary-foreground border-primary hover:bg-primary/90' 
                          : 'bg-card/50 hover:bg-primary/10 hover:border-primary/50'
                      }`}
                    >
                      <FileText className="w-5 h-5 mr-2" />
                      Topic Analysis
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setMode('url');
                        setError("");
                        setSuggestions([]);
                      }}
                      className={`flex-1 py-6 text-base font-semibold transition-all ${
                        mode === 'url' 
                          ? 'bg-primary text-primary-foreground border-primary hover:bg-primary/90' 
                          : 'bg-card/50 hover:bg-primary/10 hover:border-primary/50'
                      }`}
                    >
                      <Link className="w-5 h-5 mr-2" />
                      URL Analysis
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold mb-2">
                      {mode === 'topic' ? 'Topic or Event' : 'URL'}
                    </label>
                    <Input
                      placeholder={mode === 'topic' ? "e.g., Elections 2024, Farmer Protests..." : "e.g., https://example.com"}
                      value={mode === 'topic' ? topic : url}
                      onChange={(e) => mode === 'topic' ? setTopic(e.target.value) : setUrl(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && analyzeNarrative()}
                      className="bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold mb-2">
                      Time Period
                    </label>
                    <Select value={timeframe} onValueChange={setTimeframe}>
                      <SelectTrigger className="bg-card/50 backdrop-blur-sm border-border/50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="7">Last 7 Days</SelectItem>
                        <SelectItem value="14">Last 2 Weeks</SelectItem>
                        <SelectItem value="30">Last Month</SelectItem>
                        <SelectItem value="60">Last 2 Months</SelectItem>
                        <SelectItem value="90">Last 3 Months</SelectItem>
                        <SelectItem value="180">Last 6 Months</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Suggested Topics */}
                {mode === 'topic' && (
                  <div>
                    <label className="block text-sm font-semibold mb-2">
                      Popular Topics
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {suggestedTopics.map((suggested) => (
                        <Button
                          key={suggested}
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setTopic(suggested);
                            setMode('topic');
                          }}
                          className="text-xs hover:bg-primary/10 hover:border-primary/50"
                        >
                          {suggested}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analyze Button */}
                <Button
                  onClick={analyzeNarrative}
                  disabled={analyzing || (mode === 'topic' && !topic.trim()) || (mode === 'url' && !url.trim())}
                  className="w-full py-6 text-lg font-semibold bg-primary hover:bg-primary/90 rounded-xl"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Analyzing Narrative Patterns...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Analyze Narrative
                    </>
                  )}
                </Button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mt-4 p-4 rounded-xl bg-destructive/10 border border-destructive/30">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-destructive font-semibold mb-2">{error}</p>
                      
                      {suggestions.length > 0 && (
                        <div className="mt-3">
                          <p className="text-sm text-muted-foreground mb-2">Try these topics instead:</p>
                          <div className="flex flex-wrap gap-2">
                            {suggestions.map((suggestion, index) => (
                              <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setTopic(suggestion);
                                  setMode('topic');
                                  setError("");
                                  setSuggestions([]);
                                }}
                                className="text-xs hover:bg-primary/10 hover:border-primary/50"
                              >
                                {suggestion}
                              </Button>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <p className="text-xs text-muted-foreground mt-3">
                        💡 Tip: Try broader search terms like "Elections", "Economy", or "Technology" for better results.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Analysis Results */}
          {analysis && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-6"
              onError={(e) => {
                console.error('❌ Render error:', e);
                setError('Failed to display analysis results');
              }}
            >
              {/* Export and Share Actions */}
              <div className="flex justify-end gap-3">
                <Button
                  onClick={exportData}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Export Data
                </Button>
                <Button
                  onClick={copyAnalysis}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? "Copied!" : "Copy Analysis"}
                </Button>
                <Button
                  onClick={shareAnalysis}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <Share2 className="w-4 h-4" />
                  Share
                </Button>
              </div>

              {/* Summary Card - Always show */}
              <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                <h3 className="text-xl font-bold mb-4">Analysis Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-2xl font-bold text-primary">{analysis.totalArticles}</div>
                    <div className="text-sm text-muted-foreground">Articles Analyzed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary">{analysis.timeframe || 'N/A'}</div>
                    <div className="text-sm text-muted-foreground">Timeframe</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary">
                      {analysis.media_feeding_you ? '✓' : analysis.narrativePattern ? '✓' : '..'}
                    </div>
                    <div className="text-sm text-muted-foreground">Data Available</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary">
                      {new Date().toLocaleDateString()}
                    </div>
                    <div className="text-sm text-muted-foreground">Analyzed</div>
                  </div>
                </div>
              </div>

              {/* NEW: What Media is Feeding You */}
              {analysis.media_feeding_you && (
                <div className="p-6 rounded-xl bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-red-500 mb-2">
                        ALERT: What Media is FEEDING You on "{analysis.topic}"
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Analyzed {analysis.totalArticles} articles - Here's the narrative they want you to believe:
                      </p>
                      
                      <div className="space-y-3">
                        <div className="p-4 rounded-lg bg-card/50 border border-red-500/20">
                          <h4 className="font-semibold text-red-400 mb-2">Main Narrative Being Pushed</h4>
                          <p className="text-sm text-foreground">{analysis.media_feeding_you.main_narrative}</p>
                        </div>
                        
                        <div className="p-4 rounded-lg bg-card/50 border border-orange-500/20">
                          <h4 className="font-semibold text-orange-400 mb-2">Emotional Manipulation</h4>
                          <p className="text-sm text-foreground">{analysis.media_feeding_you.emotional_angle}</p>
                        </div>
                        
                        {analysis.media_feeding_you.key_phrases && Array.isArray(analysis.media_feeding_you.key_phrases) && analysis.media_feeding_you.key_phrases.length > 0 && (
                          <div className="p-4 rounded-lg bg-card/50 border border-yellow-500/20">
                            <h4 className="font-semibold text-yellow-400 mb-2">Repeated Phrases (Word Control)</h4>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {analysis.media_feeding_you.key_phrases.map((phrase, i) => (
                                <span key={i} className="px-3 py-1 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-sm text-yellow-300">
                                  "{phrase}"
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {analysis.media_feeding_you.key_phrases && !Array.isArray(analysis.media_feeding_you.key_phrases) && typeof analysis.media_feeding_you.key_phrases === 'string' && (
                          <div className="p-4 rounded-lg bg-card/50 border border-yellow-500/20">
                            <h4 className="font-semibold text-yellow-400 mb-2">Repeated Phrases (Word Control)</h4>
                            <p className="text-sm text-foreground">"{analysis.media_feeding_you.key_phrases}"</p>
                          </div>
                        )}
                        
                        {analysis.media_feeding_you.twisted_reality && (
                          <div className="p-4 rounded-lg bg-card/50 border border-purple-500/20">
                            <h4 className="font-semibold text-purple-400 mb-2">How Reality is Twisted</h4>
                            <p className="text-sm text-foreground">{analysis.media_feeding_you.twisted_reality}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* NEW: Manipulation Tactics Exposed */}
              {analysis.manipulation_tactics && (
                <div className="p-6 rounded-xl bg-gradient-to-r from-orange-500/10 to-yellow-500/10 border border-orange-500/30">
                  <div className="flex items-start gap-3">
                    <Eye className="w-6 h-6 text-orange-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-orange-500 mb-2">
                        TARGET: Manipulation Tactics Detected
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Learn to spot these techniques used to control what you think:
                      </p>
                      
                      <div className="grid md:grid-cols-2 gap-3">
                        {analysis.manipulation_tactics.emotional_manipulation && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Emotional Manipulation</h4>
                            <p className="text-sm text-foreground">{analysis.manipulation_tactics.emotional_manipulation}</p>
                          </div>
                        )}
                        
                        {analysis.manipulation_tactics.distraction_technique && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Distraction Technique</h4>
                            <p className="text-sm text-foreground">{analysis.manipulation_tactics.distraction_technique}</p>
                          </div>
                        )}
                        
                        {analysis.manipulation_tactics.timing_game && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Timing Game</h4>
                            <p className="text-sm text-foreground">{analysis.manipulation_tactics.timing_game}</p>
                          </div>
                        )}
                        
                        {analysis.manipulation_tactics.source_coordination && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Source Coordination</h4>
                            <p className="text-sm text-foreground">{analysis.manipulation_tactics.source_coordination}</p>
                          </div>
                        )}
                        
                        {analysis.manipulation_tactics.omission_tactic && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Omission Tactic</h4>
                            <p className="text-sm text-foreground">{analysis.manipulation_tactics.omission_tactic}</p>
                          </div>
                        )}
                        
                        {analysis.manipulation_tactics.loaded_language && Array.isArray(analysis.manipulation_tactics.loaded_language) && analysis.manipulation_tactics.loaded_language.length > 0 && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Loaded Language</h4>
                            <div className="flex flex-wrap gap-2">
                              {analysis.manipulation_tactics.loaded_language.map((phrase, i) => (
                                <span key={i} className="px-2 py-1 text-xs rounded-lg bg-orange-500/10 border border-orange-500/30">
                                  {phrase}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {analysis.manipulation_tactics.loaded_language && !Array.isArray(analysis.manipulation_tactics.loaded_language) && typeof analysis.manipulation_tactics.loaded_language === 'string' && (
                          <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                            <h4 className="font-semibold text-orange-400 mb-2">Loaded Language</h4>
                            <p className="text-sm text-foreground">{analysis.manipulation_tactics.loaded_language}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* NEW: Government Actions */}
              {analysis.government_actions && (
                <div className="p-6 rounded-xl bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/30">
                  <div className="flex items-start gap-3">
                    <Target className="w-6 h-6 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-blue-500 mb-2">
                        GOVT: Government Actions & Politics
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        What the government is actually doing (and not doing):
                      </p>
                      
                      <div className="space-y-3">
                        {analysis.government_actions.what_govt_doing && (
                          <div className="p-4 rounded-lg bg-card/50 border border-blue-500/20">
                            <h4 className="font-semibold text-blue-400 mb-2">What Government is Doing</h4>
                            <p className="text-sm text-foreground">{analysis.government_actions.what_govt_doing}</p>
                          </div>
                        )}
                        
                        {analysis.government_actions.policies_laws && (
                          <div className="p-4 rounded-lg bg-card/50 border border-cyan-500/20">
                            <h4 className="font-semibold text-cyan-400 mb-2">Policies & Laws</h4>
                            <p className="text-sm text-foreground">{analysis.government_actions.policies_laws}</p>
                          </div>
                        )}
                        
                        {analysis.government_actions.govt_silence && (
                          <div className="p-4 rounded-lg bg-card/50 border border-red-500/20">
                            <h4 className="font-semibold text-red-400 mb-2">Government Silence</h4>
                            <p className="text-sm text-foreground">{analysis.government_actions.govt_silence}</p>
                          </div>
                        )}
                        
                        {analysis.government_actions.political_angle && (
                          <div className="p-4 rounded-lg bg-card/50 border border-purple-500/20">
                            <h4 className="font-semibold text-purple-400 mb-2">Political Angle</h4>
                            <p className="text-sm text-foreground">{analysis.government_actions.political_angle}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* NEW: What's Hidden */}
              {analysis.whats_hidden && (
                <div className="p-6 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-6 h-6 text-purple-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-purple-500 mb-2">
                        SEARCH: What Media is HIDING From You
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Critical information being buried or censored:
                      </p>
                      
                      <div className="space-y-3">
                        {analysis.whats_hidden.buried_facts && Array.isArray(analysis.whats_hidden.buried_facts) && analysis.whats_hidden.buried_facts.length > 0 && (
                          <div className="p-4 rounded-lg bg-card/50 border border-purple-500/20">
                            <h4 className="font-semibold text-purple-400 mb-2">Buried Facts</h4>
                            <ul className="space-y-1">
                              {analysis.whats_hidden.buried_facts.map((fact, i) => (
                                <li key={i} className="text-sm text-foreground flex items-start gap-2">
                                  <span className="text-purple-400">•</span>
                                  <span>{fact}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {analysis.whats_hidden.buried_facts && !Array.isArray(analysis.whats_hidden.buried_facts) && typeof analysis.whats_hidden.buried_facts === 'string' && (
                          <div className="p-4 rounded-lg bg-card/50 border border-purple-500/20">
                            <h4 className="font-semibold text-purple-400 mb-2">Buried Facts</h4>
                            <p className="text-sm text-foreground">{analysis.whats_hidden.buried_facts}</p>
                          </div>
                        )}
                        
                        {analysis.whats_hidden.missing_voices && Array.isArray(analysis.whats_hidden.missing_voices) && analysis.whats_hidden.missing_voices.length > 0 && (
                          <div className="p-4 rounded-lg bg-card/50 border border-pink-500/20">
                            <h4 className="font-semibold text-pink-400 mb-2">Missing Voices</h4>
                            <ul className="space-y-1">
                              {analysis.whats_hidden.missing_voices.map((voice, i) => (
                                <li key={i} className="text-sm text-foreground flex items-start gap-2">
                                  <span className="text-pink-400">•</span>
                                  <span>{voice}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {analysis.whats_hidden.missing_voices && !Array.isArray(analysis.whats_hidden.missing_voices) && typeof analysis.whats_hidden.missing_voices === 'string' && (
                          <div className="p-4 rounded-lg bg-card/50 border border-pink-500/20">
                            <h4 className="font-semibold text-pink-400 mb-2">Missing Voices</h4>
                            <p className="text-sm text-foreground">{analysis.whats_hidden.missing_voices}</p>
                          </div>
                        )}
                        
                        {analysis.whats_hidden.overshadowing_stories && Array.isArray(analysis.whats_hidden.overshadowing_stories) && analysis.whats_hidden.overshadowing_stories.length > 0 && (
                          <div className="p-4 rounded-lg bg-card/50 border border-red-500/20">
                            <h4 className="font-semibold text-red-400 mb-2">Stories Overshadowing This</h4>
                            <ul className="space-y-1">
                              {analysis.whats_hidden.overshadowing_stories.map((story, i) => (
                                <li key={i} className="text-sm text-foreground flex items-start gap-2">
                                  <span className="text-red-400">•</span>
                                  <span>{story}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {analysis.whats_hidden.overshadowing_stories && !Array.isArray(analysis.whats_hidden.overshadowing_stories) && typeof analysis.whats_hidden.overshadowing_stories === 'string' && (
                          <div className="p-4 rounded-lg bg-card/50 border border-red-500/20">
                            <h4 className="font-semibold text-red-400 mb-2">Stories Overshadowing This</h4>
                            <p className="text-sm text-foreground">{analysis.whats_hidden.overshadowing_stories}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* NEW: Who Benefits */}
              {analysis.who_benefits && (
                <div className="p-6 rounded-xl bg-gradient-to-r from-yellow-500/10 to-green-500/10 border border-yellow-500/30">
                  <div className="flex items-start gap-3">
                    <Users className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-yellow-500 mb-2">
                        MONEY: Follow the Money: Who BENEFITS?
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Cui bono? Who gains power or profit from this narrative:
                      </p>
                      
                      <div className="space-y-3">
                        {analysis.who_benefits.power_beneficiary && (
                          <div className="p-4 rounded-lg bg-card/50 border border-yellow-500/20">
                            <h4 className="font-semibold text-yellow-400 mb-2">Power Beneficiary</h4>
                            <p className="text-sm text-foreground">{analysis.who_benefits.power_beneficiary}</p>
                          </div>
                        )}
                        
                        {analysis.who_benefits.financial_beneficiary && (
                          <div className="p-4 rounded-lg bg-card/50 border border-green-500/20">
                            <h4 className="font-semibold text-green-400 mb-2">Financial Beneficiary</h4>
                            <p className="text-sm text-foreground">{analysis.who_benefits.financial_beneficiary}</p>
                          </div>
                        )}
                        
                        {analysis.who_benefits.cui_bono && (
                          <div className="p-4 rounded-lg bg-card/50 border border-orange-500/20">
                            <h4 className="font-semibold text-orange-400 mb-2">Analysis: Cui Bono</h4>
                            <p className="text-sm text-foreground">{analysis.who_benefits.cui_bono}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* NEW: Reality Check */}
              {analysis.reality_check && (
                <div className="p-6 rounded-xl bg-gradient-to-r from-green-500/10 to-teal-500/10 border border-green-500/30">
                  <div className="flex items-start gap-3">
                    <Eye className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-green-500 mb-2">
                        CHECK: REALITY CHECK: The REAL Story
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Media narrative vs actual reality:
                      </p>
                      
                      <div className="space-y-3">
                        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                          <h4 className="font-semibold text-red-400 mb-2">❌ What Media Says</h4>
                          <p className="text-sm text-foreground">{analysis.reality_check.media_says}</p>
                        </div>
                        
                        <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/20">
                          <h4 className="font-semibold text-orange-400 mb-2">🙈 What They Hide</h4>
                          <p className="text-sm text-foreground">{analysis.reality_check.they_hide}</p>
                        </div>
                        
                        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                          <h4 className="font-semibold text-green-400 mb-2">CHECK: The REAL Story</h4>
                          <p className="text-sm text-foreground">{analysis.reality_check.real_story}</p>
                        </div>
                        
                        <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                          <h4 className="font-semibold text-blue-400 mb-2">💡 Why The Spin?</h4>
                          <p className="text-sm text-foreground">{analysis.reality_check.why_the_spin}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Overview Cards - Only show if old structure exists */}
              {analysis.narrativePattern && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                    <Newspaper className="w-8 h-8 text-primary mb-2" />
                    <div className="text-3xl font-bold">{analysis.totalArticles}</div>
                    <div className="text-sm text-muted-foreground">Articles Found</div>
                  </div>

                  <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                    <TrendingUp className={`w-8 h-8 mb-2 ${analysis.narrativePattern.rising ? 'text-green-500' : 'text-orange-500'}`} />
                    <div className="text-3xl font-bold">{analysis.narrativePattern.trend}</div>
                    <div className="text-sm text-muted-foreground">Trend</div>
                  </div>

                  <div className={`p-6 rounded-xl backdrop-blur-md border ${getSentimentBg(analysis.narrativePattern.sentiment)}`}>
                    <BarChart3 className={`w-8 h-8 mb-2 ${getSentimentColor(analysis.narrativePattern.sentiment)}`} />
                    <div className="text-3xl font-bold">{analysis.narrativePattern.sentiment}</div>
                    <div className="text-sm text-muted-foreground">Sentiment</div>
                  </div>

                  <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                    <Zap className="w-8 h-8 text-primary mb-2" />
                    <div className="text-3xl font-bold">{analysis.narrativePattern.intensity}%</div>
                    <div className="text-sm text-muted-foreground">Intensity</div>
                  </div>
                </div>
              )}

              {/* Articles Analyzed - With Citations */}
              {analysis.articles_analyzed && analysis.articles_analyzed.length > 0 && (
                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Newspaper className="w-5 h-5 text-primary" />
                    Articles Analyzed ({analysis.articles_analyzed.length} sources with specific citations)
                  </h3>
                  <div className="grid md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                    {analysis.articles_analyzed.map((article) => (
                      <div key={article.number} className="p-3 rounded-lg bg-muted/30 border border-border/50">
                        <div className="flex items-start gap-2">
                          <span className="px-2 py-1 text-xs font-bold bg-primary/20 text-primary rounded flex-shrink-0">
                            #{article.number}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold truncate">{article.title}</p>
                            <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                              <span>{article.source}</span>
                              <span>•</span>
                              <span>{article.date}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                    <p className="text-sm text-foreground">
                      <strong>How to Use:</strong> Each article is numbered (e.g., Article #1, #5). The analysis above cites these numbers 
                      as evidence for specific claims. This allows you to verify claims by checking the actual sources.
                    </p>
                  </div>
                </div>
              )}

              {/* Step-by-Step: How We Analyzed This - Only if no new structure */}
              {!analysis.media_feeding_you && analysis.narrativePattern && (
                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Search className="w-5 h-5 text-primary" />
                    Step-by-Step: How We Analyzed "{analysis.topic}"
                  </h3>
                  <div className="space-y-4">
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        1
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-1">Data Collection</h4>
                        <p className="text-sm text-muted-foreground">
                          Searched our database for articles containing "{analysis.topic}". Found {analysis.totalArticles} articles 
                          from {analysis.timeframe}. This sample size tells us how much media attention this topic is getting.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        2
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-1">Keyword Analysis</h4>
                        <p className="text-sm text-muted-foreground">
                          Analyzed word choices in headlines and content. Words like "crisis", "scandal", "controversy" indicate negative framing. 
                          Words like "progress", "achievement", "success" indicate positive framing. Found overall {analysis.narrativePattern.sentiment.toLowerCase()} tone.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        3
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-1">Timeline Tracking</h4>
                        <p className="text-sm text-muted-foreground">
                          Mapped when articles were published. If many outlets publish at the same time, it suggests coordinated messaging. 
                          We detected {analysis.narrativePattern.trend.toLowerCase()} trend in coverage volume over time.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        4
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-1">Source Diversity Check</h4>
                        <p className="text-sm text-muted-foreground">
                          Counted how many different media outlets covered this. If just 2-3 sources dominate, it's less reliable. 
                          If 10+ diverse sources, the narrative is more credible. Identified {analysis.keyNarratives?.length || 0} distinct narrative angles.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        5
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-1">Manipulation Detection</h4>
                        <p className="text-sm text-muted-foreground">
                          Checked for suspicious patterns: Are all outlets using same language? Did coverage suddenly spike? 
                          Are sources clustered? These are red flags for coordinated propaganda campaigns.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Manipulation Indicators - Educational Format - Only show if old structure and no new structure */}
              {!analysis.manipulation_tactics && analysis.manipulation_indicators && (analysis.manipulation_indicators.coordinated_timing || 
                analysis.manipulation_indicators.source_clustering || 
                analysis.manipulation_indicators.sentiment_uniformity || 
                analysis.manipulation_indicators.sudden_spike) && (
                <div className="p-6 rounded-xl bg-orange-500/10 border border-orange-500/30">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-6 h-6 text-orange-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-orange-500 mb-2">
                        Manipulation Tactics Detected - Learn to Spot Them
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        {analysis.manipulation_indicators.explanation}
                      </p>
                      
                      <div className="space-y-3">
                        {analysis.manipulation_indicators.coordinated_timing && (
                          <div className="p-3 rounded-lg bg-card/30 border border-orange-500/20">
                            <div className="flex items-center gap-2 mb-1">
                              <Clock className="w-4 h-4 text-orange-500" />
                              <span className="font-semibold">Coordinated Timing</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Multiple outlets published at the same time - suggests pre-planned campaign rather than organic news.
                            </p>
                          </div>
                        )}
                        {analysis.manipulation_indicators.source_clustering && (
                          <div className="p-3 rounded-lg bg-card/30 border border-orange-500/20">
                            <div className="flex items-center gap-2 mb-1">
                              <Target className="w-4 h-4 text-orange-500" />
                              <span className="font-semibold">Source Clustering</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Few sources dominate the narrative - lack of diverse perspectives means potential echo chamber.
                            </p>
                          </div>
                        )}
                        {analysis.manipulation_indicators.sentiment_uniformity && (
                          <div className="p-3 rounded-lg bg-card/30 border border-orange-500/20">
                            <div className="flex items-center gap-2 mb-1">
                              <BarChart3 className="w-4 h-4 text-orange-500" />
                              <span className="font-semibold">Uniform Sentiment</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              All outlets have same emotional tone - natural news coverage shows diverse opinions and reactions.
                            </p>
                          </div>
                        )}
                        {analysis.manipulation_indicators.sudden_spike && (
                          <div className="p-3 rounded-lg bg-card/30 border border-orange-500/20">
                            <div className="flex items-center gap-2 mb-1">
                              <TrendingUp className="w-4 h-4 text-orange-500" />
                              <span className="font-semibold">Sudden Spike</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Abnormal surge in coverage - may indicate manufactured controversy or diversion tactic.
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                        <p className="text-sm text-foreground">
                          <strong>What Students Should Do:</strong> When you see these patterns, cross-check with independent sources, 
                          look for what's NOT being covered, and ask "who benefits from this narrative?"
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Key Narratives - Educational Format - Only show if old structure */}
              {analysis.keyNarratives && analysis.keyNarratives.length > 0 && (
                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                <div className="mb-4">
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <LineChart className="w-5 h-5 text-primary" />
                    Competing Narratives: How Different Outlets Frame the Same Story
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Each narrative represents a different "angle" or "spin" on "{analysis.topic}". Notice how sources choose what to emphasize - 
                    this reveals their ideological lean or agenda. Students: Compare these angles to understand bias.
                  </p>
                </div>
                
                <div className="space-y-4">
                  {analysis.keyNarratives.map((narrative, index) => (
                    <div key={index} className="p-4 rounded-xl bg-muted/30 border border-border/50">
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex items-start gap-3 flex-1">
                          <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                            {index + 1}
                          </div>
                          <h4 className="font-semibold text-lg flex-1">{narrative.narrative}</h4>
                        </div>
                        <div className="px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 flex-shrink-0">
                          <span className="text-sm font-bold text-primary">{narrative.frequency} times</span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-muted-foreground mb-3">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-primary" />
                          <span>Started: {narrative.firstAppeared}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-primary" />
                          <span>Peaked: {narrative.peakDate}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Newspaper className="w-4 h-4 text-primary" />
                          <span>{narrative.sources.length} outlets pushing this</span>
                        </div>
                      </div>

                      {narrative.sources.length > 0 && (
                        <div className="p-3 rounded-lg bg-card/30 border border-border/30">
                          <p className="text-xs text-muted-foreground mb-2">
                            <strong>Media Outlets Pushing This Angle:</strong>
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {narrative.sources.slice(0, 8).map((source, i) => (
                              <span key={i} className="px-2 py-1 text-xs rounded-lg bg-background/50 border border-border/50">
                                {source}
                              </span>
                            ))}
                            {narrative.sources.length > 8 && (
                              <span className="px-2 py-1 text-xs rounded-lg bg-background/50 border border-border/50 font-semibold">
                                +{narrative.sources.length - 8} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                      
                      <div className="mt-3 p-3 rounded-lg bg-blue-500/5 border border-blue-500/20">
                        <p className="text-xs text-muted-foreground">
                          <strong>What This Means:</strong> {narrative.frequency > 15 ? 
                            'This is the DOMINANT narrative - most media wants you to think this way.' :
                            narrative.frequency > 8 ?
                            'This is a MAJOR narrative - significant media push behind this angle.' :
                            'This is an ALTERNATIVE narrative - less prominent but still present.'}
                          {narrative.sources.length < 3 ? ' ⚠️ Low source diversity suggests possible propaganda.' : ''}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-primary/20">
                  <div className="flex items-start gap-2">
                    <GraduationCap className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-foreground mb-1">Critical Thinking Exercise:</p>
                      <p className="text-sm text-muted-foreground">
                        Ask yourself: Which narrative is missing? What perspective isn't being covered? Who benefits if you believe narrative #1 vs #2? 
                        Try finding independent sources or international coverage for comparison.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              )}

              {/* Context & Timeline - Only if context data exists */}
              {analysis.context && (analysis.context.majorEvents?.length > 0 || analysis.context.relatedTopics?.length > 0) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Major Events */}
                  {analysis.context.majorEvents && analysis.context.majorEvents.length > 0 && (
                    <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-primary" />
                        Major Events
                      </h3>
                      <ul className="space-y-2">
                        {analysis.context.majorEvents.map((event, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                            <span className="text-muted-foreground">{event}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Related Topics */}
                  {analysis.context.relatedTopics && analysis.context.relatedTopics.length > 0 && (
                    <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Target className="w-5 h-5 text-primary" />
                        Related Topics
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {analysis.context.relatedTopics.map((topic, index) => (
                          <span
                            key={index}
                            className="px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/30 text-sm hover:bg-primary/20 cursor-pointer transition-colors"
                            onClick={() => {
                              setTopic(topic);
                              analyzeNarrative();
                            }}
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Timeline Visualization */}
              {analysis.timeline && analysis.timeline.length > 0 && (
                <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-primary" />
                    Coverage Timeline
                  </h3>
                  <div className="space-y-3">
                    {analysis.timeline.map((point, index) => (
                      <div key={index} className="flex items-start gap-4">
                        <div className="flex flex-col items-center">
                          <div className={`w-4 h-4 rounded-full border-2 ${getSentimentBg(point.sentiment)}`} />
                          {index < analysis.timeline.length - 1 && (
                            <div className="w-0.5 h-16 bg-border/50" />
                          )}
                        </div>
                        <div className="flex-1 pb-4">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-semibold">{point.date}</span>
                            <span className={`text-sm ${getSentimentColor(point.sentiment)}`}>
                              {point.sentiment}
                            </span>
                          </div>
                          <div className="text-sm text-muted-foreground mb-2">
                            {point.count} articles published
                          </div>
                          {point.keyEvents.length > 0 && (
                            <div className="space-y-1">
                              {point.keyEvents.map((event, i) => (
                                <div key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                                  <span className="text-primary">•</span>
                                  <span>{event}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* How It Works */}
          {!analysis && !analyzing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              {[
                {
                  icon: Newspaper,
                  title: "Data Collection",
                  description: "Analyzes news articles from multiple sources over your selected timeframe"
                },
                {
                  icon: LineChart,
                  title: "Pattern Recognition",
                  description: "Identifies trends, coordinated messaging, and narrative shifts using AI"
                },
                {
                  icon: Eye,
                  title: "Context Awareness",
                  description: "Provides historical context and highlights potential manipulation indicators"
                }
              ].map((step, index) => (
                <div key={index} className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                  <div className="p-3 bg-primary/10 border border-primary/30 rounded-xl w-fit mb-4">
                    <step.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NarrativeAnalyzer;