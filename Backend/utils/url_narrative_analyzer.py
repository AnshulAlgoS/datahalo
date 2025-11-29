"""
URL-Based Narrative Analyzer
Comprehensive analysis of news stories from URLs including timeline, manipulation detection, and source clustering
Enhanced with AI-powered article understanding
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
import os
import re
from collections import Counter, defaultdict
import json

logger = logging.getLogger("url_narrative_analyzer")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


def extract_article_content(url: str) -> Dict[str, Any]:
    """Extract article content and metadata from URL with enhanced parsing."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title (try multiple methods)
        title = None
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        elif soup.find('meta', attrs={'property': 'og:title'}):
            title = soup.find('meta', attrs={'property': 'og:title'}).get('content', '')
        elif soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        
        # Extract description/summary
        description = None
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        # Extract source/publisher
        source = None
        meta_source = soup.find('meta', attrs={'property': 'og:site_name'}) or soup.find('meta', attrs={'name': 'author'})
        if meta_source:
            source = meta_source.get('content', '')
        else:
            # Extract from URL
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            source = domain.replace('www.', '').replace('.com', '').replace('.in', '').replace('.org', '').title()
        
        # Extract publish date
        published_date = None
        meta_date = soup.find('meta', attrs={'property': 'article:published_time'}) or soup.find('meta', attrs={'name': 'publishdate'}) or soup.find('time')
        if meta_date:
            published_date = meta_date.get('content', '') or meta_date.get('datetime', '')
        
        # Extract article body (ENHANCED - multiple strategies)
        article_body = []
        
        # Strategy 1: Try article tag first
        article_tag = soup.find('article')
        if article_tag:
            paragraphs = article_tag.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 40:  # Substantial paragraphs
                    article_body.append(text)
        
        # Strategy 2: If no content, try main content areas
        if len(article_body) < 3:
            content_areas = soup.find_all(['div'], class_=re.compile(r'(story|article|content|body|post|entry)', re.I))
            for area in content_areas[:5]:  # Check first 5 matching divs
                paragraphs = area.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 40 and text not in [a for a in article_body]:
                        article_body.append(text)
        
        # Strategy 3: If still no content, get ALL paragraphs
        if len(article_body) < 3:
            all_paragraphs = soup.find_all('p')
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                # Filter out navigation, footer, header text
                if (len(text) > 40 and 
                    text not in [a for a in article_body] and
                    not any(skip in text.lower() for skip in ['cookie', 'subscribe', 'newsletter', 'follow us', 'share this'])):
                    article_body.append(text)
        
        # Strategy 4: If still empty, try getting text from specific tags
        if len(article_body) < 2:
            # Look for story/article specific containers
            for tag in ['div', 'section', 'main']:
                containers = soup.find_all(tag, attrs={'id': re.compile(r'(story|article|content|main)', re.I)})
                for container in containers:
                    text = container.get_text(separator=' ', strip=True)
                    if len(text) > 200:
                        # Split into sentences
                        sentences = re.split(r'[.!?]\s+', text)
                        article_body.extend([s.strip() + '.' for s in sentences if len(s.strip()) > 40][:10])
                        break
                if article_body:
                    break
        
        # Get full content (first 20 paragraphs for better context)
        content = ' '.join(article_body[:20])
        
        # If still no content, use description as fallback
        if not content and description:
            content = description
        
        logger.info(f"INFO: Extracted {len(article_body)} paragraphs, {len(content.split())} words")
        
        # Extract main topic/subject from title and content
        main_topic = _extract_main_topic(title, description or content[:500])
        
        # Extract keywords/tags
        keywords = []
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'}) or soup.find('meta', attrs={'property': 'article:tag'})
        if meta_keywords:
            keywords = [k.strip() for k in meta_keywords.get('content', '').split(',')]
        
        # Extract author
        author = None
        meta_author = soup.find('meta', attrs={'name': 'author'}) or soup.find('meta', attrs={'property': 'article:author'})
        if meta_author:
            author = meta_author.get('content', '')
        
        word_count = len(content.split())
        
        # Log extraction results
        if word_count > 0:
            logger.info(f"SUCCESS: Extracted article: '{title[:60]}...' from {source} ({word_count} words)")
        else:
            logger.warning(f"WARNING: Low content extracted from {source}: Only {word_count} words - using description as fallback")
            # Use description as content if article body extraction failed
            if description and len(description) > 100:
                content = description
                word_count = len(content.split())
        
        return {
            'url': url,
            'title': title or 'No title found',
            'description': description or content[:500],
            'source': source or 'Unknown Source',
            'author': author,
            'published_date': published_date or datetime.utcnow().isoformat(),
            'content': content,
            'keywords': keywords,
            'main_topic': main_topic,
            'word_count': word_count,
            'success': True,
            'extraction_quality': 'good' if word_count > 200 else 'moderate' if word_count > 50 else 'limited'
        }
        
    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {str(e)}")
        return {
            'url': url,
            'success': False,
            'error': str(e)
        }


def _extract_main_topic(title: str, content: str) -> str:
    """Extract the main topic/subject from title and content."""
    # Remove common words
    stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'has', 'have', 'will', 'be'}
    
    # Extract capitalized phrases (likely proper nouns/topics)
    text = title + ' ' + content
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    if capitalized:
        # Most common capitalized phrase
        topic_counts = Counter(capitalized)
        return topic_counts.most_common(1)[0][0]
    
    # Fallback: extract key words from title
    words = [w for w in re.findall(r'\b\w+\b', title.lower()) if w not in stopwords and len(w) > 4]
    return ' '.join(words[:2]).title() if words else "General News"


