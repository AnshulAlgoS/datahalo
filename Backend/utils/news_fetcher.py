import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client["datahalo"]
    news_collection = db["news"]
    logger.info("✅ MongoDB connected successfully")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None
    news_collection = None

def fetch_news(category="general", language="en", page_size=30):
    """Fetch latest news with auto-fallback and enhanced error handling."""
    if not NEWS_API_KEY:
        logger.error("❌ NEWS_API_KEY not configured")
        return {"count": 0, "articles": [], "error": "API key not configured"}
    
    if not news_collection:
        logger.error("❌ Database not available")
        return {"count": 0, "articles": [], "error": "Database not available"}

    logger.info(f"🌐 Fetching {category} news from NewsAPI")

    # 1️⃣ Try top-headlines first
    top_url = "https://newsapi.org/v2/top-headlines"
    top_params = {
        "apiKey": NEWS_API_KEY,
        "country": "in",
        "category": category,
        "language": language,
        "pageSize": page_size,
    }
    
    articles = []
    
    try:
        top_response = requests.get(top_url, params=top_params, timeout=10)
        top_response.raise_for_status()
        top_data = top_response.json()
        articles = top_data.get("articles", []) if top_data.get("status") == "ok" else []
        logger.info(f"📰 Got {len(articles)} articles from top-headlines")
    except Exception as e:
        logger.warning(f"⚠️ Top-headlines failed: {e}")

    # 2️⃣ Fallback to "everything" if no results
    if not articles:
        logger.info("🔄 Falling back to 'everything' search...")
        search_url = "https://newsapi.org/v2/everything"
        search_params = {
            "apiKey": NEWS_API_KEY,
            "q": category if category != "general" else "India news",
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")  # Last 7 days
        }
        try:
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            search_data = search_response.json()
            if search_data.get("status") == "ok":
                articles = search_data.get("articles", [])
                logger.info(f"📰 Got {len(articles)} articles from everything search")
            else:
                logger.error(f"❌ Fallback fetch failed: {search_data}")
                return {"count": 0, "articles": [], "error": "API fallback failed"}
        except Exception as e:
            logger.error(f"❌ Fallback request failed: {e}")
            return {"count": 0, "articles": [], "error": f"Fallback failed: {str(e)}"}

    if not articles:
        logger.warning("⚠️ No articles found from any source")
        return {"count": 0, "articles": [], "error": "No articles found"}

    # 3️⃣ Process and store articles
    stored_count = 0
    processed_articles = []
    
    try:
        # Clear old articles for this category
        delete_result = news_collection.delete_many({"category": category})
        logger.info(f"🗑️ Removed {delete_result.deleted_count} old {category} articles")
        
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
            
            try:
                news_collection.update_one(
                    {"url": article["url"]}, 
                    {"$set": article}, 
                    upsert=True
                )
                processed_articles.append(article)
                stored_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to store article: {e}")
                continue

        logger.info(f"✅ Stored {stored_count} {category} articles in DB")
        
        return {
            "count": stored_count, 
            "articles": processed_articles,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Database operation failed: {e}")
        return {"count": 0, "articles": [], "error": f"Database error: {str(e)}"}

def get_saved_articles(category="all", limit=50):
    """Get articles from MongoDB."""
    if not news_collection:
        return []
    
    try:
        query = {} if category == "all" else {"category": category}
        articles = list(news_collection.find(query).sort("fetchedAt", -1).limit(limit))
        
        # Convert ObjectId to string
        for article in articles:
            article["_id"] = str(article["_id"])
            
        logger.info(f"📚 Retrieved {len(articles)} saved articles")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Error retrieving articles: {e}")
        return []

if __name__ == "__main__":
    # Test the fetcher
    logger.info("🧪 Testing news fetcher...")
    result = fetch_news("technology", page_size=10)
    logger.info(f"Test result: {result['count']} articles fetched")