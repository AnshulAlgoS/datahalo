from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any
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
        "https://datahalo.onrender.com",
        # Allow any Vercel preview deployments
        "https://*.vercel.app",
    ],
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

# Try importing enhanced article analyzer with AI
try:
    from utils.article_analyzer_v2 import analyze_article as article_analyzer_v2_func
    ARTICLE_ANALYZER_AVAILABLE = True
    logger.info("SUCCESS: Article analyzer V2 (Enhanced) module loaded")
except ImportError as e:
    logger.warning(f"WARNING: Enhanced analyzer not available, trying V1: {e}")
    try:
        from utils.article_analyzer import analyze_article as article_analyzer_v2_func
        ARTICLE_ANALYZER_AVAILABLE = True
        logger.info("SUCCESS: Article analyzer V1 (Basic) module loaded")
    except ImportError as e2:
        logger.warning(f"WARNING: Article analyzer not available: {e2}")
        ARTICLE_ANALYZER_AVAILABLE = False

@app.post("/analyze-article")
async def analyze_article(request: ArticleRequest):
    """
    Analyze article writing quality - JournalismATS with AI Enhancement
    Scores articles against professional journalism standards using:
    - Rule-based scoring (objectivity, sources, clarity)
    - AI-powered deep analysis (bias, framing, logic)
    - Confidence scoring and transparency
    """
    logger.info("INFO: Article analyzer endpoint called")
    
    try:
        if not ARTICLE_ANALYZER_AVAILABLE:
            logger.error("ERROR: Article analyzer module not available")
            raise HTTPException(status_code=503, detail="Article analyzer module not available")
        
        article_text = request.article.strip()
        
        if not article_text:
            raise HTTPException(status_code=400, detail="Article text is required")
        
        if len(article_text.split()) < 20:
            raise HTTPException(status_code=400, detail="Article too short - minimum 20 words required")
        
        logger.info(f"SEARCH: Analyzing article ({len(article_text.split())} words)")
        
        # Step 1: Run rule-based analysis (V2 with enhanced accuracy)
        result = article_analyzer_v2_func(article_text)
        
        logger.info(f"STATS: Rule-based analysis complete")
        
        # Check if result indicates an error
        if result.get("status") == "error":
            error_msg = result.get("message", "Unknown error")
            logger.error(f"Article analysis failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Step 2: Enhance with AI analysis if NVIDIA API is available and article is long enough
        if NVIDIA_API_KEY and len(article_text.split()) >= 50:
            try:
                logger.info("AI: Running AI-enhanced analysis...")
                ai_enhancement = await _ai_enhanced_analysis(
                    article_text, 
                    result['analysis']
                )
                
                # Merge AI insights
                if ai_enhancement:
                    result['analysis']['ai_insights'] = ai_enhancement
                    logger.info("SUCCESS: AI analysis integrated")
            except Exception as ai_error:
                logger.warning(f"WARNING: AI analysis failed (non-critical): {str(ai_error)}")
                # Continue without AI - rule-based analysis is still valid
        
        logger.info(f"SUCCESS: Article analysis complete - Score: {result['analysis']['overall_score']} (Confidence: {result['analysis'].get('confidence', 'N/A')})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Article analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def _ai_enhanced_analysis(article_text: str, basic_analysis: Dict) -> Dict:
    """
    Use NVIDIA AI to provide deeper analysis beyond rule-based scoring
    """
    # Limit article length for API
    article_preview = article_text[:2000] if len(article_text) > 2000 else article_text
    
    prompt = f"""You are an expert journalism professor. Analyze this article for nuanced issues that pattern matching might miss.

Article:
{article_preview}

Current Scores:
- Objectivity: {basic_analysis['score_breakdown']['objectivity']}/100
- Source Quality: {basic_analysis['score_breakdown']['source_quality']}/100
- Bias Control: {basic_analysis['score_breakdown']['bias_control']}/100

Provide a JSON analysis focusing on:

{{
  "framing_analysis": "How is the story framed? What perspective dominates?",
  "missing_perspectives": ["Which viewpoints are absent or underrepresented?"],
  "logical_issues": ["Any logical fallacies or weak reasoning?"],
  "contextual_concerns": ["What important context is missing?"],
  "credibility_assessment": "Overall assessment of article's credibility",
  "improvement_priority": "The #1 thing to fix first",
  "grade_justification": "Why this article deserves its current score"
}}

Be specific and cite examples from the article."""

    try:
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "top_p": 0.85,
            "max_tokens": 1000
        }

        response = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]

        # Parse JSON from response
        import json
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            ai_insights = json.loads(json_match.group(0))
            return ai_insights
        
        return {"note": "AI analysis completed but JSON parsing failed", "raw": content[:500]}
        
    except Exception as e:
        logger.error(f"AI enhancement error: {str(e)}")
        return None

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
async def refresh_news_endpoint(category: str = Query("general", description="Category to refresh")):
    """
    Refresh news: Fetch fresh articles from API and APPEND to database.
    Returns ALL articles for category sorted by newest first.
    """
    try:
        logger.info(f"REFRESH: Refresh requested for '{category}' category...")

        # Use the enhanced refresh function that appends new articles
        result = refresh_news_fetcher(category=category, page_size=30)

        if result.get("status") != "success":
            error_msg = result.get("error", "Unknown error")
            raise HTTPException(status_code=500, detail=error_msg)

        logger.info(f"SUCCESS: Refresh complete: {result['count']} new articles, {result['total_in_db']} total in DB")

        return {
            "status": "success",
            "category": category,
            "source": "refreshed",
            "new_articles_count": result["count"],
            "duplicates_skipped": result.get("duplicates_skipped", 0),
            "total_articles": result["total_in_db"],
            "articles": result["all_articles"],  # All articles, newest first
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Added {result['count']} new articles. Total: {result['total_in_db']}"
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
async def get_smart_feed(pov: str = Query("general public", description="Perspective like finance, student, exam, etc.")):
    """Generate AI-powered smart feed based on saved articles and perspective."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get ALL recent articles from database for comprehensive analysis
        articles = list(news_collection.find().sort("fetchedAt", -1))

        if not articles:
            # Try to fetch some news first
            logger.info("No articles found, fetching fresh news...")
            await get_news("general")
            articles = list(news_collection.find().sort("fetchedAt", -1))

        if not articles:
            raise HTTPException(status_code=404, detail="No news articles found in database. Please fetch news first.")

        # Convert MongoDB documents to dict for AI analysis
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

        logger.info(f"ANALYZE: Analyzing {len(article_data)} articles for perspective: {pov}")
        summary = smart_analyse(article_data, pov)

        return {
            "status": "success",
            "perspective": pov,
            "articlesAnalyzed": len(article_data),
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

        # IMPROVED: More flexible search strategy
        # Strategy 1: Try exact phrase match first
        articles = list(news_collection.find({
            "$or": [
                {"title": {"$regex": topic, "$options": "i"}},
                {"description": {"$regex": topic, "$options": "i"}}
            ],
            "fetchedAt": {"$gte": start_date, "$lte": end_date}
        }).sort("fetchedAt", -1).limit(100))

        logger.info(f"STATS: Strategy 1 (exact phrase): Found {len(articles)} articles")

        # Strategy 2: If not enough, try keyword matching with better relevance
        if len(articles) < 10:
            # Extract keywords but keep minimum word length reasonable
            keywords = [word.lower() for word in topic.split() if len(word) > 2]
            
            if len(keywords) >= 2:
                # IMPROVED: For multi-word topics, require ALL keywords to match (AND logic)
                # This prevents "vit bhopal" from matching random "vit" or "bhopal" articles
                and_conditions = []
                for keyword in keywords:
                    and_conditions.append({
                        "$or": [
                            {"title": {"$regex": keyword, "$options": "i"}},
                            {"description": {"$regex": keyword, "$options": "i"}}
                        ]
                    })
                
                articles_strategy2 = list(news_collection.find({
                    "$and": and_conditions,  # Changed from OR to AND - requires ALL keywords
                    "fetchedAt": {"$gte": start_date, "$lte": end_date}
                }).sort("fetchedAt", -1).limit(100))
            elif len(keywords) == 1:
                # For single keyword, use OR logic (as before)
                articles_strategy2 = list(news_collection.find({
                    "$or": [
                        {"title": {"$regex": keywords[0], "$options": "i"}},
                        {"description": {"$regex": keywords[0], "$options": "i"}}
                    ],
                    "fetchedAt": {"$gte": start_date, "$lte": end_date}
                }).sort("fetchedAt", -1).limit(100))
            else:
                articles_strategy2 = []

            # Merge and deduplicate (FIXED: moved outside the else block)
            seen_urls = {a["url"] for a in articles}
            added_count = 0
            for article in articles_strategy2:
                if article["url"] not in seen_urls:
                    articles.append(article)
                    seen_urls.add(article["url"])
                    added_count += 1

            logger.info(f"STATS: Strategy 2 (ALL keywords must match): Found {len(articles_strategy2)} relevant, added {added_count} new, total now {len(articles)}")
            
            if len(keywords) >= 2:
                logger.info(f"SUCCESS: Using AND logic for {keywords} - requires ALL keywords in article")

        # Strategy 3: If still not enough, get recent articles from related categories
        if len(articles) < 5:
            # Determine likely category from topic
            category_map = {
                "election": "general",
                "vote": "general",
                "politic": "general",
                "government": "general",
                "economy": "business",
                "market": "business",
                "stock": "business",
                "tech": "technology",
                "ai": "technology",
                "health": "health",
                "medical": "health",
                "sport": "sports",
                "climate": "science",
                "environment": "science"
            }

            likely_category = "general"
            topic_lower = topic.lower()
            for key, cat in category_map.items():
                if key in topic_lower:
                    likely_category = cat
                    break

            logger.info(f"STATS: Strategy 3: Trying category '{likely_category}' articles...")

            category_articles = list(news_collection.find({
                "category": likely_category,
                "fetchedAt": {"$gte": start_date, "$lte": end_date}
            }).sort("fetchedAt", -1).limit(50))

            # Add articles that might be relevant with better scoring
            seen_urls = {a["url"] for a in articles}
            keywords = [word.lower() for word in topic.split() if len(word) > 2]
            
            for article in category_articles:
                if article["url"] not in seen_urls:
                    # IMPROVED: Check if article matches MULTIPLE keywords (more relevant)
                    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
                    matches = sum(1 for word in keywords if word in text)
                    
                    # Require at least 2 keywords to match (or all if only 1-2 keywords total)
                    required_matches = min(2, len(keywords))
                    if matches >= required_matches:
                        articles.append(article)
                        seen_urls.add(article["url"])

            logger.info(f"STATS: Strategy 3 (category): Total articles now {len(articles)}")

        # Strategy 4: If STILL not enough, fetch from NewsAPI
        if len(articles) < 5:
            logger.info(f"STATS: Strategy 4: Fetching from NewsAPI for '{topic}'...")

            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "apiKey": NEWS_API_KEY,
                    "q": topic,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 100,
                    "from": start_date.strftime("%Y-%m-%d"),
                }

                logger.info(f"API: Calling NewsAPI with query: '{topic}' from {start_date.strftime('%Y-%m-%d')}")
                response = requests.get(url, params=params, timeout=15)
                
                logger.info(f"API: NewsAPI response status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "ok":
                        raw_articles = data.get("articles", [])
                        logger.info(f"SUCCESS: NewsAPI returned {len(raw_articles)} raw articles")

                        seen_urls = {a["url"] for a in articles}
                        keywords = [word.lower() for word in topic.split() if len(word) > 2]
                        logger.info(f"SEARCH: Keywords for relevance check: {keywords}")
                        
                        relevant_count = 0
                        filtered_count = 0
                        
                        for item in raw_articles:
                            if item.get("title") and item.get("url") and item["title"] != "[Removed]":
                                if item["url"] not in seen_urls:
                                    # IMPROVED: Verify relevance before adding
                                    text = f"{item['title']} {item.get('description', '')}".lower()
                                    matches = sum(1 for word in keywords if word in text)
                                    
                                    # For 3+ keywords, require at least 2 to match
                                    # For 2 keywords, require both to match
                                    # For 1 keyword, require it to match
                                    required_matches = max(1, min(2, len(keywords)))
                                    
                                    if matches >= required_matches:
                                        relevant_count += 1
                                        article = {
                                            "title": item["title"],
                                            "description": item.get("description", ""),
                                            "url": item["url"],
                                            "image": item.get("urlToImage"),
                                            "source": item.get("source", {}).get("name", "Unknown"),
                                            "publishedAt": item.get("publishedAt"),
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
                                        seen_urls.add(article["url"])
                                    else:
                                        filtered_count += 1

                        logger.info(f"SUCCESS: NewsAPI: {relevant_count} relevant articles added, {filtered_count} filtered out")
                        logger.info(f"SAVE: After NewsAPI fetch: {len(articles)} total articles")
                    else:
                        logger.error(f"ERROR: NewsAPI error: {data.get('message', 'Unknown error')}")
                else:
                    logger.error(f"ERROR: NewsAPI HTTP error: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                logger.error(f"ERROR: NewsAPI fetch failed: {str(e)}", exc_info=True)

        # Strategy 5: If STILL insufficient, use SERP API to scrape Google News
        if len(articles) < 3 and SERP_API_KEY:
            logger.info(f"STATS: Strategy 5: Scraping Google News via SERP API for '{topic}'...")
            
            try:
                # Use SERP API to search Google News
                serp_url = "https://serpapi.com/search.json"
                serp_params = {
                    "api_key": SERP_API_KEY,
                    "engine": "google_news",
                    "q": topic,
                    "gl": "in",  # India region
                    "hl": "en",  # English language
                    "num": 50
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

        # INVESTIGATIVE AI prompt - expose manipulation, government actions, and hidden truths
        prompt = f"""You are an investigative journalist exposing media manipulation and government actions to wake up citizens.

INVESTIGATION: "{topic}"

DATA: {len(articles)} articles from {days} days

ARTICLES:
{articles_text}

YOUR MISSION - EXPOSE THE TRUTH:

1. **WHAT THEY'RE FEEDING YOU**: What narrative is media pushing? (cite articles)
2. **HOW THEY MANIPULATE**: What techniques are being used? Emotional language? Fear? Distraction?
3. **WHAT GOVERNMENT IS DOING**: What actions is govt taking on this? Laws? Policies? Silence?
4. **WHAT'S BEING HIDDEN**: What are they NOT telling you? What's being overshadowed?
5. **WHO BENEFITS**: Who profits from this narrative? Follow the money/power.
6. **THE REAL STORY**: What's actually happening vs what media wants you to believe?

Provide investigative JSON:

{{
  "media_feeding_you": {{
    "main_narrative": "What story is media feeding you? (cite Articles #X, #Y with quotes)",
    "emotional_angle": "Fear/Hope/Anger/Apathy - How are they making you feel?",
    "key_phrases": ["Repeated phrase from Articles #X, #Y", "Another manipulative phrase"],
    "spin_detected": "How is reality being twisted? Evidence from Articles #X, #Y",
    "coverage_level": "Heavy/Buried/Ignored - with evidence"
  }},
  
  "manipulation_tactics": {{
    "emotional_manipulation": "Fear-mongering? Hero worship? Cite Articles #X, #Y",
    "distraction_technique": "What big stories are drowning this out? Articles #X, #Y",
    "language_control": "Loaded words used: 'quotes from Articles #X, #Y'",
    "timing_games": "Why now? What else is happening? Cite evidence",
    "source_coordination": "Are outlets pushing same story? Articles #X, #Y, #Z same day/phrases",
    "omission_tactic": "What facts are being left out? Compare Articles #X vs #Y"
  }},
  
  "government_actions": {{
    "what_govt_doing": "Actual government actions mentioned in Articles #X, #Y",
    "policies_laws": "New laws/policies/decisions? Cite Articles #X, #Y",
    "official_statements": "What government said (Articles #X, #Y) vs reality",
    "enforcement_actions": "Police/courts/agencies involved? Articles #X, #Y",
    "govt_silence": "What is government NOT saying? What's absent from all articles?",
    "political_angle": "Which party/leader benefits? Evidence from Articles #X, #Y"
  }},
  
  "whats_hidden": {{
    "buried_facts": "Important data/facts only in Article #X but ignored elsewhere",
    "missing_voices": "Who is NOT being quoted? Which perspectives absent?",
    "convenient_timing": "What OTHER stories are overshadowing this? When did they break?",
    "censored_angles": "What aspects of '{topic}' are NOT being discussed at all?",
    "follow_the_money": "Financial interests not mentioned? Cite or infer"
  }},
  
  "who_benefits": {{
    "power_beneficiary": "Which politician/party/leader benefits from this narrative?",
    "financial_beneficiary": "Which companies/industries profit?",
    "evidence": "Cite Articles #X, #Y showing connections",
    "cui_bono_analysis": "Follow the money/power - who REALLY gains?"
  }},
  
  "reality_vs_narrative": {{
    "what_media_says": "Official narrative from Articles #X, #Y (with quotes)",
    "what_they_hide": "Reality not being told - evidence from Articles #X, #Y",
    "the_real_story": "What's ACTUALLY happening behind the narrative?",
    "why_the_spin": "Why is media spinning it this way? Who benefits?"
  }},
  
  "timeline": [
    {{
      "date": "YYYY-MM-DD",
      "count": number,
      "sentiment": "sentiment",
      "keyEvents": ["Headline from Article #X", "Headline from Article #Y"]
    }}
  ],
  
  "keyNarratives": [
    {{
      "narrative": "Storyline with quoted phrases from articles",
      "frequency": number,
      "sources": ["Source (Article #X)", "Source (Article #Y)"],
      "exampleHeadlines": ["Article #X: 'headline'", "Article #Y: 'headline'"]
    }}
  ],
  
  "manipulation_indicators": {{
    "coordinated_timing": true/false,
    "source_clustering": true/false,
    "sentiment_uniformity": true/false,
    "sudden_spike": true/false,
    "explanation": "Specific evidence with article numbers"
  }},
  
  "context": {{
    "majorEvents": ["Event from Article #X", "Event from Article #Y"],
    "relatedTopics": ["Topic with Article #", "Topic with Article #"],
    "potentialTriggers": ["Trigger from Article #X"],
    "missingPerspectives": ["Perspective absent from all articles"]
  }}
}}

EXPOSE EVERYTHING:
- CITE article numbers for EVERY claim
- QUOTE exact phrases showing manipulation
- NAME sources showing coordination
- Show government actions/inactions with evidence
- Reveal who BENEFITS (power/money)
- Help citizens SEE THROUGH THE LIES

CRITICAL: Return ONLY the JSON object above. No markdown, no ```json blocks, no text before or after. Start with {{ and end with }}. Pure JSON only."""

        # Call AI
        try:
            headers = {
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a data analyst. You MUST return ONLY valid JSON. No markdown, no explanations, no text outside JSON. Start with { and end with }. Every response must be pure JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "top_p": 0.9,
                "max_tokens": 4000
            }

            logger.info("AI: Calling AI for analysis...")
            response = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

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
                    
                    # INVESTIGATIVE ANALYSIS - Expose manipulation & government
                    "media_feeding_you": analysis_data.get("media_feeding_you", {}),
                    "manipulation_tactics": analysis_data.get("manipulation_tactics", {}),
                    "government_actions": analysis_data.get("government_actions", {}),
                    "whats_hidden": analysis_data.get("whats_hidden", {}),
                    "who_benefits": analysis_data.get("who_benefits", {}),
                    "reality_check": analysis_data.get("reality_vs_narrative", {}),  # Rename for frontend compatibility
                    
                    # Existing fields
                    "narrativePattern": analysis_data.get("narrativePattern", {}),
                    "timeline": analysis_data.get("timeline", [])[:8],
                    "keyNarratives": analysis_data.get("keyNarratives", [])[:5],
                    "manipulation_indicators": analysis_data.get("manipulation_indicators", {}),
                    "context": analysis_data.get("context", {})
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
            "url_narrative": "available" if URL_NARRATIVE_AVAILABLE else "not available"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "DataHalo API is live 🚀",
        "version": "2.1",
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