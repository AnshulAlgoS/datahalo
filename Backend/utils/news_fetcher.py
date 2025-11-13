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
    """Fetch latest news and APPEND to database (don't delete old articles)."""
    if not NEWS_API_KEY:
        logger.error("❌ NEWS_API_KEY not configured")
        return {"count": 0, "articles": [], "error": "API key not configured"}
    
    if news_collection is None:
        logger.error("❌ Database not available")
        return {"count": 0, "articles": [], "error": "Database not available"}

    logger.info(f"🌐 Fetching fresh {category} news from NewsAPI")

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

    # 3️⃣ Process and store NEW articles (append, don't replace)
    stored_count = 0
    new_articles = []
    duplicate_count = 0
    
    try:
        for item in articles:
            if not item.get("title") or not item.get("url") or item.get("title") == "[Removed]":
                continue
            
            # Check if article already exists
            existing = news_collection.find_one({"url": item["url"]})
            if existing:
                duplicate_count += 1
                continue  # Skip duplicates
                
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
                news_collection.insert_one(article)
                article["_id"] = str(article["_id"])  # Convert ObjectId to string
                new_articles.append(article)
                stored_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to store article: {e}")
                continue

        logger.info(f"✅ Stored {stored_count} NEW {category} articles in DB (skipped {duplicate_count} duplicates)")
        
        # Get all articles for this category sorted by newest first
        all_articles = get_saved_articles(category=category, limit=100)
        
        return {
            "count": stored_count,
            "new_articles": new_articles,
            "all_articles": all_articles,
            "total_in_db": len(all_articles),
            "duplicates_skipped": duplicate_count,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Database operation failed: {e}")
        return {"count": 0, "articles": [], "error": f"Database error: {str(e)}"}

def refresh_news(category="general", language="en", page_size=30):
    """
    Refresh news: Fetch fresh articles and append to existing ones.
    Returns all articles with newest at the top.
    """
    logger.info(f"🔄 Refreshing {category} news...")
    result = fetch_news(category, language, page_size)
    
    if result.get("status") == "success":
        logger.info(f"✅ Refresh complete: {result['count']} new articles added, {result['total_in_db']} total in DB")
    
    return result

def get_saved_articles(category="all", limit=100):
    """Get articles from MongoDB sorted by fetchedAt (newest first)."""
    if news_collection is None:
        return []
    
    try:
        query = {} if category == "all" else {"category": category}
        articles = list(
            news_collection
            .find(query)
            .sort("fetchedAt", -1)  # Sort by newest first
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for article in articles:
            article["_id"] = str(article["_id"])
            
        logger.info(f"📚 Retrieved {len(articles)} saved articles for category: {category}")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Error retrieving articles: {e}")
        return []

def clean_old_articles(days_to_keep=30):
    """
    Clean up old articles from database.
    Keeps articles from the last N days.
    """
    if news_collection is None:
        logger.error("❌ Database not available")
        return 0
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        result = news_collection.delete_many({"fetchedAt": {"$lt": cutoff_date}})
        deleted_count = result.deleted_count
        logger.info(f"🗑️ Cleaned {deleted_count} articles older than {days_to_keep} days")
        return deleted_count
    except Exception as e:
        logger.error(f"❌ Error cleaning old articles: {e}")
        return 0

def get_articles_count_by_category():
    """Get count of articles by category."""
    if news_collection is None:
        return {}
    
    try:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        results = list(news_collection.aggregate(pipeline))
        counts = {item["_id"]: item["count"] for item in results}
        logger.info(f"📊 Article counts by category: {counts}")
        return counts
    except Exception as e:
        logger.error(f"❌ Error getting article counts: {e}")
        return {}

if __name__ == "__main__":
    # Test the fetcher
    logger.info("🧪 Testing news fetcher...")
    
    # Test refresh functionality
    result = refresh_news("technology", page_size=10)
    logger.info(f"Test result: {result.get('count', 0)} new articles, {result.get('total_in_db', 0)} total")
    
    # Show article counts
    counts = get_articles_count_by_category()
    logger.info(f"Article counts: {counts}")
    
    # Test cleanup (keep last 30 days)
    # clean_old_articles(days_to_keep=30)