import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["datahalo"]
news_collection = db["news"]

def fetch_news(category="general"):
    """Fetch latest news from NewsAPI and save to MongoDB."""
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        return {"error": "Failed to fetch news"}

    articles = []
    for item in data.get("articles", []):
        article = {
            "title": item["title"],
            "description": item["description"],
            "url": item["url"],
            "image": item["urlToImage"],
            "source": item["source"]["name"],
            "publishedAt": item["publishedAt"],
            "category": category,
            "fetchedAt": datetime.utcnow(),
        }
        news_collection.insert_one(article)
        articles.append(article)

    return {"count": len(articles), "articles": articles}
