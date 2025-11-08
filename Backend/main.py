from pathlib import Path
from dotenv import load_dotenv
import os
import logging

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Verify environment variable presence
logger.info(f"NVIDIA_API_KEY present: {bool(os.getenv('NVIDIA_API_KEY'))}")
logger.info(f"SERP_API_KEY present: {bool(os.getenv('SERP_API_KEY'))}")

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local imports
from utils.serp_scraper import fetch_journalist_data
from utils.ai_analysis import analyze_journalist

# Initialize app
app = FastAPI(title="DataHalo - Journalist Credibility API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class JournalistRequest(BaseModel):
    name: str

@app.post("/analyze")
async def analyze(request: JournalistRequest):
    """Analyze journalist's credibility using scraped data and AI analysis."""
    try:
        name = request.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")

        logger.info(f"🔍 Fetching journalist data for: {name}")
        data = await fetch_journalist_data(name)

        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {name}")

        if not data.get("articles"):
            raise HTTPException(status_code=404, detail=f"No articles found for {name}")

        logger.info(f"🧠 Found {len(data['articles'])} articles — sending to AI analysis...")
        analysis = analyze_journalist(name, data)

        return {
            "status": "success",
            "journalist": name,
            "articlesAnalyzed": len(data["articles"]),
            "aiProfile": analysis,
        }

    except HTTPException as he:
        logger.error(f"❌ HTTP Error: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/fetch")
async def fetch_articles(name: str):
    """Fetch journalist articles without AI analysis."""
    try:
        if not name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        data = await fetch_journalist_data(name)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {name}")
        return data
    except HTTPException as he:
        raise
    except Exception as e:
        logger.error(f"❌ Fetch Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "DataHalo API is live 🚀"}

