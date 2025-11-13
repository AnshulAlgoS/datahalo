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

app = FastAPI(title="DataHalo - Journalist Credibility & News API")

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

@app.post("/analyze")
async def analyze(request: JournalistRequest):
    """Analyze journalist's credibility using scraped data and comprehensive AI analysis."""
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
                "aiProfile.credibilityScore.score": 1,
                "aiProfile.digitalPresence.profileImage": 1,
                "aiProfile.mainTopics": 1
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

def fetch_and_store_news(category: str = "general", language: str = "en", page_size: int = 30):
    """
    Fetch latest news from NewsAPI with fallback to 'everything' if no top-headlines.
    Enhanced with better time filtering for fresh articles.
    """
    if not NEWS_API_KEY:
        raise HTTPException(status_code=500, detail="NEWS_API_KEY not configured")
    
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    logger.info(f"🌐 Fetching '{category}' news from NewsAPI")

    # Calculate time filters for fresh content
    from datetime import timedelta
    
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    three_days_ago = now - timedelta(days=3)

    # 1️⃣ Try top-headlines with time filtering
    top_url = "https://newsapi.org/v2/top-headlines"
    top_params = {
        "apiKey": NEWS_API_KEY,
        "country": "in",
        "category": category if category != "general" else None,  # Don't specify category for general
        "language": language,
        "pageSize": page_size,
    }
    
    # Remove None values
    top_params = {k: v for k, v in top_params.items() if v is not None}
    
    try:
        response = requests.get(top_url, params=top_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"📡 NewsAPI response status: {data.get('status')}")
    except Exception as e:
        logger.error(f"❌ API request failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch from NewsAPI")

    articles = data.get("articles", []) if data.get("status") == "ok" else []
    logger.info(f"📰 Got {len(articles)} articles from top-headlines")

    # 2️⃣ Enhanced fallback to "everything" with better search terms
    if len(articles) < 10:  # Try fallback if we have too few articles
        logger.info(f"🔄 Only {len(articles)} articles from top-headlines, enhancing with 'everything' search...")
        
        # Different search strategies based on category
        search_queries = {
            "general": ["India news", "breaking news India", "latest news India"],
            "technology": ["technology India", "tech news", "startup India", "AI technology"],
            "business": ["business India", "economy India", "market news", "finance India"],
            "sports": ["sports India", "cricket India", "football India", "Olympics"],
            "science": ["science news", "research India", "innovation", "space technology"],
            "health": ["health India", "medical news", "healthcare", "wellness"],
            "entertainment": ["entertainment India", "Bollywood", "movies", "celebrity news"]
        }
        
        search_terms = search_queries.get(category, ["India news", "breaking news"])
        
        search_url = "https://newsapi.org/v2/everything"
        
        # Try multiple search terms to get diverse articles
        fallback_articles = []
        for search_term in search_terms[:2]:  # Use first 2 search terms
            search_params = {
                "apiKey": NEWS_API_KEY,
                "q": search_term,
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": min(20, page_size),
                "from": yesterday.strftime("%Y-%m-%d"),  # Only articles from last 24 hours
                "domains": "timesofindia.indiatimes.com,indianexpress.com,hindustantimes.com,ndtv.com,news18.com" if category != "technology" else "techcrunch.com,gadgets360.com,livemint.com"
            }
            
            try:
                search_response = requests.get(search_url, params=search_params, timeout=10)
                search_response.raise_for_status()
                search_data = search_response.json()
                
                if search_data.get("status") == "ok":
                    new_articles = search_data.get("articles", [])
                    fallback_articles.extend(new_articles)
                    logger.info(f"📰 Got {len(new_articles)} articles from '{search_term}' search")
                    
                    if len(fallback_articles) >= page_size:
                        break
                        
            except Exception as e:
                logger.warning(f"⚠️ Search for '{search_term}' failed: {e}")
                continue
        
        # If still no articles, try without date restriction
        if not fallback_articles:
            logger.info("🔄 Trying without date restriction...")
            search_params = {
                "apiKey": NEWS_API_KEY,
                "q": search_terms[0],
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": page_size,
            }
            
            try:
                search_response = requests.get(search_url, params=search_params, timeout=10)
                search_response.raise_for_status()
                search_data = search_response.json()
                
                if search_data.get("status") == "ok":
                    fallback_articles = search_data.get("articles", [])
                    logger.info(f"📰 Got {len(fallback_articles)} articles without date restriction")
                    
            except Exception as e:
                logger.error(f"❌ Final fallback search failed: {e}")
        
        # Combine articles from both sources
        all_articles = articles + fallback_articles
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.get("url") not in seen_urls and article.get("url"):
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        articles = unique_articles[:page_size]  # Limit to requested size
        logger.info(f"📰 Final article count: {len(articles)} (after deduplication)")
    
    if not articles:
        logger.error("❌ No articles found from any source")
        raise HTTPException(status_code=404, detail="No articles found")

    # 3️⃣ Process and store articles
    formatted_articles = []
    for item in articles:
        if not item.get("title") or not item.get("url") or item.get("title") == "[Removed]":
            continue
        
        article = {
            "title": item["title"],
            "description": item.get("description", ""),
            "url": item["url"],
            "image": item.get("urlToImage"),
            "source": item.get("source", {}).get("name", "Unknown"),
            "publishedAt": item.get("publishedAt"),
            "category": category,
            "fetchedAt": datetime.utcnow(),
        }
        formatted_articles.append(article)

    # Replace old category data
    try:
        # Clear old articles for this category
        deleted_count = news_collection.delete_many({"category": category}).deleted_count
        logger.info(f"🗑️ Removed {deleted_count} old '{category}' articles")
        
        if formatted_articles:
            for article in formatted_articles:
                news_collection.update_one(
                    {"url": article["url"]}, 
                    {"$set": article}, 
                    upsert=True
                )
    except Exception as e:
        logger.error(f"❌ Database operation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save to database")

    logger.info(f"✅ Successfully stored {len(formatted_articles)} fresh '{category}' articles in DB")
    return {"count": len(formatted_articles), "articles": formatted_articles}

