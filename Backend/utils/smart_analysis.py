# smart_analysis.py
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

if not NVIDIA_API_KEY:
    logger.error("ERROR: NVIDIA_API_KEY not found in environment!")
if not MONGO_URI:
    logger.error("ERROR: MONGO_URI not found in environment!")

# MongoDB setup
try:
    client = MongoClient(MONGO_URI)
    db = client["datahalo"]
    news_collection = db["news"]
    logger.info("SUCCESS: MongoDB connected for smart analysis")
except Exception as e:
    logger.error(f"ERROR: MongoDB connection failed: {e}")
    client = None
    db = None
    news_collection = None

# NVIDIA/OpenAI client
try:
    ai_client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    logger.info("SUCCESS: NVIDIA AI client initialized")
except Exception as e:
    logger.error(f"ERROR: Failed to initialize AI client: {e}")
    ai_client = None

def get_perspective_prompt(pov):
    """Generate customized prompts based on perspective."""
    prompts = {
        "general public": {
            "system": "You are a senior Indian news analyst who explains current affairs clearly and accurately. Write naturally as if briefing educated readers.",
            "focus": "Explain what's happening in India and globally, why it matters, and the real-world impact on citizens, economy, and society."
        },
        "journalism student": {
            "system": "You are a journalism professor analyzing how Indian media covers stories. Write naturally about media practices and techniques.",
            "focus": "Examine how Indian outlets frame stories, source information, construct narratives, and the journalistic standards demonstrated."
        },
        "finance analyst": {
            "system": "You are a financial analyst tracking Indian markets and economy. Write naturally about market movements and economic implications.",
            "focus": "Analyze market impacts, economic indicators, investment implications, and sector-specific insights relevant to India."
        },
        "government exam aspirant": {
            "system": "You are a UPSC/SSC exam coach explaining current affairs for competitive exams. Write naturally but comprehensively.",
            "focus": "Explain government policies, schemes, constitutional aspects, key facts, dates, and how topics connect to exam syllabus."
        },
        "tech student": {
            "system": "You are a tech industry analyst tracking innovation and digital India. Write naturally about technology trends.",
            "focus": "Cover tech developments, startup ecosystem, digital policies, emerging technologies, and career implications in India's tech sector."
        },
        "business student": {
            "system": "You are a business strategy consultant analyzing Indian market dynamics. Write naturally about business trends.",
            "focus": "Analyze business opportunities, market trends, competitive strategies, regulatory changes, and entrepreneurial insights in India."
        },
        "women commission": {
            "system": "You are the Chairperson of a State Women Commission focusing on women's safety, rights, welfare, and justice in India.",
            "focus": "Highlight gender impact, women's safety, legal protections, enforcement status, government schemes for women, and actionable steps for administration."
        },
        "economist": {
            "system": "You are an economist analyzing India’s macroeconomy, trade, inflation, employment, and sectoral performance.",
            "focus": "Explain fiscal/monetary policy signals, inflation trends, employment data, trade, investments, and sectoral impacts with India-specific metrics."
        },
        "ias officer": {
            "system": "You are an IAS officer focusing on governance, implementation, compliance, and service delivery.",
            "focus": "Emphasize administrative feasibility, inter-departmental coordination, implementation status, compliance risks, and citizen service outcomes."
        },
        "assistant commissioner of police": {
            "system": "You are an ACP focusing on law and order, policing outcomes, cybercrime, and enforcement challenges.",
            "focus": "Assess crime trends, enforcement effectiveness, resource needs, policy implications, cyber risks, and community policing actions."
        },
        "social worker": {
            "system": "You are a social worker focusing on welfare delivery, vulnerable communities, and grassroots impact.",
            "focus": "Identify social impact, gaps in welfare delivery, NGO-government partnerships, local challenges, and community-centric actions."
        },
        "block president": {
            "system": "You are a local block-level leader focusing on development schemes and citizen needs.",
            "focus": "Translate news into local development actions, scheme uptake, infrastructure status, and steps to improve local service delivery."
        }
    }
    
    return prompts.get(pov, prompts["general public"])

