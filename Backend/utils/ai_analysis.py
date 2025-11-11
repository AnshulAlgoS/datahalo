"""
DataHalo AI Analysis Module
Comprehensive journalist credibility analysis using NVIDIA AI
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
    credibility_score = analysis.get('credibility_score', 5)
    credibility_indicators = analysis.get('credibility_indicators', [])
    
    # Extract awards
    awards = data.get('awards', [])
    
    # Extract domain trust information
    domain_trust = primary_profile.get('trust_score', 0)
    
    # Build text corpus for AI
    corpus_parts = []
    
    # 1. Biography
    if bio:
        corpus_parts.append(f"=== BIOGRAPHY ===\n{bio}\n")
    
    # 2. Political Affiliation (NEW)
    if political_affiliation and political_affiliation.get('affiliation') != 'unknown':
        affiliation_text = "=== POLITICAL AFFILIATION ===\n"
        affiliation_text += f"Primary Affiliation: {political_affiliation.get('affiliation', 'Unknown')}\n"
        affiliation_text += f"Confidence: {political_affiliation.get('confidence', 0)}%\n"
        if political_affiliation.get('all_scores'):
            affiliation_text += f"Affiliation Scores: {json.dumps(political_affiliation['all_scores'], indent=2)}\n"
        corpus_parts.append(affiliation_text)
    
    # 3. Awards and Recognition (NEW)
    if awards:
        awards_text = "=== AWARDS & RECOGNITION ===\n"
        for idx, award in enumerate(awards[:10], 1):
            if isinstance(award, dict):
                name_award = award.get('name', 'Award')
                year = award.get('year', 'Unknown year')
                context = award.get('context', '')
                awards_text += f"\n{idx}. {name_award}"
                if year:
                    awards_text += f" ({year})"
                if context:
                    awards_text += f"\n   Context: {context[:200]}"
                awards_text += "\n"
        corpus_parts.append(awards_text)
    
    # 4. Articles (with links and metadata)
    if article_corpus:
        articles_text = "=== PUBLISHED ARTICLES ===\n"
        for idx, article in enumerate(article_corpus[:30], 1):  # Limit to 30 for token efficiency
            articles_text += f"\n{idx}. {article['title']}\n"
            articles_text += f"   URL: {article['url']}\n"
            articles_text += f"   Source: {article['domain']} (Trust Score: {article['trust_score']}/10)\n"
            articles_text += f"   Date: {article['publish_date']}\n"
            if article['snippet']:
                articles_text += f"   Summary: {article['snippet'][:200]}\n"
            if article['content_preview']:
                articles_text += f"   Content Preview: {article['content_preview'][:300]}\n"
        corpus_parts.append(articles_text)
    
    # 5. Social Media Presence
    if social_presence:
        social_text = "=== SOCIAL MEDIA PRESENCE ===\n"
        for platform, info in social_presence.items():
            social_text += f"- {platform.title()}: @{info['handle']} ({info['url']})\n"
        corpus_parts.append(social_text)
    
    # 6. Controversies
    if controversy_snippets:
        controversy_text = "=== CONTROVERSIES & CRITICISMS ===\n"
        for idx, snippet in enumerate(controversy_snippets[:10], 1):
            controversy_text += f"{idx}. [{snippet.get('severity', 'unknown').upper()}] {snippet.get('text', '')[:200]}\n"
        corpus_parts.append(controversy_text)
    
    # 7. Credibility Indicators
    if credibility_indicators:
        cred_text = "=== CREDIBILITY INDICATORS ===\n"
        positive_indicators = [i for i in credibility_indicators if i.startswith('+')]
        negative_indicators = [i for i in credibility_indicators if i.startswith('-')]
        if positive_indicators:
            cred_text += f"Positive: {', '.join(positive_indicators)}\n"
        if negative_indicators:
            cred_text += f"Negative: {', '.join(negative_indicators)}\n"
        corpus_parts.append(cred_text)
    
    # 8. Tone & Bias Analysis
    analysis_text = "=== AUTOMATED ANALYSIS ===\n"
    analysis_text += f"Emotional Tone Score: {tone_score:.2f}/10\n"
    analysis_text += f"Detected Bias: {bias_label.title()}\n"
    if bias_scores:
        analysis_text += f"Bias Breakdown: {json.dumps(bias_scores, indent=2)}\n"
    analysis_text += f"Controversy Score: {controversy_score}/10\n"
    analysis_text += f"Credibility Score: {credibility_score}/10\n"
    corpus_parts.append(analysis_text)
    
    # Combine all parts
    text_corpus = "\n\n".join(corpus_parts)[:15000]  # Increased limit for more comprehensive data
    
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
        "credibility_score": credibility_score,
        "domain_trust": domain_trust,
        "total_articles": len(article_corpus),
        "verification_rate": data.get('verification_rate', 0),
        "awards": awards,
    }

# ============================================================================
# AI ANALYSIS
# ============================================================================

def analyze_journalist(name: str, data: dict) -> Dict[str, Any]:
    """
    Comprehensive AI-powered analysis of journalist credibility.
    
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
    prompt = f"""You are DataHalo — an advanced AI journalism intelligence and credibility analysis system.

Your task: Generate a **comprehensive, factual, and deeply analytical profile** for journalist **{name}**.

You MUST analyze:
1. Career trajectory and professional background
2. Writing style, tone, and journalistic approach
3. **Political/ideological leanings** - CRITICAL: Determine if the journalist leans LEFT (liberal, progressive, socialist, anti-establishment), RIGHT (conservative, nationalist, pro-government, traditionalist), CENTER (balanced, moderate), LIBERTARIAN (free speech absolutist, anti-authoritarian), or COMMUNIST/MARXIST based on their writings, affiliations, and coverage patterns
4. Credibility indicators (awards, recognitions, controversies)
5. Digital presence and audience engagement
6. Ethical standards and integrity assessment
7. Notable works and impact on journalism

**CRITICAL INSTRUCTIONS FOR POLITICAL BIAS DETECTION:**
- Analyze article topics: Are they covering government critically or supportively?
- Look for patterns: Pro-BJP/right-wing vs Pro-Congress/left-wing vs neutral
- Check social media presence and who they engage with
- Identify if they use charged language (e.g., "saffron", "secular", "nationalist")
- Note any party affiliations, endorsements, or known political associations
- Be SPECIFIC about bias - don't be vague. If they're left-leaning, say so clearly
- If automated analysis detected political affiliation, incorporate that prominently

**REQUIRED JSON STRUCTURE:**
{{
    "name": "{name}",
    "biography": "Comprehensive 200-250 word factual summary integrating career highlights, focus areas, reputation, and public image. Include key milestones and evolution of their journalism career. MENTION their known political leanings if evident.",
    
    "careerHighlights": [
        "Key career milestone 1 with specific details",
        "Key career milestone 2 with specific details",
        "Key career milestone 3 with specific details"
    ],
    
    "mainTopics": [
        "Primary beat/topic area 1",
        "Primary beat/topic area 2",
        "Primary beat/topic area 3"
    ],
    
    "writingTone": "Analytical / Neutral / Persuasive / Emotional / Investigative / Opinionated",
    
    "ideologicalBias": "Left-leaning / Right-leaning / Centrist / Libertarian / Progressive / Conservative / Socialist / Communist / Unclear - BE SPECIFIC. If evidence shows clear left or right bias, state it directly. Include nuances like 'Left-leaning with pro-labor focus' or 'Right-wing nationalist'",
    
    "politicalAffiliation": {{
        "primary": "BJP / Congress / AAP / Communist / Regional Party / Independent / None Detected",
        "confidence": "High / Medium / Low",
        "evidence": "Specific examples from their work showing affiliation or bias - cite article topics, social media, or affiliations"
    }},
    
    "credibilityScore": {{
        "score": 75,
        "reasoning": "Detailed 3-4 sentence justification with specific evidence from articles, controversies, and track record. Reference specific metrics."
    }},
    
    "notableWorks": [
        {{
            "title": "Article/Investigation title",
            "url": "Direct URL to work",
            "impact": "Brief description of significance and impact",
            "year": "Publication year if known"
        }}
    ],
    
    "awards": [
        "Award name and year if found in data, otherwise use 'Not found in available data'"
    ],
    
    "controversies": [
        {{
            "description": "Objective summary of controversy",
            "severity": "High / Medium / Low",
            "source": "Where this information came from"
        }}
    ],
    
    "digitalPresence": {{
        "profileImage": "{corpus_data.get('profile_image', '')}",
        "verifiedLinks": {json.dumps(list(corpus_data.get('social_links', {}).values()))},
        "mediaAffiliations": ["List of publications/organizations journalist is associated with based on article domains"],
        "onlineReach": "Low / Moderate / High / Very High based on social presence and article count"
    }},
    
    "engagementInsights": {{
        "audienceSentiment": "Positive / Negative / Mixed / Polarizing",
        "influenceLevel": "Low / Moderate / High / Very High",
        "controversyLevel": "{corpus_data.get('controversy_score', 0)}/10",
        "trustworthiness": "Assessment based on domain trust scores and verification rate"
    }},
    
    "ethicalAssessment": "Comprehensive 2-3 paragraph assessment discussing journalistic integrity, fact-checking practices, source transparency, bias management, accountability for errors, and overall ethical standards. Be specific and evidence-based. DISCUSS how their political bias (if any) affects their reporting objectivity.",
    
    "articlesAnalyzed": {{
        "total": {corpus_data.get('total_articles', 0)},
        "verificationRate": "{corpus_data.get('verification_rate', 0)}%",
        "topDomains": ["Extract top 3-5 publication domains from articles"],
        "dateRange": "Earliest to latest publication dates found",
        "keyArticles": [
            {{
                "title": "Most significant article title",
                "url": "Article URL",
                "date": "Publication date",
                "significance": "Why this article matters"
            }}
        ]
    }},
    
    "toneAnalysis": {{
        "emotionalTone": "{corpus_data.get('tone_score', 0):.1f}/10",
        "bias": "{corpus_data.get('bias_label', 'unknown')}",
        "objectivity": "Assessment of fact-based vs opinion-based writing",
        "consistency": "Assessment of consistency in tone and approach across articles"
    }},
    
    "recommendationScore": {{
        "overall": 75,
        "reasoning": "Brief recommendation on credibility for readers: Should readers trust this journalist? Why or why not? MENTION their political leanings as a factor readers should be aware of.",
        "strengths": ["Strength 1", "Strength 2", "Strength 3"],
        "concerns": ["Concern 1 if any", "Concern 2 if any", "Political bias concerns if applicable"]
    }}
}}

===========================================
SOURCE DATA FOR ANALYSIS:
===========================================

{corpus_data['text_corpus']}

===========================================
ADDITIONAL METADATA:
===========================================
- Total Articles Analyzed: {corpus_data['total_articles']}
- Verification Rate: {corpus_data['verification_rate']}%
- Domain Trust Score: {corpus_data['domain_trust']}/10
- Automated Bias Detection: {corpus_data['bias_label']}
- Automated Political Affiliation: {corpus_data.get('political_affiliation', {}).get('affiliation', 'Unknown')} (Confidence: {corpus_data.get('political_affiliation', {}).get('confidence', 0)}%)
- Automated Credibility Score: {corpus_data['credibility_score']}/10
- Awards Found: {len(corpus_data.get('awards', []))}

NOW GENERATE THE COMPLETE JSON ANALYSIS:
"""
    
    # Call NVIDIA API
    client = _get_nvidia_client()
    
    try:
        logger.info(f"Sending analysis request to NVIDIA API for: {name}")
        
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-coder-32b-instruct",
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
                'credibilityScore', 'digitalPresence', 'ethicalAssessment'
            ]
            missing = [f for f in required_fields if f not in result]
            if missing:
                logger.warning(f"Missing fields in AI response: {', '.join(missing)}")
                # Add default values for missing fields
                for field in missing:
                    if field == 'credibilityScore':
                        result[field] = {"score": corpus_data['credibility_score'] * 10, "reasoning": "Based on automated analysis"}
                    elif field == 'digitalPresence':
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
                    "credibility": corpus_data['credibility_score']
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
