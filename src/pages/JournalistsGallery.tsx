// Journalism Case Studies Gallery - Educational Resource
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Search,
  Filter,
  Award,
  TrendingUp,
  Users,
  MapPin,
  ArrowLeft,
  ExternalLink,
  BookOpen,
  CheckCircle,
  FileText,
  Play,
  Lightbulb,
  Target,
  GraduationCap,
} from "lucide-react";

const JournalistsGallery = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("All");
  const [journalists, setJournalists] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJournalist, setSelectedJournalist] = useState<any>(null);
  const [showProfile, setShowProfile] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const filters = ["All", "Investigative", "War Reporting", "Political", "Digital/Tech", "Historical"];

  useEffect(() => {
    loadJournalists();
  }, []);

  const loadJournalists = async () => {
    setLoading(true);
    try {
      console.log("🌐 API_URL:", API_URL);
      console.log("📝 VITE_API_URL:", import.meta.env.VITE_API_URL);
      console.log("🔍 Fetching from:", `${API_URL}/lms/journalists/all`);
      
      const response = await axios.get(`${API_URL}/lms/journalists/all`);
      console.log("=== API RESPONSE ===");
      console.log("Status:", response.status);
      console.log("Data status:", response.data.status);
      console.log("Count:", response.data.count);
      console.log("Sample journalist:", response.data.journalists?.[0]?.name);
      console.log("==================");
      
      if (response.data.status === "success" && Array.isArray(response.data.journalists)) {
        // Transform database format to match the component's expected format
        const transformedJournalists = response.data.journalists.map((j: any) => {
          try {
            console.log("Processing journalist:", j);
            
            // Extract aiProfile (this is the main data container)
            const aiProfile = j.aiProfile || j.analysis || {};
            const scrapedData = j.scrapedData || {};
            const metadata = j._metadata || {};
            
            // Safely extract specializations
            let specializations = ["General Journalism"];
            if (Array.isArray(aiProfile.mainTopics) && aiProfile.mainTopics.length > 0) {
              specializations = aiProfile.mainTopics;
            } else if (Array.isArray(j.specializations) && j.specializations.length > 0) {
              specializations = j.specializations;
            }
            
            // Extract lessons from strengths/concerns
            let lessons = [];
            if (Array.isArray(aiProfile.recommendationScore?.strengths)) {
              lessons = aiProfile.recommendationScore.strengths;
            } else if (Array.isArray(aiProfile.lessons)) {
              lessons = aiProfile.lessons;
            } else if (aiProfile.keyLessons && Array.isArray(aiProfile.keyLessons)) {
              lessons = aiProfile.keyLessons;
            }
            if (lessons.length === 0) {
              lessons = ["Professional journalism practices", "Ethical reporting standards", "Source verification"];
            }
            
            // Get profile image - CORRECT PATH: aiProfile.digitalPresence.profileImage
            let profileImage = null;
            
            // Try the CORRECT nested path first
            if (aiProfile.digitalPresence?.profileImage) {
              profileImage = aiProfile.digitalPresence.profileImage;
            }
            // Fallback to other possible locations
            else if (j.image) {
              profileImage = j.image;
            }
            else if (j.profile_image) {
              profileImage = j.profile_image;
            }
            else if (aiProfile.profileImage) {
              profileImage = aiProfile.profileImage;
            }
            else if (aiProfile.image) {
              profileImage = aiProfile.image;
            }
            else if (scrapedData.primary_profile?.imageUrl) {
              profileImage = scrapedData.primary_profile.imageUrl;
            }
            else if (scrapedData.imageUrl) {
              profileImage = scrapedData.imageUrl;
            }
            
            // Log for debugging
            console.log(`[${j.name}] Image resolved:`, {
              digitalPresence: aiProfile.digitalPresence?.profileImage,
              direct: j.image,
              profile_image: j.profile_image, 
              aiProfile_profileImage: aiProfile.profileImage,
              scrapedData_primaryProfile: scrapedData.primary_profile?.imageUrl,
              RESOLVED: profileImage
            });
            
            // Extract full biography (not truncated) - try all possible fields
            const fullBio = aiProfile.biography || 
                           aiProfile.bio || 
                           aiProfile.summary ||
                           aiProfile.overview ||
                           j.bio || 
                           scrapedData.bio ||
                           "Journalist profile";
            
            // Extract notable works with full details
            let notableWorks = [];
            if (Array.isArray(aiProfile.notableWorks)) {
              notableWorks = aiProfile.notableWorks;
            } else if (Array.isArray(aiProfile.keyArticles)) {
              notableWorks = aiProfile.keyArticles;
            } else if (Array.isArray(aiProfile.major_stories)) {
              notableWorks = aiProfile.major_stories;
            }
            
            // Extract career highlights
            let careerHighlights = [];
            if (Array.isArray(aiProfile.careerHighlights)) {
              careerHighlights = aiProfile.careerHighlights;
            } else if (Array.isArray(aiProfile.highlights)) {
              careerHighlights = aiProfile.highlights;
            }
            
            // Extract awards with full details
            let awardsList = [];
            if (Array.isArray(aiProfile.awards)) {
              awardsList = aiProfile.awards;
            }
            
            // Extract writing style/tone
            const writingStyle = aiProfile.writingTone || 
                               aiProfile.writingStyle || 
                               aiProfile.style ||
                               null;
            
            // Extract ethical approach/assessment
            const ethicalApproach = aiProfile.ethicalAssessment || 
                                   aiProfile.ethicalApproach ||
                                   aiProfile.ethics ||
                                   null;
            
            // Extract sourcing methods (may not exist, but try)
            const sourcingMethods = aiProfile.sourcingMethods || 
                                   aiProfile.sourcing ||
                                   null;
            
            // Extract impact/influence
            const impact = aiProfile.influenceLevel || 
                         aiProfile.impact || 
                         aiProfile.influence ||
                         null;
            
            // Extract controversies (this is an array in the actual data)
            const controversies = aiProfile.controversies || [];
            
            // Extract additional metadata
            const ideology = aiProfile.ideologicalBias || 
                           aiProfile.ideology ||
                           null;
            
            const politicalAffiliation = aiProfile.politicalAffiliation || null;
                           
            const region = aiProfile.region || 
                         aiProfile.country || 
                         j.region || 
                         j.country ||
                         "International";
            
            // Extract digital presence data
            const digitalPresence = aiProfile.digitalPresence || {};
            const mediaAffiliations = digitalPresence.mediaAffiliations || [];
            const onlineReach = digitalPresence.onlineReach || null;
            const verifiedLinks = digitalPresence.verifiedLinks || [];
            
            // Extract engagement insights
            const engagementInsights = aiProfile.engagementInsights || {};
            const audienceSentiment = engagementInsights.audienceSentiment || null;
            const influenceLevel = engagementInsights.influenceLevel || null;
            const controversyLevel = engagementInsights.controversyLevel || null;
            const trustworthiness = engagementInsights.trustworthiness || null;
            
            // Extract credibility score (nested object)
            const credibilityScore = aiProfile.credibilityScore || {};
            const credibilityOverall = credibilityScore.overall || credibilityScore.score || 75;
            
            // Extract articles analyzed data
            const articlesAnalyzedData = aiProfile.articlesAnalyzed || {};
            const articlesTotal = articlesAnalyzedData.total || metadata.articlesAnalyzed || 0;
            const verificationRate = articlesAnalyzedData.verificationRate || 
                                    scrapedData.verification_rate || 
                                    null;
            const topDomains = articlesAnalyzedData.topDomains || [];
            const dateRange = articlesAnalyzedData.dateRange || null;
            
            // Extract tone analysis
            const toneAnalysis = aiProfile.toneAnalysis || {};
            const emotionalTone = toneAnalysis.emotionalTone || null;
            const bias = toneAnalysis.bias || null;
            const objectivity = toneAnalysis.objectivity || null;
            const consistency = toneAnalysis.consistency || null;
            
            // Extract recommendation score
            const recommendationScore = aiProfile.recommendationScore || {};
            const recommendationOverall = recommendationScore.overall || null;
            const recommendationReasoning = recommendationScore.reasoning || null;
            const strengths = recommendationScore.strengths || [];
            const concerns = recommendationScore.concerns || [];
            
            return {
              // Basic Info
              name: String(j.name || aiProfile.name || "Unknown Journalist"),
              bio: String(fullBio).substring(0, 200), // Short version for card
              fullBio: String(fullBio), // Full version for modal
              specializations: specializations,
              credibilityScore: Number(credibilityOverall),
              articlesPublished: Number(articlesTotal),
              awards: Number(awardsList.length),
              region: region,
              verified: Boolean(j.verified || true), // All analyzed journalists are verified
              profileImage: profileImage,
              
              // Investigation Details
              keyInvestigation: String(
                (notableWorks[0]?.title) || 
                (notableWorks[0]) ||
                (careerHighlights[0]) || 
                "Various investigations"
              ).substring(0, 100),
              
              // Full Case Study Data - Major Sections
              notableWorks: notableWorks,
              careerHighlights: careerHighlights,
              awardsList: awardsList,
              lessons: lessons,
              writingStyle: writingStyle,
              ethicalApproach: ethicalApproach,
              sourcingMethods: sourcingMethods,
              impact: impact,
              controversies: controversies,
              ideology: ideology,
              politicalAffiliation: politicalAffiliation,
              
              // Digital Presence
              mediaAffiliations: mediaAffiliations,
              onlineReach: onlineReach,
              verifiedLinks: verifiedLinks,
              
              // Engagement Insights
              audienceSentiment: audienceSentiment,
              influenceLevel: influenceLevel,
              controversyLevel: controversyLevel,
              trustworthiness: trustworthiness,
              
              // Credibility Details (full object)
              credibilityDetails: credibilityScore,
              
              // Articles Analyzed Data
              verificationRate: verificationRate,
              topDomains: topDomains,
              dateRange: dateRange,
              
              // Tone Analysis
              toneAnalysis: {
                emotionalTone: emotionalTone,
                bias: bias,
                objectivity: objectivity,
                consistency: consistency,
              },
              
              // Recommendation Score
              recommendationScore: recommendationOverall,
              recommendationReasoning: recommendationReasoning,
              strengths: strengths,
              concerns: concerns,
              
              // Analysis timestamp
              analyzedAt: metadata.analysis_timestamp || j.analysis_timestamp,
              
              // Raw data for debugging (can be removed in production)
              rawAiProfile: aiProfile,
              rawScrapedData: scrapedData,
            };
          } catch (err) {
            console.error("Error processing journalist:", j, err);
            return null;
          }
        }).filter((j: any) => j !== null); // Remove any failed transformations
        
        console.log("Transformed journalists:", transformedJournalists);
        setJournalists(transformedJournalists);
      } else {
        console.warn("Invalid response format or no journalists found");
        setJournalists([]);
      }
    } catch (error: any) {
      console.error("❌ Failed to load journalists:", error);
      console.error("❌ Error details:", error.response?.data || error.message);
      console.error("❌ API URL used:", `${API_URL}/lms/journalists/all`);
      // Fallback to showing empty state
      setJournalists([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredJournalists = journalists.filter((j) => {
    const matchesSearch =
      searchQuery === "" ||
      j.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      j.bio.toLowerCase().includes(searchQuery.toLowerCase()) ||
      j.specializations.some((s) => s.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesFilter =
      selectedFilter === "All" ||
      j.specializations.some((s) =>
        selectedFilter === "Digital/Tech"
          ? ["Disinformation", "Tech Policy", "Digital"].some((k) => s.includes(k))
          : selectedFilter === "Historical"
          ? j.region.includes("Historical")
          : s.includes(selectedFilter)
      );

    return matchesSearch && matchesFilter;
  });

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
              <GraduationCap className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-orbitron font-bold text-primary">
                Journalism Case Studies
              </h1>
              <p className="text-xs text-muted-foreground">Learn from legendary journalists</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-8 rounded-2xl bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border border-primary/20"
        >
          <div className="flex items-start gap-6">
            <div className="p-4 bg-primary/20 rounded-2xl flex-shrink-0">
              <Award className="w-12 h-12 text-primary" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-primary to-primary/50 bg-clip-text text-transparent">
                Learn from Legendary Journalists
              </h2>
              <p className="text-muted-foreground text-lg mb-4">
                Study the work of acclaimed journalists who shaped modern journalism. Each profile includes 
                their major investigations, writing style, ethical approaches, and practical lessons for aspiring journalists.
              </p>
              <div className="flex items-center gap-4 text-sm flex-wrap">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-primary" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">{journalists.length}</strong> Case Studies
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-primary" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">Real</strong> Investigations
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-primary" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">Practical</strong> Lessons
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-yellow-500" />
                  <span className="text-muted-foreground">
                    <strong className="text-foreground">Award</strong> Winners
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                placeholder="Search journalists by name, expertise, or investigation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 bg-card/50 border-border/50"
              />
            </div>
            <Button variant="outline" size="lg" className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </Button>
          </div>

          {/* Filter Pills */}
          <div className="flex gap-2 flex-wrap">
            {filters.map((filter) => (
              <Button
                key={filter}
                variant={selectedFilter === filter ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedFilter(filter)}
                className="rounded-full"
              >
                {filter}
                {selectedFilter === filter && (
                  <span className="ml-2 px-2 py-0.5 bg-primary-foreground/20 rounded-full text-xs">
                    {filteredJournalists.length}
                  </span>
                )}
              </Button>
            ))}
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing <strong>{filteredJournalists.length}</strong> case studies
          </p>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <TrendingUp className="w-4 h-4" />
            <span>Sorted by impact</span>
          </div>
        </div>

        {/* Journalists Grid */}
        {loading ? (
          <div className="col-span-2 text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-lg font-semibold mb-2">Loading journalists...</p>
            <p className="text-sm text-muted-foreground">
              Fetching analyzed journalist profiles from database
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredJournalists.length > 0 ? (
            filteredJournalists.map((journalist, idx) => (
              <motion.div
                key={journalist.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="group p-6 rounded-xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-300 cursor-pointer hover:shadow-lg"
                onClick={() => {
                  setSelectedJournalist(journalist);
                  setShowProfile(true);
                }}
              >
                <div className="flex items-start gap-4">
                  {/* Profile Image */}
                  <div className="relative flex-shrink-0">
                    {journalist.profileImage ? (
                      <div className="w-20 h-20 rounded-xl overflow-hidden border border-primary/30">
                        <img 
                          src={journalist.profileImage} 
                          alt={journalist.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            // Fallback to initials if image fails to load
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement!.innerHTML = `
                              <div class="w-20 h-20 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border border-primary/30">
                                <span class="text-2xl font-bold text-primary">
                                  ${journalist.name.split(' ').map((n: string) => n[0]).join('')}
                                </span>
                              </div>
                            `;
                          }}
                        />
                      </div>
                    ) : (
                      <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border border-primary/30">
                        <span className="text-2xl font-bold text-primary">
                          {journalist.name.split(' ').map((n: string) => n[0]).join('')}
                        </span>
                      </div>
                    )}
                    {journalist.verified && (
                      <div className="absolute -top-1 -right-1 p-1 bg-green-500 rounded-full">
                        <CheckCircle className="w-4 h-4 text-white" />
                      </div>
                    )}
                    {journalist.awards > 5 && (
                      <div className="absolute -bottom-1 -right-1 p-1 bg-yellow-500 rounded-full">
                        <Award className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>

                  {/* Profile Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-bold group-hover:text-primary transition-colors">
                          {journalist.name}
                        </h3>
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-1">{journalist.bio}</p>
                        <p className="text-xs text-primary font-semibold">
                          📌 {journalist.keyInvestigation}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-1 px-2 py-1 bg-primary/10 rounded-lg">
                          <Award className="w-4 h-4 text-primary" />
                          <span className="text-sm font-semibold">{journalist.credibilityScore}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">Impact</span>
                      </div>
                    </div>

                    {/* Specializations */}
                    <div className="flex flex-wrap gap-2 mb-3">
                      {journalist.specializations.slice(0, 3).map((spec) => (
                        <Badge key={spec} variant="secondary" className="text-xs">
                          {spec}
                        </Badge>
                      ))}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap mb-3">
                      <div className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        <span>{journalist.articlesPublished}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        <span>{journalist.region}</span>
                      </div>
                      <div className="flex items-center gap-1 text-yellow-600">
                        <Award className="w-4 h-4" />
                        <span>{journalist.awards} awards</span>
                      </div>
                    </div>

                    {/* Key Lessons */}
                    <div className="p-3 bg-primary/5 rounded-lg border border-primary/10">
                      <div className="flex items-center gap-2 mb-2">
                        <Lightbulb className="w-4 h-4 text-primary" />
                        <span className="text-xs font-semibold text-primary">Key Lessons:</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {journalist.lessons.map((lesson, i) => (
                          <span key={i} className="text-xs text-muted-foreground">
                            {i > 0 && " • "}
                            {lesson}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Educational Value */}
                <div className="mt-4 pt-4 border-t border-border/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <BookOpen className="w-3 h-3 text-primary" />
                        <span>Case study</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Play className="w-3 h-3 text-primary" />
                        <span>Interviews</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <FileText className="w-3 h-3 text-primary" />
                        <span>Analysis</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-primary group-hover:gap-2 transition-all">
                      <span className="text-sm font-medium">Explore</span>
                      <ExternalLink className="w-4 h-4" />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
              <div className="col-span-2 text-center py-12">
                <Users className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-lg font-semibold mb-2">No journalists found</p>
                <p className="text-sm text-muted-foreground">
                  {journalists.length === 0 
                    ? "No journalists have been analyzed yet. Generate a case study first!" 
                    : "Try adjusting your search or filters"}
                </p>
                {journalists.length === 0 && (
                  <Button 
                    className="mt-4" 
                    onClick={() => navigate("/")}
                  >
                    Analyze a Journalist
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Educational Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 p-6 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-primary/20"
        >
          <div className="flex items-start gap-4">
            <GraduationCap className="w-6 h-6 text-primary mt-1" />
            <div>
              <h3 className="font-bold mb-2">How to Use These Case Studies</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">1.</span>
                  <span>Click on any journalist to see their full profile, major investigations, and journalism techniques</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">2.</span>
                  <span>Study their approach to sourcing, verification, and ethical decision-making</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">3.</span>
                  <span>Apply their methods in your own articles and submit for teacher review</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">4.</span>
                  <span>Compare your work against professional standards using our Article Analyzer</span>
                </li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Journalist Profile Modal - Full Case Study */}
      <Dialog open={showProfile} onOpenChange={setShowProfile}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold flex items-center gap-3">
              {selectedJournalist?.profileImage ? (
                <img 
                  src={selectedJournalist.profileImage} 
                  alt={selectedJournalist.name}
                  className="w-20 h-20 rounded-xl object-cover border-2 border-primary shadow-lg"
                  onError={(e) => {
                    console.error("Failed to load image:", selectedJournalist.profileImage);
                    e.currentTarget.style.display = 'none';
                  }}
                />
              ) : (
                <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border-2 border-primary shadow-lg">
                  <span className="text-2xl font-bold text-primary">
                    {selectedJournalist?.name?.split(' ').map((n: string) => n[0]).join('')}
                  </span>
                </div>
              )}
              <div>
                <div>{selectedJournalist?.name}</div>
                {selectedJournalist?.verified && (
                  <Badge variant="secondary" className="mt-1">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Verified Profile
                  </Badge>
                )}
              </div>
            </DialogTitle>
          </DialogHeader>
          
          {selectedJournalist && (
            <div className="space-y-6 mt-4">
              {/* Full Bio */}
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-primary" />
                  Biography
                </h3>
                <p className="text-muted-foreground leading-relaxed">{selectedJournalist.fullBio}</p>
              </div>

              {/* Stats Row - Enhanced */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-primary/5 rounded-lg border border-primary/20">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary">{selectedJournalist.credibilityScore}</div>
                  <div className="text-xs text-muted-foreground">Credibility Score</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary">{selectedJournalist.articlesPublished}</div>
                  <div className="text-xs text-muted-foreground">Articles Analyzed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-600">{selectedJournalist.awards}</div>
                  <div className="text-xs text-muted-foreground">Awards Won</div>
                </div>
                <div className="text-center">
                  <div className="text-sm font-bold text-primary">{selectedJournalist.region}</div>
                  <div className="text-xs text-muted-foreground">Primary Region</div>
                </div>
              </div>

              {/* Verified Links */}
              {selectedJournalist.verifiedLinks && selectedJournalist.verifiedLinks.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {selectedJournalist.verifiedLinks.map((link: any, i: number) => (
                    <a
                      key={i}
                      href={typeof link === 'string' ? link : link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                    >
                      <ExternalLink className="w-3 h-3" />
                      {typeof link === 'string' ? 'Profile Link' : link.name || 'View Profile'}
                    </a>
                  ))}
                </div>
              )}

              {/* Specializations */}
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <Target className="w-5 h-5 text-primary" />
                  Areas of Expertise
                </h3>
                <div className="flex flex-wrap gap-2">
                  {selectedJournalist.specializations.map((spec: string) => (
                    <Badge key={spec} variant="secondary" className="px-3 py-1">
                      {spec}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Notable Works */}
              {selectedJournalist.notableWorks && selectedJournalist.notableWorks.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <Award className="w-5 h-5 text-primary" />
                    Notable Works & Investigations
                  </h3>
                  <div className="space-y-3">
                    {selectedJournalist.notableWorks.map((work: any, i: number) => (
                      <div key={i} className="p-4 bg-card border border-border rounded-lg">
                        <h4 className="font-semibold text-primary mb-1">
                          {typeof work === 'string' ? work : work.title || work.name}
                        </h4>
                        {work.description && (
                          <p className="text-sm text-muted-foreground">{work.description}</p>
                        )}
                        {work.impact && (
                          <p className="text-xs text-muted-foreground mt-2">
                            <strong>Impact:</strong> {work.impact}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Career Highlights */}
              {selectedJournalist.careerHighlights && selectedJournalist.careerHighlights.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    Career Highlights
                  </h3>
                  <ul className="space-y-2">
                    {selectedJournalist.careerHighlights.map((highlight: string, i: number) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-muted-foreground">{highlight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Awards */}
              {selectedJournalist.awardsList && selectedJournalist.awardsList.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Award className="w-5 h-5 text-yellow-600" />
                    Awards & Recognition
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {selectedJournalist.awardsList.map((award: any, i: number) => (
                      <div key={i} className="p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg">
                        <div className="flex items-center gap-2">
                          <Award className="w-4 h-4 text-yellow-600" />
                          <span className="text-sm font-medium">
                            {typeof award === 'string' ? award : award.name || award.title}
                          </span>
                        </div>
                        {award.year && (
                          <span className="text-xs text-muted-foreground ml-6">{award.year}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Writing Style */}
              {selectedJournalist.writingStyle && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    Writing Style & Approach
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.writingStyle === 'string' 
                      ? selectedJournalist.writingStyle 
                      : JSON.stringify(selectedJournalist.writingStyle)}
                  </p>
                </div>
              )}

              {/* Ethical Approach */}
              {selectedJournalist.ethicalApproach && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-primary" />
                    Ethical Framework
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.ethicalApproach === 'string' 
                      ? selectedJournalist.ethicalApproach 
                      : JSON.stringify(selectedJournalist.ethicalApproach)}
                  </p>
                </div>
              )}

              {/* Sourcing Methods */}
              {selectedJournalist.sourcingMethods && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Search className="w-5 h-5 text-primary" />
                    Sourcing & Verification Methods
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.sourcingMethods === 'string' 
                      ? selectedJournalist.sourcingMethods 
                      : JSON.stringify(selectedJournalist.sourcingMethods)}
                  </p>
                </div>
              )}

              {/* Impact */}
              {selectedJournalist.impact && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    Impact & Influence
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.impact === 'string' 
                      ? selectedJournalist.impact 
                      : JSON.stringify(selectedJournalist.impact)}
                  </p>
                </div>
              )}

              {/* Challenges */}
              {selectedJournalist.challenges && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary" />
                    Challenges Overcome
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.challenges === 'string' 
                      ? selectedJournalist.challenges 
                      : Array.isArray(selectedJournalist.challenges) 
                        ? selectedJournalist.challenges.join(', ')
                        : JSON.stringify(selectedJournalist.challenges)}
                  </p>
                </div>
              )}


              {/* Ideological Bias/Perspective */}
              {selectedJournalist.ideology && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Filter className="w-5 h-5 text-primary" />
                    Ideological Perspective
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.ideology === 'string' 
                      ? selectedJournalist.ideology 
                      : JSON.stringify(selectedJournalist.ideology)}
                  </p>
                </div>
              )}

              {/* Political Affiliation */}
              {selectedJournalist.politicalAffiliation && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Users className="w-5 h-5 text-primary" />
                    Political Affiliation
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {typeof selectedJournalist.politicalAffiliation === 'string' 
                      ? selectedJournalist.politicalAffiliation 
                      : JSON.stringify(selectedJournalist.politicalAffiliation)}
                  </p>
                </div>
              )}

              {/* Media Affiliations */}
              {selectedJournalist.mediaAffiliations && selectedJournalist.mediaAffiliations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <ExternalLink className="w-5 h-5 text-primary" />
                    Media Organizations
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedJournalist.mediaAffiliations.map((media: string, i: number) => (
                      <Badge key={i} variant="outline" className="px-3 py-1">
                        {media}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Digital Presence & Reach */}
              {(selectedJournalist.onlineReach || selectedJournalist.influenceLevel) && (
                <div className="p-4 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-lg border border-primary/10">
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    Digital Presence & Influence
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedJournalist.onlineReach && (
                      <div>
                        <span className="text-sm text-muted-foreground">Online Reach</span>
                        <p className="text-lg font-semibold text-primary">{selectedJournalist.onlineReach}</p>
                      </div>
                    )}
                    {selectedJournalist.influenceLevel && (
                      <div>
                        <span className="text-sm text-muted-foreground">Influence Level</span>
                        <p className="text-lg font-semibold text-primary">{selectedJournalist.influenceLevel}</p>
                      </div>
                    )}
                    {selectedJournalist.audienceSentiment && (
                      <div>
                        <span className="text-sm text-muted-foreground">Audience Sentiment</span>
                        <p className="text-lg font-semibold text-primary">{selectedJournalist.audienceSentiment}</p>
                      </div>
                    )}
                    {selectedJournalist.controversyLevel && (
                      <div>
                        <span className="text-sm text-muted-foreground">Controversy Level</span>
                        <p className="text-lg font-semibold text-orange-600">{selectedJournalist.controversyLevel}</p>
                      </div>
                    )}
                    {selectedJournalist.trustworthiness && (
                      <div>
                        <span className="text-sm text-muted-foreground">Trustworthiness</span>
                        <p className="text-lg font-semibold text-primary">{selectedJournalist.trustworthiness}</p>
                      </div>
                    )}
                    {selectedJournalist.verificationRate && (
                      <div>
                        <span className="text-sm text-muted-foreground">Verification Rate</span>
                        <p className="text-lg font-semibold text-green-600">{selectedJournalist.verificationRate}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tone Analysis */}
              {selectedJournalist.toneAnalysis && Object.keys(selectedJournalist.toneAnalysis).some(k => selectedJournalist.toneAnalysis[k]) && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    Content Analysis
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {selectedJournalist.toneAnalysis.emotionalTone && (
                      <div className="p-3 bg-card border border-border rounded-lg">
                        <span className="text-xs text-muted-foreground">Emotional Tone</span>
                        <p className="text-sm font-medium">{selectedJournalist.toneAnalysis.emotionalTone}</p>
                      </div>
                    )}
                    {selectedJournalist.toneAnalysis.bias && (
                      <div className="p-3 bg-card border border-border rounded-lg">
                        <span className="text-xs text-muted-foreground">Bias</span>
                        <p className="text-sm font-medium">{selectedJournalist.toneAnalysis.bias}</p>
                      </div>
                    )}
                    {selectedJournalist.toneAnalysis.objectivity && (
                      <div className="p-3 bg-card border border-border rounded-lg">
                        <span className="text-xs text-muted-foreground">Objectivity</span>
                        <p className="text-sm font-medium">{selectedJournalist.toneAnalysis.objectivity}</p>
                      </div>
                    )}
                    {selectedJournalist.toneAnalysis.consistency && (
                      <div className="p-3 bg-card border border-border rounded-lg">
                        <span className="text-xs text-muted-foreground">Consistency</span>
                        <p className="text-sm font-medium">{selectedJournalist.toneAnalysis.consistency}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recommendation Score */}
              {selectedJournalist.recommendationScore !== null && (
                <div className={`p-4 rounded-lg border ${
                  selectedJournalist.recommendationScore >= 7 
                    ? 'bg-green-500/5 border-green-500/20' 
                    : selectedJournalist.recommendationScore >= 4 
                      ? 'bg-yellow-500/5 border-yellow-500/20'
                      : 'bg-red-500/5 border-red-500/20'
                }`}>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Award className="w-5 h-5 text-primary" />
                    Educational Recommendation Score: {selectedJournalist.recommendationScore}/10
                  </h3>
                  {selectedJournalist.recommendationReasoning && (
                    <p className="text-sm text-muted-foreground mb-3">{selectedJournalist.recommendationReasoning}</p>
                  )}
                  
                  {/* Strengths */}
                  {selectedJournalist.strengths && selectedJournalist.strengths.length > 0 && (
                    <div className="mb-3">
                      <h4 className="text-sm font-semibold text-green-600 mb-2">✓ Strengths:</h4>
                      <ul className="space-y-1">
                        {selectedJournalist.strengths.map((strength: string, i: number) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Concerns */}
                  {selectedJournalist.concerns && selectedJournalist.concerns.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-orange-600 mb-2">⚠ Concerns:</h4>
                      <ul className="space-y-1">
                        {selectedJournalist.concerns.map((concern: string, i: number) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                            <span className="text-orange-600 mt-0.5 flex-shrink-0">•</span>
                            {concern}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Top Domains / Sources */}
              {selectedJournalist.topDomains && selectedJournalist.topDomains.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <ExternalLink className="w-5 h-5 text-primary" />
                    Primary Publication Sources
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedJournalist.topDomains.map((domain: string, i: number) => (
                      <Badge key={i} variant="secondary" className="px-3 py-1">
                        {domain}
                      </Badge>
                    ))}
                  </div>
                  {selectedJournalist.dateRange && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Analysis period: {selectedJournalist.dateRange}
                    </p>
                  )}
                </div>
              )}

              {/* Key Lessons for Students */}
              <div className="bg-gradient-to-r from-primary/10 to-primary/5 p-4 rounded-lg border border-primary/20">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-primary" />
                  Key Lessons for Aspiring Journalists
                </h3>
                <ul className="space-y-2">
                  {selectedJournalist.lessons.map((lesson: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">{lesson}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Analysis Metadata */}
              {selectedJournalist.analyzedAt && (
                <div className="text-xs text-muted-foreground text-center p-3 bg-muted/20 rounded-lg">
                  <p>
                    <strong>Profile analyzed:</strong> {new Date(selectedJournalist.analyzedAt).toLocaleDateString()} • 
                    <strong> Articles analyzed:</strong> {selectedJournalist.articlesPublished}
                  </p>
                  <p className="mt-1">
                    This case study was generated using AI analysis of the journalist's published work, 
                    public statements, and professional history for educational purposes.
                  </p>
                </div>
              )}

              {/* Call to Action */}
              <div className="p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-primary/20">
                <p className="text-sm text-muted-foreground mb-3">
                  <strong className="text-foreground">Apply these principles</strong> in your own investigative work. 
                  Study this journalist's methodology, ethical framework, and storytelling techniques to develop your skills.
                </p>
                <div className="flex gap-2">
                  <Button 
                    className="flex-1" 
                    onClick={() => {
                      setShowProfile(false);
                      navigate('/dashboard');
                    }}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Investigating
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => {
                      setShowProfile(false);
                      navigate('/article-analyzer');
                    }}
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Analyze Article
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default JournalistsGallery;
