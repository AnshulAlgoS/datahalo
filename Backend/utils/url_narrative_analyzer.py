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
        
        # Extract article body (improved)
        article_body = []
        
        # Try article tag first
        article_tag = soup.find('article')
        if article_tag:
            paragraphs = article_tag.find_all('p')
        else:
            paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:  # Only substantial paragraphs
                article_body.append(text)
        
        # Get full content (first 15 paragraphs for better context)
        content = ' '.join(article_body[:15])
        
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
        
        logger.info(f"✅ Extracted article: '{title[:60]}...' from {source}")
        
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
            'word_count': len(content.split()),
            'success': True
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
    """Use AI to deeply analyze the article content and extract key insights."""
    if not ai_api_key:
        return {}
    
    try:
        # Build detailed prompt for article analysis
        prompt = f"""Analyze this news article in detail:

Title: {article.get('title', '')}
Source: {article.get('source', '')}
Content: {article.get('content', '')[:2000]}

Provide a JSON analysis with:

{{
  "summary": "concise 2-3 sentence summary",
  "key_points": ["point 1", "point 2", "point 3"],
  "main_subjects": ["subject 1", "subject 2"],
  "political_angle": "describe the political/ideological angle if any",
  "tone": "Neutral/Supportive/Critical/Alarmist",
  "credibility_signals": ["signal 1", "signal 2"],
  "potential_biases": ["bias 1", "bias 2"],
  "target_audience": "who this article is aimed at",
  "narrative_framing": "how the story is framed",
  "missing_context": ["what context is missing"],
  "questions_raised": ["what questions does this raise"]
}}

Be specific and cite details from the article."""

        headers = {
            "Authorization": f"Bearer {ai_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "top_p": 0.85,
            "max_tokens": 1500
        }

        logger.info("🤖 Calling AI for article analysis...")
        response = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]

        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            analysis = json.loads(json_match.group(0))
            logger.info("✅ AI article analysis complete")
            return analysis
        else:
            return json.loads(content)
            
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        return {}


