"""
DataHalo AI Analysis Module
Comprehensive journalist profile and transparency analysis using NVIDIA AI
"""

from fastapi import HTTPException
from openai import OpenAI
import os
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_analysis")

USER_AGENT = "DataHaloBot/1.0"

# ============================================================================
# NVIDIA CLIENT INITIALIZATION
# ============================================================================

def _get_nvidia_client():
    """
    Initialize OpenAI client for NVIDIA API.
    Ensures NVIDIA_API_KEY is present before making calls.
    """
    key = os.getenv("NVIDIA_API_KEY")
    if not key:
        raise HTTPException(
            status_code=500,
            detail="NVIDIA_API_KEY not set in environment variables!"
        )
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=key
    )

# ============================================================================
# DATA PREPARATION
# ============================================================================

def _prepare_analysis_corpus(name: str, data: dict) -> Dict[str, Any]:
    """
    Prepare comprehensive data corpus for AI analysis.
    Extracts and organizes all available journalist information.
    """
    
    # Extract primary profile
    primary_profile = data.get('primary_profile', {}) or {}
    
    # Extract articles with full metadata
    articles = data.get('articles', [])
    raw_pages = data.get('raw_pages', [])
    
    # Build comprehensive article list with links
    article_corpus = []
    for article in articles:
        if article and isinstance(article, dict):
            article_entry = {
                "title": article.get('title', 'Untitled'),
                "url": article.get('url', ''),
                "domain": article.get('domain', ''),
                "snippet": article.get('snippet', ''),
                "publish_date": article.get('publish_date', 'Unknown'),
                "trust_score": article.get('trust_score', 0),
                "content_preview": article.get('content_preview', '')
            }
            if article_entry['url']:  # Only include if has valid URL
                article_corpus.append(article_entry)
    
    # Extract social media presence
    social_links = primary_profile.get('social_links', [])
    social_presence = {}
    for link in social_links:
        if isinstance(link, dict):
            platform = link.get('platform', 'unknown')
            social_presence[platform] = {
                "handle": link.get('handle', ''),
                "url": link.get('url', '')
            }
    
    # Extract bio and description
    bio = primary_profile.get('bio', '') or ''
    
    # Extract profile image
    profile_image = primary_profile.get('profile_image', '') or ''
    
    # Extract contact information
    emails = primary_profile.get('emails', [])
    
    # Extract analysis data
    analysis = data.get('analysis', {}) or {}
    tone_score = analysis.get('tone_score', 0)
    bias_label = analysis.get('bias_label', 'unknown')
    bias_scores = analysis.get('bias_scores', {})
    political_affiliation = analysis.get('political_affiliation', {})
    controversy_score = analysis.get('controversy_score', 0)
    controversy_snippets = analysis.get('controversy_snippets', [])
    credibility_indicators = analysis.get('credibility_indicators', [])
    
    # Extract awards
    awards = data.get('awards', [])
    
    # Extract domain trust information
    domain_trust = primary_profile.get('trust_score', 0)
    
    # Calculate Halo Score first
    halo_data = {
        'total_articles': len(article_corpus),
        'social_links': social_presence,
        'verification_rate': data.get('verification_rate', 0),
        'awards': awards,
        'domain_trust': domain_trust,
        'controversy_score': controversy_score,
        'articles': article_corpus,
        'bio': bio,
        'profile_image': profile_image,
        'emails': emails,
        'political_affiliation': political_affiliation
    }
    
    halo_score_result = calculate_halo_score(name, halo_data)
    
    # Build text corpus for AI
    corpus_parts = []
    
    # 1. Biography
    if bio:
        corpus_parts.append(f"=== BIOGRAPHY ===\n{bio}\n")
    
    # 2. Political Affiliation (Enhanced)
    if political_affiliation and political_affiliation.get('affiliation') != 'unknown':
        affiliation_text = "=== POLITICAL AFFILIATION ===\n"
        affiliation_text += f"Primary Affiliation: {political_affiliation.get('affiliation', 'Unknown')}\n"
        affiliation_text += f"Confidence: {political_affiliation.get('confidence', 0)}%\n"
        if political_affiliation.get('all_scores'):
            affiliation_text += f"Affiliation Scores: {json.dumps(political_affiliation['all_scores'], indent=2)}\n"
        if political_affiliation.get('evidence'):
            affiliation_text += f"Evidence: {political_affiliation.get('evidence', '')}\n"
        corpus_parts.append(affiliation_text)
    
    # 3. Awards and Recognition (Enhanced)
    if awards:
        awards_text = "=== AWARDS & RECOGNITION ===\n"
        for idx, award in enumerate(awards[:15], 1):  # Increased from 10 to 15
            if isinstance(award, dict):
                name_award = award.get('name', 'Award')
                year = award.get('year', 'Unknown year')
                context = award.get('context', '')
                organization = award.get('organization', '')
                awards_text += f"\n{idx}. {name_award}"
                if year and year != 'Unknown year':
                    awards_text += f" ({year})"
                if organization:
                    awards_text += f" - {organization}"
                if context:
                    awards_text += f"\n   Context: {context[:300]}"  # Increased context length
                awards_text += "\n"
        corpus_parts.append(awards_text)
    
    # 4. Notable Works (Enhanced - First 50 articles for better AI analysis)
    if article_corpus:
        articles_text = "=== PUBLISHED ARTICLES ===\n"
        for idx, article in enumerate(article_corpus[:50], 1):  # Increased from 30 to 50
            articles_text += f"\n{idx}. {article['title']}\n"
            articles_text += f"   URL: {article['url']}\n"
            articles_text += f"   Source: {article['domain']} (Trust Score: {article['trust_score']}/10)\n"
            articles_text += f"   Date: {article['publish_date']}\n"
            if article['snippet']:
                articles_text += f"   Summary: {article['snippet'][:300]}\n"  # Increased snippet length
            if article['content_preview']:
                articles_text += f"   Content Preview: {article['content_preview'][:500]}\n"  # Increased preview length
        corpus_parts.append(articles_text)
    
    # 5. Social Media Presence (Enhanced)
    if social_presence:
        social_text = "=== SOCIAL MEDIA PRESENCE ===\n"
        for platform, info in social_presence.items():
            social_text += f"- {platform.title()}: @{info['handle']} ({info['url']})\n"
            # Add follower count if available
            if info.get('followers'):
                social_text += f"  Followers: {info['followers']}\n"
        corpus_parts.append(social_text)
    
    # 6. Controversies (Enhanced)
    if controversy_snippets:
        controversy_text = "=== CONTROVERSIES & CRITICISMS ===\n"
        for idx, snippet in enumerate(controversy_snippets[:15], 1):  # Increased from 10 to 15
            if isinstance(snippet, dict):
                severity = snippet.get('severity', 'unknown').upper()
                text = snippet.get('text', '')
                source = snippet.get('source', '')
                date = snippet.get('date', '')
                controversy_text += f"{idx}. [{severity}] {text[:300]}\n"  # Increased text length
                if source:
                    controversy_text += f"   Source: {source}\n"
                if date:
                    controversy_text += f"   Date: {date}\n"
        corpus_parts.append(controversy_text)
    
    # 7. Observational Indicators (Enhanced)
    if credibility_indicators:
        indicators_text = "=== OBSERVATIONAL INDICATORS ===\n"
        positive_indicators = [i for i in credibility_indicators if i.startswith('+')]
        negative_indicators = [i for i in credibility_indicators if i.startswith('-')]
        neutral_indicators = [i for i in credibility_indicators if not i.startswith(('+', '-'))]
        
        if positive_indicators:
            indicators_text += f" Positive: {', '.join(positive_indicators)}\n"
        if negative_indicators:
            indicators_text += f" Negative: {', '.join(negative_indicators)}\n"
        if neutral_indicators:
            indicators_text += f" Neutral: {', '.join(neutral_indicators)}\n"
        corpus_parts.append(indicators_text)
    
    # 8. Enhanced Analysis Metrics
    analysis_text = "=== AUTOMATED ANALYSIS ===\n"
    analysis_text += f"Emotional Tone Score: {tone_score:.2f}/10\n"
    analysis_text += f"Detected Bias: {bias_label.title()}\n"
    if bias_scores:
        analysis_text += f"Bias Breakdown: {json.dumps(bias_scores, indent=2)}\n"
    analysis_text += f"Controversy Score: {controversy_score}/10\n"
    analysis_text += f"Halo Score: {halo_score_result['score']}/100 ({halo_score_result['level']})\n"
    analysis_text += f"Halo Breakdown: Reach={halo_score_result['breakdown']['reach_index']}, "
    analysis_text += f"Engagement={halo_score_result['breakdown']['engagement_ratio']}, "
    analysis_text += f"Transparency={halo_score_result['breakdown']['transparency_layer']}, "
    analysis_text += f"Work={halo_score_result['breakdown']['work_footprint']}, "
    analysis_text += f"Resonance={halo_score_result['breakdown']['public_resonance']}\n"
    corpus_parts.append(analysis_text)
    
    # Combine all parts (increased limit for more comprehensive analysis)
    text_corpus = "\n\n".join(corpus_parts)[:20000]  # Increased from 15000 to 20000
    
    return {
        "name": name,
        "text_corpus": text_corpus,
        "profile_image": profile_image,
        "social_links": social_presence,
        "articles": article_corpus,
        "bio": bio,
        "emails": emails,
        "tone_score": tone_score,
        "bias_label": bias_label,
        "political_affiliation": political_affiliation,
        "controversy_score": controversy_score,
        "halo_score_result": halo_score_result,
        "domain_trust": domain_trust,
        "total_articles": len(article_corpus),
        "verification_rate": data.get('verification_rate', 0),
        "awards": awards,
    }