def _select_articles_for_pov(articles, pov):
    settings = {
        "government exam aspirant": {
            "allowed": {"general", "business", "technology", "science", "health"},
            "excluded": {"entertainment", "sports"},
            "caps": {"general": 18, "business": 14, "technology": 10, "science": 4, "health": 4},
            "max": 50,
        },
        "finance analyst": {
            "allowed": {"business", "technology", "science", "general", "health"},
            "excluded": {"entertainment", "sports"},
            "caps": {"business": 18, "technology": 12, "science": 10, "general": 10, "health": 8},
            "max": 50,
        },
        "tech student": {
            "allowed": {"technology", "science", "business", "general", "health"},
            "excluded": {"entertainment", "sports"},
            "caps": {"technology": 18, "science": 12, "business": 10, "general": 8, "health": 6},
            "max": 50,
        },
        "business student": {
            "allowed": {"business", "technology", "general", "science", "health"},
            "excluded": {"entertainment", "sports"},
            "caps": {"business": 18, "technology": 12, "general": 10, "science": 8, "health": 6},
            "max": 50,
        },
        "journalism student": {
            "allowed": {"general", "technology", "business", "science", "health", "sports", "entertainment"},
            "excluded": set(),
            "caps": {"general": 12, "technology": 8, "business": 8, "science": 6, "health": 6, "sports": 5, "entertainment": 5},
            "max": 50,
        },
        "general public": {
            "allowed": {"general", "technology", "business", "science", "health", "sports", "entertainment"},
            "excluded": set(),
            "caps": {"general": 14, "technology": 8, "business": 8, "science": 6, "health": 6, "sports": 5, "entertainment": 5},
            "max": 45,
        },
    }

    cfg = settings.get(pov.lower(), settings["general public"])

    def _article_dt(a):
        ts = a.get("fetchedAt")
        if ts:
            try:
                return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            except:
                pass
        ts = a.get("publishedAt")
        if ts:
            try:
                return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            except:
                pass
        return datetime.min

    dedup = {}
    for a in articles:
        u = a.get("url") or f"{a.get('title','')}:{a.get('source','')}"
        if u not in dedup:
            dedup[u] = a

    sorted_items = sorted(dedup.values(), key=_article_dt, reverse=True)

    buckets = {}
    for a in sorted_items:
        cat = (a.get("category") or "general").lower()
        if cat in cfg["excluded"]:
            continue
        if cfg["allowed"] and cat not in cfg["allowed"]:
            continue
        buckets.setdefault(cat, []).append(a)

    selected = []
    per_cat_taken = {k: 0 for k in cfg["caps"].keys()}
    for cat in cfg["allowed"]:
        cap = cfg["caps"].get(cat, 5)
        for a in buckets.get(cat, []):
            if per_cat_taken.get(cat, 0) >= cap:
                break
            selected.append(a)
            per_cat_taken[cat] = per_cat_taken.get(cat, 0) + 1
            if len(selected) >= cfg["max"]:
                break
        if len(selected) >= cfg["max"]:
            break

    if len(selected) < cfg["max"]:
        for cat, items in buckets.items():
            if len(selected) >= cfg["max"]:
                break
            for a in items:
                if len(selected) >= cfg["max"]:
                    break
                if a in selected:
                    continue
                selected.append(a)

    return selected

