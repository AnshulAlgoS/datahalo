import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { 
  Users, 
  ArrowLeft, 
  Search, 
  TrendingUp, 
  Calendar,
  FileText,
  Award,
  Filter,
  Loader2,
  AlertCircle,
  Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const API_URL = import.meta.env.VITE_API_URL || "https://datahalo.onrender.com" || "http://localhost:8000";

interface JournalistData {
  _id: string;
  name: string;
  analysis_timestamp: string;
  articlesAnalyzed: number;
  aiProfile: {
    haloScore?: {
      score: number;
      level: string;
      description: string;
    };
    digitalPresence?: {
      profileImage?: string;
    };
    mainTopics?: string[];
    ideologicalBias?: string;
  };
}

const JournalistsGallery = () => {
  const navigate = useNavigate();
  const [journalists, setJournalists] = useState<JournalistData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterLevel, setFilterLevel] = useState<string>("all");
  const [fetchingProfile, setFetchingProfile] = useState(false);

  useEffect(() => {
    fetchJournalists();
  }, []);

  const fetchJournalists = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/journalists?limit=50`);
      const data = await response.json();
      
      if (data.status === "success") {
        setJournalists(data.journalists);
      } else {
        setError("Failed to load journalists");
      }
    } catch (err) {
      setError("Failed to connect to server");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredJournalists = journalists.filter((j) => {
    const matchesSearch = j.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterLevel === "all" || j.aiProfile?.haloScore?.level === filterLevel;
    return matchesSearch && matchesFilter;
  });

  const handleViewProfile = async (journalistName: string) => {
    try {
      setFetchingProfile(true);
      
      // Fetch full journalist data from API
      const response = await fetch(`${API_URL}/journalist/${encodeURIComponent(journalistName)}`);
      const data = await response.json();
      
      if (data.status === "success" && data.journalist) {
        // Store the full data in sessionStorage for the profile page
        const profileData = {
          status: "success",
          journalist: data.journalist.name,
          articlesAnalyzed: data.journalist.articlesAnalyzed,
          aiProfile: data.journalist.aiProfile
        };
        
        sessionStorage.setItem(`journalist_${journalistName}`, JSON.stringify(profileData));
        
        // Navigate to profile page
        navigate(`/profile/${encodeURIComponent(journalistName)}`);
      } else {
        setError("Failed to fetch journalist data");
      }
    } catch (err) {
      console.error("Error fetching journalist profile:", err);
      setError("Failed to load profile. Please try again.");
    } finally {
      setFetchingProfile(false);
    }
  };

  const getHaloScoreColor = (score?: number) => {
    if (!score) return "text-muted-foreground";
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-blue-500";
    if (score >= 40) return "text-yellow-500";
    return "text-orange-500";
  };

  const getHaloScoreGlow = (score?: number) => {
    if (!score) return "";
    if (score >= 80) return "shadow-[0_0_20px_rgba(34,197,94,0.4)]";
    if (score >= 60) return "shadow-[0_0_20px_rgba(59,130,246,0.4)]";
    if (score >= 40) return "shadow-[0_0_20px_rgba(234,179,8,0.4)]";
    return "shadow-[0_0_20px_rgba(249,115,22,0.4)]";
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", { 
        month: "short", 
        day: "numeric", 
        year: "numeric" 
      });
    } catch {
      return "Unknown";
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Loading Overlay */}
      {fetchingProfile && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-foreground font-semibold">Loading profile...</p>
          </div>
        </div>
      )}
      
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
            <div className="flex items-center justify-between mb-6">
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
                    <Users className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h1 className="font-orbitron text-2xl md:text-3xl font-bold">
                      Journalists <span className="text-primary">Gallery</span>
                    </h1>
                    <p className="text-sm text-muted-foreground">
                      {journalists.length} analyzed profiles
                    </p>
                  </div>
                </div>
              </div>

              <Button
                onClick={fetchJournalists}
                disabled={loading}
                className="px-4 py-2 bg-primary/10 hover:bg-primary/20 border border-primary/30 rounded-xl transition-all"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                <span className="ml-2">Refresh</span>
              </Button>
            </div>

            {/* Search and Filter */}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  placeholder="Search journalists..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50"
                />
              </div>

              <div className="flex gap-2">
                <Button
                  variant={filterLevel === "all" ? "default" : "outline"}
                  onClick={() => setFilterLevel("all")}
                  className="px-4"
                >
                  All
                </Button>
                <Button
                  variant={filterLevel === "Elite" ? "default" : "outline"}
                  onClick={() => setFilterLevel("Elite")}
                  className="px-4"
                >
                  Elite
                </Button>
                <Button
                  variant={filterLevel === "Established" ? "default" : "outline"}
                  onClick={() => setFilterLevel("Established")}
                  className="px-4"
                >
                  Established
                </Button>
                <Button
                  variant={filterLevel === "Emerging" ? "default" : "outline"}
                  onClick={() => setFilterLevel("Emerging")}
                  className="px-4"
                >
                  Emerging
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
              <p className="text-muted-foreground">Loading journalists...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-xl mb-4">
                <AlertCircle className="w-12 h-12 text-destructive" />
              </div>
              <p className="text-destructive mb-4">{error}</p>
              <Button onClick={fetchJournalists}>Try Again</Button>
            </div>
          ) : filteredJournalists.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Users className="w-16 h-16 text-muted-foreground/50 mb-4" />
              <p className="text-muted-foreground">No journalists found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredJournalists.map((journalist, index) => (
                <motion.div
                  key={journalist._id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.05 }}
                  onClick={() => handleViewProfile(journalist.name)}
                  className="group relative cursor-pointer"
                >
                  <div className={`relative p-6 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-500 h-full ${journalist.aiProfile?.haloScore?.score ? getHaloScoreGlow(journalist.aiProfile.haloScore.score) : ""}`}>
                    {/* Glow effect */}
                    <div
                      className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{
                        boxShadow: "0 0 40px hsl(var(--primary) / 0.3)",
                      }}
                    />

                    {/* Profile Image or Initials */}
                    <div className="relative mb-4 flex justify-center">
                      {journalist.aiProfile?.digitalPresence?.profileImage ? (
                        <img
                          src={journalist.aiProfile.digitalPresence.profileImage}
                          alt={journalist.name}
                          className="w-20 h-20 rounded-full object-cover border-2 border-primary/30"
                        />
                      ) : (
                        <div className="w-20 h-20 rounded-full bg-primary/20 border-2 border-primary/30 flex items-center justify-center">
                          <span className="text-2xl font-bold text-primary">
                            {journalist.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
                          </span>
                        </div>
                      )}
                      
                      {/* Halo Score Badge */}
                      {journalist.aiProfile?.haloScore?.score && (
                        <div className={`absolute -top-2 -right-2 px-3 py-1 rounded-full bg-card border-2 border-primary/50 ${getHaloScoreColor(journalist.aiProfile.haloScore.score)} font-bold text-sm`}>
                          {journalist.aiProfile.haloScore.score}
                        </div>
                      )}
                    </div>

                    {/* Name */}
                    <h3 className="text-xl font-bold text-center mb-2 text-foreground group-hover:text-primary transition-colors">
                      {journalist.name}
                    </h3>

                    {/* Halo Level */}
                    {journalist.aiProfile?.haloScore?.level && (
                      <div className="flex justify-center mb-3">
                        <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/30">
                          <span className="text-xs font-semibold text-primary">
                            {journalist.aiProfile.haloScore.level}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Stats */}
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <FileText className="w-4 h-4 text-primary" />
                        <span>{journalist.articlesAnalyzed} articles analyzed</span>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="w-4 h-4 text-primary" />
                        <span>Analyzed {formatDate(journalist.analysis_timestamp)}</span>
                      </div>

                      {journalist.aiProfile?.ideologicalBias && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <TrendingUp className="w-4 h-4 text-primary" />
                          <span className="truncate">{journalist.aiProfile.ideologicalBias}</span>
                        </div>
                      )}
                    </div>

                    {/* Topics */}
                    {journalist.aiProfile?.mainTopics && journalist.aiProfile.mainTopics.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {journalist.aiProfile.mainTopics.slice(0, 3).map((topic, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 text-xs rounded-lg bg-muted/50 text-muted-foreground border border-border/50"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Hover indicator */}
                    <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="text-primary text-sm font-semibold">
                        View Profile →
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JournalistsGallery;