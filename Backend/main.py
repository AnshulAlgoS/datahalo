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

class URLNarrativeRequest(BaseModel):
    url: str

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

        # IMPROVED: More flexible search strategy
        # Strategy 1: Try exact phrase match first
        articles = list(news_collection.find({
            "$or": [
                {"title": {"$regex": topic, "$options": "i"}},
                {"description": {"$regex": topic, "$options": "i"}}
            ],
            "fetchedAt": {"$gte": start_date, "$lte": end_date}
        }).sort("fetchedAt", -1).limit(100))

        logger.info(f"📊 Strategy 1 (exact phrase): Found {len(articles)} articles")

        # Strategy 2: If not enough, try keyword matching (each word separately)
        if len(articles) < 10:
            keywords = [word.lower() for word in topic.split() if len(word) > 3]
            if keywords:
                # Create OR conditions for each keyword
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.extend([
                        {"title": {"$regex": keyword, "$options": "i"}},
                        {"description": {"$regex": keyword, "$options": "i"}}
                    ])

                articles_strategy2 = list(news_collection.find({
                    "$or": keyword_conditions,
                    "fetchedAt": {"$gte": start_date, "$lte": end_date}
                }).sort("fetchedAt", -1).limit(100))

                # Merge and deduplicate
                seen_urls = {a["url"] for a in articles}
                for article in articles_strategy2:
                    if article["url"] not in seen_urls:
                        articles.append(article)
                        seen_urls.add(article["url"])

                logger.info(f"📊 Strategy 2 (keywords): Added {len(articles_strategy2)} articles, total now {len(articles)}")

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

            logger.info(f"📊 Strategy 3: Trying category '{likely_category}' articles...")

            category_articles = list(news_collection.find({
                "category": likely_category,
                "fetchedAt": {"$gte": start_date, "$lte": end_date}
            }).sort("fetchedAt", -1).limit(50))

            # Add articles that might be relevant
            seen_urls = {a["url"] for a in articles}
            for article in category_articles:
                if article["url"] not in seen_urls:
                    # Check if article is somewhat relevant
                    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
                    if any(word.lower() in text for word in topic.split() if len(word) > 3):
                        articles.append(article)
                        seen_urls.add(article["url"])

            logger.info(f"📊 Strategy 3 (category): Total articles now {len(articles)}")

        # Strategy 4: If STILL not enough, fetch from NewsAPI
        if len(articles) < 5:
            logger.info(f"📊 Strategy 4: Fetching from NewsAPI...")

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

                response = requests.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") == "ok" and data.get("articles"):
                        logger.info(f"✅ NewsAPI returned {len(data['articles'])} articles")

                        seen_urls = {a["url"] for a in articles}
                        for item in data["articles"]:
                            if item.get("title") and item.get("url") and item["title"] != "[Removed]":
                                if item["url"] not in seen_urls:
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

                        logger.info(f"💾 After NewsAPI fetch: {len(articles)} total articles")
            except Exception as e:
                logger.error(f"❌ NewsAPI fetch failed: {str(e)}")

        # Final check
        if len(articles) < 3:
            logger.error(f"❌ Insufficient articles: only {len(articles)} found")

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

        logger.info(f"✅ Analysis ready with {len(articles)} articles")

        # Prepare article summaries for AI (limit to most relevant/recent 30)
        articles = articles[:30]
        article_summaries = []

        for article in articles:
            article_summaries.append({
                "title": article.get("title", ""),
                "description": article.get("description", "")[:200],  # Truncate long descriptions
                "source": article.get("source", "Unknown"),
                "date": article.get("publishedAt", "")[:10] if article.get("publishedAt") else "",
            })

        # Enhanced AI prompt with better structure
        prompt = f"""Analyze media narrative for: "{topic}"

Dataset: {len(articles)} articles from past {days} days

Sample Articles:
{chr(10).join([f"{i+1}. [{a['source']}] {a['title']}" for i, a in enumerate(article_summaries[:10])])}

Provide JSON analysis:

{{
  "narrativePattern": {{
    "rising": true/false,
    "trend": "Rising/Stable/Declining/Volatile",
    "sentiment": "Positive/Negative/Mixed/Neutral",
    "intensity": 0-100
  }},
  "timeline": [
    {{
      "date": "YYYY-MM-DD",
      "count": number,
      "sentiment": "sentiment",
      "keyEvents": ["event 1", "event 2"]
    }}
  ],
  "keyNarratives": [
    {{
      "narrative": "main storyline",
      "frequency": number,
      "sources": ["source1", "source2"],
      "firstAppeared": "YYYY-MM-DD",
      "peakDate": "YYYY-MM-DD"
    }}
  ],
  "manipulation_indicators": {{
    "coordinated_timing": true/false,
    "source_clustering": true/false,
    "sentiment_uniformity": true/false,
    "sudden_spike": true/false,
    "explanation": "detailed explanation"
  }},
  "context": {{
    "majorEvents": ["event 1", "event 2"],
    "relatedTopics": ["topic1", "topic2"],
    "potentialTriggers": ["trigger1", "trigger2"]
  }}
}}

Be specific and cite actual articles."""

        # Call AI
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
                "max_tokens": 3000
            }

            logger.info("🤖 Calling AI for analysis...")
            response = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            ai_response = response.json()
            content = ai_response["choices"][0]["message"]["content"]

            logger.info(f"✅ AI response received")

            # Parse JSON
            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                analysis_data = json.loads(json_match.group(0))
            else:
                analysis_data = json.loads(content)

            result = {
                "status": "success",
                "analysis": {
                    "topic": topic,
                    "timeframe": f"{days} days",
                    "totalArticles": len(articles),
                    "narrativePattern": analysis_data.get("narrativePattern", {}),
                    "timeline": analysis_data.get("timeline", [])[:8],
                    "keyNarratives": analysis_data.get("keyNarratives", [])[:5],
                    "manipulation_indicators": analysis_data.get("manipulation_indicators", {}),
                    "context": analysis_data.get("context", {})
                }
            }

            logger.info(f"✅ Narrative analysis complete for '{topic}'")
            return result

        except Exception as e:
            logger.error(f"❌ AI analysis failed: {str(e)}")
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
        logger.error(f"❌ Narrative analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ---------------- URL-NARRATIVE MODULE ---------------- #

# Try importing comprehensive URL narrative analyzer
try:
    from utils.url_narrative_analyzer import analyze_url_narrative
    URL_NARRATIVE_AVAILABLE = True
    logger.info("✅ URL narrative analyzer module loaded")
except ImportError as e:
    logger.warning(f"⚠️ URL narrative analyzer not available: {e}")
    URL_NARRATIVE_AVAILABLE = False

@app.post("/analyze-url-narrative")
async def analyze_url_narrative_endpoint(request: URLNarrativeRequest):
    """Analyze media narratives for a given URL."""
    logger.info(f"🎯 URL Narrative endpoint called with URL: {request.url}")
    
    try:
        if not URL_NARRATIVE_AVAILABLE:
            logger.error("❌ URL narrative analyzer module not available")
            raise HTTPException(status_code=503, detail="URL narrative analyzer module not available")
        
        url = request.url.strip()
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        logger.info(f"🔍 Starting URL narrative analysis for: '{url}'")
        
        # Use the comprehensive URL narrative analyzer
        result = await analyze_url_narrative(url, SERP_API_KEY, NVIDIA_API_KEY)
        
        logger.info(f"📊 Analysis result status: {result.get('status')}")
        
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
        
        logger.info(f"✅ URL narrative analysis complete")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ URL narrative analysis error: {str(e)}", exc_info=True)
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