import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

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
    { value: "general", label: "🌐 General", icon: "🌍" },
    { value: "technology", label: "💻 Technology", icon: "🚀" },
    { value: "business", label: "💼 Business", icon: "📈" },
    { value: "sports", label: "⚽ Sports", icon: "🏆" },
    { value: "science", label: "🔬 Science", icon: "🧪" },
    { value: "entertainment", label: "🎬 Entertainment", icon: "🎭" },
    { value: "health", label: "🏥 Health", icon: "💊" }
  ];

  const perspectives = [
    { value: "general public", label: "👥 General Public", icon: "🌍" },
    { value: "finance analyst", label: "📊 Finance Analyst", icon: "💰" },
    { value: "government exam aspirant", label: "📚 Govt. Exam Aspirant", icon: "🎯" },
    { value: "tech student", label: "💻 Tech Student", icon: "⚡" },
    { value: "business student", label: "🎓 Business Student", icon: "📋" }
  ];

  const fetchNews = async () => {
    setLoading(true);
    setError("");
    try {
      // Load articles from database (fast)
      const res = await fetch(`http://127.0.0.1:8000/news?category=${category}`);
      const data = await res.json();
      
      if (data.status === "success") {
        setArticles(data.articles || []);
        console.log(`📚 Loaded ${data.articles?.length || 0} articles from database`);
      } else {
        setError("Failed to load articles from database");
      }
    } catch (error) {
      console.error("Error loading articles:", error);
      setError("Network error while loading articles");
    } finally {
      setLoading(false);
    }
  };

  const refreshNews = async () => {
    setLoading(true);
    setError("");
    try {
      // Step 1: Fetch fresh news from API and save to database
      console.log(`🔄 Refreshing ${category} news...`);
      const refreshRes = await fetch(`http://127.0.0.1:8000/refresh-news?category=${category}`);
      const refreshData = await refreshRes.json();
      
      if (refreshData.status === "success") {
        // Step 2: Update frontend with the refreshed articles
        setArticles(refreshData.articles || []);
        console.log(`✅ Refreshed with ${refreshData.fresh_fetched} fresh articles`);
        
        // Optional: Show success message
        const successMessage = `Refreshed with ${refreshData.fresh_fetched} fresh articles!`;
        console.log(successMessage);
      } else {
        setError("Failed to refresh news");
      }
    } catch (error) {
      console.error("Error refreshing news:", error);
      setError("Network error while refreshing news");
    } finally {
      setLoading(false);
    }
  };

  const generateSmartFeed = async () => {
    setAiLoading(true);
    setError("");
    setSmartFeed("");
    
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/smart-feed?pov=${encodeURIComponent(perspective)}`,
        { method: "POST" }
      );
      const data = await res.json();
      
      if (data.status === "success") {
        setSmartFeed(data.summary || "No smart feed available.");
      } else {
        setError(data.detail || "Failed to generate smart feed");
      }
    } catch (error) {
      console.error("Error fetching smart feed:", error);
      setError("Network error while generating smart feed");
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [category]);

  const selectedCategory = categories.find(cat => cat.value === category);
  const selectedPerspective = perspectives.find(persp => persp.value === perspective);

  return (
    <section className="relative min-h-screen bg-black text-white overflow-hidden p-8 flex flex-col items-center">
      {/* Animated Background */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-[#000814] via-[#00111f] to-black"
        animate={{ opacity: [0.9, 1, 0.9] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />

      <div className="relative z-10 w-full max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl font-orbitron font-bold mb-4 bg-gradient-to-r from-[#00bfff] to-[#00e5ff] bg-clip-text text-transparent">
            ⚡ DataHalo News Hub
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Get the latest news and AI-powered insights tailored to your perspective
          </p>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6 text-center"
          >
            <p className="text-red-200">❌ {error}</p>
          </motion.div>
        )}

        {/* Controls Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-wrap gap-6 justify-center items-center mb-12 p-6 bg-gradient-to-r from-[#001122] to-[#002244] rounded-2xl border border-[#00bfff30]"
        >
          <div className="flex flex-col items-center gap-2">
            <label className="text-sm font-medium text-[#00d4ff]">📰 Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-3 bg-[#000814] border border-[#00bfff60] rounded-xl focus:outline-none focus:border-[#00bfff] text-white font-medium min-w-[160px] transition-all duration-200"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.icon} {cat.label.replace(/🌐|💻|💼|⚽|🔬|🎬|🏥/, '')}
                </option>
              ))}
            </select>
          </div>

          <Button
            onClick={refreshNews}
            disabled={loading}
            className="px-8 py-3 bg-gradient-to-r from-[#00bfff] to-[#00d4ff] hover:from-[#00d4ff] hover:to-[#00e5ff] text-black font-bold rounded-xl shadow-[0_0_25px_#00bfff60] transition-all duration-300 transform hover:scale-105"
          >
            {loading ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-black border-t-transparent rounded-full mr-2" />
                Loading...
              </>
            ) : (
              <>🔄 Refresh {selectedCategory?.icon}</>
            )}
          </Button>
        </motion.div>

        {/* Basic News Feed */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold mb-8 text-center text-[#00d4ff] flex items-center justify-center gap-3">
            📰 Latest {selectedCategory?.label} News
            <span className="text-lg bg-[#00bfff20] px-3 py-1 rounded-full">
              {articles.length} articles
            </span>
          </h2>

          {articles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {articles.slice(0, 24).map((article, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="group"
                >
                  <Card className="h-full bg-gradient-to-br from-[#001122] to-[#002244] border border-[#00bfff40] hover:border-[#00bfff80] transition-all duration-300 transform hover:scale-105 hover:shadow-[0_0_30px_#00bfff40]">
                    {article.image && (
                      <div className="relative overflow-hidden rounded-t-lg">
                        <img
                          src={article.image}
                          alt={article.title}
                          className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-110"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                          }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                      </div>
                    )}
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg font-semibold text-[#00d4ff] line-clamp-2 group-hover:text-[#00e5ff] transition-colors">
                        {article.title}
                      </CardTitle>
                      <CardDescription className="text-gray-300 text-sm line-clamp-3">
                        {article.description || "No description available."}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
                        <span className="bg-[#00bfff20] px-2 py-1 rounded-full">
                          {article.source}
                        </span>
                        <span>
                          {new Date(article.publishedAt).toLocaleDateString()}
                        </span>
                      </div>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-[#00bfff] hover:text-[#00e5ff] hover:underline transition-colors font-medium"
                      >
                        Read Full Article →
                      </a>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="animate-spin h-12 w-12 border-4 border-[#00bfff] border-t-transparent rounded-full" />
              <span className="ml-4 text-xl text-gray-300">Loading articles...</span>
            </div>
          ) : (
            <div className="text-center py-16">
              <p className="text-xl text-gray-400">No articles found for this category.</p>
              <Button onClick={fetchNews} className="mt-4">
                Try Again
              </Button>
            </div>
          )}
        </motion.div>

        {/* Smart Feed Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-8"
        >
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-[#00ffcc] to-[#00d4ff] bg-clip-text text-transparent">
              🧠 AI Smart Feed
            </h2>
            <p className="text-lg text-gray-300 max-w-3xl mx-auto">
              Get personalized insights and analysis based on your perspective using advanced AI
            </p>
          </div>

          <div className="flex flex-wrap gap-6 justify-center items-center mb-8 p-6 bg-gradient-to-r from-[#001122] to-[#002244] rounded-2xl border border-[#00ffcc30]">
            <div className="flex flex-col items-center gap-2">
              <label className="text-sm font-medium text-[#00ffcc]">🎯 Your Perspective</label>
              <select
                value={perspective}
                onChange={(e) => setPerspective(e.target.value)}
                className="px-4 py-3 bg-[#000814] border border-[#00ffcc60] rounded-xl focus:outline-none focus:border-[#00ffcc] text-white font-medium min-w-[200px] transition-all duration-200"
              >
                {perspectives.map(persp => (
                  <option key={persp.value} value={persp.value}>
                    {persp.icon} {persp.label.replace(/👥|📊|📚|💻|🎓/, '')}
                  </option>
                ))}
              </select>
            </div>

            <Button
              onClick={generateSmartFeed}
              disabled={aiLoading || articles.length === 0}
              className="px-8 py-3 bg-gradient-to-r from-[#00ffcc] to-[#00d4ff] hover:from-[#00d4ff] hover:to-[#00e5ff] text-black font-bold rounded-xl shadow-[0_0_25px_#00ffcc60] transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
            >
              {aiLoading ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-black border-t-transparent rounded-full mr-2" />
                  Analyzing...
                </>
              ) : (
                <>⚙️ Generate Smart Analysis {selectedPerspective?.icon}</>
              )}
            </Button>
          </div>

          {/* Smart Feed Display */}
          {smartFeed && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="relative"
            >
              <Card className="bg-gradient-to-br from-[#001122] to-[#002244] border border-[#00ffcc60] shadow-[0_0_40px_#00ffcc30]">
                <CardHeader className="pb-4">
                  <CardTitle className="text-2xl font-bold text-[#00ffcc] flex items-center gap-3">
                    🧠 Smart Analysis for {selectedPerspective?.label}
                  </CardTitle>
                  <CardDescription className="text-gray-300">
                    AI-powered insights tailored to your perspective
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-invert max-w-none">
                    <div className="text-gray-200 whitespace-pre-line leading-relaxed text-base">
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
              <p className="text-lg text-gray-400 mb-4">
                Ready to get personalized insights? Select your perspective and generate your smart feed!
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
};

export default News;