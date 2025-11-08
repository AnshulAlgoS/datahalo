"use client";
import React, {useState} from "react";
import axios from "axios";
import {motion, AnimatePresence} from "framer-motion";
import {ChevronDown, ChevronUp, Link as LinkIcon, Newspaper, Globe} from "lucide-react";

export default function JournalistAnalyzer() {
    const [name, setName] = useState("");
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [logs, setLogs] = useState([]);
    const [error, setError] = useState("");
    const [expanded, setExpanded] = useState(false);

    const addLog = (msg) => setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

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
            const response = await axios.post(
                "http://localhost:8000/analyze",
                {name: name.trim()},
                {timeout: 90000, headers: {"Content-Type": "application/json"}}
            );
            addLog("✅ Analysis received.");
            setAnalysis(response.data);
        } catch (error) {
            const message = error.response?.data?.detail || error.message;
            setError(`Analysis failed: ${message}`);
            addLog(`❌ Error: ${message}`);
        } finally {
            setLoading(false);
        }
    };

    const profile = analysis
        ? analysis.aiProfile?.profile || analysis.aiProfile || {}
        : {};
    const articles = Array.isArray(analysis?.articles)
        ? analysis.articles
        : Array.isArray(profile?.articles)
        ? profile.articles
        : [];
    const imageSrc =
        profile.image ||
        analysis?.image ||
        "/placeholder.jpg";
    const bioText =
        profile.bio ||
        profile.bio_section ||
        analysis?.bio ||
        "No biography found.";
    const socials =
        Array.isArray(profile.social_links)
            ? profile.social_links
            : Array.isArray(analysis?.social_links)
            ? analysis.social_links
            : [];

    return (
        <div className="max-w-5xl mx-auto mt-16 p-8 rounded-2xl shadow-xl bg-card/80 backdrop-blur-md border border-border">
            <motion.h1
                initial={{opacity: 0, y: -10}}
                animate={{opacity: 1, y: 0}}
                className="text-4xl font-orbitron font-bold text-primary mb-6 text-center"
            >
                Journalist Credibility Analyzer
            </motion.h1>

            {/* Input Section */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <input
                    type="text"
                    placeholder="Enter journalist name (e.g., Barkha Dutt)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
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

            {error && (
                <div className="p-3 mb-6 rounded-md bg-destructive/20 border border-destructive text-destructive text-sm">
                    {error}
                </div>
            )}

            {/* Results Section */}
            {analysis && (
                <motion.div
                    initial={{opacity: 0, y: 20}}
                    animate={{opacity: 1, y: 0}}
                    className="rounded-xl border border-border bg-card/90 shadow-md p-6 space-y-6"
                >
                    {/* Profile Header */}
                    <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                        <motion.img
                            src={imageSrc}
                            alt={analysis.journalist}
                            className="w-32 h-32 rounded-full object-cover border border-border shadow-sm"
                        />
                        <div className="flex-1">
                            <h2 className="text-2xl font-semibold text-primary font-orbitron">
                                {analysis.journalist}
                            </h2>
                            <p className="text-muted-foreground mt-2">
                                {bioText}
                            </p>

                            {/* Social Links */}
                            {socials.length > 0 && (
                                <div className="flex flex-wrap gap-2 mt-3">
                                    {socials.map((link, i) => {
                                        try {
                                            const domain = new URL(link).hostname.replace("www.", "");
                                            return (
                                                <a
                                                    key={i}
                                                    href={link}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-md bg-muted hover:bg-muted/60 border border-border"
                                                >
                                                    <LinkIcon size={12}/> {domain}
                                                </a>
                                            );
                                        } catch {
                                            return null;
                                        }
                                    })}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Quick Summary */}
                    <div className="border-t border-border pt-4">
                        <p className="text-sm text-muted-foreground">
                            <strong>Articles Analyzed:</strong>{" "}
                            {analysis.articlesAnalyzed || articles.length || 0}
                        </p>
                    </div>

                    {/* Expandable Detailed Analysis */}
                    <div className="border-t border-border pt-4">
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className="flex items-center gap-2 text-primary font-medium hover:underline"
                        >
                            {expanded ? (
                                <>
                                    <ChevronUp size={16}/> Hide Detailed Analysis
                                </>
                            ) : (
                                <>
                                    <ChevronDown size={16}/> View Detailed Analysis
                                </>
                            )}
                        </button>

                        <AnimatePresence>
                            {expanded && (
                                <motion.div
                                    initial={{opacity: 0, y: 10}}
                                    animate={{opacity: 1, y: 0}}
                                    exit={{opacity: 0, y: 10}}
                                    className="mt-4 space-y-4"
                                >
                                    {/* AI Analysis Text */}
                                    <div className="p-4 bg-muted/30 rounded-lg border border-border">
                                        <pre className="text-xs whitespace-pre-wrap text-foreground">
                                            {typeof analysis.aiProfile === "string"
                                                ? analysis.aiProfile
                                                : JSON.stringify(analysis.aiProfile, null, 2)}
                                        </pre>
                                    </div>

                                    {/* Articles List */}
                                    <div className="space-y-2">
                                        <h3 className="font-semibold flex items-center gap-2 text-primary">
                                            <Newspaper size={16}/> Articles
                                        </h3>
                                        {articles.length > 0 ? (
                                            <ul className="space-y-2">
                                                {articles.slice(0, 8).map((a, i) => (
                                                    <li
                                                        key={i}
                                                        className="p-3 rounded-md border border-border bg-background/50 hover:bg-background/80 transition"
                                                    >
                                                        <a
                                                            href={a.link || a.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="font-medium hover:underline"
                                                        >
                                                            {a.title || a.headline || "Untitled"}
                                                        </a>
                                                        <p className="text-xs text-muted-foreground mt-1">
                                                            Source: {a.source || a.domain || "Unknown"}
                                                        </p>
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="text-sm text-muted-foreground">No articles found.</p>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </motion.div>
            )}

            {/* Logs */}
            <div className="mt-10 border border-border rounded-md p-4 max-h-64 overflow-y-auto font-mono text-xs bg-card/70 backdrop-blur-sm text-muted-foreground">
                <h2 className="font-semibold mb-2 text-primary text-sm font-orbitron">Live Logs</h2>
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
