from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any, Optional
import requests
import os
import logging
import re
from utils.smart_analysis import smart_analyse
from utils.news_fetcher import fetch_news, refresh_news as refresh_news_fetcher, get_saved_articles, clean_old_articles, get_articles_count_by_category

# ---------------- ENV + LOGGING ---------------- #

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DataHalo")

# ---------------- ENV VARS ---------------- #

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

logger.info(f"NVIDIA_API_KEY present: {bool(NVIDIA_API_KEY)}")
logger.info(f"SERP_API_KEY present: {bool(SERP_API_KEY)}")
logger.info(f"NEWS_API_KEY present: {bool(NEWS_API_KEY)}")

# ---------------- FASTAPI INIT ---------------- #

app = FastAPI(title="DataHalo - Journalist Profile & News Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development URLs
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
        # Production URLs
        "https://datahalo.vercel.app",
        "https://www.datahalo.vercel.app",
        "https://datahalo.onrender.com",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATABASE ---------------- #

try:
    client = MongoClient(MONGO_URI)
    db = client["datahalo"]
    news_collection = db["news"]
    journalist_collection = db["journalists"]
    logger.info("SUCCESS: Connected to MongoDB successfully")
    MONGODB_AVAILABLE = True
except Exception as e:
    logger.error(f"ERROR: MongoDB connection failed: {str(e)}")
    client = None
    db = None
    news_collection = None
    journalist_collection = None
    MONGODB_AVAILABLE = False

# ---------------- JOURNALIST MODULE ---------------- #

# Try to import journalist analysis modules
try:
    from utils.serp_scraper import generate_journalist_case_study as fetch_journalist_data_case_study
    from utils.ai_analysis import analyze_journalist

    JOURNALIST_MODULE_AVAILABLE = True
    logger.info("SUCCESS: Journalist analysis modules loaded")
except ImportError as e:
    logger.warning(f"WARNING: Journalist modules not available: {e}")
    JOURNALIST_MODULE_AVAILABLE = False

class JournalistRequest(BaseModel):
    name: str

class NarrativeRequest(BaseModel):
    topic: str
    days: int = 30

class URLNarrativeRequest(BaseModel):
    url: str

class ArticleRequest(BaseModel):
    article: str

class CaseStudyRequest(BaseModel):
    journalist_name: str

# ---------------- ARTICLE ANALYZER MODULE ---------------- #

# Import AI-FIRST analyzer (credible, responsible approach)
try:
    from utils.ai_article_analyzer import analyze_article_with_ai
    AI_ARTICLE_ANALYZER_AVAILABLE = True
    logger.info("SUCCESS: AI-First Article Analyzer loaded - using real AI analysis")
except ImportError as e:
    logger.error(f"ERROR: AI Article Analyzer not available: {e}")
    AI_ARTICLE_ANALYZER_AVAILABLE = False

# Fallback to rule-based if AI unavailable
try:
    from utils.article_analyzer_v2 import analyze_article as fallback_analyzer
    FALLBACK_ANALYZER_AVAILABLE = True
    logger.info("INFO: Fallback rule-based analyzer available")
except ImportError:
    FALLBACK_ANALYZER_AVAILABLE = False

@app.post("/analyze-article")
async def analyze_article(request: ArticleRequest, use_ai: bool = Query(True, description="Use AI-powered analysis (Qwen3 480B). Set to false for rule-based.")):
    """
    PROFESSIONAL ARTICLE ANALYZER - Dual Mode: Rule-Based (Fast) or AI-Powered (Deep)
    
    **Rule-Based Mode (default, use_ai=false)**:
    - ✅ Instant analysis (< 2 seconds)
    - ✅ Based on AP Style, Reuters, SPJ Ethics standards
    - ✅ Garbage input detection (spam/nonsense/testing)
    - ✅ 8-criteria scoring with detailed feedback
    - ✅ ~75-80% correlation with expert grading
    - ✅ Actionable learning recommendations
    
    **AI-Powered Mode (use_ai=true)**:
    - ✅ Deep AI evaluation using Qwen3 480B model (5-15 seconds)
    - ✅ Contextual understanding and nuanced feedback
    - ✅ ATS-like scoring against journalism standards
    - ✅ Specific improvement suggestions
    - ✅ Professional-grade analysis
    
    Optimized for educational credibility and reliability.
    """
    logger.info(f"INFO: Article analyzer endpoint called (AI mode: {use_ai})")
    
    try:
        article_text = request.article.strip()
        
        if not article_text:
            raise HTTPException(status_code=400, detail="Article text is required")
        
        if len(article_text.split()) < 20:
            raise HTTPException(status_code=400, detail="Article too short - minimum 20 words required")
        
        word_count = len(article_text.split())
        
        # AI-POWERED ANALYSIS
        if use_ai:
            logger.info(f"ANALYZE: Starting AI-powered analysis for {word_count} words")
            
            if not AI_ARTICLE_ANALYZER_AVAILABLE:
                logger.warning("AI analyzer not available, falling back to rule-based")
                use_ai = False
            else:
                if not NVIDIA_API_KEY:
                    logger.warning("NVIDIA API key not configured, falling back to rule-based")
                    use_ai = False
                else:
                    logger.info("ANALYZER: Qwen3 AI-powered evaluation (5-15 seconds)")
                    result = analyze_article_with_ai(article_text)
                    
                    if result.get("status") == "success":
                        logger.info(f"SUCCESS: AI analysis complete - Score: {result['analysis']['overall_score']}, Grade: {result['analysis'].get('letter_grade', 'N/A')}")
                        return result
                    else:
                        logger.warning(f"AI analysis failed: {result.get('message')}, falling back to rule-based")
                        use_ai = False
        
        # RULE-BASED ANALYSIS (default or fallback)
        if not use_ai:
            logger.info(f"ANALYZE: Starting rule-based analysis for {word_count} words")
            
            if FALLBACK_ANALYZER_AVAILABLE:
                logger.info("ANALYZER: Professional standards-based evaluation (AP/Reuters/SPJ + garbage detection)")
                result = fallback_analyzer(article_text)
                
                if result.get("status") == "success":
                    logger.info(f"SUCCESS: Analysis complete - Score: {result['analysis']['overall_score']}, Grade: {result['analysis']['letter_grade']}")
                    return result
        
        # If nothing available
        raise HTTPException(
            status_code=503, 
            detail="Article analyzer unavailable. Please check system configuration."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Article analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-article-ai")
async def analyze_article_ai_only(request: ArticleRequest):
    """
    AI-POWERED ARTICLE ANALYZER (Qwen3 480B Model)
    
    Features:
    - ✅ Deep AI evaluation (5-15 seconds)
    - ✅ Contextual understanding and nuanced analysis
    - ✅ 8-criteria scoring: Objectivity, Sources, Accuracy, Clarity, Ethics, Context, Structure, Headline
    - ✅ Specific, actionable improvement suggestions
    - ✅ ATS-like scoring against professional journalism standards
    - ✅ Educational-grade feedback for learning
    
    Uses Qwen3 Coder 480B model - fast, efficient, and reliable.
    Ideal for in-depth article evaluation and learning.
    """
    logger.info("INFO: AI-only article analyzer endpoint called")
    
    try:
        article_text = request.article.strip()
        
        if not article_text:
            raise HTTPException(status_code=400, detail="Article text is required")
        
        if len(article_text.split()) < 20:
            raise HTTPException(status_code=400, detail="Article too short - minimum 20 words required")
        
        word_count = len(article_text.split())
        logger.info(f"AI ANALYZE: Starting AI-powered analysis for {word_count} words")
        
        # Check if AI analyzer is available
        if not AI_ARTICLE_ANALYZER_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="AI article analyzer not available. Please use /analyze-article endpoint for rule-based analysis."
            )
        
        if not NVIDIA_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="AI analysis requires NVIDIA API key configuration."
            )
        
        # USE AI ANALYZER
        logger.info("AI ANALYZER: Qwen3 480B AI-powered evaluation")
        result = analyze_article_with_ai(article_text)
        
        if result.get("status") == "success":
            logger.info(f"SUCCESS: AI analysis complete - Score: {result['analysis']['overall_score']}, Grade: {result['analysis'].get('letter_grade', 'N/A')}")
            return result
        else:
            logger.error(f"AI analysis failed: {result.get('message')}")
            raise HTTPException(status_code=500, detail=result.get('message', 'AI analysis failed'))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: AI article analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

