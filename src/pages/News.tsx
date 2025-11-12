import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

interface Article {
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: string;
  category?: string;
}

const News = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState("general");

  const fetchNews = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/news?category=${category}`);
      const data = await res.json();
      setArticles(data.articles || []);
    } catch (error) {
      console.error("Error fetching news:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [category]);

  return (
    <section className="relative min-h-screen bg-black text-white overflow-hidden p-8 flex flex-col items-center">
      {/* Animated background */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-[#000814] via-[#00111f] to-black"
        animate={{ opacity: [0.9, 1, 0.9] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
      />

      <div className="relative z-10 w-full max-w-6xl">
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center text-5xl font-orbitron font-bold mb-8 bg-gradient-to-r from-[#00bfff] to-[#00e5ff] bg-clip-text text-transparent"
        >
          ⚡ DataHalo News Feed
        </motion.h1>

        {/* Category Filter + Refresh */}
        <div className="flex flex-wrap gap-4 justify-center items-center mb-10">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-4 py-2 bg-transparent border border-[#00bfff80] rounded-lg focus:outline-none text-white"
          >
            <option value="general">General</option>
            <option value="technology">Technology</option>
            <option value="business">Business</option>
            <option value="sports">Sports</option>
            <option value="science">Science</option>
            <option value="entertainment">Entertainment</option>
            <option value="health">Health</option>
          </select>

          <Button
            onClick={fetchNews}
            className="px-6 py-3 bg-[#00bfff] hover:bg-[#00d4ff] text-black font-semibold rounded-xl shadow-[0_0_20px_#00bfff80]"
          >
            {loading ? "Refreshing..." : "🔄 Refresh"}
          </Button>
        </div>

        {/* News Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.length > 0 ? (
            articles.slice(0, 24).map((article, index) => (
              <motion.div
                key={index}
                className="p-5 rounded-2xl bg-gradient-to-br from-[#001a33] to-[#002244] border border-[#00bfff50] shadow-[0_0_20px_#00bfff40] hover:shadow-[0_0_40px_#00bfff80] transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <h3 className="text-xl font-semibold mb-2 text-[#00d4ff]">
                  {article.title}
                </h3>
                <p className="text-gray-300 text-sm mb-3">
                  {article.description}
                </p>
                <div className="text-xs text-gray-500 mb-2">
                  {article.source} —{" "}
                  {new Date(article.publishedAt).toLocaleDateString()}
                </div>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#00bfff] hover:underline"
                >
                  Read Full Article →
                </a>
              </motion.div>
            ))
          ) : (
            <p className="text-gray-400 text-lg text-center col-span-full">
              No articles found.
            </p>
          )}
        </div>
      </div>
    </section>
  );
};

export default News;