def smart_analyse(articles, pov="general public", region_context=None):
    """
    Analyze latest Indian news with in-depth, accurate insights.
    Natural language, no formulas, focused on current affairs.
    """
    try:
        # Auto-cleanup old articles
        auto_cleanup_on_analysis()
        
        if not articles:
            return "No articles available for analysis."
        
        if not ai_client:
            return "AI analysis service is currently unavailable."

        selected = _select_articles_for_pov(articles, pov)
        articles_to_analyze = selected
        total_articles = len(articles)
        
        logger.info(f"Analyzing {len(articles_to_analyze)} latest articles out of {total_articles} total")
        
        # Prepare articles with dates for context
        article_texts = []
        sources_set = set()
        categories_set = set()
        
        for i, article in enumerate(articles_to_analyze, 1):
            title = article.get('title', 'No title')
            description = article.get('description') or 'No description'  # Handle None
            source = article.get('source', 'Unknown')
            category = article.get('category', 'general')
            published = article.get('publishedAt', '')
            
            # Extract date for context
            try:
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                date_str = pub_date.strftime('%B %d, %Y')
            except:
                date_str = "Recent"
            
            sources_set.add(source)
            categories_set.add(category)
            
            # Truncate description (safely handle None)
            desc_truncated = description[:250] + "..." if description and len(description) > 250 else description
            
            article_text = f"[{i}] ({date_str}) {title}\n    Source: {source}\n    {desc_truncated}\n"
            article_texts.append(article_text)

        combined_text = "\n".join(article_texts)
        
        # Get perspective config
        prompt_config = get_perspective_prompt(pov.lower())
        
        # Natural, in-depth analysis prompt
        extra_focus = ""
        if pov.lower() == "government exam aspirant":
            extra_focus = "\nADDITIONAL INSTRUCTIONS FOR EXAM PREP:\n- Do not include entertainment or sports\n- Map topics to UPSC GS papers and key syllabus areas\n- Emphasize government schemes, constitutional articles, committees, reports, indices\n- Provide factual bullet points suitable for revision\n"
        elif pov.lower() == "women commission":
            extra_focus += "\nWOMEN-FOCUSED ACTION:\n- Prioritize incidents and developments related to women's safety and rights\n- Highlight legal protections, enforcement status, and gaps\n- Provide 4-6 clear administrative and policing action steps\n- Emphasize prevention, rapid response, survivor support, and accountability\n"
        elif pov.lower() == "assistant commissioner of police":
            extra_focus += "\nLAW & ORDER ACTION:\n- Focus on crime trends, hotspots, and enforcement effectiveness\n- Include cybercrime, fraud, and public safety updates\n- Provide 4-6 specific policing actions (deployment, surveillance, outreach, coordination)\n- Note FIR patterns, investigation progress, and resource needs\n"
        elif pov.lower() == "ias officer":
            extra_focus += "\nGOVERNANCE ACTION:\n- Emphasize implementation status of schemes and compliance risks\n- Identify inter-departmental coordination needs and bottlenecks\n- Provide 4-6 actionable administrative steps for service delivery improvement\n- Include monitoring metrics and citizen feedback mechanisms\n"
        elif pov.lower() == "economist":
            extra_focus += "\nECONOMY FOCUS:\n- Emphasize inflation, employment, trade, investment, sector performance\n- Link news to macro indicators and state-level implications\n- Provide 4-6 policy-relevant takeaways and risk signals\n"
        elif pov.lower() == "social worker":
            extra_focus += "\nWELFARE FOCUS:\n- Prioritize vulnerable groups, welfare delivery gaps, and local challenges\n- Provide 4-6 community-centric actions and NGO-government collaboration ideas\n- Emphasize health, education, and protection services\n"
        elif pov.lower() == "block president":
            extra_focus += "\nLOCAL DEVELOPMENT FOCUS:\n- Emphasize block/panchayat-level schemes and infrastructure status\n- Provide 4-6 citizen-facing actions to improve local service delivery\n- Include roads, water, electricity, health, and school improvements\n"

        if region_context:
            rc_state = (region_context.get("state") or "").strip()
            rc_district = (region_context.get("district") or "").strip()
            if rc_state or rc_district:
                local_line = "\nREGIONAL FOCUS:" \
                    + (f" Emphasize developments related to {rc_district}, " if rc_district else " ") \
                    + (f"{rc_state}." if rc_state else "") \
                    + " If limited local news, acknowledge and prioritize closest relevant Indian context (state-level, then national).\n"
                extra_focus += local_line

        user_prompt = f"""You are analyzing INDIAN current affairs for {pov}. Focus ONLY on news directly related to India - Indian politics, economy, society, policies, and India's international relations.{extra_focus}

WHAT TO COVER:
{prompt_config['focus']}

STRUCTURE WITH CLEAR HEADINGS AND BULLET POINTS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TODAY'S TOP DEVELOPMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

List 6-10 concise bullet points with facts, names, dates, and numbers.

• [Specific event with numbers/dates]
• [Policy decision and immediate impact]
• [Economic/market development]
• [Governance/regulatory update]
• [...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAJOR STORIES - IN DEPTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cover 4-6 significant INDIAN stories. For each:

[STORY TITLE]
• What happened (with dates, names, numbers)
• Why it happened (context/background)
• Impact on India (economy, citizens, policy)
• What to watch next

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY POINTS TO REMEMBER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

List 8-12 specific facts:

• [Fact with context]
• [Fact with context]
• [...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE BIG PICTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

List 5 bullet points connecting patterns and trends across stories.

• [Pattern/Trend]
• [Link between developments]
• [...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS FOR {pov.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

List 4-6 practical, audience-specific takeaways.

• [Direct relevance]
• [Actionable insight]
• [...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT TO WATCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

List 4-6 upcoming developments:

• [Specific event/decision/deadline]
• [Expected development]
• [...]

LATEST NEWS ARTICLES (sorted by date):
{combined_text}

CRITICAL INSTRUCTIONS:

1. INDIAN FOCUS ONLY:
   - ONLY analyze articles about India, Indian companies, Indian policies, Indian politics
   - Skip international news unless it directly impacts India
   - Skip cryptocurrency, foreign sports, foreign companies unless Indian angle
   - If most articles are not India-related, say "Limited Indian news available"

2. ACCURACY FIRST:
   - Only state facts explicitly mentioned in the articles
   - Do NOT make up dates, numbers, or details
   - If you're unsure, say "According to reports" or "Details unclear"
   - Check dates carefully - articles may be old

3. STRUCTURE:
   - Use the heading format with ━━━ separators
   - Use bullet points (•) throughout; keep items concise
   - NO markdown, NO stars, NO emojis

4. QUALITY:
   - Be specific with names, numbers, dates from articles
   - Explain WHY things matter, not just WHAT happened
   - Connect stories to show bigger trends
   - Write naturally, not like a template

If articles are old or not India-focused, acknowledge this and work with what's available."""

        # Call NVIDIA API
        logger.info(f"Starting AI analysis for {pov}")
        
        # Extended timeout and retry logic for comprehensive analysis
        max_retries = 3
        for attempt in range(max_retries):
            try:
                timeout_seconds = 300  # 5 minutes for comprehensive analysis
                logger.info(f"AI: Attempt {attempt + 1}/{max_retries} - calling NVIDIA API (timeout: {timeout_seconds}s)...")
                
                response = ai_client.chat.completions.create(
                    model="qwen/qwen3-coder-480b-a35b-instruct",
                    messages=[
                        {
                            "role": "system", 
                            "content": prompt_config['system'] + " Write naturally in flowing prose. NO templates, NO formulas, NO markdown. Write like a professional analyst writing for educated readers who want depth and accuracy."
                        },
                        {
                            "role": "user", 
                            "content": user_prompt
                        }
                    ],
                    temperature=0.4,
                    max_tokens=4500,
                    top_p=0.9,
                    timeout=timeout_seconds
                )
                logger.info("AI: Request completed successfully!")
                break  # Success
                
            except Exception as e:
                error_str = str(e).lower()
                if 'timeout' in error_str or 'timed out' in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"AI: Timeout on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.error(f"AI: All {max_retries} attempts timed out - using fallback analysis")
                        return generate_fallback_analysis(articles_to_analyze, pov)
                else:
                    logger.error(f"AI: Error on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(5)
                    else:
                        logger.error("AI: All retry attempts failed - using fallback")
                        return generate_fallback_analysis(articles_to_analyze, pov)

        analysis_content = response.choices[0].message.content.strip()
        
        # Clean up any formatting artifacts
        analysis_content = analysis_content.replace("**", "")
        analysis_content = analysis_content.replace("*", "")
        analysis_content = analysis_content.replace("###", "")
        analysis_content = analysis_content.replace("##", "")
        analysis_content = analysis_content.replace("#", "")
        
        # Remove emojis
        emoji_pattern = r'[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002600-\U000027BF\U0001F900-\U0001F9FF\U0001F1E0-\U0001F1FF]'
        import re
        analysis_content = re.sub(emoji_pattern, '', analysis_content)
        
        # Remove AI references
        analysis_content = analysis_content.replace("AI analysis", "Analysis")
        analysis_content = analysis_content.replace("AI-generated", "Professional")
        analysis_content = analysis_content.replace("According to the AI", "Analysis shows")
        analysis_content = analysis_content.replace("As an AI", "From an analytical perspective")
        
        # Build header
        current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        perspective_title = pov.title()
        
        analysis_scope = f"{len(articles_to_analyze)} latest articles"
        if total_articles > len(articles_to_analyze):
            analysis_scope += f" (from {total_articles} available)"
        
        from collections import Counter
        cat_counts = Counter([(a.get('category') or 'general') for a in articles_to_analyze])
        coverage = ", ".join([f"{k}: {v}" for k, v in sorted(cat_counts.items())])

        header = f"""
================================================================================================
                  CURRENT AFFAIRS ANALYSIS - INDIA
                  Perspective: {perspective_title}
================================================================================================

Generated: {current_time}
        Sources: {len(sources_set)} outlets | Analyzed: {analysis_scope}
        Category Coverage: {coverage}

Analysis of the latest Indian and global news with focus on Indian context,
policies, economy, politics, and society. Based on most recent articles.

================================================================================

"""
        
        footer = f"""

================================================================================
                    DataHalo Current Affairs Analysis
================================================================================
"""
        
        final_analysis = header + analysis_content + footer
        
        logger.info(f"Analysis complete: {len(final_analysis)} chars, {len(sources_set)} sources")
        return final_analysis

    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return f"""Analysis Error
================================================================================

Could not complete analysis due to technical error: {str(e)}

Please try again. If issue persists, contact support.

================================================================================"""

def cleanup_old_articles(days_old=7):
    """Delete articles older than specified days."""
    if news_collection is None:
        logger.error("Cannot cleanup - database not available")
        return 0
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        logger.info(f"Cleaning articles older than {days_old} days (before {cutoff_date.strftime('%Y-%m-%d')})")
        
        result = news_collection.delete_many({
            "fetchedAt": {"$lt": cutoff_date}
        })
        
        deleted_count = result.deleted_count
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} old articles")
        
        remaining = news_collection.count_documents({})
        logger.info(f"Remaining: {remaining} articles")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return 0