async def analyze_article_with_ai(article: Dict[str, Any], ai_api_key: str) -> Dict[str, Any]:
    """Simple, clear article analysis: what happened, background, and future impact."""
    if not ai_api_key:
        return {}
    
    try:
        # SIMPLIFIED prompt for clear article summary
        prompt = f"""Analyze this news article and provide a clear, simple summary.

ARTICLE:
Title: {article.get('title', '')}
Source: {article.get('source', '')}
Date: {article.get('published_date', 'Unknown')[:10]}

Content:
{article.get('content', '')[:2000]}

Provide analysis in this JSON format:

{{
  "what_happened": "Clear summary of the main event or story in 2-3 sentences",
  
  "key_facts": [
    "Important fact 1",
    "Important fact 2",
    "Important fact 3",
    "Important fact 4"
  ],
  
  "background": "What led to this? What's the context and history?",
  
  "who_involved": ["Person/organization 1", "Person/organization 2"],
  
  "future_impact": {{
    "on_people": "How will this affect common people?",
    "on_government": "How will this affect government/policy?",
    "on_economy": "Economic impact if relevant",
    "timeline": "When will we see effects?"
  }},
  
  "why_it_matters": "Why should people care about this story?"
}}

Keep it simple, factual, and easy to understand."""

        headers = {
            "Authorization": f"Bearer {ai_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful news analyst who explains news stories in simple, clear language. Focus on facts: what happened, why it matters, and what comes next."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 1200  # Reduced to speed up response
        }

        logger.info("AI: Calling AI for article analysis...")
        
        # Extended timeout and retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                timeout_seconds = 300  # 5 minutes for thorough article analysis
                logger.info(f"AI: Attempt {attempt + 1}/{max_retries} (timeout: {timeout_seconds}s)")
                
                response = requests.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout_seconds
                )
                response.raise_for_status()
                logger.info("AI: Article analysis completed successfully!")
                break  # Success, exit retry loop
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"AI: Timeout on attempt {attempt + 1}/{max_retries}, waiting {wait_time}s before retry...")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"AI: All {max_retries} attempts timed out - analysis taking longer than expected")
                    raise
            except requests.exceptions.RequestException as e:
                logger.error(f"AI: Request error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(5)
                else:
                    raise

        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]

        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            analysis = json.loads(json_match.group(0))
            logger.info("SUCCESS: AI article analysis complete")
            return analysis
        else:
            return json.loads(content)
            
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        return {}


def find_related_articles(original_article: Dict[str, Any], days: int = 14, serp_api_key: str = None) -> List[Dict[str, Any]]:
    """Find related articles about the same story using SERP API (Google News search)."""
    try:
        # Extract key terms from title
        title = original_article['title']
        # Remove common words and extract keywords
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are', 'was', 'were'}
        words = [w for w in re.findall(r'\b\w+\b', title.lower()) if w not in stopwords and len(w) > 3]
        
        # Use top 3 keywords for search
        search_query = ' '.join(words[:3])
        
        logger.info(f"SERP: Searching Google News for related articles: {search_query}")
        
        # Use SERP API for Google News search
        if serp_api_key:
            try:
                serp_url = "https://serpapi.com/search"
                params = {
                    "engine": "google_news",
                    "q": search_query,
                    "api_key": serp_api_key,
                    "gl": "us",
                    "hl": "en"
                }
                
                response = requests.get(serp_url, params=params, timeout=20)
                response.raise_for_status()
                data = response.json()
                
                related_articles = []
                
                # Extract from news_results
                if data.get('news_results'):
                    for item in data['news_results'][:50]:  # Limit to 50
                        related_articles.append({
                            'title': item.get('title', 'No title'),
                            'description': item.get('snippet', ''),
                            'source': item.get('source', {}).get('name', 'Unknown') if isinstance(item.get('source'), dict) else item.get('source', 'Unknown'),
                            'url': item.get('link', ''),
                            'published_date': item.get('date', datetime.utcnow().isoformat()),
                            'image': item.get('thumbnail', '')
                        })
                
                logger.info(f"SERP: Found {len(related_articles)} related articles from Google News")
                return related_articles
                
            except Exception as serp_error:
                logger.error(f"SERP API failed: {str(serp_error)}")
        
        # Fallback: Try NewsAPI if SERP fails
        if NEWS_API_KEY:
            logger.info("FALLBACK: Trying NewsAPI...")
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": NEWS_API_KEY,
                "q": search_query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100,
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d")
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            # Check for NewsAPI errors
            if response.status_code == 401:
                logger.warning("NewsAPI key invalid - skipping NewsAPI fallback")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            related_articles = []
            if data.get('status') == 'ok' and data.get('articles'):
                for article in data['articles']:
                    if article.get('title') and article['title'] != '[Removed]':
                        related_articles.append({
                            'title': article['title'],
                            'description': article.get('description', ''),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'url': article['url'],
                            'published_date': article.get('publishedAt', ''),
                            'image': article.get('urlToImage', '')
                        })
            
            logger.info(f"NewsAPI: Found {len(related_articles)} related articles")
            return related_articles
        
        logger.warning("No search APIs available - returning empty results")
        return []
        
    except Exception as e:
        logger.error(f"Failed to find related articles: {str(e)}")
        return []


