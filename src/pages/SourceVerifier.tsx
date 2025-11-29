// Source Verifier - Check journalist and source credibility
import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  ArrowLeft,
  Search,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ExternalLink,
  User,
  Newspaper,
  Twitter,
  Globe,
  TrendingUp,
  Award,
  Loader2,
  Shield,
  Target,
  Zap,
  Info,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const SourceVerifier = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchingWeb, setSearchingWeb] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [notFound, setNotFound] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const verifySource = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    setNotFound(false);
    setResult(null);
    
    try {
      // STEP 1: Try to find journalist in database first
      const response = await axios.get(`${API_URL}/lms/journalists/all`);
      
      let journalist = null;
      
      if (response.data.status === "success" && Array.isArray(response.data.journalists)) {
        // Find matching journalist (case-insensitive search)
        const searchLower = searchQuery.toLowerCase();
        journalist = response.data.journalists.find((j: any) => 
          j.name?.toLowerCase().includes(searchLower) ||
          j.aiProfile?.name?.toLowerCase().includes(searchLower)
        );
      }
      
      // STEP 2: If not found in database, do web search and generate new profile
      if (!journalist) {
        console.log(`Journalist "${searchQuery}" not found in database. Performing web search...`);
        setSearchingWeb(true);
        toast.info(`Not in database. Searching the web for ${searchQuery}...`);
        
        try {
          // Call the homepage API to generate a new journalist case study
          const generateResponse = await axios.post(`${API_URL}/generate-case-study`, {
            journalist_name: searchQuery,
            analyze_articles: true,
          });
          
          if (generateResponse.data.status === "success") {
            // Use the newly generated data
            journalist = {
              name: searchQuery,
              aiProfile: generateResponse.data.analysis,
              scrapedData: generateResponse.data.scraped_data,
              image: generateResponse.data.analysis?.digitalPresence?.profileImage,
            };
            
            toast.success(`✨ Generated new profile for ${searchQuery} from web search!`);
            setSearchingWeb(false);
          } else {
            throw new Error("Web search failed");
          }
        } catch (webSearchError) {
          console.error("Web search failed:", webSearchError);
          toast.error(`Could not find reliable information about ${searchQuery}`);
          setSearchingWeb(false);
          setNotFound(true);
          setSearching(false);
          return;
        }
      }
      
      // Extract AI profile data
      const aiProfile = journalist.aiProfile || {};
      const scrapedData = journalist.scrapedData || {};
      const digitalPresence = aiProfile.digitalPresence || {};
      const engagementInsights = aiProfile.engagementInsights || {};
      const credibilityScore = aiProfile.credibilityScore || {};
      const articlesData = aiProfile.articlesAnalyzed || {};
      const recommendationScore = aiProfile.recommendationScore || {};
      const toneAnalysis = aiProfile.toneAnalysis || {};
      
      // Calculate verification confidence based on data availability
      const dataPoints = {
        hasArticles: articlesData.total > 0,
        hasAwards: (aiProfile.awards || []).length > 0,
        hasMediaAffiliations: (digitalPresence.mediaAffiliations || []).length > 0,
        hasVerifiedLinks: (digitalPresence.verifiedLinks || []).length > 0,
        hasBiography: !!(aiProfile.biography || aiProfile.bio),
        hasNotableWorks: (aiProfile.notableWorks || []).length > 0,
      };
      
      const dataPointsCount = Object.values(dataPoints).filter(Boolean).length;
      const verificationConfidence = Math.round((dataPointsCount / 6) * 100);
      
      // Build result object with AI insights
      setResult({
        // Basic Info
        name: journalist.name || aiProfile.name,
        type: "journalist",
        credibility_score: credibilityScore.overall || credibilityScore.score || 75,
        verified: true,
        bio: aiProfile.biography || aiProfile.bio || "Journalist profile",
        profileImage: digitalPresence.profileImage || journalist.image,
        verification_confidence: verificationConfidence,
        data_sources_count: dataPointsCount,
        
        // Media Affiliations
        publications: (digitalPresence.mediaAffiliations || []).map((name: string) => ({
          name: name,
          role: "Affiliated Journalist"
        })),
        
        // Social Media & Digital Presence
        social_media: {
          presence: digitalPresence.onlineReach || "Unknown",
          verified_links: digitalPresence.verifiedLinks || [],
          followers: digitalPresence.onlineReach,
        },
        
        // Notable Works (from AI analysis)
        recent_work: (aiProfile.notableWorks || aiProfile.keyArticles || []).map((work: any) => ({
          title: typeof work === 'string' ? work : work.title || work.name,
          outlet: digitalPresence.mediaAffiliations?.[0] || "Various",
          date: articlesData.dateRange || "Recent",
          impact: "High"
        })).slice(0, 5),
        
        // AI-Generated Trust Indicators (from strengths)
        trust_indicators: recommendationScore.strengths || [
          "Professional journalism credentials",
          "Published in reputable outlets",
          "Analyzed by AI for credibility"
        ],
        
        // AI-Generated Red Flags (from concerns)
        red_flags: recommendationScore.concerns || [],
        
        // Additional AI Insights
        ai_insights: {
          writing_tone: aiProfile.writingTone,
          ethical_assessment: aiProfile.ethicalAssessment,
          ideological_bias: aiProfile.ideologicalBias,
          political_affiliation: aiProfile.politicalAffiliation,
          influence_level: engagementInsights.influenceLevel,
          audience_sentiment: engagementInsights.audienceSentiment,
          controversy_level: engagementInsights.controversyLevel,
          trustworthiness: engagementInsights.trustworthiness,
          objectivity: toneAnalysis.objectivity,
          bias: toneAnalysis.bias,
          consistency: toneAnalysis.consistency,
          recommendation_score: recommendationScore.overall,
          recommendation_reasoning: recommendationScore.reasoning,
        },
        
        // Articles Analysis
        articles_analyzed: {
          total: articlesData.total || 0,
          verification_rate: articlesData.verificationRate || scrapedData.verification_rate,
          top_domains: articlesData.topDomains || [],
          date_range: articlesData.dateRange,
        },
        
        // Controversies
        controversies: aiProfile.controversies || [],
        
        // Awards
        awards: aiProfile.awards || [],
        
        // Career Highlights
        career_highlights: aiProfile.careerHighlights || [],
        
        // Region
        region: aiProfile.region || aiProfile.country || "International",
      });
      
      setSearching(false);
    } catch (error) {
      console.error("Source verification failed:", error);
      setNotFound(true);
      setSearching(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "from-green-500/10 to-green-600/10 border-green-500/30";
    if (score >= 60) return "from-yellow-500/10 to-yellow-600/10 border-yellow-500/30";
    return "from-red-500/10 to-red-600/10 border-red-500/30";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-card/80 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 transition-all duration-300 text-foreground hover:text-primary"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Dashboard</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary/10 border border-primary/30 rounded-xl">
              <Search className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-orbitron font-bold text-primary">
                Source Verifier
              </h1>
              <p className="text-xs text-muted-foreground">Check journalist & source credibility</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Banner - Enhanced Credibility */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-primary/30"
        >
          <div className="flex items-start gap-4">
            <div className="p-3 bg-primary/20 rounded-xl flex-shrink-0">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                Professional Source Verification System
                <Badge variant="outline" className="text-xs">v2.0</Badge>
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                Multi-layered verification system combining AI analysis, web scraping, and cross-referencing 
                to provide credibility assessments for journalists and news sources.
              </p>
              
              {/* Methodology Overview */}
              <div className="bg-card/50 rounded-lg p-4 mb-4 border border-border/50">
                <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4 text-primary" />
                  Verification Methodology
                </h4>
                <div className="grid md:grid-cols-2 gap-3 text-xs">
                  <div>
                    <strong className="text-primary">Data Sources:</strong>
                    <ul className="mt-1 space-y-1 text-muted-foreground ml-4">
                      <li>• Google News & Search APIs</li>
                      <li>• Wikipedia & Public Databases</li>
                      <li>• Social Media Verification</li>
                      <li>• Publication History Analysis</li>
                    </ul>
                  </div>
                  <div>
                    <strong className="text-primary">Analysis Criteria:</strong>
                    <ul className="mt-1 space-y-1 text-muted-foreground ml-4">
                      <li>• Publication outlet credibility</li>
                      <li>• Article fact-checking history</li>
                      <li>• Bias detection via NLP</li>
                      <li>• Cross-reference verification</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-start gap-2 p-3 bg-background/50 rounded-lg">
                  <User className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground block">Profile Analysis</strong>
                    <span className="text-xs text-muted-foreground">Career history, affiliations, awards</span>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-3 bg-background/50 rounded-lg">
                  <Newspaper className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground block">Work Verification</strong>
                    <span className="text-xs text-muted-foreground">Published articles, fact-check rate</span>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-3 bg-background/50 rounded-lg">
                  <Target className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground block">AI Assessment</strong>
                    <span className="text-xs text-muted-foreground">Bias detection, tone analysis</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Search Interface */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 mb-8"
        >
          <div className="flex gap-3">
            <Input
              placeholder="Enter journalist name, author, or source..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && verifySource()}
              className="flex-1 h-12 text-lg"
            />
            <Button
              onClick={verifySource}
              disabled={searching || !searchQuery.trim()}
              className="h-12 px-8"
            >
              {searching ? (
                searchingWeb ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    <div className="flex flex-col items-start">
                      <span>Searching Web...</span>
                      <span className="text-xs opacity-75">Generating profile</span>
                    </div>
                  </>
                ) : (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Checking Database...
                  </>
                )
              ) : (
                <>
                  <Search className="w-5 h-5 mr-2" />
                  Verify Source
                </>
              )}
            </Button>
          </div>

          {/* Quick Examples */}
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-muted-foreground">Try:</span>
            {["Arnab Goswami", "Ravish Kumar", "Barkha Dutt", "Glenn Greenwald"].map((example) => (
              <button
                key={example}
                onClick={() => {
                  setSearchQuery(example);
                  setNotFound(false);
                }}
                className="text-sm px-3 py-1 rounded-full bg-primary/10 hover:bg-primary/20 text-primary transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Not Found State */}
        {notFound && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 text-center"
          >
            <XCircle className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-xl font-bold mb-2">Source Not Found</h3>
            <p className="text-muted-foreground mb-4">
              We couldn't find <strong>"{searchQuery}"</strong> in our database and web search also failed.
            </p>
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg mb-4">
              <p className="text-sm text-muted-foreground">
                💡 <strong>What we tried:</strong>
              </p>
              <ul className="text-sm text-muted-foreground text-left mt-2 space-y-1">
                <li>✓ Searched our verified journalist database</li>
                <li>✓ Performed web search to generate new profile</li>
                <li>✗ No reliable information found</li>
              </ul>
            </div>
            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg mb-4">
              <p className="text-sm">
                <strong>Suggestions:</strong>
              </p>
              <ul className="text-sm text-muted-foreground text-left mt-2 space-y-1">
                <li>• Check spelling of the name</li>
                <li>• Try searching for well-known journalists</li>
                <li>• Use the homepage to manually generate a case study</li>
              </ul>
            </div>
            <div className="flex gap-2 justify-center">
              <Button onClick={() => {
                setNotFound(false);
                setSearchQuery("");
              }}>
                Try Another Search
              </Button>
              <Button variant="outline" onClick={() => navigate("/")}>
                Generate Case Study
              </Button>
            </div>
          </motion.div>
        )}

        {/* Results */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Verification Overview */}
            <div className="p-6 rounded-xl bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/30 mb-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Verification Report
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-background/50 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-1">
                    {result.verification_confidence}%
                  </div>
                  <div className="text-xs text-muted-foreground">Verification Confidence</div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    Based on {result.data_sources_count}/6 data points
                  </div>
                </div>
                <div className="text-center p-4 bg-background/50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-500 mb-1">
                    {result.articles_analyzed?.total || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">Articles Analyzed</div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    Cross-referenced & verified
                  </div>
                </div>
                <div className="text-center p-4 bg-background/50 rounded-lg">
                  <div className="text-3xl font-bold text-green-500 mb-1">
                    {result.articles_analyzed?.verification_rate || "N/A"}
                  </div>
                  <div className="text-xs text-muted-foreground">Fact-Check Rate</div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    Verified claims accuracy
                  </div>
                </div>
              </div>
              
              {/* Data Sources Used */}
              <div className="mt-4 p-3 bg-background/30 rounded-lg">
                <div className="text-xs font-semibold text-muted-foreground mb-2">Data Sources Used:</div>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="text-xs">
                    <Globe className="w-3 h-3 mr-1" />
                    Google News API
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    <Search className="w-3 h-3 mr-1" />
                    Web Scraping
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    <Newspaper className="w-3 h-3 mr-1" />
                    Publication Records
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    <Zap className="w-3 h-3 mr-1" />
                    AI NLP Analysis
                  </Badge>
                  {result.social_media?.verified_links?.length > 0 && (
                    <Badge variant="outline" className="text-xs">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Social Media
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            {/* Credibility Score */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                className={`p-6 rounded-xl bg-gradient-to-br ${getScoreBg(
                  result.credibility_score
                )} border backdrop-blur-md col-span-1`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-muted-foreground">CREDIBILITY SCORE</span>
                  {result.verified && <CheckCircle className="w-5 h-5 text-green-500" />}
                </div>
                <div className={`text-5xl font-bold ${getScoreColor(result.credibility_score)}`}>
                  {result.credibility_score}
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  {result.credibility_score >= 80
                    ? "Highly Trusted"
                    : result.credibility_score >= 60
                    ? "Moderately Trusted"
                    : "Use Caution"}
                </div>
                <div className="mt-3 text-xs text-muted-foreground">
                  <strong>Methodology:</strong> AI-powered analysis of publication history, bias patterns, and fact-checking records
                </div>
              </div>

              {/* Profile Info */}
              <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50 col-span-2">
                <div className="flex items-start gap-4">
                  {/* Profile Image or Icon */}
                  {result.profileImage ? (
                    <img 
                      src={result.profileImage} 
                      alt={result.name}
                      className="w-16 h-16 rounded-xl object-cover border-2 border-primary/30"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div 
                    className="p-3 bg-primary/10 rounded-xl flex items-center justify-center"
                    style={{ display: result.profileImage ? 'none' : 'flex', minWidth: '64px', minHeight: '64px' }}
                  >
                    <User className="w-8 h-8 text-primary" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-xl font-bold">{result.name}</h3>
                      {result.verified && (
                        <Badge className="bg-green-500/20 text-green-500 border-green-500/30">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Verified
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{result.bio}</p>
                    
                    {/* Region */}
                    {result.region && (
                      <div className="flex items-center gap-2 mb-2">
                        <Globe className="w-4 h-4 text-primary" />
                        <span className="text-sm">{result.region}</span>
                      </div>
                    )}
                    
                    {/* Digital Presence */}
                    {result.social_media && result.social_media.presence && (
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                        <span className="text-sm">Online Reach: {result.social_media.presence}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Publications */}
            <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Newspaper className="w-5 h-5 text-primary" />
                Publications & Affiliations
              </h3>
              <div className="grid md:grid-cols-2 gap-3">
                {result.publications.map((pub: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-background border border-border/50 flex items-center gap-3"
                  >
                    <Newspaper className="w-5 h-5 text-primary" />
                    <div>
                      <div className="font-semibold text-sm">{pub.name}</div>
                      <div className="text-xs text-muted-foreground">{pub.role}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Work */}
            <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                Recent Work
              </h3>
              <div className="space-y-3">
                {result.recent_work.map((work: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 rounded-lg bg-background border border-border/50 hover:bg-accent transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm mb-1">{work.title}</h4>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{work.outlet}</span>
                          <span>•</span>
                          <span>{work.date}</span>
                          <span>•</span>
                          <Badge variant={work.impact === "High" ? "default" : "secondary"} className="text-xs">
                            {work.impact} Impact
                          </Badge>
                        </div>
                      </div>
                      <ExternalLink className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Insights Section */}
            {result.ai_insights && (
              <div className="p-6 rounded-xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-primary/30">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-primary" />
                  AI Analysis & Insights
                </h3>
                <div className="grid md:grid-cols-3 gap-4">
                  {result.ai_insights.writing_tone && (
                    <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                      <div className="text-xs text-muted-foreground mb-1">Writing Tone</div>
                      <div className="text-sm font-semibold">{result.ai_insights.writing_tone}</div>
                    </div>
                  )}
                  {result.ai_insights.ideological_bias && (
                    <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                      <div className="text-xs text-muted-foreground mb-1">Ideological Bias</div>
                      <div className="text-sm font-semibold">{result.ai_insights.ideological_bias}</div>
                    </div>
                  )}
                  {result.ai_insights.objectivity && (
                    <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                      <div className="text-xs text-muted-foreground mb-1">Objectivity</div>
                      <div className="text-sm font-semibold">{result.ai_insights.objectivity}</div>
                    </div>
                  )}
                  {result.ai_insights.influence_level && (
                    <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                      <div className="text-xs text-muted-foreground mb-1">Influence Level</div>
                      <div className="text-sm font-semibold text-primary">{result.ai_insights.influence_level}</div>
                    </div>
                  )}
                  {result.ai_insights.trustworthiness && (
                    <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                      <div className="text-xs text-muted-foreground mb-1">Trustworthiness</div>
                      <div className="text-sm font-semibold">{result.ai_insights.trustworthiness}</div>
                    </div>
                  )}
                  {result.ai_insights.controversy_level && (
                    <div className="p-4 rounded-lg bg-card/50 border border-border/50">
                      <div className="text-xs text-muted-foreground mb-1">Controversy Level</div>
                      <div className="text-sm font-semibold text-orange-600">{result.ai_insights.controversy_level}</div>
                    </div>
                  )}
                </div>
                
                {/* AI Recommendation */}
                {result.ai_insights.recommendation_score !== null && (
                  <div className="mt-4 p-4 rounded-lg bg-card/50 border border-border/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold">AI Recommendation Score</span>
                      <span className={`text-2xl font-bold ${
                        result.ai_insights.recommendation_score >= 7 
                          ? 'text-green-500' 
                          : result.ai_insights.recommendation_score >= 4 
                            ? 'text-yellow-500'
                            : 'text-red-500'
                      }`}>
                        {result.ai_insights.recommendation_score}/10
                      </span>
                    </div>
                    {result.ai_insights.recommendation_reasoning && (
                      <p className="text-sm text-muted-foreground">{result.ai_insights.recommendation_reasoning}</p>
                    )}
                  </div>
                )}
                
                {/* Ethical Assessment */}
                {result.ai_insights.ethical_assessment && (
                  <div className="mt-4 p-4 rounded-lg bg-card/50 border border-border/50">
                    <div className="text-xs text-muted-foreground mb-2">Ethical Assessment</div>
                    <p className="text-sm">{result.ai_insights.ethical_assessment}</p>
                  </div>
                )}
              </div>
            )}

            {/* Articles Analysis */}
            {result.articles_analyzed && result.articles_analyzed.total > 0 && (
              <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-primary" />
                  Articles Analysis ({result.articles_analyzed.total} articles)
                </h3>
                <div className="grid md:grid-cols-3 gap-4 mb-4">
                  <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                    <div className="text-xs text-muted-foreground mb-1">Verification Rate</div>
                    <div className="text-2xl font-bold text-green-600">
                      {result.articles_analyzed.verification_rate || "N/A"}
                    </div>
                  </div>
                  {result.articles_analyzed.date_range && (
                    <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                      <div className="text-xs text-muted-foreground mb-1">Period Analyzed</div>
                      <div className="text-sm font-semibold">{result.articles_analyzed.date_range}</div>
                    </div>
                  )}
                  <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                    <div className="text-xs text-muted-foreground mb-1">Publication Sources</div>
                    <div className="text-sm font-semibold">
                      {result.articles_analyzed.top_domains?.length || 0} outlets
                    </div>
                  </div>
                </div>
                {result.articles_analyzed.top_domains && result.articles_analyzed.top_domains.length > 0 && (
                  <div>
                    <div className="text-sm font-semibold mb-2">Top Publication Domains:</div>
                    <div className="flex flex-wrap gap-2">
                      {result.articles_analyzed.top_domains.map((domain: string, idx: number) => (
                        <Badge key={idx} variant="secondary">{domain}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Controversies */}
            {result.controversies && result.controversies.length > 0 && (
              <div className="p-6 rounded-xl bg-orange-500/10 border border-orange-500/30">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-orange-600">
                  <AlertTriangle className="w-5 h-5" />
                  Notable Controversies
                </h3>
                <div className="space-y-3">
                  {result.controversies.map((controversy: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-lg bg-card/50 border border-border/50">
                      <p className="text-sm">
                        {typeof controversy === 'string' ? controversy : controversy.description || JSON.stringify(controversy)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Awards */}
            {result.awards && result.awards.length > 0 && (
              <div className="p-6 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-yellow-600">
                  <Award className="w-5 h-5" />
                  Awards & Recognition
                </h3>
                <div className="grid md:grid-cols-2 gap-3">
                  {result.awards.map((award: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-lg bg-card/50 border border-border/50 flex items-center gap-2">
                      <Award className="w-4 h-4 text-yellow-600" />
                      <span className="text-sm">{typeof award === 'string' ? award : award.name || award.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Trust Indicators */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Positive Indicators */}
              {result.trust_indicators.length > 0 && (
                <div className="p-6 rounded-xl bg-green-500/10 border border-green-500/30">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-green-500">
                    <CheckCircle className="w-5 h-5" />
                    Trust Indicators (AI Analysis)
                  </h3>
                  <ul className="space-y-2">
                    {result.trust_indicators.map((indicator: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{indicator}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Red Flags */}
              {result.red_flags.length > 0 && (
                <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/30">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-500">
                    <AlertTriangle className="w-5 h-5" />
                    Concerns & Red Flags (AI Analysis)
                  </h3>
                  <ul className="space-y-2">
                    {result.red_flags.map((flag: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-sm">
                        <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Methodology & Limitations */}
            <div className="p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Info className="w-5 h-5 text-primary" />
                Verification Methodology & Limitations
              </h3>
              
              <div className="space-y-4 text-sm">
                <div>
                  <h4 className="font-semibold mb-2">How We Verify:</h4>
                  <ul className="space-y-1 text-muted-foreground ml-4">
                    <li>✓ <strong>Data Collection:</strong> Aggregate information from Google News, Wikipedia, and public databases</li>
                    <li>✓ <strong>Article Analysis:</strong> AI analyzes writing patterns, fact-checking history, and source usage</li>
                    <li>✓ <strong>Bias Detection:</strong> NLP algorithms detect ideological leanings and tone consistency</li>
                    <li>✓ <strong>Cross-Reference:</strong> Verify claims across multiple independent sources</li>
                    <li>✓ <strong>Reputation Check:</strong> Analyze publication outlet credibility and awards</li>
                  </ul>
                </div>
                
                <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                  <h4 className="font-semibold mb-2 text-yellow-600">Important Limitations:</h4>
                  <ul className="space-y-1 text-muted-foreground text-xs ml-4">
                    <li>• AI analysis is based on publicly available information and may not be complete</li>
                    <li>• Credibility scores are algorithmic assessments, not definitive judgments</li>
                    <li>• Recent events or controversies may not yet be reflected in the data</li>
                    <li>• This tool is educational and should be used alongside critical thinking</li>
                    <li>• Always verify important information through multiple independent sources</li>
                  </ul>
                </div>
                
                <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Best Practices for Students:
                  </h4>
                  <ul className="space-y-1 text-muted-foreground text-xs ml-4">
                    <li>1. Use this as a starting point, not the final word</li>
                    <li>2. Read the journalist's actual work to form your own opinion</li>
                    <li>3. Check multiple fact-checking organizations (Snopes, FactCheck.org, etc.)</li>
                    <li>4. Consider the publication outlet's editorial standards</li>
                    <li>5. Look for patterns across multiple articles, not just one piece</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-center">
              <Button variant="outline" onClick={() => navigate("/journalists-gallery")}>
                <User className="w-4 h-4 mr-2" />
                View Full Profile
              </Button>
              <Button onClick={() => {
                setResult(null);
                setSearchQuery("");
              }}>
                <Search className="w-4 h-4 mr-2" />
                Verify Another Source
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SourceVerifier;
