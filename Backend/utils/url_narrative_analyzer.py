"""
URL-Based Narrative Analyzer
Comprehensive analysis of news stories from URLs including timeline, manipulation detection, and source clustering
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
import os
import re
from collections import Counter, defaultdict

logger = logging.getLogger("url_narrative_analyzer")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


def extract_article_content(url: str) -> Dict[str, Any]:
    """Extract article content and metadata from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = None
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
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
            source = domain.replace('www.', '').replace('.com', '').replace('.in', '').title()
        
        # Extract publish date
        published_date = None
        meta_date = soup.find('meta', attrs={'property': 'article:published_time'}) or soup.find('meta', attrs={'name': 'publishdate'})
        if meta_date:
            published_date = meta_date.get('content', '')
        
        # Extract article body
        article_body = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 50:  # Only substantial paragraphs
                article_body.append(text)
        
        content = ' '.join(article_body[:10])  # First 10 paragraphs
        
        # Extract keywords/tags
        keywords = []
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'}) or soup.find('meta', attrs={'property': 'article:tag'})
        if meta_keywords:
            keywords = [k.strip() for k in meta_keywords.get('content', '').split(',')]
        
        return {
            'url': url,
            'title': title or 'No title found',
            'description': description or content[:500],
            'source': source or 'Unknown Source',
            'published_date': published_date or datetime.utcnow().isoformat(),
            'content': content,
            'keywords': keywords,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {str(e)}")
        return {
            'url': url,
            'success': False,
            'error': str(e)
        }


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
        Complete analysis including timeline, manipulation detection, sentiment mapping, and source clustering
    """
    try:
        # Step 1: Extract article content from URL
        original_article = extract_article_content(url)
        
        if not original_article.get("title"):
            raise ValueError("Could not extract article content from URL")
        
        # Step 2: Find related articles
        related_articles = find_related_articles(original_article, days)
        
        # Combine original with related articles
        all_articles = [original_article] + related_articles
        
        if len(all_articles) < 3:
            # Not enough data for comprehensive analysis
            return {
                "status": "limited_data",
                "analysis": {
                    "url": url,
                    "title": original_article.get("title"),
                    "totalArticles": len(all_articles),
                    "message": "Not enough related articles found for comprehensive analysis",
                    "originalArticle": original_article
                }
            }
        
        # Step 3: Analyze timeline
        timeline = analyze_timeline(all_articles)
        
        # Step 4: Detect manipulation indicators
        manipulation_indicators = detect_manipulation(all_articles, timeline)
        
        # Step 5: Analyze sentiment mapping
        sentiment_map = analyze_sentiment_map(all_articles)
        
        # Step 6: Analyze source clustering
        source_clustering = analyze_source_clustering(all_articles)
        
        # Step 7: Compile comprehensive analysis
        analysis_result = {
            "url": url,
            "title": original_article.get("title"),
            "source": original_article.get("source"),
            "publishedDate": original_article.get("published_date"),
            "totalArticles": len(all_articles),
            "timeframe": f"{days} days",
            
            # Narrative pattern
            "narrativePattern": {
                "rising": len(all_articles) > 10,
                "trend": "Rising" if len(all_articles) > 20 else "Stable" if len(all_articles) > 10 else "Emerging",
                "sentiment": get_overall_sentiment(sentiment_map),
                "intensity": min(100, len(all_articles) * 5)  # Scale intensity based on coverage
            },
            
            # Timeline
            "timeline": timeline[:10],  # Limit to recent 10 points
            
            # Key narratives (extracted from source clusters)
            "keyNarratives": _build_key_narratives(source_clustering, timeline, all_articles),
            
            # Manipulation indicators
            "manipulation_indicators": manipulation_indicators,
            
            # Context
            "context": {
                "majorEvents": [
                    event
                    for point in timeline[:5]
                    for event in point.get('keyEvents', [])
                ][:10],
                "relatedTopics": _extract_related_topics(all_articles)[:8],
                "potentialTriggers": []
            },
            
            # Source details
            "sourceAnalysis": source_clustering,
            
            # Sentiment details
            "sentimentAnalysis": sentiment_map,
            
            # Original article
            "originalArticle": {
                "title": original_article.get("title"),
                "url": url,
                "source": original_article.get("source"),
                "published": original_article.get("published_date"),
                "description": original_article.get("description", "")[:200]
            }
        }
        
        # Step 8: Generate export data
        export_data = generate_export_data(analysis_result)
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "export": export_data
        }
        
    except Exception as e:
        import traceback
        logger.error(f"URL narrative analysis failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