def find_related_articles(original_article: Dict[str, Any], days: int = 14) -> List[Dict[str, Any]]:
    """Find related articles about the same story across different outlets."""
    if not NEWS_API_KEY:
        return []
    
    try:
        # Extract key terms from title
        title = original_article['title']
        # Remove common words and extract keywords
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are', 'was', 'were'}
        words = [w for w in re.findall(r'\b\w+\b', title.lower()) if w not in stopwords and len(w) > 3]
        
        # Use top 3 keywords for search
        search_query = ' '.join(words[:3])
        
        logger.info(f"Searching for related articles with query: {search_query}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Search NewsAPI
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
        
        logger.info(f"Found {len(related_articles)} related articles")
        return related_articles
        
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
    """Detect potential manipulation indicators."""
    indicators = {
        'coordinated_timing': False,
        'source_clustering': False,
        'sentiment_uniformity': False,
        'sudden_spike': False,
        'explanation': []
    }
    
    if len(articles) < 3:
        indicators['explanation'] = 'Insufficient data for manipulation analysis'
        return indicators
    
    # 1. Coordinated Timing Detection
    # Check if many articles published within short time window
    dates = [a.get('published_date', '') for a in articles if a.get('published_date')]
    if dates:
        date_hours = defaultdict(int)
        for date_str in dates:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                hour_key = dt.strftime('%Y-%m-%d %H:00')
                date_hours[hour_key] += 1
            except:
                continue
        
        # If 30%+ articles in same hour
        max_in_hour = max(date_hours.values()) if date_hours else 0
        if max_in_hour / len(articles) > 0.3:
            indicators['coordinated_timing'] = True
            indicators['explanation'].append(f"{max_in_hour} articles published in same hour window - possible coordinated release")
    
    # 2. Source Clustering Detection
    # Check if articles dominated by few sources
    sources = [a.get('source', '') for a in articles if a.get('source')]
    if sources:
        source_counts = Counter(sources)
        top_source_count = source_counts.most_common(1)[0][1] if source_counts else 0
        
        # If one source has 40%+ of articles
        if top_source_count / len(sources) > 0.4:
            indicators['source_clustering'] = True
            indicators['explanation'].append(f"One source ({source_counts.most_common(1)[0][0]}) accounts for {top_source_count}/{len(sources)} articles")
    
    # 3. Sentiment Uniformity Detection
    # Check if all articles have same sentiment
    sentiments = [t['sentiment'] for t in timeline if t.get('sentiment')]
    if sentiments:
        sentiment_counts = Counter(sentiments)
        dominant_sentiment_ratio = sentiment_counts.most_common(1)[0][1] / len(sentiments) if sentiment_counts else 0
        
        # If 80%+ articles have same sentiment
        if dominant_sentiment_ratio > 0.8:
            indicators['sentiment_uniformity'] = True
            indicators['explanation'].append(f"{int(dominant_sentiment_ratio*100)}% of coverage has uniform {sentiment_counts.most_common(1)[0][0]} sentiment")
    
    # 4. Sudden Spike Detection
    # Check if there's abnormal spike in coverage
    if timeline and len(timeline) > 2:
        counts = [t['count'] for t in timeline]
        avg_count = sum(counts) / len(counts)
        max_count = max(counts)
        
        # If spike is 3x average
        if max_count > avg_count * 3:
            indicators['sudden_spike'] = True
            indicators['explanation'].append(f"Sudden spike of {max_count} articles on {timeline[counts.index(max_count)]['date']} (3x average)")
    
    # Compile explanation
    if not any([indicators['coordinated_timing'], indicators['source_clustering'], 
                indicators['sentiment_uniformity'], indicators['sudden_spike']]):
        indicators['explanation'] = 'No manipulation indicators detected in the data'
    else:
        indicators['explanation'] = ' | '.join(indicators['explanation'])
    
    return indicators


def analyze_source_clustering(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze which journalists and outlets are pushing the same angle."""
    source_analysis = {
        'total_sources': 0,
        'top_sources': [],
        'source_distribution': {},
        'narrative_clusters': []
    }
    
    if not articles:
        return source_analysis
    
    # Count sources
    sources = [a.get('source', 'Unknown') for a in articles]
    source_counts = Counter(sources)
    
    source_analysis['total_sources'] = len(source_counts)
    source_analysis['top_sources'] = source_counts.most_common(10)
    source_analysis['source_distribution'] = dict(source_counts)
    
    # Detect narrative clusters (sources pushing similar angles)
    # Group by sentiment/keywords
    negative_sources = []
    positive_sources = []
    neutral_sources = []
    
    negative_keywords = ['crisis', 'scandal', 'controversy', 'issue', 'problem']
    positive_keywords = ['success', 'achievement', 'growth', 'progress']
    
    for article in articles:
        title_lower = article.get('title', '').lower()
        source = article.get('source', 'Unknown')
        
        if any(k in title_lower for k in negative_keywords):
            negative_sources.append(source)
        elif any(k in title_lower for k in positive_keywords):
            positive_sources.append(source)
        else:
            neutral_sources.append(source)
    
    if negative_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Negative/Critical',
            'sources': list(set(negative_sources)),
            'count': len(negative_sources)
        })
    
    if positive_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Positive/Supportive',
            'sources': list(set(positive_sources)),
            'count': len(positive_sources)
        })
    
    if neutral_sources:
        source_analysis['narrative_clusters'].append({
            'angle': 'Neutral/Factual',
            'sources': list(set(neutral_sources)),
            'count': len(neutral_sources)
        })
    
    return source_analysis


def analyze_sentiment_map(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Map how sentiment changes across platforms and time."""
    sentiment_map = {
        'by_source': {},
        'by_date': {},
        'overall': {'positive': 0, 'negative': 0, 'neutral': 0}
    }
    
    negative_keywords = ['crisis', 'scandal', 'controversy', 'issue', 'problem', 'concern', 'critical', 'failure']
    positive_keywords = ['success', 'achievement', 'growth', 'progress', 'improve', 'win', 'victory', 'breakthrough']
    
    for article in articles:
        title_lower = article.get('title', '').lower() + ' ' + article.get('description', '').lower()
        source = article.get('source', 'Unknown')
        date = article.get('published_date', '')[:10] if article.get('published_date') else 'Unknown'
        
        # Determine sentiment
        neg_count = sum(1 for k in negative_keywords if k in title_lower)
        pos_count = sum(1 for k in positive_keywords if k in title_lower)
        
        if neg_count > pos_count:
            sentiment = 'negative'
        elif pos_count > neg_count:
            sentiment = 'positive'
        else:
            sentiment = 'neutral'
        
        # Update maps
        if source not in sentiment_map['by_source']:
            sentiment_map['by_source'][source] = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
        sentiment_map['by_source'][source][sentiment] += 1
        sentiment_map['by_source'][source]['total'] += 1
        
        if date not in sentiment_map['by_date']:
            sentiment_map['by_date'][date] = {'positive': 0, 'negative': 0, 'neutral': 0}
        sentiment_map['by_date'][date][sentiment] += 1
        
        sentiment_map['overall'][sentiment] += 1
    
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
        logger.info(f"🔍 Starting comprehensive URL narrative analysis for: {url}")
        
        # Step 1: Extract article content from URL
        logger.info("📄 Step 1: Extracting article content...")
        original_article = extract_article_content(url)
        
        if not original_article.get("success") or not original_article.get("title"):
            raise ValueError(f"Could not extract article content from URL: {original_article.get('error', 'Unknown error')}")
        
        logger.info(f"✅ Article extracted: '{original_article['title'][:60]}...' ({original_article.get('word_count', 0)} words)")
        
        # Step 2: AI Analysis of the original article
        logger.info("🤖 Step 2: Performing AI analysis of article content...")
        ai_analysis = await analyze_article_with_ai(original_article, ai_api_key)
        
        # Step 3: Find related articles across different outlets
        logger.info(f"🔎 Step 3: Searching for related articles (last {days} days)...")
        related_articles = find_related_articles(original_article, days)
        logger.info(f"✅ Found {len(related_articles)} related articles")
        
        # Combine original with related articles
        all_articles = [original_article] + related_articles
        
        # Step 4: Analyze timeline
        logger.info("📅 Step 4: Analyzing coverage timeline...")
        timeline = analyze_timeline(all_articles)
        
        # Step 5: Detect manipulation indicators
        logger.info("🔍 Step 5: Detecting manipulation indicators...")
        manipulation_indicators = detect_manipulation(all_articles, timeline)
        
        # Step 6: Analyze sentiment mapping
        logger.info("😊 Step 6: Mapping sentiment across sources...")
        sentiment_map = analyze_sentiment_map(all_articles)
        
        # Step 7: Analyze source clustering
        logger.info("📰 Step 7: Analyzing source clusters and narrative angles...")
        source_clustering = analyze_source_clustering(all_articles)
        
        # Step 8: Compile comprehensive analysis with clear explanations
        logger.info("📊 Step 8: Compiling comprehensive analysis...")
        
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
                    "⚠️ Multiple manipulation indicators detected" if sum([
                        manipulation_indicators.get('coordinated_timing', False),
                        manipulation_indicators.get('source_clustering', False),
                        manipulation_indicators.get('sentiment_uniformity', False),
                        manipulation_indicators.get('sudden_spike', False)
                    ]) >= 2 else
                    "⚠️ Some manipulation indicators present" if any([
                        manipulation_indicators.get('coordinated_timing', False),
                        manipulation_indicators.get('source_clustering', False),
                        manipulation_indicators.get('sentiment_uniformity', False),
                        manipulation_indicators.get('sudden_spike', False)
                    ]) else
                    "✅ No significant manipulation indicators detected"
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
        
        logger.info(f"✅ URL narrative analysis complete! {len(all_articles)} articles analyzed across {source_clustering.get('total_sources', 0)} sources")
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "export": export_data
        }
        
    except Exception as e:
        import traceback
        logger.error(f"❌ URL narrative analysis failed: {str(e)}")
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
