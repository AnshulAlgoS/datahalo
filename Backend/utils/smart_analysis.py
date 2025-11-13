# smart_analysis.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

if not NVIDIA_API_KEY:
    logger.error("❌ NVIDIA_API_KEY not found in environment!")
if not MONGO_URI:
    logger.error("❌ MONGO_URI not found in environment!")

# MongoDB setup
try:
    client = MongoClient(MONGO_URI)
    db = client["datahalo"]
    news_collection = db["news"]
    logger.info("✅ MongoDB connected for smart analysis")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None
    news_collection = None

# NVIDIA/OpenAI client
try:
    ai_client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    logger.info("✅ NVIDIA AI client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI client: {e}")
    ai_client = None

def get_perspective_prompt(pov):
    """Generate customized prompts based on perspective."""
    prompts = {
        "general public": {
            "system": "You are an experienced news analyst who specializes in explaining current events clearly for everyday citizens.",
            "instruction": "Focus on how these developments affect daily life, society, and the economy. Explain complex topics in accessible terms and highlight what matters most to ordinary people."
        },
        "finance analyst": {
            "system": "You are a seasoned financial analyst with expertise in market dynamics and economic trends.",
            "instruction": "Analyze market impacts, economic indicators, investment implications, and risks. Focus on sector performance, currency effects, policy impacts, and trading opportunities."
        },
        "government exam aspirant": {
            "system": "You are an expert in civil services preparation with deep knowledge of current affairs and their exam relevance.",
            "instruction": "Provide analysis suitable for UPSC, SSC, and other competitive exams. Include key facts, important dates, policy details, government schemes, notable personalities, and potential exam questions. Structure information for effective memorization and recall."
        },
        "tech student": {
            "system": "You are a technology industry expert who understands innovation trends and their implications for tech professionals.",
            "instruction": "Focus on technological developments, innovation trends, startup ecosystem updates, digital transformation, policy changes affecting tech, and emerging technologies. Explain technical concepts and their industry implications."
        },
        "business student": {
            "system": "You are a business strategy expert who analyzes market trends and entrepreneurial opportunities.",
            "instruction": "Analyze business opportunities, market dynamics, corporate strategies, regulatory changes, and entrepreneurial insights. Examine business models, competitive landscapes, and industry developments that affect business planning and strategy."
        }
    }
    
    return prompts.get(pov, prompts["general public"])

def smart_analyse(articles, pov="general public"):
    """
    Analyzes and summarizes given articles from a chosen point of view.
    Enhanced to provide clean, professional notes without AI-generated feel.
    """
    try:
        if not articles:
            return "No articles available for analysis."
        
        if not ai_client:
            return "AI analysis service is currently unavailable. Please check the configuration."

        # Prepare article content
        article_texts = []
        for i, article in enumerate(articles[:15], 1):  # Limit to 15 articles to avoid token limits
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            source = article.get('source', 'Unknown source')
            category = article.get('category', 'general')
            
            article_text = f"{i}. {title}\n   Source: {source} | Category: {category}\n   Summary: {description}\n"
            article_texts.append(article_text)

        combined_text = "\n".join(article_texts)
        
        # Get perspective-specific prompt
        prompt_config = get_perspective_prompt(pov.lower())
        
        # Enhanced prompt for natural, professional analysis
        user_prompt = f"""
        You are analyzing news for a {pov}. Write a comprehensive analysis in a clean, professional format without using markdown symbols, asterisks, or AI-generated language patterns.

        Based on these {len(articles)} news articles, provide your analysis in this exact format:

        EXECUTIVE SUMMARY
        Write a clear 3-4 sentence overview of the main developments and their significance for a {pov}.

        KEY DEVELOPMENTS
        List 5-7 most important points in simple numbered format (1. 2. 3. etc.) without any special formatting.

        DETAILED ANALYSIS
        Provide deeper insights specifically relevant to a {pov}. Focus on practical implications, opportunities, and challenges.

        IMPORTANT CONSIDERATIONS
        Highlight 3-4 critical factors that a {pov} should be aware of or monitor closely.

        CONCLUSION
        Summarize the overall outlook and key takeaways in 2-3 sentences.

        Articles to analyze:
        {combined_text}

        Remember: Write in a natural, professional tone. Avoid using asterisks, hashtags, markdown formatting, or phrases like "AI analysis" or "generated content". Make it sound like notes from an expert analyst.
        """

        # Send to NVIDIA API
        response = ai_client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": f"{prompt_config['system']} Write in clear, professional language without markdown formatting or AI-generated phrases. Focus on delivering valuable insights in a natural, human-like analytical style."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused, professional output
            max_tokens=2500,
        )

        analysis_content = response.choices[0].message.content.strip()
        
        # Clean up any remaining markdown or AI patterns
        analysis_content = analysis_content.replace("**", "")
        analysis_content = analysis_content.replace("*", "")
        analysis_content = analysis_content.replace("#", "")
        analysis_content = analysis_content.replace("AI analysis", "Analysis")
        analysis_content = analysis_content.replace("AI-generated", "Generated")
        analysis_content = analysis_content.replace("According to the AI", "According to the analysis")
        
        # Add professional header
        current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        perspective_title = pov.title()
        
        header = f"NEWS ANALYSIS FOR {perspective_title.upper()}\nGenerated on {current_time}\nBased on {len(articles)} recent articles\n\n"
        
        # Add separator line
        separator = "=" * 80 + "\n\n"
        
        final_analysis = header + separator + analysis_content
        
        logger.info(f"Analysis completed for {pov} perspective ({len(final_analysis)} characters)")
        return final_analysis

    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return f"Analysis could not be completed due to a technical error: {str(e)}\n\nPlease try again or contact support if the issue persists."

def test_smart_analysis():
    """Test function for smart analysis."""
    if not news_collection:
        logger.error("❌ Cannot test - database not available")
        return
    
    try:
        # Get some test articles
        test_articles = list(news_collection.find().limit(5))
        if not test_articles:
            logger.warning("⚠️ No test articles found in database")
            return
        
        # Test with different perspectives
        perspectives = ["general public", "finance analyst", "government exam aspirant"]
        
        for pov in perspectives:
            logger.info(f"🧪 Testing analysis for {pov}...")
            result = smart_analyse(test_articles, pov)
            logger.info(f"✅ {pov} analysis completed ({len(result)} characters)")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_smart_analysis()