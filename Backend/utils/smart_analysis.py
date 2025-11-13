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
    """Generate customized prompts based on perspective with enhanced focus."""
    prompts = {
        "general public": {
            "system": "You are a senior news analyst specializing in making complex news accessible to everyday citizens. Your analysis is clear, actionable, and focused on real-world impact.",
            "instruction": "Focus on practical implications for daily life, societal impact, and economic effects. Highlight what matters most to ordinary people, including opportunities, risks, and actionable insights.",
            "key_focus": [
                "How this affects everyday life and livelihood",
                "Economic impact on households and communities",
                "Social and cultural implications",
                "Public services and infrastructure changes",
                "Safety, health, and quality of life factors"
            ]
        },
        "finance analyst": {
            "system": "You are an expert financial analyst with deep expertise in market dynamics, economic indicators, and investment strategies. Your insights drive investment decisions.",
            "instruction": "Provide comprehensive financial analysis including market impacts, economic indicators, investment opportunities, risks, and sector-specific insights. Include quantitative assessments where relevant.",
            "key_focus": [
                "Market movements and sector performance",
                "Economic indicators and policy impacts",
                "Investment opportunities and risks",
                "Currency, commodity, and equity implications",
                "Corporate earnings and valuation impacts",
                "Trading strategies and portfolio considerations"
            ]
        },
        "government exam aspirant": {
            "system": "You are an expert in competitive exam preparation with extensive knowledge of current affairs, their exam relevance, and question patterns for UPSC, SSC, and other civil services exams.",
            "instruction": "Structure analysis for maximum exam utility. Include key facts, dates, names, government schemes, policy details, constitutional/legal aspects, and potential exam questions. Present information for effective memorization.",
            "key_focus": [
                "Key facts: dates, names, places, numbers",
                "Government schemes and policies",
                "Constitutional and legal aspects",
                "International relations and treaties",
                "Important personalities and their roles",
                "Potential MCQs and essay topics",
                "Connections to syllabus topics"
            ]
        },
        "tech student": {
            "system": "You are a technology industry expert tracking innovation trends, emerging technologies, and their implications for tech professionals and students.",
            "instruction": "Focus on technological developments, innovation patterns, startup ecosystem, digital transformation, tech policy, and emerging technologies. Explain technical concepts clearly and connect them to career opportunities.",
            "key_focus": [
                "Emerging technologies and innovation trends",
                "Startup ecosystem and funding news",
                "Tech policy and regulatory changes",
                "Industry hiring and skill demands",
                "Product launches and technical breakthroughs",
                "Digital transformation initiatives",
                "Learning opportunities and career paths"
            ]
        },
        "business student": {
            "system": "You are a business strategy consultant who analyzes market trends, competitive dynamics, and entrepreneurial opportunities for business students and aspiring entrepreneurs.",
            "instruction": "Analyze business opportunities, market dynamics, competitive strategies, regulatory environment, and entrepreneurial insights. Focus on strategic frameworks, case study angles, and business model analysis.",
            "key_focus": [
                "Market opportunities and business models",
                "Competitive analysis and industry structure",
                "Strategic moves by major players",
                "Regulatory changes affecting business",
                "Funding, M&A, and partnership trends",
                "Case study insights and frameworks",
                "Entrepreneurial lessons and opportunities"
            ]
        }
    }
    
    return prompts.get(pov, prompts["general public"])

