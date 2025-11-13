import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { buildApiUrl, API_ENDPOINTS } from "../config/api";
import { 
  Globe, 
  Cpu, 
  Building2, 
  Trophy, 
  Microscope, 
  Clapperboard, 
  Heart,
  Users,
  TrendingUp,
  GraduationCap,
  Target,
  Zap,
  ClipboardList,
  RefreshCw,
  Newspaper,
  Brain,
  Sparkles,
  ExternalLink,
  Calendar,
  Tag,
  AlertCircle,
  Loader2
} from "lucide-react";

interface Article {
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: string;
  image?: string;
  category?: string;
}

const News = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState("general");
  const [aiLoading, setAiLoading] = useState(false);
  const [perspective, setPerspective] = useState("general public");
  const [smartFeed, setSmartFeed] = useState("");
  const [error, setError] = useState("");

  const categories = [
    { value: "general", label: "General", icon: Globe },
    { value: "technology", label: "Technology", icon: Cpu },
    { value: "business", label: "Business", icon: Building2 },
    { value: "sports", label: "Sports", icon: Trophy },
    { value: "science", label: "Science", icon: Microscope },
    { value: "entertainment", label: "Entertainment", icon: Clapperboard },
    { value: "health", label: "Health", icon: Heart }
  ];

  const perspectives = [
    { value: "general public", label: "General Public", icon: Users },
    { value: "finance analyst", label: "Finance Analyst", icon: TrendingUp },
    { value: "government exam aspirant", label: "Govt. Exam Aspirant", icon: GraduationCap },
    { value: "tech student", label: "Tech Student", icon: Cpu },
    { value: "business student", label: "Business Student", icon: ClipboardList }
  ];

  const fetchNews = async () => {
    setLoading(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.NEWS);
      const res = await fetch(`${apiUrl}?category=${category}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'omit',
        mode: 'cors'
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      setArticles(data.articles || []);
    } catch (error: any) {
      console.error("Error fetching news:", error);
      setError(error.message || "Failed to fetch news");
    } finally {
      setLoading(false);
    }
  };

  const refreshNews = async () => {
    setLoading(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.REFRESH_NEWS);
      const res = await fetch(`${apiUrl}?category=${category}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'omit',
        mode: 'cors'
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      await res.json(); // Consume response
      await fetchNews(); // Re-fetch articles
    } catch (error: any) {
      console.error("Error refreshing news:", error);
      setError(error.message || "Failed to refresh news");
    } finally {
      setLoading(false);
    }
  };

  const generateSmartFeed = async () => {
    setAiLoading(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.SMART_FEED);
      const res = await fetch(`${apiUrl}?pov=${encodeURIComponent(perspective)}`, {
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'omit',
        mode: 'cors'
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      setSmartFeed(data.summary || "No smart feed available.");
    } catch (error: any) {
      console.error("Error fetching smart feed:", error);
      setError(error.message || "Failed to generate smart feed");
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [category]);

  const selectedCategory = categories.find(cat => cat.value === category);
  const selectedPerspective = perspectives.find(persp => persp.value === perspective);
  const CategoryIcon = selectedCategory?.icon || Globe;
  const PerspectiveIcon = selectedPerspective?.icon || Users;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-card/30 to-background" />
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-[100px] animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-[100px] animate-pulse delay-1000" />
      
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-primary/10 rounded-2xl border border-primary/20">
              <Newspaper className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-primary via-primary/80 to-secondary bg-clip-text text-transparent">
              News Intelligence
            </h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            AI-powered news analysis and insights tailored to your perspective
          </p>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-destructive/10 border border-destructive/20 rounded-2xl p-4 mb-8 max-w-2xl mx-auto"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-destructive shrink-0" />
              <p className="text-destructive font-medium">{error}</p>
            </div>
          </motion.div>
        )}

        {/* Controls Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card/50 backdrop-blur-md border border-border/50 rounded-3xl p-8 mb-12 shadow-[0_8px_30px_rgb(0,0,0,0.04)]"
        >
          <div className="flex flex-wrap gap-8 justify-center items-center">
            {/* Category Selector */}
            <div className="flex flex-col items-center gap-3">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <Tag className="w-4 h-4" />
                Category
              </div>
              <div className="relative">
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="appearance-none bg-background border border-border/50 rounded-xl px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-foreground font-medium min-w-[160px] transition-all duration-200"
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
                <CategoryIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
              </div>
            </div>

            {/* Refresh Button */}
            <Button
              onClick={refreshNews}
              disabled={loading}
              size="lg"
              className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-[0_0_20px_rgb(var(--primary)/0.3)] transition-all duration-300 hover:shadow-[0_0_30px_rgb(var(--primary)/0.4)] hover:scale-105 disabled:hover:scale-100"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh News
                </>
              )}
            </Button>
          </div>
        </motion.div>

        {/* News Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mb-16"
        >
          <div className="flex items-center justify-center gap-3 mb-8">
            <CategoryIcon className="w-6 h-6 text-primary" />
            <h2 className="text-3xl font-bold text-center">
              Latest {selectedCategory?.label} News
            </h2>
            <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium">
              {articles.length} articles
            </div>
          </div>

          {articles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.slice(0, 24).map((article, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="group"
                >
                  <Card className="h-full bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] hover:scale-[1.02]">
                    {article.image && (
                      <div className="relative overflow-hidden rounded-t-lg">
                        <img
                          src={article.image}
                          alt={article.title}
                          className="w-full h-48 object-cover transition-transform duration-500 group-hover:scale-110"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                          }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                      </div>
                    )}
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg font-semibold text-foreground line-clamp-2 group-hover:text-primary transition-colors leading-snug">
                        {article.title}
                      </CardTitle>
                      <CardDescription className="text-muted-foreground text-sm line-clamp-3 leading-relaxed">
                        {article.description || "No description available."}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                        <div className="flex items-center gap-1 bg-secondary/10 px-2 py-1 rounded-full">
                          <Tag className="w-3 h-3" />
                          <span className="font-medium">{article.source}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-primary hover:text-primary/80 font-medium text-sm transition-colors group/link"
                      >
                        Read Full Article
                        <ExternalLink className="w-3 h-3 transition-transform group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5" />
                      </a>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-4">
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
              <span className="text-xl text-muted-foreground">Loading latest articles...</span>
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="bg-muted/50 rounded-2xl p-8 max-w-md mx-auto">
                <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-xl text-muted-foreground mb-4">No articles found</p>
                <Button onClick={fetchNews} variant="outline">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </Button>
              </div>
            </div>
          )}
        </motion.div>

        {/* AI Smart Feed Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-8"
        >
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-3 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl border border-primary/20">
                <Brain className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                AI Smart Analysis
              </h2>
            </div>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Get personalized insights and analysis powered by advanced AI technology
            </p>
          </div>

          <div className="bg-card/50 backdrop-blur-md border border-border/50 rounded-3xl p-8 mb-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
            <div className="flex flex-wrap gap-8 justify-center items-center">
              {/* Perspective Selector */}
              <div className="flex flex-col items-center gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <Target className="w-4 h-4" />
                  Your Perspective
                </div>
                <div className="relative">
                  <select
                    value={perspective}
                    onChange={(e) => setPerspective(e.target.value)}
                    className="appearance-none bg-background border border-border/50 rounded-xl px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-foreground font-medium min-w-[200px] transition-all duration-200"
                  >
                    {perspectives.map(persp => (
                      <option key={persp.value} value={persp.value}>
                        {persp.label}
                      </option>
                    ))}
                  </select>
                  <PerspectiveIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                </div>
              </div>

              {/* Generate Button */}
              <Button
                onClick={generateSmartFeed}
                disabled={aiLoading || articles.length === 0}
                size="lg"
                className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-primary-foreground rounded-xl shadow-[0_0_20px_rgb(var(--primary)/0.3)] transition-all duration-300 hover:shadow-[0_0_35px_rgb(var(--primary)/0.4)] hover:scale-105 disabled:hover:scale-100"
              >
                {aiLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate Smart Analysis
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Smart Feed Display */}
          {smartFeed && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-md border border-primary/20 shadow-[0_0_40px_rgb(var(--primary)/0.1)]">
                <CardHeader className="pb-4">
                  <CardTitle className="text-2xl font-bold flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-xl">
                      <Brain className="w-6 h-6 text-primary" />
                    </div>
                    Smart Analysis
                    <div className="ml-auto flex items-center gap-2 text-sm bg-primary/10 text-primary px-3 py-1 rounded-full">
                      <PerspectiveIcon className="w-3 h-3" />
                      {selectedPerspective?.label}
                    </div>
                  </CardTitle>
                  <CardDescription>
                    AI-powered insights tailored to your perspective
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-neutral dark:prose-invert max-w-none">
                    <div className="text-foreground/90 whitespace-pre-line leading-relaxed text-base">
                      {smartFeed}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* CTA when no smart feed */}
          {!smartFeed && !aiLoading && articles.length > 0 && (
            <div className="text-center py-8">
              <div className="bg-muted/30 rounded-2xl p-6 max-w-2xl mx-auto">
                <Zap className="w-8 h-8 text-primary mx-auto mb-4" />
                <p className="text-lg text-muted-foreground mb-4">
                  Ready for personalized insights? Select your perspective and generate your smart analysis!
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default News;