# ============================================================================
# HALO SCORE CALCULATION
# ============================================================================

def calculate_halo_score(name: str, data: dict) -> dict:
    """
    Calculate the Halo Score - journalist's influence, transparency, and engagement fingerprint.
    Not about right/wrong - about visibility, consistency, and accountability.
    """
    
    # Extract data for calculation
    total_articles = data.get('total_articles', 0)
    social_links = data.get('social_links', {})
    verification_rate = data.get('verification_rate', 0)
    awards = data.get('awards', [])
    domain_trust = data.get('domain_trust', 0)
    controversy_score = data.get('controversy_score', 0)
    
    # REACH INDEX (0-25 points)
    # Measures how widely journalist's work appears
    reach_score = 0
    if total_articles >= 100:
        reach_score += 10  # High article count
    elif total_articles >= 50:
        reach_score += 7
    elif total_articles >= 20:
        reach_score += 5
    elif total_articles >= 10:
        reach_score += 3
    
    # Domain diversity bonus
    if len(data.get('articles', [])) > 0:
        domains = set()
        for article in data['articles'][:30]:
            domain = article.get('domain', '')
            if domain:
                domains.add(domain)
        
        if len(domains) >= 10:
            reach_score += 8  # Very diverse reach
        elif len(domains) >= 5:
            reach_score += 5  # Good reach
        elif len(domains) >= 3:
            reach_score += 3  # Moderate reach
    
    # Award bonus for reach
    if len(awards) >= 3:
        reach_score += 7
    elif len(awards) >= 1:
        reach_score += 4
    
    reach_score = min(25, reach_score)  # Cap at 25
    
    # ENGAGEMENT RATIO (0-20 points)
    # How people interact with their content
    engagement_score = 0
    
    # Social media presence
    social_platforms = len(social_links)
    if social_platforms >= 4:
        engagement_score += 8
    elif social_platforms >= 2:
        engagement_score += 5
    elif social_platforms >= 1:
        engagement_score += 3
    
    # Article engagement indicators (trust scores, verification)
    if verification_rate >= 80:
        engagement_score += 8
    elif verification_rate >= 60:
        engagement_score += 6
    elif verification_rate >= 40:
        engagement_score += 4
    elif verification_rate >= 20:
        engagement_score += 2
    
    # Domain trust factor
    if domain_trust >= 8:
        engagement_score += 4
    elif domain_trust >= 6:
        engagement_score += 2
    
    engagement_score = min(20, engagement_score)  # Cap at 20
    
    # TRANSPARENCY LAYER (0-25 points)
    # How clearly they disclose affiliations/biases
    transparency_score = 0
    
    # Profile completeness
    if data.get('bio'):
        transparency_score += 5
    if data.get('profile_image'):
        transparency_score += 3
    if data.get('emails'):
        transparency_score += 2
    
    # Social verification
    transparency_score += min(10, social_platforms * 2)  # Max 10 points
    
    # Political affiliation transparency
    political_affiliation = data.get('political_affiliation', {})
    if political_affiliation and political_affiliation.get('affiliation') != 'unknown':
        confidence = political_affiliation.get('confidence', 0)
        if confidence >= 70:
            transparency_score += 5  # Clear political stance = transparent
        elif confidence >= 50:
            transparency_score += 3
    
    transparency_score = min(25, transparency_score)  # Cap at 25
    
    # WORK FOOTPRINT (0-20 points)
    # Volume + consistency of journalistic work
    work_score = 0
    
    # Article volume
    if total_articles >= 200:
        work_score += 12
    elif total_articles >= 100:
        work_score += 10
    elif total_articles >= 50:
        work_score += 8
    elif total_articles >= 20:
        work_score += 6
    elif total_articles >= 10:
        work_score += 4
    elif total_articles >= 5:
        work_score += 2
    
    # Award recognition
    work_score += min(8, len(awards) * 2)  # Max 8 points from awards
    
    work_score = min(20, work_score)  # Cap at 20
    
    # PUBLIC RESONANCE (0-10 points)
    # Impact of their reporting
    resonance_score = 0
    
    # Controversy can indicate high public attention (not necessarily bad)
    if controversy_score >= 7:
        resonance_score += 4  # High controversy = high attention
    elif controversy_score >= 4:
        resonance_score += 2
    
    # Awards indicate public/industry recognition
    if len(awards) >= 5:
        resonance_score += 6
    elif len(awards) >= 3:
        resonance_score += 4
    elif len(awards) >= 1:
        resonance_score += 2
    
    resonance_score = min(10, resonance_score)  # Cap at 10
    
    # CALCULATE FINAL HALO SCORE
    total_halo_score = reach_score + engagement_score + transparency_score + work_score + resonance_score
    
    # Determine level
    if total_halo_score >= 85:
        level = "Exceptional"
    elif total_halo_score >= 70:
        level = "High"
    elif total_halo_score >= 55:
        level = "Good"
    elif total_halo_score >= 40:
        level = "Moderate"
    else:
        level = "Emerging"
    
    # Generate description
    transparency_level = "High" if transparency_score >= 20 else "Medium" if transparency_score >= 15 else "Low"
    reach_level = "Strong" if reach_score >= 20 else "Medium" if reach_score >= 15 else "Limited"
    
    bias_activity = "High" if controversy_score >= 6 else "Medium" if controversy_score >= 3 else "Low"
    
    description = f"{transparency_level} Transparency, {reach_level} Reach, {bias_activity} Bias Activity"
    
    # Calculate unique domains safely
    unique_domains = set()
    if data.get('articles'):
        for article in data['articles'][:30]:
            domain = article.get('domain', '')
            if domain and isinstance(domain, str):
                unique_domains.add(domain)
    
    return {
        "score": total_halo_score,
        "level": level,
        "description": description,
        "breakdown": {
            "reach_index": reach_score,
            "engagement_ratio": engagement_score,
            "transparency_layer": transparency_score,
            "work_footprint": work_score,
            "public_resonance": resonance_score
        },
        "reasoning": f"Based on {total_articles} articles across {len(unique_domains)} domains, {social_platforms} social platforms, {len(awards)} awards, and {verification_rate}% verification rate."
    }