def smart_analyse(articles, pov="general public"):
    """
    Enhanced smart analysis providing fast, accurate, comprehensive insights.
    Delivers professional analysis with key points, actionable notes, and structured format.
    """
    try:
        if not articles:
            return "No articles available for analysis."
        
        if not ai_client:
            return "AI analysis service is currently unavailable. Please check the configuration."

        # Prepare article content with enhanced metadata
        article_texts = []
        sources_set = set()
        categories_set = set()
        
        for i, article in enumerate(articles[:20], 1):  # Increased to 20 for better analysis
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            source = article.get('source', 'Unknown')
            category = article.get('category', 'general')
            published = article.get('publishedAt', '')
            
            sources_set.add(source)
            categories_set.add(category)
            
            article_text = f"[{i}] {title}\n    Source: {source} | Category: {category}\n    {description}\n"
            article_texts.append(article_text)

        combined_text = "\n".join(article_texts)
        
        # Get perspective-specific configuration
        prompt_config = get_perspective_prompt(pov.lower())
        focus_areas = "\n".join([f"  - {focus}" for focus in prompt_config['key_focus']])
        
        # Enhanced prompt for superior analysis quality
        user_prompt = f"""Analyze these {len(articles)} news articles from the perspective of a {pov}.

YOUR ANALYSIS FOCUS AREAS:
{focus_areas}

REQUIRED OUTPUT STRUCTURE (use clean formatting without markdown symbols):

EXECUTIVE SUMMARY
Write 3-4 powerful sentences capturing the essence of major developments and their critical significance for a {pov}. Make it compelling and insightful.

KEY HIGHLIGHTS
List 7-10 most important points in clear numbered format:
1. [First key point with specific details and context]
2. [Second key point with actionable insight]
... continue with concrete, valuable points

DEEP DIVE ANALYSIS
Provide comprehensive analysis specifically tailored for a {pov}:
- Connect multiple news items to reveal patterns and trends
- Explain WHY these developments matter (not just WHAT happened)
- Discuss implications, opportunities, and potential risks
- Include expert perspective and strategic insights
- Make complex topics clear and actionable

CRITICAL INSIGHTS
Highlight 5-6 crucial factors a {pov} must understand:
1. [Insight with specific reasoning]
2. [Insight with practical application]
... continue with high-value insights

ACTIONABLE TAKEAWAYS
Provide 4-5 specific actions or considerations:
- What should a {pov} do with this information?
- What opportunities should be explored?
- What risks should be monitored?
- What decisions should be informed by this analysis?

OUTLOOK & CONCLUSION
Summarize the overall situation, emerging trends, and key takeaways in 3-4 sentences. End with forward-looking perspective.

NEWS ARTICLES TO ANALYZE:
{combined_text}

ANALYSIS GUIDELINES:
- Be specific with facts, numbers, and examples
- Connect dots between different news items
- Avoid generic statements; provide unique insights
- Write naturally without AI phrases or markdown formatting
- Focus on accuracy, depth, and practical value
- Make every sentence count with meaningful information"""

        # Call NVIDIA API with optimized parameters for speed and quality
        logger.info(f"🚀 Starting AI analysis for {pov} ({len(articles)} articles)")
        
        response = ai_client.chat.completions.create(
            model="qwen/qwen2.5-coder-32b-instruct",  # Faster, higher quality model
            messages=[
                {
                    "role": "system", 
                    "content": f"{prompt_config['system']} Deliver exceptionally clear, accurate, and actionable analysis. Write like a senior analyst briefing stakeholders—professional, insightful, and value-packed. NO markdown formatting, NO asterisks, NO AI-generated language patterns."
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            temperature=0.3,  # Balanced for accuracy and creativity
            max_tokens=3500,  # Increased for comprehensive analysis
            top_p=0.85,  # Focused sampling for quality
        )

        analysis_content = response.choices[0].message.content.strip()
        
        # Post-processing for clean, professional output
        analysis_content = analysis_content.replace("**", "")
        analysis_content = analysis_content.replace("*", "")
        analysis_content = analysis_content.replace("###", "")
        analysis_content = analysis_content.replace("##", "")
        analysis_content = analysis_content.replace("#", "")
        analysis_content = analysis_content.replace("AI analysis", "Analysis")
        analysis_content = analysis_content.replace("AI-generated", "Professional")
        analysis_content = analysis_content.replace("According to the AI", "Analysis shows")
        analysis_content = analysis_content.replace("As an AI", "From analytical perspective")
        
        # Build professional header
        current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        perspective_title = pov.title()
        
        header = f"""
════════════════════════════════════════════════════════════════════════════════
                        NEWS INTELLIGENCE BRIEF
                    Perspective: {perspective_title}
════════════════════════════════════════════════════════════════════════════════

Generated: {current_time}
Sources: {len(sources_set)} news outlets
Articles Analyzed: {len(articles)}
Categories: {', '.join(sorted(categories_set))}

════════════════════════════════════════════════════════════════════════════════

"""
        
        footer = f"""

════════════════════════════════════════════════════════════════════════════════
                    End of Analysis | DataHalo News Intelligence
════════════════════════════════════════════════════════════════════════════════
"""
        
        final_analysis = header + analysis_content + footer
        
        logger.info(f"✅ Analysis completed successfully: {len(final_analysis)} chars, {len(sources_set)} sources")
        return final_analysis

    except Exception as e:
        logger.error(f"❌ Analysis error: {e}", exc_info=True)
        return f"""Analysis Error
════════════════════════════════════════════════════════════════════════════════

The analysis could not be completed due to a technical error.

Error Details: {str(e)}

Please try again in a few moments. If the issue persists, please contact support.

Troubleshooting Tips:
- Ensure you have selected a valid category with available articles
- Check your internet connection
- Try a different perspective or category
- Refresh the page and try again

════════════════════════════════════════════════════════════════════════════════"""

def test_smart_analysis():
    """Enhanced test function with multiple perspectives."""
    if not news_collection:
        logger.error("❌ Cannot test - database not available")
        return
    
    try:
        # Get test articles
        test_articles = list(news_collection.find().limit(10))
        if not test_articles:
            logger.warning("⚠️ No test articles found in database")
            return
        
        # Test with all perspectives
        perspectives = [
            "general public", 
            "finance analyst", 
            "government exam aspirant",
            "tech student",
            "business student"
        ]
        
        for pov in perspectives:
            logger.info(f"🧪 Testing analysis for {pov}...")
            start_time = datetime.now()
            
            result = smart_analyse(test_articles, pov)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ {pov} analysis completed in {duration:.2f}s ({len(result)} characters)")
            logger.info(f"📊 Preview: {result[:200]}...")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_smart_analysis()