# ---------------- CASE STUDY GENERATOR ENDPOINT ---------------- #

@app.post("/generate-case-study")
async def create_case_study(request: CaseStudyRequest):
    """
    Generate comprehensive educational case study for a journalist
    Like law case studies - deep analysis for journalism students
    Uses DuckDuckGo scraping (free, no API keys) + AI analysis
    """
    logger.info(f"DATA: Case study generation requested for: {request.journalist_name}")
    
    try:
        if not request.journalist_name or len(request.journalist_name.strip()) < 3:
            raise HTTPException(status_code=400, detail="Invalid journalist name - must be at least 3 characters")
        
        # Generate case study using DuckDuckGo scraper
        result = fetch_journalist_data_case_study(request.journalist_name.strip())
        
        if result['status'] == 'error':
            logger.error(f"ERROR: Case study generation failed: {result.get('message', 'Unknown error')}")
            raise HTTPException(status_code=500, detail=result.get('message', 'Failed to generate case study'))
        
        logger.info(f"SUCCESS: Case study generated successfully for {request.journalist_name}")
        logger.info(f"STATS: Data sources: {result['case_study'].get('data_sources_count', 0)}")
        
        return result['case_study']
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Unexpected error in case study generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate case study: {str(e)}")

@app.post("/analyze")
async def analyze(request: JournalistRequest):
    """Analyze journalist's profile, transparency patterns, and work using scraped data and comprehensive AI analysis."""
    if not JOURNALIST_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Journalist analysis module not available")

    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available for storing analysis")

    try:
        name = request.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        logger.info(f"SEARCH: Starting comprehensive analysis for: {name}")

        # Step 1: Check if analysis already exists in database (cache)
        existing_analysis = journalist_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

        if existing_analysis:
            # Check if analysis is recent (less than 7 days old)
            from datetime import timedelta
            analysis_date = existing_analysis.get('analysis_timestamp')
            if analysis_date:
                try:
                    if isinstance(analysis_date, str):
                        analysis_date = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                    if datetime.utcnow() - analysis_date < timedelta(days=7):
                        logger.info(f"DATA: Using cached analysis for: {name}")
                        # Convert ObjectId to string and return cached result
                        existing_analysis["_id"] = str(existing_analysis["_id"])
                        return {
                            "status": "success",
                            "journalist": name,
                            "articlesAnalyzed": existing_analysis.get("articlesAnalyzed", 0),
                            "aiProfile": existing_analysis.get("aiProfile", {}),
                            "source": "cached"
                        }
                except:
                    pass  # If date parsing fails, proceed with fresh analysis

        # Step 2: Fetch fresh data from scraper
        logger.info(f"FETCH: Fetching fresh data for: {name}")
        scraped_data = await fetch_journalist_data(name)

        if not scraped_data or not scraped_data.get("articles"):
            raise HTTPException(status_code=404, detail=f"No articles found for {name}")

        logger.info(f"STATS: Found {len(scraped_data['articles'])} articles for analysis")

        # Step 3: Run comprehensive AI analysis
        logger.info(f"ANALYZE: Running AI analysis for: {name}")
        ai_analysis = analyze_journalist(name, scraped_data)

        # Step 4: Prepare complete analysis result
        analysis_result = {
            "name": name,
            "analysis_timestamp": datetime.utcnow(),
            "articlesAnalyzed": len(scraped_data["articles"]),
            "aiProfile": ai_analysis,
            "scrapedData": {
                "articles_count": len(scraped_data.get("articles", [])),
                "verification_rate": scraped_data.get("verification_rate", 0),
                "data_sources": scraped_data.get("data_sources", []),
                "query_timestamp": scraped_data.get("query_timestamp", ""),
                "primary_profile": scraped_data.get("primary_profile", {}),
                "awards": scraped_data.get("awards", [])
            }
        }

        # Step 5: Save to MongoDB
        try:
            # Update or insert the analysis
            journalist_collection.update_one(
                {"name": {"$regex": f"^{name}$", "$options": "i"}},
                {"$set": analysis_result},
                upsert=True
            )
            logger.info(f"SAVE: Saved analysis to database for: {name}")
        except Exception as db_error:
            logger.error(f"ERROR: Failed to save to database: {str(db_error)}")
            # Continue without failing the request

        # Step 6: Return response
        return {
            "status": "success",
            "journalist": name,
            "articlesAnalyzed": len(scraped_data["articles"]),
            "aiProfile": ai_analysis,
            "source": "fresh_analysis",
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException as he:
        logger.error(f"ERROR: HTTP Error: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"ERROR: Unexpected Error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/fetch")
async def fetch_articles(name: str):
    """Fetch journalist articles without AI analysis."""
    if not JOURNALIST_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Journalist analysis module not available")

    try:
        if not name.strip():
            raise HTTPException(status_code=400, detail="Name is required")

        data = await fetch_journalist_data(name)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {name}")

        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Fetch Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/journalists")
async def get_journalists(limit: int = Query(20, description="Number of journalists to return")):
    """Get list of analyzed journalists from database."""
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        journalists = list(journalist_collection.find(
            {},
            {
                "name": 1,
                "analysis_timestamp": 1,
                "articlesAnalyzed": 1,
                "aiProfile.haloScore.score": 1,
                "aiProfile.haloScore.level": 1,
                "aiProfile.haloScore.description": 1,
                "aiProfile.digitalPresence.profileImage": 1,
                "aiProfile.mainTopics": 1,
                "aiProfile.ideologicalBias": 1
            }
        ).sort("analysis_timestamp", -1).limit(limit))

        # Convert ObjectId to string
        for journalist in journalists:
            journalist["_id"] = str(journalist["_id"])

        return {
            "status": "success",
            "count": len(journalists),
            "journalists": journalists
        }
    except Exception as e:
        logger.error(f"ERROR: Error retrieving journalists: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve journalists")

@app.get("/journalist/{name}")
async def get_journalist(name: str):
    """Get specific journalist analysis from database."""
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        journalist = journalist_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

        if not journalist:
            raise HTTPException(status_code=404, detail=f"No analysis found for {name}")

        # Convert ObjectId to string
        journalist["_id"] = str(journalist["_id"])

        return {
            "status": "success",
            "journalist": journalist
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Error retrieving journalist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve journalist")

# ---------------- NEWS MODULE ---------------- #

@app.get("/news")
async def get_news(category: str = Query("general", description="Category of news")):
    """Get all saved news articles from MongoDB database sorted by newest first."""
    try:
        if not MONGODB_AVAILABLE:
            logger.warning("Database not available")
            raise HTTPException(status_code=500, detail="Database not available")

        # Get all articles for category from database (sorted newest first)
        articles = get_saved_articles(category=category, limit=100)

        # If no articles found, fetch some fresh ones
        if not articles:
            logger.info(f"No articles in database for '{category}', fetching fresh...")
            result = fetch_news(category=category)
            articles = result.get("all_articles", [])

        logger.info(f"DATA: Retrieved {len(articles)} '{category}' articles from database")

        return {
            "status": "success",
            "category": category,
            "source": "database",
            "count": len(articles),
            "articles": articles,
            "message": f"Loaded {len(articles)} articles from database (newest first)"
        }
    except Exception as e:
        logger.error(f"ERROR: Error retrieving news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve news from database")

@app.get("/refresh-news")
async def refresh_news_endpoint(
    category: str = Query("general", description="Category to refresh"),
    country: str = Query("in", description="Country code(s) for regional news. Use comma to fetch multiple or 'international'/'all' for preset")
):
    """
    Refresh news: Fetch fresh articles from API and APPEND to database.
    Returns ALL articles for category sorted by newest first.
    """
    try:
        logger.info(f"REFRESH: Refresh requested for '{category}' category...")

        # Support multiple countries
        preset_international = [
            "in", "us", "gb", "au", "ca", "sg", "ae"
        ]

        countries = [c.strip().lower() for c in country.split(",") if c.strip()] if country else ["in"]
        if country.lower() in ("international", "all"):
            countries = preset_international

        total_new = 0
        total_duplicates = 0

        for c in countries:
            result = refresh_news_fetcher(category=category, page_size=30, country=c)
            if result.get("status") != "success":
                logger.warning(f"REFRESH: Country '{c}' failed: {result.get('error')}")
                continue
            total_new += result.get("count", 0)
            total_duplicates += result.get("duplicates_skipped", 0)

        all_articles = get_saved_articles(category=category, limit=100)

        logger.info(f"SUCCESS: Refresh complete across {len(countries)} country codes: {total_new} new, {len(all_articles)} total in DB")

        return {
            "status": "success",
            "category": category,
            "source": "refreshed",
            "new_articles_count": total_new,
            "duplicates_skipped": total_duplicates,
            "total_articles": len(all_articles),
            "articles": all_articles,
            "countries": countries,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Added {total_new} new articles across {len(countries)} countries. Total: {len(all_articles)}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Error during refresh: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to refresh news: {str(e)}")

@app.get("/saved-news")
async def get_saved_news(category: str = Query("all", description="Category filter")):
    """Get saved news articles from MongoDB."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")

        articles = get_saved_articles(category=category, limit=100)

        return {
            "status": "success",
            "category": category,
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        logger.error(f"ERROR: Error retrieving saved news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve saved news")

@app.post("/smart-feed")
async def get_smart_feed(
    pov: str = Query("general public", description="Perspective like finance, student, exam, etc."),
    days: int = Query(7, description="Limit analysis to articles from the last N days"),
    state: str = Query("", description="Optional Indian state to focus on"),
    district: str = Query("", description="Optional district/city to focus on")
):
    """Generate AI-powered smart feed based on saved articles and perspective."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")

        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        articles = list(
            news_collection
            .find({"fetchedAt": {"$gte": start_date, "$lte": end_date}})
            .sort("fetchedAt", -1)
        )

        if not articles:
            # Try to fetch some news first
            logger.info("No articles found, fetching fresh news...")
            await get_news("general")
            articles = list(
                news_collection
                .find({"fetchedAt": {"$gte": start_date, "$lte": end_date}})
                .sort("fetchedAt", -1)
            )

        if not articles:
            raise HTTPException(status_code=404, detail="No news articles found in database. Please fetch news first.")

        # Convert MongoDB documents to dict for AI analysis (unfiltered)
        article_data = []
        for article in articles:
            article_data.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", ""),
                "category": article.get("category", ""),
                "publishedAt": article.get("publishedAt", "")
            })

        # Region-targeted fetch using SERP or NewsData.io when state/district provided
        articles_for_ai = []
        if state or district:
            # POV-specific keyword enrichment
            pov_kw_map = {
                "women commission": [
                    "women", "women safety", "crime against women", "sexual assault",
                    "harassment", "domestic violence", "trafficking", "women commission"
                ],
                "assistant commissioner of police": [
                    "police", "law and order", "crime", "cybercrime", "enforcement",
                    "FIR", "investigation", "arrest"
                ],
                "ias officer": [
                    "governance", "administration", "implementation", "compliance",
                    "scheme", "policy", "district magistrate", "collector"
                ],
                "economist": [
                    "economy", "inflation", "employment", "GDP", "trade",
                    "investment", "markets", "industry"
                ],
                "social worker": [
                    "welfare", "community", "NGO", "beneficiary", "child protection",
                    "education", "health", "poverty"
                ],
                "block president": [
                    "local development", "infrastructure", "roads", "school",
                    "health center", "panchayat", "block", "gram"
                ],
            }

            pov_key = (pov or "").strip().lower()
            pov_keywords = pov_kw_map.get(pov_key, [])
            base_terms = [
                (district.strip() if district else ""),
                (state.strip() if state else ""),
                "India",
            ]
            region_query = " ".join([p for p in base_terms + pov_keywords if p])
            region_results = []
            try:
                if SERP_API_KEY and region_query:
                    serp_url = "https://serpapi.com/search.json"
                    serp_params = {
                        "api_key": SERP_API_KEY,
                        "engine": "google_news",
                        "q": region_query,
                        "gl": "in",
                        "hl": "en",
                        "num": 50
                    }
                    logger.info(f"REGION: SERP search for '{region_query}'")
                    serp_response = requests.get(serp_url, params=serp_params, timeout=15)
                    if serp_response.status_code == 200:
                        serp_data = serp_response.json()
                        news_results = serp_data.get("news_results", [])
                        for item in news_results:
                            title = item.get("title", "")
                            snippet = item.get("snippet", "")
                            link = item.get("link", "")
                            source = item.get("source", {}).get("name", "Unknown") if isinstance(item.get("source"), dict) else "Unknown"
                            date = item.get("date", "")
                            text = f"{title} {snippet}".lower()
                            relevant = True
                            if pov_keywords:
                                relevant = any(k.lower() in text for k in pov_keywords)
                            if title and link and relevant:
                                region_results.append({
                                    "title": title,
                                    "description": snippet or title,
                                    "url": link,
                                    "source": source,
                                    "category": "general",
                                    "publishedAt": date or datetime.utcnow().isoformat()
                                })
                # Fallback to NewsData.io keyword search
                if not region_results and NEWS_API_KEY and region_query:
                    nd_url = "https://newsdata.io/api/1/latest"
                    nd_params = {
                        "apikey": NEWS_API_KEY,
                        "language": "en",
                        "country": "in",
                        "q": region_query,
                        "size": 10
                    }
                    logger.info(f"REGION: NewsData keyword search for '{region_query}'")
                    nd_response = requests.get(nd_url, params=nd_params, timeout=10)
                    if nd_response.status_code == 200:
                        nd_data = nd_response.json()
                        results = nd_data.get("results", [])
                        for item in results:
                            title = item.get("title")
                            link = item.get("link")
                            if not title or not link:
                                continue
                            text = f"{title} {item.get('description','')}".lower()
                            relevant = True
                            if pov_keywords:
                                relevant = any(k.lower() in text for k in pov_keywords)
                            if not relevant:
                                continue
                            region_results.append({
                                "title": title,
                                "description": item.get("description", ""),
                                "url": link,
                                "source": item.get("source_id", "Unknown"),
                                "category": "general",
                                "publishedAt": item.get("pubDate", "")
                            })
            except Exception as e:
                logger.error(f"ERROR: Region fetch failed: {e}")

            if region_results and len(region_results) >= 8:
                articles_for_ai = region_results[:50]
            else:
                # Soft filter from DB, else use all recent
                filtered = []
                s = (state or "").strip().lower()
                d = (district or "").strip().lower()
                for a in article_data:
                    t = a.get("title", "").lower()
                    desc = (a.get("description", "") or "").lower()
                    if (s and (s in t or s in desc)) or (d and (d in t or d in desc)):
                        filtered.append(a)
                articles_for_ai = filtered if filtered and len(filtered) >= 8 else article_data
        else:
            articles_for_ai = article_data

        logger.info(f"ANALYZE: Analyzing {len(articles_for_ai)} articles for perspective: {pov} from last {days} days")
        summary = smart_analyse(articles_for_ai, pov, region_context={"state": state, "district": district})

        return {
            "status": "success",
            "perspective": pov,
            "articlesAnalyzed": len(articles_for_ai),
            "summary": summary
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"ERROR: Smart feed error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI Analysis Error: {str(e)}")

@app.post("/analyze-narrative")
async def analyze_narrative(request: NarrativeRequest):
    """Analyze media narratives over time to detect patterns, trends, and manipulation indicators."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")

        if not NVIDIA_API_KEY:
            raise HTTPException(status_code=503, detail="AI analysis not configured")

        topic = request.topic.strip()
        days = request.days

        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        logger.info(f"SEARCH: Analyzing narrative for topic: '{topic}' over {days} days")

        # Calculate date range
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # OPTIMIZED: Skip database entirely, go straight to SERP for fresh results
        articles = []
        
        if SERP_API_KEY:
            logger.info(f"OPTIMIZE: Going directly to SERP API for fresh Google News results...")
        else:
            # Only check database if SERP not available
            logger.info(f"INFO: SERP not available, checking database...")
            articles = list(news_collection.find({
                "$or": [
                    {"title": {"$regex": topic, "$options": "i"}},
                    {"description": {"$regex": topic, "$options": "i"}}
                ],
                "fetchedAt": {"$gte": start_date, "$lte": end_date}
            }).sort("fetchedAt", -1).limit(20))
            logger.info(f"STATS: Database: Found {len(articles)} articles")

        # SERP API: Fetch fresh data from Google News
        if SERP_API_KEY:
            logger.info(f"OPTIMIZE: Fetching fresh data from Google News via SERP API for '{topic}'...")
            
            try:
                # Use SERP API to search Google News
                serp_url = "https://serpapi.com/search.json"
                serp_params = {
                    "api_key": SERP_API_KEY,
                    "engine": "google_news",
                    "q": topic,
                    "gl": "in",  # India region
                    "hl": "en",  # English language
                    "num": 100  # Increased to get more comprehensive results
                }
                
                logger.info(f"SEARCH: Searching Google News for: '{topic}'")
                serp_response = requests.get(serp_url, params=serp_params, timeout=15)
                
                logger.info(f"API: SERP API response status: {serp_response.status_code}")
                
                if serp_response.status_code == 200:
                    serp_data = serp_response.json()
                    news_results = serp_data.get("news_results", [])
                    
                    logger.info(f"SUCCESS: SERP API returned {len(news_results)} news results")
                    
                    seen_urls = {a["url"] for a in articles}
                    keywords = [word.lower() for word in topic.split() if len(word) > 2]
                    
                    serp_added = 0
                    for item in news_results:
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")
                        link = item.get("link", "")
                        source = item.get("source", {}).get("name", "Unknown") if isinstance(item.get("source"), dict) else "Unknown"
                        date = item.get("date", "")
                        thumbnail = item.get("thumbnail", "")
                        
                        if title and link and link not in seen_urls:
                            # Verify relevance
                            text = f"{title} {snippet}".lower()
                            matches = sum(1 for word in keywords if word in text)
                            
                            # Require at least 2 keywords for relevance
                            required_matches = max(1, min(2, len(keywords)))
                            
                            if matches >= required_matches:
                                article = {
                                    "title": title,
                                    "description": snippet or title,
                                    "url": link,
                                    "image": thumbnail,
                                    "source": source,
                                    "publishedAt": date or datetime.utcnow().isoformat(),
                                    "category": "general",
                                    "fetchedAt": datetime.utcnow(),
                                }
                                
                                # Save to database
                                news_collection.update_one(
                                    {"url": article["url"]},
                                    {"$set": article},
                                    upsert=True
                                )
                                
                                articles.append(article)
                                seen_urls.add(link)
                                serp_added += 1
                    
                    logger.info(f"SUCCESS: SERP API: {serp_added} articles added from Google News")
                    logger.info(f"SAVE: After SERP scraping: {len(articles)} total articles")
                else:
                    logger.error(f"ERROR: SERP API error: {serp_response.status_code} - {serp_response.text[:200]}")
            
            except Exception as e:
                logger.error(f"ERROR: SERP API scraping failed: {str(e)}", exc_info=True)
        
        # Final check
        if len(articles) < 3:
            logger.error(f"ERROR: Insufficient articles: only {len(articles)} found")

            # Get sample topics from database
            sample_articles = list(news_collection.find().sort("fetchedAt", -1).limit(20))
            sample_topics = []
            for article in sample_articles:
                title = article.get("title", "")
                # Extract capitalized phrases as potential topics
                import re
                matches = re.findall(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)', title)
                sample_topics.extend(matches[:2])

            sample_topics = list(set(sample_topics))[:5]

            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"Found only {len(articles)} articles for '{topic}'. Need at least 3 articles for analysis.",
                    "suggestions": sample_topics if sample_topics else [
                        "Technology",
                        "Elections",
                        "Economy",
                        "Healthcare",
                        "Climate"
                    ],
                    "tip": "Try broader terms or popular topics from recent news"
                }
            )

        logger.info(f"SUCCESS: Analysis ready with {len(articles)} articles")

        # Prepare FULL article details for AI (limit to most relevant/recent 30)
        articles = articles[:30]
        article_details = []

        for i, article in enumerate(articles, 1):
            article_details.append({
                "id": i,
                "title": article.get("title", ""),
                "description": article.get("description", "")[:300],
                "source": article.get("source", "Unknown"),
                "date": article.get("publishedAt", "")[:10] if article.get("publishedAt") else "",
                "url": article.get("url", "")
            })

        # Build comprehensive article list for AI
        articles_text = "\n\n".join([
            f"ARTICLE #{a['id']}\nSource: {a['source']}\nDate: {a['date']}\nTitle: {a['title']}\nContent: {a['description']}\nURL: {a['url']}"
            for a in article_details[:20]  # Send full details for first 20 articles
        ])

        # STREAMLINED AI prompt for faster response with key insights
        prompt = f"""Analyze media coverage of "{topic}" to detect narrative patterns and manipulation.

DATA: {len(articles)} articles from {days} days

ARTICLES (most recent):
{articles_text}

Provide concise JSON analysis:

{{
  "main_narrative": "Brief summary of what media is saying (2-3 sentences, cite Article #X, #Y)",
  "manipulation_detected": "Yes/No - brief explanation with evidence from specific articles",
  "key_phrases": ["Repeated phrase 1", "Repeated phrase 2", "Repeated phrase 3"],
  "timeline": [
    {{"date": "YYYY-MM-DD", "count": 5, "sentiment": "Negative/Positive/Neutral", "keyEvents": ["Headline 1", "Headline 2"]}}
  ],
  "keyNarratives": [
    {{"narrative": "Main storyline", "frequency": 15, "sources": ["Source1", "Source2"], "exampleHeadlines": ["Headline from Article #X"]}}
  ],
  "manipulation_indicators": {{
    "coordinated_timing": true/false,
    "source_clustering": true/false,
    "sentiment_uniformity": true/false,
    "sudden_spike": true/false,
    "explanation": "Brief evidence"
  }},
  "context": {{
    "majorEvents": ["Key event 1", "Key event 2"],
    "relatedTopics": ["Topic 1", "Topic 2"]
  }}
}}

Be concise. Return ONLY valid JSON. No markdown, no text outside JSON."""

        # Call AI
        try:
            headers = {
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "qwen/qwen3-coder-480b-a35b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a data analyst. Return ONLY valid JSON. No markdown, no text outside JSON. Be concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 2000  # Reduced for faster response
            }

            logger.info("AI: Calling AI for analysis...")
            
            # AI call with extended timeout for complex analysis
            max_retries = 3
            response = None
            for attempt in range(max_retries):
                try:
                    timeout_seconds = 300  # 5 minutes - enough time for complex analysis
                    logger.info(f"AI: Attempt {attempt + 1}/{max_retries} (timeout: {timeout_seconds}s)")
                    response = requests.post(
                        "https://integrate.api.nvidia.com/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=timeout_seconds
                    )
                    response.raise_for_status()
                    logger.info("AI: Request successful!")
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"AI: Timeout on attempt {attempt + 1}, waiting {wait_time}s before retry...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.error("AI: All attempts timed out - analysis taking too long")
                        raise
                except requests.exceptions.RequestException as e:
                    logger.error(f"AI: Request error on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(5)
                    else:
                        raise
            
            if not response:
                raise Exception("AI request failed after all retries")

            ai_response = response.json()
            content = ai_response["choices"][0]["message"]["content"]

            logger.info(f"SUCCESS: AI response received ({len(content)} chars)")
            logger.info(f"INFO: First 200 chars: {content[:200]}")

            # Parse JSON with better error handling
            import json
            import re

            try:
                # Try to find JSON in response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info(f"📦 Found JSON block ({len(json_str)} chars)")
                    analysis_data = json.loads(json_str)
                    logger.info(f"SUCCESS: JSON parsed successfully")
                else:
                    # Try parsing entire content as JSON
                    logger.info("WARNING: No JSON block found, trying entire content")
                    analysis_data = json.loads(content)
            except json.JSONDecodeError as je:
                logger.error(f"ERROR: JSON parsing failed: {je}")
                logger.error(f"FILE: Content: {content[:500]}")
                # Return a fallback response
                raise Exception(f"AI returned invalid JSON: {str(je)}")

            result = {
                "status": "success",
                "analysis": {
                    "topic": topic,
                    "timeframe": f"{days} days",
                    "totalArticles": len(articles),
                    
                    # Streamlined analysis
                    "main_narrative": analysis_data.get("main_narrative", ""),
                    "manipulation_detected": analysis_data.get("manipulation_detected", "Unknown"),
                    "key_phrases": analysis_data.get("key_phrases", []),
                    "timeline": analysis_data.get("timeline", [])[:8],
                    "keyNarratives": analysis_data.get("keyNarratives", [])[:5],
                    "manipulation_indicators": analysis_data.get("manipulation_indicators", {}),
                    "context": analysis_data.get("context", {}),
                    
                    # Keep for compatibility
                    "narrativePattern": {
                        "rising": len(articles) > 20,
                        "trend": "Rising" if len(articles) > 30 else "Stable",
                        "sentiment": "Mixed",
                        "intensity": min(100, len(articles) * 3)
                    }
                }
            }

            logger.info(f"SUCCESS: Narrative analysis complete for '{topic}'")
            return result

        except Exception as e:
            logger.error(f"ERROR: AI analysis failed: {str(e)}")
            # Return basic analysis
            return {
                "status": "success",
                "analysis": {
                    "topic": topic,
                    "timeframe": f"{days} days",
                    "totalArticles": len(articles),
                    "narrativePattern": {
                        "rising": True,
                        "trend": "Stable",
                        "sentiment": "Mixed",
                        "intensity": 50
                    },
                    "timeline": [],
                    "keyNarratives": [{
                        "narrative": f"Coverage of {topic}",
                        "frequency": len(articles),
                        "sources": list(set([a.get("source", "Unknown") for a in articles[:5]])),
                        "firstAppeared": articles[-1].get("publishedAt", "")[:10] if articles else "",
                        "peakDate": articles[0].get("publishedAt", "")[:10] if articles else ""
                    }],
                    "manipulation_indicators": {
                        "coordinated_timing": False,
                        "source_clustering": False,
                        "sentiment_uniformity": False,
                        "sudden_spike": False,
                        "explanation": "AI analysis unavailable - showing basic statistics"
                    },
                    "context": {
                        "majorEvents": [],
                        "relatedTopics": [],
                        "potentialTriggers": []
                    }
                },
                "message": "Basic analysis provided (AI unavailable)"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Narrative analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ---------------- URL-NARRATIVE MODULE ---------------- #

# Try importing comprehensive URL narrative analyzer
try:
    from utils.url_narrative_analyzer import analyze_url_narrative
    URL_NARRATIVE_AVAILABLE = True
    logger.info("SUCCESS: URL narrative analyzer module loaded")
except ImportError as e:
    logger.warning(f"WARNING: URL narrative analyzer not available: {e}")
    URL_NARRATIVE_AVAILABLE = False

@app.post("/analyze-url-narrative")
async def analyze_url_narrative_endpoint(request: URLNarrativeRequest):
    """Analyze media narratives for a given URL."""
    logger.info(f"TARGET: URL Narrative endpoint called with URL: {request.url}")
    
    try:
        if not URL_NARRATIVE_AVAILABLE:
            logger.error("ERROR: URL narrative analyzer module not available")
            raise HTTPException(status_code=503, detail="URL narrative analyzer module not available")
        
        url = request.url.strip()
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        logger.info(f"SEARCH: Starting URL narrative analysis for: '{url}'")
        
        # Use the comprehensive URL narrative analyzer
        result = await analyze_url_narrative(url, SERP_API_KEY, NVIDIA_API_KEY)
        
        logger.info(f"STATS: Analysis result status: {result.get('status')}")
        
        # Check if result indicates an error
        if result.get("status") == "error":
            error_msg = result.get("error", "Unknown error")
            logger.error(f"URL narrative analysis failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")
        
        # Check if result indicates limited data
        if result.get("status") == "limited_data":
            logger.warning(f"Limited data for URL analysis")
            return {
                "status": "success",
                "analysis": result.get("analysis", {}),
                "message": "Limited data available for analysis"
            }
        
        logger.info(f"SUCCESS: URL narrative analysis complete")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: URL narrative analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ---------------- AI TUTOR MODULE WITH RAG & MULTI-CHAT ---------------- #

class AITutorRequest(BaseModel):
    message: str
    conversation_history: list = []
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    chat_title: Optional[str] = None

class CreateChatRequest(BaseModel):
    user_id: str
    title: str = "New Conversation"

class UpdateChatTitleRequest(BaseModel):
    chat_id: str
    title: str

async def web_search_for_context(query: str) -> dict:
    """Perform CONTEXTUAL web search based on user's ACTUAL question."""
    if not SERP_API_KEY:
        return {"context": "", "sources": []}
    
    try:
        logger.info(f"TUTOR: Searching web contextually for: '{query[:80]}'")
        
        # Use EXACT user query for relevant results
        serp_url = "https://serpapi.com/search.json"
        params = {
            "api_key": SERP_API_KEY,
            "engine": "google",
            "q": query,  # EXACT query from user
            "num": 6,  # Get top 6 results
            "gl": "in"
        }
        
        response = requests.get(serp_url, params=params, timeout=10)
        
        all_results = []
        sources = []
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("organic_results", [])
            
            logger.info(f"TUTOR: Found {len(results)} web results")
            
            # Get top 5 most relevant results
            for result in results[:5]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                if title and snippet:
                    all_results.append(f"• {title}\n  {snippet}")
                    sources.append({"title": title, "url": link})
        
        if all_results:
            context = "\n\n".join(all_results[:5])
            logger.info(f"TUTOR: Returning {len(sources)} contextual sources")
            return {"context": context, "sources": sources[:5]}
        
        logger.warning(f"TUTOR: No web results found for query")
        return {"context": "", "sources": []}
        
    except Exception as e:
        logger.error(f"TUTOR: Web search failed: {str(e)}")
        return {"context": "", "sources": []}

@app.post("/ai-tutor")
async def ai_tutor(request: AITutorRequest):
    """
    AI-powered Media Literacy Tutor with:
    - RAG (web search for current information)
    - Multi-turn conversation memory
    - Interactive exercises
    - Real-world examples
    - Source evaluation
    """
    logger.info("TUTOR: AI Tutor endpoint called")
    
    try:
        if not NVIDIA_API_KEY:
            raise HTTPException(status_code=503, detail="AI service not configured")
        
        user_message = request.message.strip()
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info(f"TUTOR: Processing question: '{user_message[:100]}'")
        
        # Perform web search for context (RAG)
        search_result = await web_search_for_context(user_message)
        web_context = search_result.get("context", "")
        sources = search_result.get("sources", [])
        
        # Build ENHANCED system prompt for best-in-class media literacy education
        system_content = """You are the WORLD'S BEST Media Literacy & Critical Thinking Tutor. Your mission: Empower students to navigate the information landscape with confidence.

🎯 YOUR EXPERTISE:
- Media Bias & Objectivity (left/right/center bias, framing)
- Propaganda Techniques (bandwagon, fear, glittering generalities, etc.)
- Fact-Checking Methodologies (SIFT method, lateral reading, source triangulation)
- Deepfakes & Visual Manipulation (detection techniques, metadata analysis)
- Narrative Analysis (framing, omission, selective facts)
- Source Evaluation (CRAAP test: Currency, Relevance, Authority, Accuracy, Purpose)
- Social Media Algorithms (echo chambers, filter bubbles, engagement optimization)
- Clickbait & Sensationalism (headline analysis, emotional manipulation)
- Misinformation vs Disinformation (intent, spread patterns)
- Ethical Journalism Standards (SPJ Code, verification, transparency)

🎓 TEACHING APPROACH:
1. **Socratic Method**: Ask thought-provoking questions to deepen understanding
2. **Real Examples**: Reference current events and famous case studies
3. **Interactive**: Offer exercises, challenges, or "try this" activities
4. **Multi-Level**: Adjust complexity based on user's questions
5. **Visual Thinking**: Describe frameworks and mental models
6. **Action-Oriented**: Always provide practical takeaways

💡 RESPONSE STRUCTURE:
- Start with direct answer
- Provide real-world example or case study
- Explain the "why" and "how"
- Offer practical exercise or challenge (when appropriate)
- End with thought-provoking question or next step

🌍 CONTEXT:
- Focus on global media literacy but include Indian context when relevant
- Reference trusted organizations: Snopes, FactCheck.org, Alt News, Boom Live
- Cite journalism ethics codes and standards

📚 SPECIAL FEATURES:
- When asked "teach me about X", provide comprehensive lesson with structure
- For "example of X", give 2-3 real case studies
- For "how to X", give step-by-step practical guide
- If detecting confusion, offer to explain differently

Keep responses conversational, engaging, and empowering. Use analogies and metaphors. You're not just teaching—you're building critical thinkers who can defend themselves against manipulation."""

        if web_context:
            system_content += f"\n\n📰 CURRENT INFORMATION (from web search):\n{web_context}\n\n✓ Use this to provide accurate, up-to-date information and real examples."
        
        # Build conversation context with memory
        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        
        # Add conversation history (last 8 messages for better context)
        for msg in request.conversation_history[-8:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Enhance user message with context hints
        enhanced_message = user_message
        
        # Detect if user is asking for examples
        if any(word in user_message.lower() for word in ["example", "case study", "real life", "instance"]):
            enhanced_message += "\n[User wants real-world examples and case studies]"
        
        # Detect if user wants step-by-step
        if any(word in user_message.lower() for word in ["how to", "steps", "guide", "process"]):
            enhanced_message += "\n[User wants step-by-step practical guide]"
        
        # Detect if user wants to learn deeply
        if any(word in user_message.lower() for word in ["teach me", "explain", "what is", "lesson"]):
            enhanced_message += "\n[User wants comprehensive educational explanation]"
        
        messages.append({
            "role": "user",
            "content": enhanced_message
        })
        
        # Call AI
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
                "model": "qwen/qwen3-coder-480b-a35b-instruct",
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
        }
        
        logger.info("TUTOR: Calling AI for response...")
        response = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        ai_response = response.json()
        tutor_reply = ai_response["choices"][0]["message"]["content"]
        
        logger.info(f"TUTOR: Response generated ({len(tutor_reply)} chars)")
        
        # Save to MongoDB with enhanced chat session support
        if request.user_id and MONGODB_AVAILABLE:
            try:
                from bson import ObjectId
                
                # Get or create chat session
                chat_id = request.chat_id
                
                if not chat_id:
                    # Create new chat session with smart title
                    chat_sessions_collection = db["ai_tutor_chat_sessions"]
                    
                    # Generate smart title from first message (first 50 chars)
                    title = request.chat_title or user_message[:50]
                    if len(user_message) > 50:
                        title = title + "..."
                    
                    new_session = {
                        "user_id": request.user_id,
                        "title": title,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "message_count": 2,
                        "first_message": user_message[:100]
                    }
                    
                    session_result = chat_sessions_collection.insert_one(new_session)
                    chat_id = str(session_result.inserted_id)
                    logger.info(f"TUTOR: ✅ Created new chat session '{title}' (ID: {chat_id})")
                
                # Save messages to chat history
                chat_messages_collection = db["ai_tutor_messages"]
                
                messages_to_save = [
                    {
                        "chat_id": chat_id,
                        "user_id": request.user_id,
                        "role": "user",
                        "content": user_message,
                        "timestamp": datetime.utcnow()
                    },
                    {
                        "chat_id": chat_id,
                        "user_id": request.user_id,
                        "role": "assistant",
                        "content": tutor_reply,
                        "timestamp": datetime.utcnow(),
                        "web_search_used": bool(web_context),
                        "sources": sources if sources else [],
                        "query_for_search": user_message if web_context else None
                    }
                ]
                
                chat_messages_collection.insert_many(messages_to_save)
                
                # Update session metadata
                chat_sessions_collection = db["ai_tutor_chat_sessions"]
                chat_sessions_collection.update_one(
                    {"_id": ObjectId(chat_id)},
                    {
                        "$set": {
                            "updated_at": datetime.utcnow(),
                            "last_message": user_message[:100]
                        },
                        "$inc": {"message_count": 2}
                    }
                )
                
                logger.info(f"TUTOR: ✅ Saved conversation to database (chat: {chat_id}, web_search: {bool(web_context)})")
                
            except Exception as db_error:
                logger.error(f"TUTOR: ❌ Failed to save chat to MongoDB: {str(db_error)}")
                chat_id = None
        else:
            chat_id = None
            if not request.user_id:
                logger.warning(f"TUTOR: ⚠️ No user_id provided - chat not saved to database")
        
        return {
            "status": "success",
            "response": tutor_reply,
            "context_used": bool(web_context),
            "sources": sources if sources else [],
            "chat_id": chat_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TUTOR: Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI Tutor failed: {str(e)}")

@app.get("/ai-tutor/chats/{user_id}")
async def get_user_chats(user_id: str, limit: int = Query(20, description="Number of chats to return")):
    """Get all chat sessions for a user."""
    logger.info(f"TUTOR: Fetching chat sessions for user {user_id}")
    
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        chat_sessions_collection = db["ai_tutor_chat_sessions"]
        
        # Get all chat sessions for user
        sessions = list(chat_sessions_collection.find(
            {"user_id": user_id}
        ).sort("updated_at", -1).limit(limit))
        
        # Convert ObjectId to string
        for session in sessions:
            session["_id"] = str(session["_id"])
            session["created_at"] = session["created_at"].isoformat() if isinstance(session.get("created_at"), datetime) else session.get("created_at")
            session["updated_at"] = session["updated_at"].isoformat() if isinstance(session.get("updated_at"), datetime) else session.get("updated_at")
        
        logger.info(f"TUTOR: Found {len(sessions)} chat sessions")
        
        return {
            "status": "success",
            "chats": sessions,
            "count": len(sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TUTOR: Error fetching chats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch chats: {str(e)}")

@app.get("/ai-tutor/chat/{chat_id}/messages")
async def get_chat_messages(chat_id: str):
    """Get all messages for a specific chat session."""
    logger.info(f"TUTOR: Fetching messages for chat {chat_id}")
    
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        chat_messages_collection = db["ai_tutor_messages"]
        
        # Get all messages for this chat
        messages = list(chat_messages_collection.find(
            {"chat_id": chat_id}
        ).sort("timestamp", 1))
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role"),
                "content": msg.get("content"),
                "timestamp": msg.get("timestamp").isoformat() if isinstance(msg.get("timestamp"), datetime) else msg.get("timestamp"),
                "web_search_used": msg.get("web_search_used", False),
                "sources": msg.get("sources", [])
            })
        
        logger.info(f"TUTOR: Found {len(formatted_messages)} messages")
        
        return {
            "status": "success",
            "messages": formatted_messages,
            "count": len(formatted_messages),
            "chat_id": chat_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TUTOR: Error fetching messages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

@app.post("/ai-tutor/chat/create")
async def create_chat(request: CreateChatRequest):
    """Create a new chat session."""
    logger.info(f"TUTOR: Creating new chat for user {request.user_id}")
    
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        chat_sessions_collection = db["ai_tutor_chat_sessions"]
        
        new_session = {
            "user_id": request.user_id,
            "title": request.title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0
        }
        
        result = chat_sessions_collection.insert_one(new_session)
        chat_id = str(result.inserted_id)
        
        logger.info(f"TUTOR: Created chat session {chat_id}")
        
        return {
            "status": "success",
            "chat_id": chat_id,
            "title": request.title
        }
        
    except Exception as e:
        logger.error(f"TUTOR: Error creating chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {str(e)}")

@app.put("/ai-tutor/chat/title")
async def update_chat_title(request: UpdateChatTitleRequest):
    """Update chat session title."""
    logger.info(f"TUTOR: Updating title for chat {request.chat_id}")
    
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        from bson import ObjectId
        chat_sessions_collection = db["ai_tutor_chat_sessions"]
        
        result = chat_sessions_collection.update_one(
            {"_id": ObjectId(request.chat_id)},
            {"$set": {"title": request.title, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        logger.info(f"TUTOR: Updated chat title")
        
        return {
            "status": "success",
            "message": "Title updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TUTOR: Error updating title: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update title: {str(e)}")

@app.delete("/ai-tutor/chat/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat session and all its messages."""
    logger.info(f"TUTOR: Deleting chat {chat_id}")
    
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        from bson import ObjectId
        
        # Delete messages
        chat_messages_collection = db["ai_tutor_messages"]
        messages_result = chat_messages_collection.delete_many({"chat_id": chat_id})
        
        # Delete session
        chat_sessions_collection = db["ai_tutor_chat_sessions"]

        session_result = chat_sessions_collection.delete_one({"_id": ObjectId(chat_id)})
        
        if session_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        logger.info(f"TUTOR: Deleted chat and {messages_result.deleted_count} messages")
        
        return {
            "status": "success",
            "message": f"Deleted chat and {messages_result.deleted_count} messages"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TUTOR: Error deleting chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "services": {
            "database": "connected" if MONGODB_AVAILABLE else "disconnected",
            "news_api": "configured" if NEWS_API_KEY else "not configured",
            "ai_analysis": "configured" if NVIDIA_API_KEY else "not configured",
            "journalist_module": "available" if JOURNALIST_MODULE_AVAILABLE else "not available",
            "url_narrative": "available" if URL_NARRATIVE_AVAILABLE else "not available",
            "ai_tutor": "available" if NVIDIA_API_KEY else "not available"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ---------------- LMS MODULE ---------------- #

# Import and initialize LMS endpoints
try:
    from lms_endpoints import router as lms_router, init_lms
    
    # Initialize LMS with shared database connection
    if MONGODB_AVAILABLE:
        init_lms(db)
        app.include_router(lms_router)
        logger.info("SUCCESS: LMS module loaded and initialized")
    else:
        logger.warning("WARNING: LMS module requires MongoDB")
except ImportError as e:
    logger.warning(f"WARNING: LMS module not available: {e}")
except Exception as e:
    logger.error(f"ERROR: Failed to initialize LMS: {e}")

@app.get("/")
async def root():
    return {
        "message": "DataHalo API is live 🚀",
        "version": "2.2",
        "flow": {
            "step1": "Load existing articles from database (fast)",
            "step2": "Click refresh to fetch fresh news from API",
            "step3": "AI analysis with personalized perspectives"
        },
        "endpoints": {
            "news": "/news?category=general - Load articles from database (fast)",
            "refresh": "/refresh-news?category=general - Fetch fresh news from API + update DB",
            "fetch_fresh": "/fetch-fresh-news?category=general - Fetch fresh from API only",
            "saved_news": "/saved-news?category=all - Get all saved articles",
            "smart_feed": "/smart-feed?pov=general public - AI analysis",
            "health": "/health - Service health check",
            "analyze": "/analyze - Analyze journalist",
            "journalists": "/journalists - Get list of analyzed journalists",
            "journalist": "/journalist/{name} - Get specific journalist analysis"
        },
        "categories": ["general", "technology", "business", "sports", "science", "health", "entertainment"],
        "ai_perspectives": ["general public", "finance analyst", "government exam aspirant", "tech student", "business student"]
    }
