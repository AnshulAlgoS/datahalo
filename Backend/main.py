from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
import requests
import os
import logging
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
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
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
    logger.info("✅ Connected to MongoDB successfully")
    MONGODB_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {str(e)}")
    client = None
    db = None
    news_collection = None
    journalist_collection = None
    MONGODB_AVAILABLE = False

# ---------------- JOURNALIST MODULE ---------------- #

# Try to import journalist analysis modules
try:
    from utils.serp_scraper import fetch_journalist_data
    from utils.ai_analysis import analyze_journalist

    JOURNALIST_MODULE_AVAILABLE = True
    logger.info("✅ Journalist analysis modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ Journalist modules not available: {e}")
    JOURNALIST_MODULE_AVAILABLE = False

class JournalistRequest(BaseModel):
    name: str

class NarrativeRequest(BaseModel):
    topic: str
    days: int = 30

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

        logger.info(f"🔍 Starting comprehensive analysis for: {name}")

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
                        logger.info(f"📚 Using cached analysis for: {name}")
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
        logger.info(f"🕷️ Fetching fresh data for: {name}")
        scraped_data = await fetch_journalist_data(name)

        if not scraped_data or not scraped_data.get("articles"):
            raise HTTPException(status_code=404, detail=f"No articles found for {name}")

        logger.info(f"📊 Found {len(scraped_data['articles'])} articles for analysis")

        # Step 3: Run comprehensive AI analysis
        logger.info(f"🧠 Running AI analysis for: {name}")
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
            logger.info(f"💾 Saved analysis to database for: {name}")
        except Exception as db_error:
            logger.error(f"❌ Failed to save to database: {str(db_error)}")
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
        logger.error(f"❌ HTTP Error: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected Error during analysis: {str(e)}", exc_info=True)
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
        logger.error(f"❌ Fetch Error: {str(e)}", exc_info=True)
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
        logger.error(f"❌ Error retrieving journalists: {str(e)}")
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
        logger.error(f"❌ Error retrieving journalist: {str(e)}")
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
        
        logger.info(f"📚 Retrieved {len(articles)} '{category}' articles from database")
        
        return {
            "status": "success",
            "category": category,
            "source": "database",
            "count": len(articles),
            "articles": articles,
            "message": f"Loaded {len(articles)} articles from database (newest first)"
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve news from database")

@app.get("/refresh-news")
async def refresh_news_endpoint(category: str = Query("general", description="Category to refresh")):
    """
    Refresh news: Fetch fresh articles from API and APPEND to database.
    Returns ALL articles for category sorted by newest first.
    """
    try:
        logger.info(f"🔄 Refresh requested for '{category}' category...")
        
        # Use the enhanced refresh function that appends new articles
        result = refresh_news_fetcher(category=category, page_size=30)
        
        if result.get("status") != "success":
            error_msg = result.get("error", "Unknown error")
            raise HTTPException(status_code=500, detail=error_msg)
        
        logger.info(f"✅ Refresh complete: {result['count']} new articles, {result['total_in_db']} total in DB")
        
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
        logger.error(f"❌ Error during refresh: {str(e)}", exc_info=True)
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
        logger.error(f"❌ Error retrieving saved news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve saved news")

@app.post("/smart-feed")
async def get_smart_feed(pov: str = Query("general public", description="Perspective like finance, student, exam, etc.")):
    """Generate AI-powered smart feed based on saved articles and perspective."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get recent articles from database
        articles = list(news_collection.find().sort("fetchedAt", -1).limit(20))

        if not articles:
            # Try to fetch some news first
            logger.info("No articles found, fetching fresh news...")
            await get_news("general")
            articles = list(news_collection.find().sort("fetchedAt", -1).limit(20))

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

        logger.info(f"🧠 Analyzing {len(article_data)} articles for perspective: {pov}")
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
        logger.error(f"❌ Smart feed error: {str(e)}", exc_info=True)
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
        
        logger.info(f"🔍 Analyzing narrative for topic: '{topic}' over {days} days")
        
        # Calculate date range
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Search for articles related to the topic (more flexible search)
        # Split topic into keywords for better matching
        keywords = topic.lower().split()
        regex_patterns = [{"title": {"$regex": word, "$options": "i"}} for word in keywords]
        regex_patterns.extend([{"description": {"$regex": word, "$options": "i"}} for word in keywords])
        
        query = {
            "$or": regex_patterns,
            "fetchedAt": {"$gte": start_date, "$lte": end_date}
        }
        
        articles = list(news_collection.find(query).sort("fetchedAt", -1).limit(200))
        
        logger.info(f"📊 Found {len(articles)} articles in database for '{topic}'")
        
        if len(articles) < 5:  # Need at least 5 articles for meaningful analysis
            # Try to fetch some relevant news from NewsAPI with multiple search strategies
            logger.info(f"Insufficient articles ({len(articles)}), fetching from NewsAPI...")
            
            search_queries = [topic]
            # Add variations for better results
            if len(keywords) > 1:
                search_queries.append(" OR ".join(keywords))
                search_queries.append(keywords[0])  # Try primary keyword alone
            
            fetched_count = 0
            for search_query in search_queries:
                if fetched_count >= 20:  # Stop if we have enough
                    break
                    
                try:
                    url = "https://newsapi.org/v2/everything"
                    params = {
                        "apiKey": NEWS_API_KEY,
                        "q": search_query,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 100,
                        "from": start_date.strftime("%Y-%m-%d"),
                        "to": end_date.strftime("%Y-%m-%d")
                    }
                    
                    logger.info(f"🌐 Searching NewsAPI with query: '{search_query}'")
                    response = requests.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("status") == "ok" and data.get("articles"):
                            logger.info(f"✅ NewsAPI returned {len(data['articles'])} articles")
                            
                            # Save articles to database
                            for item in data["articles"]:
                                if item.get("title") and item.get("url"):
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
                                    news_collection.update_one(
                                        {"url": article["url"]},
                                        {"$set": article},
                                        upsert=True
                                    )
                                    fetched_count += 1
                            
                            logger.info(f"💾 Saved {fetched_count} relevant articles")
                        else:
                            logger.warning(f"⚠️ NewsAPI status: {data.get('status')}, message: {data.get('message', 'No message')}")
                    else:
                        logger.error(f"❌ NewsAPI HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as fetch_error:
                    logger.error(f"❌ Failed to fetch from NewsAPI: {str(fetch_error)}")
                    
            # Re-query database after fetching
            articles = list(news_collection.find(query).sort("fetchedAt", -1).limit(200))
            logger.info(f"📊 After fetching: {len(articles)} total articles")
        
        if len(articles) < 3:
            # Still not enough articles - provide helpful error
            suggestions = []
            
            # Get some recent topics from database
            recent_articles = list(news_collection.find().sort("fetchedAt", -1).limit(50))
            recent_topics = set()
            for article in recent_articles:
                title = article.get("title", "")
                # Extract potential topics (simple extraction)
                words = title.split()
                for i, word in enumerate(words):
                    if len(word) > 5 and word[0].isupper():
                        if i < len(words) - 1:
                            topic_candidate = f"{word} {words[i+1]}"
                            recent_topics.add(topic_candidate)
            
            suggestions = list(recent_topics)[:5]
            
            raise HTTPException(
                status_code=404, 
                detail={
                    "message": f"Insufficient articles found for '{topic}' (found {len(articles)}). Try a broader search term or different topic.",
                    "suggestions": suggestions if suggestions else [
                        "Elections 2024",
                        "Economic Policy",
                        "Technology",
                        "Climate Change",
                        "Healthcare"
                    ],
                    "tip": "Try searching for broader topics like 'Elections', 'Economy', or 'Technology' for better results."
                }
            )
        
        # Prepare article data for AI analysis
        article_texts = []
        sources = set()
        dates = []
        
        for article in articles:
            article_texts.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "source": article.get("source", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
                "fetchedAt": article.get("fetchedAt")
            })
            sources.add(article.get("source", "Unknown"))
            if article.get("fetchedAt"):
                dates.append(article["fetchedAt"])
        
        logger.info(f"🧠 Sending {len(article_texts)} articles to AI for analysis...")
        
        # Build AI analysis prompt
        prompt = f"""You are an expert media analyst specializing in narrative patterns and propaganda detection.

Analyze the following {len(articles)} news articles about "{topic}" collected over the past {days} days.

TASK: Provide a comprehensive narrative analysis detecting patterns, trends, sentiment shifts, and manipulation indicators.

ARTICLES DATA:
{str(article_texts[:50])}

ANALYSIS REQUIREMENTS:

1. **Narrative Pattern** (Required):
   - Is coverage rising or declining?
   - What's the dominant trend (Rising, Stable, Declining, Volatile)?
   - Overall sentiment (Positive, Negative, Mixed, Neutral)
   - Intensity level (0-100%)

2. **Timeline Analysis** (5-7 key dates):
   - Date: [YYYY-MM-DD format]
   - Article count on that date
   - Sentiment on that date
   - Key events that day (2-3 specific events)

3. **Key Narratives** (Top 3-5):
   - Specific narrative/storyline being pushed
   - Frequency (how many times mentioned)
   - Sources promoting it
   - When it first appeared
   - When it peaked

4. **Manipulation Indicators**:
   - Coordinated timing: Do multiple outlets publish similar stories at same time?
   - Source clustering: Are only certain types of outlets covering this?
   - Sentiment uniformity: Is sentiment suspiciously uniform across sources?
   - Sudden spike: Was there an unnatural surge in coverage?
   - Explanation: WHY you detected manipulation (be specific)

5. **Context**:
   - Major events during this period (3-5 specific events with dates)
   - Related topics being covered
   - Potential triggers for this narrative

RESPONSE FORMAT (MUST BE VALID JSON):
{{
  "narrativePattern": {{
    "rising": true/false,
    "trend": "Rising/Stable/Declining/Volatile",
    "sentiment": "Positive/Negative/Mixed/Neutral",
    "intensity": 75
  }},
  "timeline": [
    {{
      "date": "2024-01-15",
      "count": 12,
      "sentiment": "Negative",
      "keyEvents": ["Event 1", "Event 2"]
    }}
  ],
  "keyNarratives": [
    {{
      "narrative": "Specific storyline being pushed",
      "frequency": 45,
      "sources": ["Source 1", "Source 2"],
      "firstAppeared": "2024-01-10",
      "peakDate": "2024-01-15"
    }}
  ],
  "manipulation_indicators": {{
    "coordinated_timing": true/false,
    "source_clustering": true/false,
    "sentiment_uniformity": true/false,
    "sudden_spike": true/false,
    "explanation": "Detailed explanation with specific examples"
  }},
  "context": {{
    "majorEvents": ["Event 1 (Date)", "Event 2 (Date)"],
    "relatedTopics": ["Topic 1", "Topic 2"],
    "potentialTriggers": ["Trigger 1", "Trigger 2"]
  }}
}}

Be extremely specific and cite actual article titles/dates. No speculation."""

        # Call NVIDIA AI API
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
                "max_tokens": 4000
            }
            
            logger.info("🤖 Calling NVIDIA AI API...")
            response = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            ai_response = response.json()
            content = ai_response["choices"][0]["message"]["content"]
            
            logger.info(f"✅ AI analysis received ({len(content)} characters)")
            
            # Extract JSON from response
            import json
            import re
            
            # Try to find JSON block
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                analysis_data = json.loads(json_match.group(0))
            else:
                analysis_data = json.loads(content)
            
            # Add metadata
            result = {
                "status": "success",
                "analysis": {
                    "topic": topic,
                    "timeframe": f"{days} days",
                    "totalArticles": len(articles),
                    "narrativePattern": analysis_data.get("narrativePattern", {}),
                    "timeline": analysis_data.get("timeline", [])[:10],  # Limit timeline
                    "keyNarratives": analysis_data.get("keyNarratives", [])[:5],  # Limit narratives
                    "manipulation_indicators": analysis_data.get("manipulation_indicators", {}),
                    "context": analysis_data.get("context", {})
                }
            }
            
            logger.info(f"✅ Narrative analysis complete for '{topic}'")
            return result
            
        except requests.exceptions.RequestException as api_error:
            logger.error(f"❌ AI API Error: {str(api_error)}")
            raise HTTPException(status_code=500, detail="AI analysis API error")
        except json.JSONDecodeError as json_error:
            logger.error(f"❌ JSON Parse Error: {str(json_error)}")
            logger.error(f"AI Response content: {content[:500]}")
            # Return basic analysis if AI fails
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
                    "keyNarratives": [],
                    "manipulation_indicators": {
                        "coordinated_timing": False,
                        "source_clustering": False,
                        "sentiment_uniformity": False,
                        "sudden_spike": False,
                        "explanation": "Analysis inconclusive - AI response parsing failed"
                    },
                    "context": {
                        "majorEvents": [],
                        "relatedTopics": [],
                        "potentialTriggers": []
                    }
                },
                "message": "Analysis completed with limited AI insights"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Narrative analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Narrative analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "services": {
            "database": "connected" if MONGODB_AVAILABLE else "disconnected",
            "news_api": "configured" if NEWS_API_KEY else "not configured",
            "ai_analysis": "configured" if NVIDIA_API_KEY else "not configured",
            "journalist_module": "available" if JOURNALIST_MODULE_AVAILABLE else "not available"
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