def analyze_timeline(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze coverage timeline to detect patterns."""
    timeline_data = defaultdict(list)
    
    for article in articles:
        try:
            date_str = article.get('published_date', '')
            if date_str:
                # Parse date
                if 'T' in date_str:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                else:
                    date = datetime.strptime(date_str[:10], '%Y-%m-%d').date()
                
                timeline_data[str(date)].append(article)
        except:
            continue
    
    # Build timeline with key events
    timeline = []
    for date in sorted(timeline_data.keys()):
        articles_on_date = timeline_data[date]
        
        # Detect sentiment (simplified)
        negative_keywords = ['crisis', 'scandal', 'controversy', 'issue', 'problem', 'concern', 'critical']
        positive_keywords = ['success', 'achievement', 'growth', 'progress', 'improve', 'win', 'victory']
        
        neg_count = sum(1 for a in articles_on_date if any(k in a.get('title', '').lower() for k in negative_keywords))
        pos_count = sum(1 for a in articles_on_date if any(k in a.get('title', '').lower() for k in positive_keywords))
        
        if neg_count > pos_count:
            sentiment = "Negative"
        elif pos_count > neg_count:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"
        
        timeline.append({
            'date': date,
            'count': len(articles_on_date),
            'sentiment': sentiment,
            'keyEvents': [a['title'] for a in articles_on_date[:2]]  # Top 2 headlines
        })
    
    return timeline


def detect_manipulation(articles: List[Dict[str, Any]], timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced detection of potential narrative manipulation indicators with deeper analysis."""
    indicators = {
        'coordinated_timing': False,
        'source_clustering': False,
        'sentiment_uniformity': False,
        'sudden_spike': False,
        'language_uniformity': False,
        'suspicious_patterns': [],
        'confidence_score': 0,
        'explanation': []
    }
    
    if len(articles) < 3:
        indicators['explanation'] = 'Insufficient data for comprehensive manipulation analysis - need at least 3 articles'
        indicators['confidence_score'] = 0
        return indicators
    
    manipulation_score = 0
    max_possible_score = 0
    
    # 1. ENHANCED Coordinated Timing Detection
    dates = [a.get('published_date', '') for a in articles if a.get('published_date')]
    if dates:
        # Check both hourly and daily clustering
        date_hours = defaultdict(int)
        date_days = defaultdict(int)
        
        for date_str in dates:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                hour_key = dt.strftime('%Y-%m-%d %H:00')
                day_key = dt.strftime('%Y-%m-%d')
                date_hours[hour_key] += 1
                date_days[day_key] += 1
            except:
                continue
        
        max_possible_score += 25
        
        # Check hourly clustering (strong indicator)
        max_in_hour = max(date_hours.values()) if date_hours else 0
        hour_ratio = max_in_hour / len(articles) if articles else 0
        
        if hour_ratio > 0.5:
            indicators['coordinated_timing'] = True
            manipulation_score += 25
            indicators['explanation'].append(f"CRITICAL: {max_in_hour}/{len(articles)} articles ({int(hour_ratio*100)}%) published within same hour - highly suspicious coordinated release")
            indicators['suspicious_patterns'].append("Hourly clustering suggests pre-planned media campaign")
        elif hour_ratio > 0.3:
            indicators['coordinated_timing'] = True
            manipulation_score += 15
            indicators['explanation'].append(f"WARNING: {max_in_hour} articles published in same hour window - possible coordinated timing")
            indicators['suspicious_patterns'].append("Moderate hourly clustering detected")
        
        # Check daily clustering (weaker but still relevant)
        max_in_day = max(date_days.values()) if date_days else 0
        day_ratio = max_in_day / len(articles) if articles else 0
        
        if day_ratio > 0.7 and len(date_days) == 1:
            manipulation_score += 10
            indicators['explanation'].append(f"All {len(articles)} articles published on same day - possible coordinated campaign")
    
    # 2. ENHANCED Source Clustering Detection
    sources = [a.get('source', '') for a in articles if a.get('source')]
    if sources:
        source_counts = Counter(sources)
        unique_sources = len(source_counts)
        top_3_sources = sum(count for _, count in source_counts.most_common(3))
        
        max_possible_score += 25
        
        # Single source domination
        if unique_sources == 1:
            indicators['source_clustering'] = True
            manipulation_score += 25
            indicators['explanation'].append(f"CRITICAL: Only ONE source ({sources[0]}) - no independent verification possible")
            indicators['suspicious_patterns'].append("Single source narrative - high manipulation risk")
        elif unique_sources <= 2:
            indicators['source_clustering'] = True
            manipulation_score += 20
            indicators['explanation'].append(f"WARNING: Only {unique_sources} sources - very limited diversity")
            indicators['suspicious_patterns'].append("Minimal source diversity")
        else:
            top_source_ratio = source_counts.most_common(1)[0][1] / len(sources)
            top_3_ratio = top_3_sources / len(sources) if sources else 0
            
            if top_source_ratio > 0.5:
                indicators['source_clustering'] = True
                manipulation_score += 15
                indicators['explanation'].append(f"Source clustering: {source_counts.most_common(1)[0][0]} accounts for {int(top_source_ratio*100)}% of articles")
                indicators['suspicious_patterns'].append("One source dominates narrative")
            elif top_3_ratio > 0.75:
                indicators['source_clustering'] = True
                manipulation_score += 10
                indicators['explanation'].append(f"Top 3 sources account for {int(top_3_ratio*100)}% of coverage")
                indicators['suspicious_patterns'].append("Limited source diversity")
    
    # 3. ENHANCED Sentiment Uniformity Detection
    sentiments = [t['sentiment'] for t in timeline if t.get('sentiment')]
    if sentiments and len(sentiments) >= 2:
        sentiment_counts = Counter(sentiments)
        dominant_sentiment = sentiment_counts.most_common(1)[0]
        uniformity_ratio = dominant_sentiment[1] / len(sentiments) if sentiments else 0
        
        max_possible_score += 20
        
        if uniformity_ratio >= 0.95:
            indicators['sentiment_uniformity'] = True
            manipulation_score += 20
            indicators['explanation'].append(f"EXTREME uniformity: {int(uniformity_ratio*100)}% of coverage has {dominant_sentiment[0].lower()} sentiment - suggests coordinated messaging")
            indicators['suspicious_patterns'].append("Near-total sentiment uniformity across all coverage")
        elif uniformity_ratio > 0.85:
            indicators['sentiment_uniformity'] = True
            manipulation_score += 15
            indicators['explanation'].append(f"High uniformity: {int(uniformity_ratio*100)}% {dominant_sentiment[0].lower()} sentiment - limited perspective diversity")
            indicators['suspicious_patterns'].append("Dominant sentiment with minimal dissenting views")
        elif uniformity_ratio > 0.75:
            manipulation_score += 8
            indicators['explanation'].append(f"Moderate uniformity: {int(uniformity_ratio*100)}% {dominant_sentiment[0].lower()} sentiment")
    
    # 4. ENHANCED Sudden Spike Detection with Statistical Analysis
    if timeline and len(timeline) >= 3:
        counts = [t['count'] for t in timeline]
        avg_count = sum(counts) / len(counts)
        max_count = max(counts)
        
        # Calculate standard deviation for more accurate spike detection
        variance = sum((x - avg_count) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        
        max_possible_score += 15
        
        if max_count > avg_count * 5:
            indicators['sudden_spike'] = True
            manipulation_score += 15
            indicators['explanation'].append(f"EXTREME spike: {max_count} articles on {timeline[counts.index(max_count)]['date']} (5x average) - possible manufactured controversy")
            indicators['suspicious_patterns'].append("Abnormal coverage surge suggests coordinated push")
        elif max_count > avg_count * 3:
            indicators['sudden_spike'] = True
            manipulation_score += 10
            indicators['explanation'].append(f"Sudden spike: {max_count} articles on {timeline[counts.index(max_count)]['date']} (3x average)")
            indicators['suspicious_patterns'].append("Significant coverage spike detected")
        elif std_dev > 0 and max_count > avg_count + (2 * std_dev):
            manipulation_score += 5
            indicators['explanation'].append(f"Statistical outlier detected in coverage pattern")
    
    # 5. NEW: Language Uniformity Detection (headline similarity)
    titles = [a.get('title', '').lower() for a in articles if a.get('title')]
    if len(titles) >= 5:
        max_possible_score += 15
        
        # Extract common phrases (3+ words)
        common_phrases = []
        for title in titles:
            words = title.split()
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if len(phrase) > 15:  # Substantial phrase
                    common_phrases.append(phrase)
        
        if common_phrases:
            phrase_counts = Counter(common_phrases)
            most_common_phrase, phrase_freq = phrase_counts.most_common(1)[0]
            phrase_ratio = phrase_freq / len(titles)
            
            if phrase_ratio > 0.4:
                indicators['language_uniformity'] = True
                manipulation_score += 15
                indicators['explanation'].append(f"Identical language: '{most_common_phrase}' appears in {int(phrase_ratio*100)}% of headlines - copy-paste journalism")
                indicators['suspicious_patterns'].append("Uniform language suggests single talking point source")
            elif phrase_ratio > 0.25:
                indicators['language_uniformity'] = True
                manipulation_score += 10
                indicators['explanation'].append(f"Repeated phrasing: '{most_common_phrase}' in {int(phrase_ratio*100)}% of headlines")
                indicators['suspicious_patterns'].append("Similar language patterns across sources")
    
    # Calculate confidence score (0-100)
    if max_possible_score > 0:
        indicators['confidence_score'] = min(100, int((manipulation_score / max_possible_score) * 100))
    
    # Compile final assessment
    if not any([indicators['coordinated_timing'], indicators['source_clustering'], 
                indicators['sentiment_uniformity'], indicators['sudden_spike'], indicators['language_uniformity']]):
        indicators['explanation'] = 'No significant manipulation indicators detected - coverage appears organic with healthy diversity'
        indicators['confidence_score'] = 0
    else:
        if not indicators['explanation']:
            indicators['explanation'] = 'Analysis complete'
        else:
            indicators['explanation'] = ' | '.join(indicators['explanation'])
    
    # Add risk level assessment
    if indicators['confidence_score'] >= 70:
        indicators['risk_level'] = 'HIGH'
        indicators['recommendation'] = 'Critical: Multiple strong manipulation indicators present. Cross-check with independent international sources and alternative media.'
    elif indicators['confidence_score'] >= 40:
        indicators['risk_level'] = 'MEDIUM'
        indicators['recommendation'] = 'Caution: Some manipulation patterns detected. Seek additional perspectives and verify key claims independently.'
    else:
        indicators['risk_level'] = 'LOW'
        indicators['recommendation'] = 'Normal: Coverage appears relatively organic. Standard media literacy practices apply.'
    
    return indicators


def analyze_source_clustering(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced analysis of source patterns and narrative angles with deeper insights."""
    source_analysis = {
        'total_sources': 0,
        'unique_sources': 0,
        'top_sources': [],
        'source_distribution': {},
        'narrative_clusters': [],
        'diversity_metrics': {},
        'source_credibility': {},
        'geographic_distribution': {}
    }
    
    if not articles:
        return source_analysis
    
    # Count and categorize sources
    sources = [a.get('source', 'Unknown') for a in articles]
    source_counts = Counter(sources)
    
    source_analysis['total_sources'] = len(sources)
    source_analysis['unique_sources'] = len(source_counts)
    source_analysis['top_sources'] = source_counts.most_common(10)
    source_analysis['source_distribution'] = dict(source_counts)
    
    # Calculate diversity metrics
    if len(sources) > 0:
        # Herfindahl-Hirschman Index (measure of concentration, 0-1)
        # Lower = more diverse, Higher = more concentrated
        market_shares = [count / len(sources) for count in source_counts.values()]
        hhi = sum(share ** 2 for share in market_shares)
        
        source_analysis['diversity_metrics'] = {
            'concentration_index': round(hhi, 3),
            'diversity_score': round((1 - hhi) * 100, 1),  # Convert to 0-100 scale
            'interpretation': (
                'Excellent diversity' if hhi < 0.15 else
                'Good diversity' if hhi < 0.25 else
                'Moderate diversity' if hhi < 0.40 else
                'Low diversity - concentrated sources' if hhi < 0.60 else
                'Very low diversity - possible echo chamber'
            ),
            'unique_to_total_ratio': round(len(source_counts) / len(sources), 2)
        }
    
    # Enhanced narrative clustering with more sophisticated analysis
    negative_sources = defaultdict(list)
    positive_sources = defaultdict(list)
    neutral_sources = defaultdict(list)
    alarmist_sources = defaultdict(list)
    dismissive_sources = defaultdict(list)
    
    # Expanded keyword sets for better detection
    negative_keywords = ['crisis', 'scandal', 'controversy', 'issue', 'problem', 'concern', 'critical', 
                         'failure', 'threat', 'danger', 'risk', 'alarming', 'troubling', 'devastating']
    positive_keywords = ['success', 'achievement', 'growth', 'progress', 'improve', 'win', 'victory', 
                         'breakthrough', 'triumph', 'advancement', 'innovation', 'excellence']
    alarmist_keywords = ['urgent', 'crisis', 'emergency', 'catastrophe', 'disaster', 'shocking', 'alarming']
    dismissive_keywords = ['overblown', 'exaggerated', 'myth', 'false alarm', 'nothing to see']
    
    for article in articles:
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        title_lower = (title + ' ' + description).lower()
        source = article.get('source', 'Unknown')
        
        # Count keyword matches for more accurate classification
        neg_count = sum(1 for k in negative_keywords if k in title_lower)
        pos_count = sum(1 for k in positive_keywords if k in title_lower)
        alarm_count = sum(1 for k in alarmist_keywords if k in title_lower)
        dismiss_count = sum(1 for k in dismissive_keywords if k in title_lower)
        
        # Classify based on dominant sentiment
        if alarm_count >= 2:
            alarmist_sources[source].append(title[:60])
        elif dismiss_count >= 1:
            dismissive_sources[source].append(title[:60])
        elif neg_count > pos_count and neg_count >= 1:
            negative_sources[source].append(title[:60])
        elif pos_count > neg_count and pos_count >= 1:
            positive_sources[source].append(title[:60])
        else:
            neutral_sources[source].append(title[:60])
    
    # Build narrative clusters with examples
    if alarmist_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Alarmist/Sensational',
            'description': 'Using urgent, crisis language to amplify importance',
            'sources': list(alarmist_sources.keys()),
            'count': sum(len(v) for v in alarmist_sources.values()),
            'examples': [titles[0] for titles in list(alarmist_sources.values())[:3]],
            'manipulation_risk': 'High - emotional language designed to provoke reaction'
        })
    
    if negative_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Negative/Critical',
            'description': 'Emphasizing problems, failures, or concerns',
            'sources': list(negative_sources.keys()),
            'count': sum(len(v) for v in negative_sources.values()),
            'examples': [titles[0] for titles in list(negative_sources.values())[:3]],
            'manipulation_risk': 'Medium - may be justified criticism or manufactured negativity'
        })
    
    if positive_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Positive/Supportive',
            'description': 'Highlighting achievements, progress, or success',
            'sources': list(positive_sources.keys()),
            'count': sum(len(v) for v in positive_sources.values()),
            'examples': [titles[0] for titles in list(positive_sources.values())[:3]],
            'manipulation_risk': 'Medium - may be genuine good news or promotional content'
        })
    
    if dismissive_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Dismissive/Minimizing',
            'description': 'Downplaying significance or contradicting other narratives',
            'sources': list(dismissive_sources.keys()),
            'count': sum(len(v) for v in dismissive_sources.values()),
            'examples': [titles[0] for titles in list(dismissive_sources.values())[:3]],
            'manipulation_risk': 'Medium - either debunking or defensive spin'
        })
    
    if neutral_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Neutral/Factual',
            'description': 'Balanced reporting without clear emotional framing',
            'sources': list(neutral_sources.keys()),
            'count': sum(len(v) for v in neutral_sources.values()),
            'examples': [titles[0] for titles in list(neutral_sources.values())[:3]],
            'manipulation_risk': 'Low - appears objective'
        })
    
    # Identify potential echo chambers (sources only in one cluster)
    source_to_clusters = defaultdict(set)
    for cluster in source_analysis['narrative_clusters']:
        for source in cluster['sources']:
            source_to_clusters[source].add(cluster['angle'])
    
    echo_chamber_sources = [s for s, clusters in source_to_clusters.items() if len(clusters) == 1]
    balanced_sources = [s for s, clusters in source_to_clusters.items() if len(clusters) > 1]
    
    source_analysis['source_credibility'] = {
        'echo_chamber_sources': echo_chamber_sources[:10],
        'balanced_sources': balanced_sources[:10],
        'credibility_note': f"{len(balanced_sources)} sources show multiple perspectives vs {len(echo_chamber_sources)} show single narrative"
    }
    
    return source_analysis


def analyze_sentiment_map(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced sentiment analysis mapping across platforms, time, and intensity with scoring."""
    sentiment_map = {
        'by_source': {},
        'by_date': {},
        'overall': {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0},
        'intensity_scores': {},
        'emotional_trajectory': [],
        'sentiment_shifts': []
    }
    
    # Expanded and weighted keyword sets
    negative_keywords = {
        'strong': ['crisis', 'scandal', 'disaster', 'catastrophe', 'devastating', 'alarming', 'shocking', 'outrage'],
        'moderate': ['controversy', 'issue', 'problem', 'concern', 'critical', 'failure', 'threat', 'danger'],
        'mild': ['question', 'doubt', 'challenge', 'difficulty', 'setback']
    }
    
    positive_keywords = {
        'strong': ['breakthrough', 'triumph', 'revolutionary', 'excellent', 'outstanding', 'phenomenal'],
        'moderate': ['success', 'achievement', 'growth', 'progress', 'improve', 'win', 'victory'],
        'mild': ['better', 'good', 'positive', 'forward', 'advance']
    }
    
    for article in articles:
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        text_lower = (title + ' ' + description).lower().strip()
        source = article.get('source', '') or 'Unknown'
        date = article.get('published_date', '')[:10] if article.get('published_date') else 'Unknown'
        
        # Calculate sentiment with intensity scoring
        neg_score = 0
        pos_score = 0
        
        # Weight negative sentiment
        neg_score += sum(3 for k in negative_keywords['strong'] if k in text_lower)
        neg_score += sum(2 for k in negative_keywords['moderate'] if k in text_lower)
        neg_score += sum(1 for k in negative_keywords['mild'] if k in text_lower)
        
        # Weight positive sentiment
        pos_score += sum(3 for k in positive_keywords['strong'] if k in text_lower)
        pos_score += sum(2 for k in positive_keywords['moderate'] if k in text_lower)
        pos_score += sum(1 for k in positive_keywords['mild'] if k in text_lower)
        
        # Determine sentiment category and intensity
        if neg_score > 0 and pos_score > 0:
            sentiment = 'mixed'
            intensity = min(10, neg_score + pos_score)
        elif neg_score > pos_score:
            sentiment = 'negative'
            intensity = min(10, neg_score)
        elif pos_score > neg_score:
            sentiment = 'positive'
            intensity = min(10, pos_score)
        else:
            sentiment = 'neutral'
            intensity = 0
        
        # Update source-based map with intensity
        if source not in sentiment_map['by_source']:
            sentiment_map['by_source'][source] = {
                'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0,
                'total': 0, 'avg_intensity': 0, 'intensity_sum': 0
            }
        
        sentiment_map['by_source'][source][sentiment] += 1
        sentiment_map['by_source'][source]['total'] += 1
        sentiment_map['by_source'][source]['intensity_sum'] += intensity
        sentiment_map['by_source'][source]['avg_intensity'] = round(
            sentiment_map['by_source'][source]['intensity_sum'] / sentiment_map['by_source'][source]['total'], 1
        )
        
        # Update date-based map
        if date not in sentiment_map['by_date']:
            sentiment_map['by_date'][date] = {
                'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0,
                'avg_intensity': 0, 'intensity_sum': 0, 'count': 0
            }
        
        sentiment_map['by_date'][date][sentiment] += 1
        sentiment_map['by_date'][date]['intensity_sum'] += intensity
        sentiment_map['by_date'][date]['count'] += 1
        sentiment_map['by_date'][date]['avg_intensity'] = round(
            sentiment_map['by_date'][date]['intensity_sum'] / sentiment_map['by_date'][date]['count'], 1
        )
        
        # Update overall
        sentiment_map['overall'][sentiment] += 1
        
        # Track intensity by article
        if intensity > 0:
            if source not in sentiment_map['intensity_scores']:
                sentiment_map['intensity_scores'][source] = []
            sentiment_map['intensity_scores'][source].append({
                'title': title[:60],
                'sentiment': sentiment,
                'intensity': intensity,
                'date': date
            })
    
    # Calculate emotional trajectory over time
    sorted_dates = sorted(sentiment_map['by_date'].keys())
    for date in sorted_dates:
        day_data = sentiment_map['by_date'][date]
        sentiment_map['emotional_trajectory'].append({
            'date': date,
            'dominant_sentiment': max(
                [(k, v) for k, v in day_data.items() if k in ['positive', 'negative', 'neutral', 'mixed']],
                key=lambda x: x[1],
                default=('neutral', 0)
            )[0],
            'intensity': day_data['avg_intensity'],
            'article_count': day_data['count']
        })
    
    # Detect sentiment shifts (day-to-day changes)
    for i in range(1, len(sentiment_map['emotional_trajectory'])):
        prev = sentiment_map['emotional_trajectory'][i-1]
        curr = sentiment_map['emotional_trajectory'][i]
        
        if prev['dominant_sentiment'] != curr['dominant_sentiment']:
            sentiment_map['sentiment_shifts'].append({
                'from_date': prev['date'],
                'to_date': curr['date'],
                'shift': f"{prev['dominant_sentiment']} → {curr['dominant_sentiment']}",
                'intensity_change': round(curr['intensity'] - prev['intensity'], 1)
            })
    
    # Calculate overall sentiment metrics
    total_articles = sum(sentiment_map['overall'].values())
    if total_articles > 0:
        sentiment_map['overall_metrics'] = {
            'positive_pct': round((sentiment_map['overall']['positive'] / total_articles) * 100, 1),
            'negative_pct': round((sentiment_map['overall']['negative'] / total_articles) * 100, 1),
            'neutral_pct': round((sentiment_map['overall']['neutral'] / total_articles) * 100, 1),
            'mixed_pct': round((sentiment_map['overall']['mixed'] / total_articles) * 100, 1),
            'polarization_index': round(abs(
                (sentiment_map['overall']['positive'] - sentiment_map['overall']['negative']) / total_articles
            ), 2)
        }
    
    return sentiment_map


def generate_export_data(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive export data for research."""
    export_data = {
        'metadata': {
            'export_date': datetime.utcnow().isoformat(),
            'platform': 'DataHalo URL Narrative Analyzer',
            'version': '2.0',
            'citation': f"DataHalo. ({datetime.utcnow().year}). URL-Based Narrative Analysis. Retrieved from https://datahalo.vercel.app",
            'recommended_citation': "For academic use: DataHalo. (YEAR). URL-Based Narrative Analysis: [Article Title]. DataHalo Narrative Analyzer. https://datahalo.vercel.app/narrative-analyzer"
        },
        'analysis': analysis_result,
        'research_notes': {
            'methodology': 'Multi-source article aggregation with AI-powered pattern recognition',
            'data_sources': 'NewsAPI, Web Scraping, MongoDB',
            'limitations': 'Analysis limited to English language articles and available data sources',
            'use_cases': [
                'Academic research on media narratives',
                'Journalism studies and media literacy',
                'UPSC exam preparation and current affairs analysis',
                'Dissertation and thesis research',
                'Media manipulation detection studies'
            ]
        }
    }
    
    return export_data


def get_overall_sentiment(sentiment_map: Dict[str, Any]) -> str:
    positive = sentiment_map.get('overall', {}).get('positive', 0)
    negative = sentiment_map.get('overall', {}).get('negative', 0)
    neutral = sentiment_map.get('overall', {}).get('neutral', 0)

    if positive > negative and positive > neutral:
        return "Positive"
    elif negative > positive and negative > neutral:
        return "Negative"
    else:
        return "Neutral"


def _build_key_narratives(source_clustering: Dict[str, Any], timeline: List[Dict[str, Any]], articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build key narratives from source clustering data."""
    key_narratives = []
    
    narrative_clusters = source_clustering.get('narrative_clusters', [])
    
    for cluster in narrative_clusters[:5]:
        # Get first and peak dates from timeline
        first_date = timeline[-1]['date'] if timeline else "Unknown"
        peak_date = max(timeline, key=lambda x: x['count'])['date'] if timeline else "Unknown"
        
        key_narratives.append({
            "narrative": f"{cluster.get('angle', 'Coverage')} narrative across {cluster.get('count', 0)} articles",
            "frequency": cluster.get('count', 0),
            "sources": cluster.get('sources', [])[:10],  # Limit to 10 sources
            "firstAppeared": first_date,
            "peakDate": peak_date
        })
    
    # If no clusters, create a default one
    if not key_narratives and articles:
        sources = list(set([a.get('source', 'Unknown') for a in articles]))[:10]
        first_date = timeline[-1]['date'] if timeline else "Unknown"
        peak_date = max(timeline, key=lambda x: x['count'])['date'] if timeline else "Unknown"
        
        key_narratives.append({
            "narrative": f"Coverage of {articles[0].get('title', 'this story')[:50]}...",
            "frequency": len(articles),
            "sources": sources,
            "firstAppeared": first_date,
            "peakDate": peak_date
        })
    
    return key_narratives


def _extract_related_topics(articles: List[Dict[str, Any]]) -> List[str]:
    """Extract related topics from articles."""
    # Extract common words from titles
    all_words = []
    stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'this', 'that', 'with', 'from', 'by'}
    
    for article in articles:
        title = article.get('title', '').lower()
        words = re.findall(r'\b[a-z]{4,}\b', title)
        all_words.extend([w for w in words if w not in stopwords])
    
    # Get most common words
    word_counts = Counter(all_words)
    related_topics = [word.title() for word, count in word_counts.most_common(8) if count > 1]
    
    return related_topics if related_topics else ["News", "Media", "Coverage"]


async def analyze_url_narrative(url: str, serp_api_key: str, ai_api_key: str, days: int = 14) -> Dict[str, Any]:
    """
    Main function to perform comprehensive URL-based narrative analysis
    
    Args:
        url: The article URL to analyze
        serp_api_key: SerpAPI key for finding related articles  
        ai_api_key: NVIDIA API key for AI analysis
        days: Number of days to look back for related articles
    
    Returns:
        Complete analysis including AI insights, timeline, manipulation detection, sentiment mapping, and source clustering
    """
    try:
        logger.info(f"SEARCH: Starting comprehensive URL narrative analysis for: {url}")
        
        # Step 1: Extract article content from URL
        logger.info("FILE: Step 1: Extracting article content...")
        original_article = extract_article_content(url)
        
        if not original_article.get("success") or not original_article.get("title"):
            raise ValueError(f"Could not extract article content from URL: {original_article.get('error', 'Unknown error')}")
        
        logger.info(f"SUCCESS: Article extracted: '{original_article['title'][:60]}...' ({original_article.get('word_count', 0)} words)")
        
        # Step 2: AI Analysis of the original article
        logger.info("AI: Step 2: Performing AI analysis of article content...")
        ai_analysis = await analyze_article_with_ai(original_article, ai_api_key)
        
        # Step 3: Find related articles across different outlets
        logger.info(f"FIND: Step 3: Searching for related articles (last {days} days)...")
        related_articles = find_related_articles(original_article, days, serp_api_key)
        logger.info(f"SUCCESS: Found {len(related_articles)} related articles")
        
        # Combine original with related articles
        all_articles = [original_article] + related_articles
        
        # Step 4: Analyze timeline
        logger.info("📅 Step 4: Analyzing coverage timeline...")
        timeline = analyze_timeline(all_articles)
        
        # Step 5: Detect manipulation indicators
        logger.info("SEARCH: Step 5: Detecting manipulation indicators...")
        manipulation_indicators = detect_manipulation(all_articles, timeline)
        
        # Step 6: Analyze sentiment mapping
        logger.info("😊 Step 6: Mapping sentiment across sources...")
        sentiment_map = analyze_sentiment_map(all_articles)
        
        # Step 7: Analyze source clustering
        logger.info("NEWS: Step 7: Analyzing source clusters and narrative angles...")
        source_clustering = analyze_source_clustering(all_articles)
        
        # Step 8: Compile comprehensive analysis with clear explanations
        logger.info("STATS: Step 8: Compiling comprehensive analysis...")
        
        # Build clear narrative explanations
        coverage_scale = len(all_articles)
        coverage_description = (
            f"This story has {coverage_scale} articles across {source_clustering.get('total_sources', 0)} sources. "
            f"{'Major coverage' if coverage_scale > 20 else 'Moderate coverage' if coverage_scale > 10 else 'Limited coverage'} "
            f"indicates this is {'a highly significant' if coverage_scale > 20 else 'an important' if coverage_scale > 10 else 'an emerging'} narrative."
        )
        
        # Sentiment explanation
        overall_sentiment = get_overall_sentiment(sentiment_map)
        sentiment_counts = sentiment_map.get('overall', {})
        sentiment_description = (
            f"Overall sentiment is {overall_sentiment}. "
            f"Analysis shows {sentiment_counts.get('positive', 0)} positive, "
            f"{sentiment_counts.get('negative', 0)} negative, and "
            f"{sentiment_counts.get('neutral', 0)} neutral articles. "
            f"This {'' if overall_sentiment == 'Neutral' else 'non-'}balanced coverage suggests "
            f"{'varied perspectives' if overall_sentiment == 'Neutral' else 'a dominant narrative angle'}."
        )
        
        # Timeline description
        timeline_description = ""
        if timeline and len(timeline) > 1:
            first_date = timeline[-1]['date']
            latest_date = timeline[0]['date']
            peak = max(timeline, key=lambda x: x['count'])
            timeline_description = (
                f"Coverage spans from {first_date} to {latest_date}. "
                f"Peak coverage was on {peak['date']} with {peak['count']} articles. "
                f"{'Coverage is accelerating' if timeline[0]['count'] > timeline[-1]['count'] else 'Coverage is declining'}."
            )
        
        analysis_result = {
            "url": url,
            "title": original_article.get("title"),
            "source": original_article.get("source"),
            "author": original_article.get("author"),
            "publishedDate": original_article.get("published_date"),
            "mainTopic": original_article.get("main_topic"),
            "wordCount": original_article.get("word_count"),
            
            # AI Insights - THE KEY ADDITION
            "articleInsights": {
                **ai_analysis,
                "extraction_quality": "high" if original_article.get('word_count', 0) > 500 else "moderate",
                "readability": "detailed analysis" if original_article.get('word_count', 0) > 800 else "standard article"
            },
            
            # Coverage summary with clear explanations
            "coverageSummary": {
                "totalArticles": len(all_articles),
                "relatedArticles": len(related_articles),
                "totalSources": source_clustering.get('total_sources', 0),
                "timeframe": f"{days} days",
                "description": coverage_description,
                "sentimentDescription": sentiment_description,
                "timelineDescription": timeline_description
            },
            
            # Narrative pattern
            "narrativePattern": {
                "rising": len(all_articles) > 10,
                "trend": "Rising" if len(all_articles) > 20 else "Stable" if len(all_articles) > 10 else "Emerging",
                "sentiment": overall_sentiment,
                "intensity": min(100, len(all_articles) * 5)  # Scale intensity based on coverage
            },
            
            # Timeline with explanations
            "timeline": timeline[:10],  # Limit to recent 10 points
            
            # Key narratives (extracted from source clusters)
            "keyNarratives": _build_key_narratives(source_clustering, timeline, all_articles),
            
            # Manipulation indicators with detailed explanations
            "manipulation_indicators": {
                **manipulation_indicators,
                "overall_assessment": (
                    "WARNING: Multiple manipulation indicators detected" if sum([
                        manipulation_indicators.get('coordinated_timing', False),
                        manipulation_indicators.get('source_clustering', False),
                        manipulation_indicators.get('sentiment_uniformity', False),
                        manipulation_indicators.get('sudden_spike', False)
                    ]) >= 2 else
                    "WARNING: Some manipulation indicators present" if any([
                        manipulation_indicators.get('coordinated_timing', False),
                        manipulation_indicators.get('source_clustering', False),
                        manipulation_indicators.get('sentiment_uniformity', False),
                        manipulation_indicators.get('sudden_spike', False)
                    ]) else
                    "SUCCESS: No significant manipulation indicators detected"
                )
            },
            
            # Context with better organization
            "context": {
                "majorEvents": [
                    event
                    for point in timeline[:5]
                    for event in point.get('keyEvents', [])
                ][:10],
                "relatedTopics": _extract_related_topics(all_articles)[:8],
                "potentialTriggers": ai_analysis.get('questions_raised', [])[:5] if ai_analysis else [],
                "missingContext": ai_analysis.get('missing_context', [])[:5] if ai_analysis else []
            },
            
            # Detailed source analysis
            "sourceAnalysis": {
                **source_clustering,
                "diversity_score": min(100, source_clustering.get('total_sources', 0) * 10),
                "concentration_risk": "High" if source_clustering.get('total_sources', 0) < 3 else "Moderate" if source_clustering.get('total_sources', 0) < 8 else "Low"
            },
            
            # Detailed sentiment analysis
            "sentimentAnalysis": {
                **sentiment_map,
                "consistency": "uniform" if any([
                    v > 0.8 for v in [
                        sentiment_counts.get('positive', 0) / max(sum(sentiment_counts.values()), 1),
                        sentiment_counts.get('negative', 0) / max(sum(sentiment_counts.values()), 1),
                        sentiment_counts.get('neutral', 0) / max(sum(sentiment_counts.values()), 1)
                    ]
                ]) else "varied"
            },
            
            # Original article details
            "originalArticle": {
                "title": original_article.get("title"),
                "url": url,
                "source": original_article.get("source"),
                "author": original_article.get("author"),
                "published": original_article.get("published_date"),
                "description": original_article.get("description", "")[:300],
                "keywords": original_article.get("keywords", [])[:10],
                "excerpt": original_article.get("content", "")[:500]
            },
            
            # Research utility
            "researchNotes": {
                "dataQuality": "high" if len(all_articles) > 10 else "moderate" if len(all_articles) > 5 else "limited",
                "analysisConfidence": "high" if len(all_articles) > 15 and source_clustering.get('total_sources', 0) > 5 else "moderate",
                "recommendedActions": _generate_recommendations(len(all_articles), source_clustering, manipulation_indicators)
            }
        }
        
        # Step 9: Generate export data for researchers
        logger.info("📦 Step 9: Generating export data...")
        export_data = generate_export_data(analysis_result)
        
        logger.info(f"SUCCESS: URL narrative analysis complete! {len(all_articles)} articles analyzed across {source_clustering.get('total_sources', 0)} sources")
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "export": export_data
        }
        
    except Exception as e:
        import traceback
        logger.error(f"ERROR: URL narrative analysis failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def _generate_recommendations(article_count: int, source_clustering: Dict, manipulation_indicators: Dict) -> List[str]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    if article_count < 5:
        recommendations.append("Limited data - consider expanding timeframe or search terms")
    
    if source_clustering.get('total_sources', 0) < 3:
        recommendations.append("Low source diversity - verify information with additional sources")
    
    if manipulation_indicators.get('sentiment_uniformity'):
        recommendations.append("Uniform sentiment detected - seek alternative perspectives")
    
    if manipulation_indicators.get('coordinated_timing'):
        recommendations.append("Coordinated timing detected - investigate source relationships")
    
    if not recommendations:
        recommendations.append("Analysis shows healthy media coverage with good source diversity")
    
    return recommendations