@app.get("/news")
async def get_news(category: str = Query("general", description="Category of news")):
    """Get saved news articles from MongoDB database (fast load)."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get articles from database only
        query = {} if category == "all" else {"category": category}
        articles = list(news_collection.find(query).sort("fetchedAt", -1).limit(30))
        
        # Convert MongoDB ObjectId to string
        for article in articles:
            article["_id"] = str(article["_id"])
        
        logger.info(f"📚 Retrieved {len(articles)} '{category}' articles from database")
        
        return {
            "status": "success",
            "category": category,
            "source": "database",
            "count": len(articles),
            "articles": articles,
            "message": f"Loaded {len(articles)} articles from database"
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve news from database")

@app.get("/fetch-fresh-news")
async def fetch_fresh_news(category: str = Query("general", description="Category to fetch fresh news")):
    """Fetch fresh news from NewsAPI and store in MongoDB (only when refresh is clicked)."""
    try:
        logger.info(f"🔄 User requested fresh '{category}' news from API...")
        
        # Fetch fresh news from API
        result = fetch_and_store_news(category)
        
        return {
            "status": "success",
            "category": category,
            "source": "fresh_api",
            "fetched": result["count"],
            "articles": result["articles"],
            "message": f"Fetched {result['count']} fresh articles from NewsAPI"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Error fetching fresh news: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch fresh news")

@app.get("/refresh-news")
async def refresh_news(category: str = Query("general", description="Category to refresh")):
    """Complete refresh flow: Fetch fresh news → Save to DB → Return updated articles."""
    try:
        logger.info(f"🔄 Complete refresh requested for '{category}' category...")
        
        # Step 1: Clear old cache (optional - removes articles older than 2 hours)
        deleted_count = 0
        if MONGODB_AVAILABLE:
            from datetime import timedelta
            two_hours_ago = datetime.utcnow() - timedelta(hours=2)
            
            deleted_count = news_collection.delete_many({
                "category": category,
                "fetchedAt": {"$lt": two_hours_ago}
            }).deleted_count
            
            logger.info(f"🗑️ Removed {deleted_count} cached '{category}' articles older than 2 hours")
        
        # Step 2: Fetch fresh news from API
        fresh_result = fetch_and_store_news(category, page_size=50)
        
        # Step 3: Get all current articles from database (including the fresh ones)
        query = {"category": category}
        all_articles = list(news_collection.find(query).sort("fetchedAt", -1).limit(50))
        
        # Convert ObjectId to string
        for article in all_articles:
            article["_id"] = str(article["_id"])
        
        logger.info(f"✅ Refresh complete: {fresh_result['count']} fresh articles fetched")
        
        return {
            "status": "success",
            "category": category,
            "source": "refreshed",
            "fresh_fetched": fresh_result["count"],
            "total_articles": len(all_articles),
            "articles": all_articles,
            "cleared_cache": deleted_count,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Refreshed with {fresh_result['count']} fresh articles"
        }
    except Exception as e:
        logger.error(f"❌ Error during refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh news")

@app.get("/saved-news")
async def get_saved_news(category: str = Query("all", description="Category filter")):
    """Get saved news articles from MongoDB."""
    try:
        if not MONGODB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        query = {} if category == "all" else {"category": category}
        articles = list(news_collection.find(query).sort("fetchedAt", -1).limit(50))
        
        # Convert MongoDB ObjectId to string
        for article in articles:
            article["_id"] = str(article["_id"])
        
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