def auto_cleanup_on_analysis():
    """Auto cleanup before analysis."""
    try:
        deleted = cleanup_old_articles(days_old=7)
        if deleted > 0:
            logger.info(f"Auto-cleanup: Removed {deleted} old articles")
        return deleted
    except Exception as e:
        logger.error(f"Auto-cleanup error: {e}")
        return 0


def generate_fallback_analysis(articles, pov):
    """Generate a basic analysis without AI when API fails."""
    try:
        current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Group by category and source
        by_category = {}
        sources_set = set()
        
        for article in articles[:20]:  # Limit to 20 for fallback
            category = article.get('category', 'general')
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            sources_set.add(source)
            
            if category not in by_category:
                by_category[category] = []
            by_category[category].append({'title': title, 'source': source})
        
        # Build fallback report
        report = f"""
================================================================================
                  CURRENT AFFAIRS SUMMARY - INDIA
                  Perspective: {pov.title()}
================================================================================

Generated: {current_time}
Sources: {len(sources_set)} outlets | Analyzed: {len(articles)} articles
Status: Quick Summary (AI analysis temporarily unavailable)

================================================================================

TOP STORIES BY CATEGORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for category, items in sorted(by_category.items()):
            report += f"\n{category.upper()}\n" + "─" * 60 + "\n"
            for item in items[:5]:  # Top 5 per category
                report += f"• {item['title']}\n  ({item['source']})\n\n"
        
        report += """
================================================================================
NOTE: This is a basic summary. The full AI analysis is temporarily unavailable
due to high server load. Please try again in a few minutes for detailed insights.

Alternative: Use the individual article analyzer or narrative tracker for
specific stories that interest you.
================================================================================
"""
        
        return report
        
    except Exception as e:
        logger.error(f"Fallback analysis error: {e}")
        return f"Analysis temporarily unavailable. Please try again in a few minutes. Error: {str(e)}"


if __name__ == "__main__":
    logger.info("Smart analysis module loaded")
