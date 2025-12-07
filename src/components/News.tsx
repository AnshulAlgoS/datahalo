import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { buildApiUrl, API_ENDPOINTS } from "../config/api";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
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
  Loader2,
  Copy,
  Download,
  X
} from "lucide-react";
import html2canvas from "html2canvas";

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
  const [selectedPerspective, setSelectedPerspective] = useState("general public");
  const [analyzingNews, setAnalyzingNews] = useState(false);
  const [savedArticles, setSavedArticles] = useState<Article[]>([]);
  const [smartAnalysis, setSmartAnalysis] = useState("");
  const [analysisCount, setAnalysisCount] = useState<number | null>(null);
  const [selectedState, setSelectedState] = useState("");
  const [district, setDistrict] = useState("");
  const [judgePov, setJudgePov] = useState("women commission");
  const analysisRef = useRef<HTMLDivElement | null>(null);

  const categories = [
    { value: "general", label: "General", icon: Globe },
    { value: "technology", label: "Technology", icon: Cpu },
    { value: "business", label: "Business", icon: Building2 },
    { value: "sports", label: "Sports", icon: Trophy },
    { value: "science", label: "Science", icon: Microscope },
    { value: "entertainment", label: "Entertainment", icon: Clapperboard },
    { value: "health", label: "Health", icon: Heart }
  ];

  const judgePerspectives = [
    { value: "women commission", label: "Women Commission" },
    { value: "economist", label: "Economist" },
    { value: "ias officer", label: "IAS Officer" },
    { value: "assistant commissioner of police", label: "ACP" },
    { value: "social worker", label: "Social Worker" },
    { value: "block president", label: "Block President" }
  ];

  const indianStates = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi","Jammu and Kashmir","Ladakh","Puducherry","Chandigarh","Andaman and Nicobar Islands","Dadra and Nagar Haveli and Daman and Diu","Lakshadweep"
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
      setSavedArticles(data.articles || []);
    } catch (err: unknown) {
      const msg = getErrorMessage(err) || "Failed to fetch news";
      console.error("Error fetching news:", err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const refreshNews = async () => {
    setLoading(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.REFRESH_NEWS);
      const res = await fetch(`${apiUrl}?category=${category}&country=in`, {
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
      
      await res.json();
      await fetchNews();
    } catch (err: unknown) {
      const msg = getErrorMessage(err) || "Failed to refresh news";
      console.error("Error refreshing news:", err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const generateSmartFeed = async () => {
    setAiLoading(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.SMART_FEED);
      const res = await fetch(`${apiUrl}?pov=${encodeURIComponent(perspective)}&days=7`, {
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
    } catch (err: unknown) {
      const msg = getErrorMessage(err) || "Failed to generate smart feed";
      console.error("Error fetching smart feed:", err);
      setError(msg);
    } finally {
      setAiLoading(false);
    }
  };

  const handleGenerateAnalysis = async () => {
    setAnalyzingNews(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.SMART_FEED);
      const res = await fetch(`${apiUrl}?pov=${encodeURIComponent(perspective)}&days=7`, {
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
      setSmartAnalysis(data.summary || "No analysis available.");
      setSmartFeed(data.summary || "No smart feed available.");
      setAnalysisCount(typeof data.articlesAnalyzed === "number" ? data.articlesAnalyzed : null);
    } catch (err: unknown) {
      const msg = getErrorMessage(err) || "Failed to generate analysis";
      console.error("Error generating analysis:", err);
      setError(msg);
      setSmartAnalysis("");
    } finally {
      setAnalyzingNews(false);
    }
  };

  const triggerAnalysis = async (
    pov: string,
    opts?: { state?: string; district?: string; days?: number }
  ) => {
    setAnalyzingNews(true);
    setError("");
    try {
      const apiUrl = buildApiUrl(API_ENDPOINTS.SMART_FEED);
      const params = new URLSearchParams();
      params.set("pov", pov);
      params.set("days", String(opts?.days ?? 7));
      if (opts?.state) params.set("state", opts.state);
      if (opts?.district) params.set("district", opts.district);
      const res = await fetch(`${apiUrl}?${params.toString()}`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        credentials: "omit",
        mode: "cors",
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      const data = await res.json();
      setSmartAnalysis(data.summary || "");
      setSmartFeed(data.summary || "");
      setAnalysisCount(
        typeof data.articlesAnalyzed === "number" ? data.articlesAnalyzed : null
      );
      setPerspective(pov);
    } catch (err: unknown) {
      const msg = getErrorMessage(err) || "Failed to generate analysis";
      console.error("Error generating analysis:", err);
      setError(msg);
      setSmartAnalysis("");
    } finally {
      setAnalyzingNews(false);
    }
  };

  const exportAnalysisPdf = async () => {
    if (!analysisRef.current) return;
    const canvas = await html2canvas(analysisRef.current, { scale: 2, useCORS: true, backgroundColor: "#0b0b0f" });
    const dataUrl = canvas.toDataURL("image/png");
    const w = window.open("", "_blank", "noopener,noreferrer");
    if (!w) return;
    w.document.write(`<!doctype html><html><head><title>Analysis</title><style>body{margin:0;padding:0;background:#0b0b0f}</style></head><body><img src="${dataUrl}" style="width:100%"/></body></html>`);
    w.document.close();
    w.focus();
    w.print();
  };

  useEffect(() => {
    fetchNews();
  }, [category]);

  const selectedCategory = categories.find(cat => cat.value === category);
  const CategoryIcon = selectedCategory?.icon || Globe;

  return (
    <section id="news" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background effects matching HowItWorks */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background" />
      
      <div className="relative z-10 max-w-7xl mx-auto w-full">
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="relative inline-flex p-4 rounded-xl bg-primary/10 border border-primary/30">
              <Newspaper className="w-8 h-8 text-primary" />
            </div>
          </div>
          <h2 className="font-orbitron text-4xl md:text-6xl font-bold mb-6">
            News <span className="text-primary">Intelligence</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            AI-powered news analysis and insights tailored to your perspective
          </p>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative p-6 rounded-2xl bg-destructive/10 backdrop-blur-md border border-destructive/30 mb-8 max-w-2xl mx-auto"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-destructive shrink-0" />
              <p className="text-destructive font-medium">{error}</p>
            </div>
          </motion.div>
        )}

        {/* Controls Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="relative mb-16"
        >
          <div className="relative p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-500">
            {/* Glow effect */}
            <div
              className="absolute inset-0 rounded-2xl opacity-0 hover:opacity-100 transition-opacity duration-500"
              style={{
                boxShadow: "0 0 40px hsl(var(--primary) / 0.3)",
              }}
            />
            
            <div className="relative flex flex-wrap gap-8 justify-center items-center">
              {/* Category Selector */}
              <div className="flex flex-col items-center gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <Tag className="w-4 h-4" />
                  <span>Category</span>
                </div>
                <div className="relative">
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="appearance-none bg-background/50 backdrop-blur-sm border border-border/50 rounded-xl px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-foreground font-medium min-w-[180px] transition-all duration-200"
                  >
                    {categories.map(cat => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                  <CategoryIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-primary pointer-events-none" />
                </div>
              </div>

              {/* Refresh Button */}
              <Button
                onClick={refreshNews}
                disabled={loading}
                size="lg"
                className="relative group bg-primary/10 hover:bg-primary text-primary hover:text-primary-foreground border border-primary/30 rounded-xl transition-all duration-300 hover:shadow-[0_0_20px_hsl(var(--primary)/0.5)]"
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
          </div>
        </motion.div>

        {/* News Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <div className="flex items-center justify-center gap-3 mb-8">
            <CategoryIcon className="w-6 h-6 text-primary" />
            <h3 className="text-2xl md:text-3xl font-bold">
              Latest {selectedCategory?.label} News
            </h3>
            <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium border border-primary/30">
              {articles.length}
            </div>
          </div>

          {articles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.slice(0, 9).map((article, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.05 }}
                  viewport={{ once: true }}
                  className="group"
                >
                  <div className="relative h-full p-6 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-500">
                    {/* Glow effect */}
                    <div
                      className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{
                        boxShadow: "0 0 30px hsl(var(--primary) / 0.2)",
                      }}
                    />
                    
                    {article.image && (
                      <div className="relative overflow-hidden rounded-xl mb-4">
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
                    
                    <div className="relative">
                      <h4 className="text-lg font-bold text-foreground line-clamp-2 mb-3 group-hover:text-primary transition-colors leading-snug">
                        {article.title}
                      </h4>
                      <p className="text-muted-foreground text-sm line-clamp-3 mb-4 leading-relaxed">
                        {article.description || "No description available."}
                      </p>
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                        <div className="flex items-center gap-1 bg-primary/10 px-2 py-1 rounded-full border border-primary/20">
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
                        Read Article
                        <ExternalLink className="w-3 h-3 transition-transform group-hover/link:translate-x-1" />
                      </a>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : loading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
              <span className="text-xl text-muted-foreground">Loading latest articles...</span>
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="relative p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 max-w-md mx-auto">
                <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-xl text-muted-foreground mb-4">No articles found</p>
                <Button onClick={fetchNews} variant="outline" className="border-primary/30 hover:bg-primary/10">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </Button>
              </div>
            </div>
          )}
        </motion.div>

        {/* Smart Analysis Section - Enhanced */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <div className="p-6 rounded-2xl bg-gradient-to-br from-primary/10 via-accent/5 to-primary/5 border border-primary/30 backdrop-blur-md">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 rounded-xl bg-primary/20 border border-primary/40">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2 text-foreground">
                  AI-Powered Smart Analysis
                </h3>
                <p className="text-sm text-muted-foreground">
                  Get comprehensive news summaries tailored to your perspective. Our AI analyzes current news
                  and provides educational insights with complete context and actionable takeaways.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Button onClick={() => triggerAnalysis("general public")} disabled={analyzingNews} className="px-8 py-6 text-lg font-semibold rounded-xl">
                  Top Developments
                </Button>
                <Button onClick={() => triggerAnalysis("government exam aspirant")} disabled={analyzingNews} className="px-8 py-6 text-lg font-semibold rounded-xl">
                  Govt Exam Prep
                </Button>
                <Button onClick={() => triggerAnalysis(judgePov, { state: selectedState || undefined, district: district || undefined })} disabled={analyzingNews} className="px-8 py-6 text-lg font-semibold rounded-xl">
                  District Insights
                </Button>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-muted-foreground mb-1">State</div>
                  <Select value={selectedState} onValueChange={(v) => setSelectedState(v)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent>
                      {indianStates.map((s) => (
                        <SelectItem key={s} value={s}>{s}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground mb-1">District/City</div>
                  <input value={district} onChange={(e) => setDistrict(e.target.value)} placeholder="Type district/city" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base md:text-sm" />
                </div>
                <div>
                  <Select value={judgePov} onValueChange={(v) => setJudgePov(v)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select perspective" />
                    </SelectTrigger>
                    <SelectContent>
                      {judgePerspectives.map((p) => (
                        <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Analysis Result - Enhanced Display */}
            {smartAnalysis && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                transition={{ duration: 0.5 }}
                className="mt-6 pt-6 border-t border-border/50"
              >
                <div className="flex items-start gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-green-500/10 border border-green-500/30">
                    <Sparkles className="w-5 h-5 text-green-500" />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg text-foreground mb-1">
                      Analysis for: {perspective}
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      Generated {new Date().toLocaleTimeString()} • Based on {analysisCount ?? savedArticles.length} articles
                    </p>
                  </div>
                </div>

                <div className="prose prose-sm max-w-none dark:prose-invert" ref={analysisRef}>
                  <div className="p-4 rounded-xl bg-card/50 border border-border/50">
                    <div className="text-foreground">
                      {renderSmartAnalysis(smartAnalysis)}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(smartAnalysis);
                    }}
                    className="flex items-center gap-2"
                  >
                    <Copy className="w-4 h-4" />
                    Copy Analysis
                  </Button>
                  <Button variant="outline" size="sm" onClick={exportAnalysisPdf} className="flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Export PDF
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSmartAnalysis("")}
                    className="flex items-center gap-2 ml-auto text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                  >
                    <X className="w-4 h-4" />
                    Clear
                  </Button>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default News;
  const renderSmartAnalysis = (content: string) => {
    const lines = content.split("\n");
    const elements: JSX.Element[] = [];
    let bullets: string[] = [];
    let inMajorStories = false;
    const flushBullets = () => {
      if (bullets.length) {
        elements.push(
          <ul className="list-disc pl-6 space-y-2">
            {bullets.map((b, i) => (
              <li key={i} className="text-foreground">
                {b.replace(/^•\s*/, "")}
              </li>
            ))}
          </ul>
        );
        bullets = [];
      }
    };
    for (let i = 0; i < lines.length; i++) {
      const t = lines[i].trim();
      if (!t) {
        flushBullets();
        continue;
      }
      const isSep = t.includes("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
      const isHeadingUpper = /^[A-Z0-9' -]+$/.test(t) && t.length > 3 && !t.includes("DataHalo Current Affairs Analysis") && !t.includes("CURRENT AFFAIRS ANALYSIS");
      const next = (lines[i + 1] || "").trim();
      if (isSep) {
        flushBullets();
        elements.push(<div className="my-4 border-t border-border/50" />);
        continue;
      }
      if (t.includes("MAJOR STORIES - IN DEPTH")) {
        flushBullets();
        inMajorStories = true;
        elements.push(<h3 className="text-xl md:text-2xl font-bold mt-4">{t}</h3>);
        continue;
      }
      if (t.includes("KEY POINTS TO REMEMBER") || t.includes("THE BIG PICTURE") || t.includes("WHAT TO WATCH") || t.includes("LATEST NEWS ARTICLES")) {
        flushBullets();
        inMajorStories = false;
        elements.push(<h3 className="text-xl md:text-2xl font-bold mt-4">{t}</h3>);
        continue;
      }
      if (t.startsWith("• ")) {
        bullets.push(t);
        continue;
      }
      if (t.includes("CURRENT AFFAIRS ANALYSIS")) {
        flushBullets();
        elements.push(<h2 className="text-2xl md:text-3xl font-bold">{t}</h2>);
        continue;
      }
      if (isHeadingUpper || (inMajorStories && next.startsWith("• "))) {
        flushBullets();
        elements.push(<h3 className="text-lg md:text-xl font-bold mt-3">{t}</h3>);
        continue;
      }
      elements.push(<p className="text-sm md:text-base leading-relaxed">{t}</p>);
    }
    flushBullets();
    return <div className="space-y-2">{elements}</div>;
  };
  const getErrorMessage = (e: unknown) => {
    if (typeof e === "object" && e && "message" in e) {
      const m = (e as Record<string, unknown>).message;
      return typeof m === "string" ? m : "Unknown error";
    }
    return "Unknown error";
  };