# ============================================================================
# AI ANALYSIS
# ============================================================================

def analyze_journalist(name: str, data: dict) -> Dict[str, Any]:
    """
    Comprehensive AI-powered analysis of journalist profile and transparency patterns.
    
    Args:
        name: Journalist name
        data: Complete scraped data dictionary
    
    Returns:
        Comprehensive analysis dictionary with all metadata
    """
    
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=404, detail="Invalid data format")
    
    logger.info(f"Starting AI analysis for journalist: {name}")
    
    # Prepare comprehensive corpus
    try:
        corpus_data = _prepare_analysis_corpus(name, data)
    except Exception as e:
        logger.error(f"Error preparing corpus: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data preparation failed: {str(e)}")
    
    if not corpus_data['text_corpus']:
        raise HTTPException(
            status_code=404,
            detail="Insufficient journalist data found for analysis"
        )
    
    # Build AI prompt
    prompt = f"""You are DataHalo — an advanced AI journalism intelligence and transparency analysis system.

Your task: Generate a **comprehensive, factual, and deeply analytical profile** for journalist **{name}** with MAXIMUM accuracy in political affiliation detection.

**CRITICAL INSTRUCTIONS FOR POLITICAL AFFILIATION (99% ACCURACY REQUIRED):**

⚠️ **NEVER DEFAULT TO ANY PARTY WITHOUT CONCRETE EVIDENCE**
⚠️ **DO NOT GUESS - IF UNCERTAIN, USE "Independent" or "Insufficient Data"**

**STEP-BY-STEP POLITICAL BIAS DETECTION PROCESS:**

1. **COUNT ARTICLE PATTERNS (Primary Evidence):**
   From the {corpus_data['total_articles']} articles analyzed below, count:
   - How many articles CRITICIZE BJP/Modi government vs SUPPORT them?
   - How many articles CRITICIZE Congress vs SUPPORT them?
   - How many articles CRITICIZE AAP/other parties vs SUPPORT them?
   
   **CRITICAL MATH:**
   - If 70%+ articles criticize one party consistently → Anti-[Party]
   - If 70%+ articles support one party consistently → Pro-[Party]
   - If criticism is balanced across all parties → Independent
   - If less than 10 articles → Mark as "Insufficient Data"

2. **PUBLICATION ANALYSIS (Secondary Evidence):**
   Look at the domains in "topDomains" below:
   
   **Right-Leaning Outlets:** OpIndia, Swarajya, Republic TV, Times Now, India Today (sometimes), Zee News
   - If 70%+ articles from these → Likely "Right-leaning" or "Pro-BJP"
   
   **Left-Leaning Outlets:** The Wire, Scroll.in, Newslaundry, The Quint, NDTV, Caravan, Outlook
   - If 70%+ articles from these → Likely "Left-leaning" or "Anti-BJP"
   
   **Neutral Outlets:** The Hindu, Indian Express, Hindustan Times, Live Mint, Business Standard
   - If most articles from these → Likely "Centrist" or "Independent"

3. **LANGUAGE PATTERN ANALYSIS:**
   Look for these linguistic markers in article titles/snippets:
   
   **Pro-BJP Language:** "development", "progress", "strong leader", "nationalist", "patriotic"
   **Anti-BJP Language:** "authoritarian", "fascist", "hindutva", "communal", "press freedom"
   **Pro-Congress Language:** "secular", "inclusive", "Gandhi legacy", "liberal values"
   **Neutral Language:** Factual reporting without charged political terms

4. **AUTOMATED SCORES CROSS-CHECK:**
   The automated analysis detected:
   - Bias Label: {corpus_data['bias_label']}
   - Political Affiliation: {corpus_data.get('political_affiliation', {}).get('affiliation', 'Unknown')}
   - Confidence: {corpus_data.get('political_affiliation', {}).get('confidence', 0)}%
   
   **USE THIS AS A HINT ONLY - VERIFY WITH ARTICLE EVIDENCE**

5. **FINAL DECISION MATRIX:**

   | Evidence | Classification | Confidence |
   |----------|---------------|------------|
   | 70%+ pro-BJP articles + right-wing outlets | "Pro-BJP/Right-leaning" | High |
   | 70%+ anti-BJP articles + left-wing outlets | "Anti-BJP/Left-leaning" | High |
   | 70%+ pro-Congress articles | "Pro-Congress" | High |
   | Balanced criticism of all parties + neutral outlets | "Independent/Centrist" | High |
   | Mixed signals, no clear pattern | "Independent" | Medium |
   | Less than 10 articles analyzed | "Insufficient Data" | Low |
   | Cannot determine from evidence | "None Detected" | Low |

**FORBIDDEN DEFAULTS:**
❌ DO NOT default to "Congress" without evidence
❌ DO NOT assume "Left-leaning" just because they criticize government
❌ DO NOT confuse "Anti-BJP" with "Pro-Congress" (they are different!)
❌ DO NOT ignore the media outlets they write for

**REQUIRED JSON STRUCTURE:**
{{
    "name": "{name}",
    "biography": "Comprehensive 250-300 word factual summary. MUST mention their political leanings ONLY if clearly evident from analyzed articles. Do NOT speculate.",
    
    "careerHighlights": [
        "Most significant career milestone with specific details",
        "Second major achievement",
        "Third accomplishment"
    ],
    
    "mainTopics": [
        "Primary coverage area based on article analysis",
        "Secondary topic focus",
        "Third area"
    ],
    
    "writingTone": "Based on article analysis: Analytical / Neutral / Persuasive / Investigative / Advocacy-driven",
    
    "ideologicalBias": "EVIDENCE-BASED ONLY. Choose ONE from: 'Anti-BJP/Left-leaning' / 'Pro-BJP/Right-leaning' / 'Pro-Congress' / 'Independent/Centrist' / 'Insufficient Data' / 'None Detected'. Include specific nuance if detected.",
    
    "politicalAffiliation": {{
        "primary": "MUST match evidence from articles. Options: 'Anti-BJP' / 'Pro-BJP' / 'Pro-Congress' / 'Anti-Congress' / 'Independent' / 'Centrist' / 'Insufficient Data' / 'None Detected'. NEVER guess.",
        "confidence": "High (70%+ articles show pattern) / Medium (50-70%) / Low (<50% or insufficient articles)",
        "evidence": "MANDATORY: List 3-5 ACTUAL article titles/snippets from the SOURCE DATA below that demonstrate their bias. Format: 'Article: [Title] - [Why it shows bias]'. If no clear evidence, write: 'Insufficient evidence from analyzed articles to determine political affiliation.' DO NOT FABRICATE."
    }},
    
    "haloScore": {{
        "score": {corpus_data['halo_score_result']['score']},
        "level": "{corpus_data['halo_score_result']['level']}",
        "description": "{corpus_data['halo_score_result']['description']}",
        "breakdown": {json.dumps(corpus_data['halo_score_result']['breakdown'])},
        "reasoning": "{corpus_data['halo_score_result']['reasoning']}"
    }},
    
    "notableWorks": [
        {{
            "title": "Most impactful article title from analyzed set",
            "url": "Direct URL from SOURCE DATA",
            "impact": "Specific impact description",
            "year": "Publication year if available",
            "significance": "Why notable (awards, public impact, investigations)"
        }},
        {{
            "title": "Second notable work",
            "url": "URL from SOURCE DATA", 
            "impact": "Impact description",
            "year": "Publication year",
            "significance": "Specific reason for notability"
        }},
        {{
            "title": "Third most significant work",
            "url": "URL from SOURCE DATA",
            "impact": "Measurable impact or recognition",
            "year": "Publication year",
            "significance": "Evidence of importance"
        }}
    ],
    
    "awards": [
        "Only include awards mentioned in SOURCE DATA below - do not fabricate"
    ],
    
    "controversies": [
        {{
            "description": "Factual controversy description from SOURCE DATA",
            "severity": "High / Medium / Low based on impact",
            "source": "Where mentioned",
            "year": "When occurred"
        }}
    ],
    
    "digitalPresence": {{
        "profileImage": "{corpus_data.get('profile_image', '')}",
        "verifiedLinks": {json.dumps([{{"platform": k, "url": v.get("url", "")}} for k, v in corpus_data.get('social_links', {}).items()])},
        "mediaAffiliations": ["Extract ONLY from article domains in SOURCE DATA - be precise"],
        "onlineReach": "Low / Moderate / High / Very High based on article count and social presence"
    }},
    
    "engagementInsights": {{
        "audienceSentiment": "Based on controversy score and article reception",
        "influenceLevel": "Based on article count and publication quality",
        "controversyLevel": "{corpus_data.get('controversy_score', 0)}/10",
        "trustworthiness": "Based on domain trust ({corpus_data['domain_trust']}/10) and verification rate ({corpus_data['verification_rate']}%)"
    }},
    
    "ethicalAssessment": "3-4 paragraph assessment of journalistic integrity, fact-checking, transparency, bias disclosure, and accountability. MUST discuss how their political bias (if detected) affects objectivity. Reference Halo Score components. Be specific with examples from analyzed articles.",
    
    "articlesAnalyzed": {{
        "total": {corpus_data.get('total_articles', 0)},
        "verificationRate": "{corpus_data.get('verification_rate', 0)}%",
        "topDomains": ["List top 5-7 domains from analyzed articles - these reveal outlet affiliations"],
        "dateRange": "Range of publication dates from analyzed articles",
        "keyArticles": [
            {{
                "title": "Most significant article from analyzed set",
                "url": "Article URL",
                "date": "Publication date",
                "significance": "Why significant"
            }}
        ]
    }},
    
    "toneAnalysis": {{
        "emotionalTone": "{corpus_data.get('tone_score', 0):.1f}/10",
        "bias": "{corpus_data.get('bias_label', 'unknown')}",
        "objectivity": "Percentage of fact-based vs opinion writing",
        "consistency": "Pattern consistency across articles"
    }},
    
    "recommendationScore": {{
        "overall": {corpus_data['halo_score_result']['score']},
        "reasoning": "Should readers trust this journalist? Discuss reliability, bias transparency, and track record. MENTION political leanings as a transparency factor. Reference Halo Score.",
        "strengths": ["Specific strength from evidence", "Second strength", "Third strength"],
        "concerns": ["Specific concern if any", "Political bias transparency concerns if applicable"]
    }}
}}

===========================================
SOURCE DATA FOR ANALYSIS:
===========================================

{corpus_data['text_corpus']}

===========================================
CRITICAL METADATA:
===========================================
- Total Articles Analyzed: {corpus_data['total_articles']}
- Verification Rate: {corpus_data['verification_rate']}%
- Domain Trust Score: {corpus_data['domain_trust']}/10
- Automated Bias Detection: {corpus_data['bias_label']}
- Automated Political Hint: {corpus_data.get('political_affiliation', {}).get('affiliation', 'Unknown')} ({corpus_data.get('political_affiliation', {}).get('confidence', 0)}% confidence)
- Automated Halo Score: {corpus_data['halo_score_result']['score']}/100
- Awards Found: {len(corpus_data.get('awards', []))}

**FINAL REMINDER:**
- If you cannot determine political affiliation with 70%+ confidence → Use "Independent" or "Insufficient Data"
- NEVER fabricate evidence
- ONLY use information from SOURCE DATA above
- Political affiliation must be backed by SPECIFIC article examples

NOW GENERATE THE COMPLETE JSON ANALYSIS:
"""
    
    # Call NVIDIA API
    client = _get_nvidia_client()
    
    try:
        logger.info(f"Sending analysis request to NVIDIA API for: {name}")
        
        completion = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are DataHalo AI - an expert journalism analyst. Respond ONLY with valid JSON following the exact structure provided. Do NOT include markdown formatting, code blocks, or explanations outside the JSON structure."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower for more factual responses
            max_tokens=4000,
            top_p=0.9,
            stream=False
        )
        
        response_text = completion.choices[0].message.content.strip()
        logger.info(f"Received response from NVIDIA API ({len(response_text)} chars)")
        
        # Extract JSON from response
        try:
            # Find JSON boundaries
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = [
                'name', 'biography', 'mainTopics', 'writingTone',
                'digitalPresence', 'ethicalAssessment'
            ]
            missing = [f for f in required_fields if f not in result]
            if missing:
                logger.warning(f"Missing fields in AI response: {', '.join(missing)}")
                # Add default values for missing fields
                for field in missing:
                    if field == 'digitalPresence':
                        result[field] = {
                            "profileImage": corpus_data.get('profile_image', ''),
                            "verifiedLinks": list(corpus_data.get('social_links', {}).values()),
                            "mediaAffiliations": [],
                            "onlineReach": "Moderate"
                        }
                    else:
                        result[field] = "Not available"
            
            # Add metadata
            result['_metadata'] = {
                "analysis_timestamp": data.get('query_timestamp', ''),
                "data_sources": corpus_data['total_articles'],
                "verification_rate": corpus_data['verification_rate'],
                "automated_scores": {
                    "tone": corpus_data['tone_score'],
                    "bias": corpus_data['bias_label'],
                    "controversy": corpus_data['controversy_score'],
                    "halo_score": corpus_data['halo_score_result']['score']
                }
            }
            
            logger.info(f"✅ Successfully analyzed journalist: {name}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            raise HTTPException(
                status_code=500,
                detail=f"AI returned invalid JSON: {str(e)}. Please retry."
            )
    
    except Exception as e:
        logger.error(f"NVIDIA API error for {name}: {str(e)}")
        
        # Check for specific error types
        error_str = str(e).lower()
        if any(x in error_str for x in ["403", "authorization", "forbidden", "unauthorized"]):
            raise HTTPException(
                status_code=401,
                detail="NVIDIA API authorization failed. Please check your API key and permissions."
            )
        elif "rate limit" in error_str or "429" in error_str:
            raise HTTPException(
                status_code=429,
                detail="API rate limit exceeded. Please try again later."
            )
        elif "timeout" in error_str:
            raise HTTPException(
                status_code=504,
                detail="API request timed out. Please try again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis failed: {str(e)}"
            )

# ============================================================================
# BATCH ANALYSIS (for multiple journalists)
# ============================================================================

def analyze_journalists_batch(journalists_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple journalists in batch.
    
    Args:
        journalists_data: List of journalist data dictionaries
    
    Returns:
        List of analysis results
    """
    results = []
    
    for data in journalists_data:
        name = data.get('name', 'Unknown')
        try:
            result = analyze_journalist(name, data)
            results.append(result)
            logger.info(f"✅ Batch analysis complete for: {name}")
        except Exception as e:
            logger.error(f"✗ Batch analysis failed for {name}: {str(e)}")
            results.append({
                "name": name,
                "error": str(e),
                "status": "failed"
            })
    
    return results