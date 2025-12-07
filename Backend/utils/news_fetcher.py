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
    logger.info("SUCCESS: MongoDB connected successfully")
except Exception as e:
    logger.error(f"ERROR: MongoDB connection failed: {e}")
    client = None
    db = None
    news_collection = None

def fetch_news(category="general", language="en", page_size=30, country="in"):
    """Fetch latest news and APPEND to database (don't delete old articles)."""
    if not NEWS_API_KEY:
        logger.error("ERROR: NEWS_API_KEY not configured")
        return {"count": 0, "articles": [], "error": "API key not configured"}
    
    if news_collection is None:
        logger.error("ERROR: Database not available")
        return {"count": 0, "articles": [], "error": "Database not available"}

    logger.info(f"WEB: Fetching fresh {category} news from NewsData.io")

    # NewsData.io API - different from NewsAPI.org!
    # Map categories to NewsData.io format
    category_map = {
        "general": "top",
        "business": "business",
        "technology": "technology",
        "entertainment": "entertainment",
        "health": "health",
        "science": "science",
        "sports": "sports"
    }
    
    newsdata_category = category_map.get(category, "top")
    
    # NewsData.io latest endpoint
    url = f"https://newsdata.io/api/1/latest"
    params = {
        "apikey": NEWS_API_KEY,
        "language": language,
        "category": newsdata_category,
        "country": country,
        "size": min(page_size, 10)
    }
    
    articles = []
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            results = data.get("results", [])
            logger.info(f"NEWS: Got {len(results)} articles from NewsData.io")
            
            # Convert NewsData.io format to our format
            for item in results:
                if not item.get("title") or not item.get("link"):
                    continue
                    
                articles.append({
                    "title": item["title"],
                    "description": item.get("description", ""),
                    "url": item["link"],
                    "image": item.get("image_url"),
                    "source": {"name": item.get("source_id", "Unknown")},
                    "publishedAt": item.get("pubDate"),
                    "content": item.get("content", "")
                })
        else:
            logger.error(f"ERROR: NewsData.io API error: {data}")
            return {"count": 0, "articles": [], "error": data.get("message", "API error")}
            
    except Exception as e:
        logger.error(f"ERROR: NewsData.io request failed: {e}")
        return {"count": 0, "articles": [], "error": f"API request failed: {str(e)}"}

    if not articles:
        logger.warning("WARNING: No articles found from NewsData.io")
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
                "image": item.get("image"),
                "source": item.get("source", {}).get("name", "Unknown"),
                "publishedAt": item.get("publishedAt"),
                "category": category,
                "fetchedAt": datetime.utcnow(),
            }
            
            try:
                result = news_collection.insert_one(article)
                article["_id"] = str(result.inserted_id)
                new_articles.append(article)
                stored_count += 1
            except Exception as e:
                logger.error(f"ERROR: Failed to store article: {e}")
                continue

        logger.info(f"SUCCESS: Stored {stored_count} NEW {category} articles in DB (skipped {duplicate_count} duplicates)")
        
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
        logger.error(f"ERROR: Database operation failed: {e}")
        return {"count": 0, "articles": [], "error": f"Database error: {str(e)}"}

def refresh_news(category="general", language="en", page_size=30, country="in"):
    """
    Refresh news: Fetch fresh articles and append to existing ones.
    Returns all articles with newest at the top.
    """
    logger.info(f"REFRESH: Refreshing {category} news...")
    result = fetch_news(category, language, page_size, country)
    
    if result.get("status") == "success":
        logger.info(f"SUCCESS: Refresh complete: {result['count']} new articles added, {result['total_in_db']} total in DB")
    
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
            
        logger.info(f"DATA: Retrieved {len(articles)} saved articles for category: {category}")
        return articles
        
    except Exception as e:
        logger.error(f"ERROR: Error retrieving articles: {e}")
        return []

def clean_old_articles(days_to_keep=30):
    """
    Clean up old articles from database.
    Keeps articles from the last N days.
    """
    if news_collection is None:
        logger.error("ERROR: Database not available")
        return 0
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        result = news_collection.delete_many({"fetchedAt": {"$lt": cutoff_date}})
        deleted_count = result.deleted_count
        logger.info(f"CLEAN: Cleaned {deleted_count} articles older than {days_to_keep} days")
        return deleted_count
    except Exception as e:
        logger.error(f"ERROR: Error cleaning old articles: {e}")
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
        logger.info(f"STATS: Article counts by category: {counts}")
        return counts
    except Exception as e:
        logger.error(f"ERROR: Error getting article counts: {e}")
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
