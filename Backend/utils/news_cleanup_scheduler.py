"""
Automatic News Cleanup Scheduler
Runs periodic cleanup of old news articles to keep database fresh
"""

import os
import logging
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("news_cleanup")

MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client["datahalo"]
    news_collection = db["news"]
    logger.info("MongoDB connected for cleanup scheduler")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    news_collection = None


def cleanup_old_news(days_old=7):
    """
    Delete news articles older than specified days.
    Default: 7 days to keep news fresh and relevant.
    """
    if not news_collection:
        logger.error("Cannot cleanup - database not available")
        return
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_iso = cutoff_date.isoformat()
        
        logger.info(f"=== AUTOMATIC CLEANUP STARTING ===")
        logger.info(f"Deleting articles older than {days_old} days (before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # Count articles before cleanup
        total_before = news_collection.count_documents({})
        old_count = news_collection.count_documents({"publishedAt": {"$lt": cutoff_iso}})
        
        logger.info(f"Total articles: {total_before}")
        logger.info(f"Articles to delete: {old_count}")
        
        if old_count == 0:
            logger.info("No old articles to delete. Database is fresh!")
            return
        
        # Delete old articles
        result = news_collection.delete_many({
            "publishedAt": {"$lt": cutoff_iso}
        })
        
        deleted_count = result.deleted_count
        total_after = news_collection.count_documents({})
        
        logger.info(f"Successfully deleted {deleted_count} old articles")
        logger.info(f"Remaining articles: {total_after}")
        logger.info(f"=== CLEANUP COMPLETED ===\n")
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")


def run_scheduler():
    """
    Run the cleanup scheduler.
    Cleans up old articles every 24 hours at 2 AM.
    """
    # Schedule cleanup every day at 2 AM
    schedule.every().day.at("02:00").do(cleanup_old_news)
    
    # Also schedule every 12 hours as backup
    schedule.every(12).hours.do(cleanup_old_news)
    
    logger.info("News cleanup scheduler started")
    logger.info("Scheduled tasks:")
    logger.info("  - Daily cleanup at 2:00 AM")
    logger.info("  - Backup cleanup every 12 hours")
    logger.info("  - Articles older than 7 days will be removed")
    
    # Run initial cleanup on startup
    logger.info("\nRunning initial cleanup on startup...")
    cleanup_old_news()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    logger.info("Starting News Cleanup Scheduler...")
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
