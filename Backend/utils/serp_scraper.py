"""
WORKING Journalist Case Study Scraper using SERP API
Uses SerpAPI for reliable Google/Bing results + Wikipedia API
NO blocking issues - professional API solution
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize AI client
try:
    ai_client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    logger.info("SUCCESS: AI client initialized")
except Exception as e:
    logger.error(f"ERROR: Failed to initialize AI client: {e}")
    ai_client = None


class WorkingJournalistScraper:
    """
    ACTUALLY WORKING scraper using SERP API (real Google results)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.serp_api_key = SERP_API_KEY
        self.youtube_api_key = YOUTUBE_API_KEY
        
        if not self.serp_api_key:
            logger.warning("WARNING: SERP_API_KEY not configured")
    
    def serp_google_search(self, query: str, max_results: int = 30) -> List[Dict[str, str]]:
        """
        Use SERP API to get real Google search results
        100% reliable, no blocking
        """
        if not self.serp_api_key:
            logger.warning("WARNING: SERP API key not available")
            return []
        
        try:
            logger.info(f"SEARCH: SERP API Google: {query}")
            
            url = "https://serpapi.com/search"
            params = {
                'api_key': self.serp_api_key,
                'q': query,
                'engine': 'google',
                'num': max_results,
                'hl': 'en',
                'gl': 'us'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Get organic results
                for result in data.get('organic_results', []):
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'source': 'serp_api_google'
                    })
                
                # Also get news results if available
                for result in data.get('news_results', []):
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'source': 'serp_api_news'
                    })
                
                logger.info(f"SUCCESS: SERP API found {len(results)} results")
                return results
            else:
                logger.warning(f"WARNING: SERP API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"ERROR: SERP API failed: {e}")
            return []
    
    def get_journalist_image(self, journalist_name: str) -> Optional[str]:
        """
        Scrape journalist's image from Google Images or Wikipedia
        """
        try:
            logger.info(f"📸 Searching for journalist image: {journalist_name}")
            
            # Method 1: Use SERP API to get Google Images (most reliable)
            if self.serp_api_key:
                try:
                    url = "https://serpapi.com/search"
                    params = {
                        'api_key': self.serp_api_key,
                        'q': f'{journalist_name} journalist',
                        'engine': 'google_images',
                        'num': 5,
                        'hl': 'en'
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        images = data.get('images_results', [])
                        if images:
                            # Get the first high-quality image
                            image_url = images[0].get('original', '')
                            if image_url:
                                logger.info(f"SUCCESS: Found Google image via SERP API")
                                return image_url
                except Exception as e:
                    logger.debug(f"SERP API Images failed: {e}")
            
            # Method 2: Try Wikipedia image as fallback
            try:
                api_url = "https://en.wikipedia.org/w/api.php"
                search_params = {
                    'action': 'opensearch',
                    'search': journalist_name,
                    'limit': 1,
                    'namespace': 0,
                    'format': 'json'
                }
                
                response = self.session.get(api_url, params=search_params, timeout=10)
                if response.status_code == 200 and response.text.strip():
                    search_data = response.json()
                    
                    if search_data and len(search_data) > 1 and search_data[1]:
                        page_title = search_data[1][0]
                        
                        # Get page image
                        image_params = {
                            'action': 'query',
                            'titles': page_title,
                            'prop': 'pageimages',
                            'piprop': 'original',
                            'format': 'json'
                        }
                        
                        image_response = self.session.get(api_url, params=image_params, timeout=10)
                        if image_response.status_code == 200 and image_response.text.strip():
                            image_data = image_response.json()
                            
                            pages = image_data.get('query', {}).get('pages', {})
                            if pages:
                                page = list(pages.values())[0]
                                image_url = page.get('original', {}).get('source', '')
                                if image_url:
                                    logger.info(f"SUCCESS: Found Wikipedia image")
                                    return image_url
            except Exception as e:
                logger.debug(f"Wikipedia image search failed: {e}")
            
            logger.info(f"WARNING: No image found for {journalist_name}")
            return None
            
        except Exception as e:
            logger.error(f"ERROR: Image search failed: {e}")
            return None
    
    def wikipedia_api(self, journalist_name: str) -> Optional[Dict[str, Any]]:
        """
        Wikipedia API - always works - WITH IMAGE
        """
        try:
            logger.info(f"BOOK: Wikipedia: {journalist_name}")
            
            api_url = "https://en.wikipedia.org/w/api.php"
            
            # Search
            search_params = {
                'action': 'opensearch',
                'search': journalist_name,
                'limit': 5,
                'namespace': 0,
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=search_params, timeout=10)
            
            # Check if response is valid JSON
            if response.status_code != 200 or not response.text.strip():
                logger.warning(f"WARNING: Wikipedia returned empty response")
                return None
                
            search_data = response.json()
            
            if not search_data or len(search_data) < 2 or not search_data[1]:
                logger.warning(f"WARNING: No Wikipedia results for {journalist_name}")
                return None
            
            page_title = search_data[1][0]
            page_url = search_data[3][0] if len(search_data) > 3 else ""
            
            # Get full content
            content_params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'extracts|info|pageimages',
                'exintro': False,
                'explaintext': True,
                'inprop': 'url',
                'piprop': 'original',
                'format': 'json'
            }
            
            content_response = self.session.get(api_url, params=content_params, timeout=10)
            
            if content_response.status_code != 200 or not content_response.text.strip():
                logger.warning(f"WARNING: Wikipedia content returned empty")
                return None
                
            content_data = content_response.json()
            
            pages = content_data.get('query', {}).get('pages', {})
            if not pages:
                return None
                
            page = list(pages.values())[0]
            
            # Get image from Wikipedia
            image_url = page.get('original', {}).get('source', '')
            
            return {
                'title': page_title,
                'extract': page.get('extract', ''),
                'url': page_url,
                'image': image_url,
                'source': 'wikipedia'
            }
            
        except Exception as e:
            logger.error(f"ERROR: Wikipedia failed: {e}")
            return None
    
    def youtube_search(self, journalist_name: str) -> List[Dict[str, str]]:
        """
        Search YouTube for interviews, talks, and videos
        """
        try:
            logger.info(f"🎥 YouTube search: {journalist_name}")
            
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'key': self.youtube_api_key,
                'q': f'{journalist_name} interview journalist',
                'part': 'snippet',
                'type': 'video',
                'maxResults': 15,
                'order': 'relevance'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    snippet = item.get('snippet', {})
                    video_id = item.get('id', {}).get('videoId')
                    
                    if video_id:
                        videos.append({
                            'title': snippet.get('title', ''),
                            'description': snippet.get('description', ''),
                            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                            'url': f'https://www.youtube.com/watch?v={video_id}',
                            'channel': snippet.get('channelTitle', ''),
                            'published': snippet.get('publishedAt', ''),
                            'source': 'youtube'
                        })
                
                logger.info(f"SUCCESS: YouTube found {len(videos)} videos")
                return videos
            else:
                logger.warning(f"WARNING: YouTube API returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"ERROR: YouTube search failed: {e}")
            return []
    
    def scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape article content using BeautifulSoup - WITH IMAGES
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ""
            for selector in ['h1', 'meta[property="og:title"]', 'title']:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get('content', elem.get_text(strip=True))
                    if title:
                        break
            
            # Extract featured image
            image_url = ""
            for selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]']:
                elem = soup.select_one(selector)
                if elem:
                    image_url = elem.get('content', '')
                    if image_url:
                        break
            
            # Extract author and date
            author = ""
            published_date = ""
            
            for selector in ['meta[name="author"]', 'meta[property="article:author"]']:
                elem = soup.select_one(selector)
                if elem:
                    author = elem.get('content', '')
                    if author:
                        break
            
            for selector in ['meta[property="article:published_time"]', 'time']:
                elem = soup.select_one(selector)
                if elem:
                    published_date = elem.get('content', elem.get('datetime', elem.get_text(strip=True)))
                    if published_date:
                        break
            
            # Extract content
            content = ""
            for selector in ['article', 'div.article-content', 'div.story-body', 'main']:
                elem = soup.select_one(selector)
                if elem:
                    for tag in elem.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                        tag.decompose()
                    
                    paragraphs = elem.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                        break
            
            word_count = len(content.split()) if content else 0
            
            if word_count > 50:
                return {
                    'url': url,
                    'domain': urlparse(url).netloc,
                    'title': title,
                    'content': content[:2000],
                    'word_count': word_count,
                    'image': image_url,
                    'author': author,
                    'published_date': published_date
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Scrape failed {url}: {e}")
            return None
    
    def comprehensive_search(self, journalist_name: str) -> Dict[str, Any]:
        """
        Comprehensive search using SERP API + Wikipedia
        """
        try:
            logger.info(f"DATA: === COMPREHENSIVE SEARCH: {journalist_name} ===")
            
            all_data = {
                'journalist_name': journalist_name,
                'sections': {},
                'metadata': {
                    'sources_used': [],
                    'total_results': 0
                }
            }
            
            # Source 1: Get journalist profile image (Google Images via SERP API)
            journalist_image = self.get_journalist_image(journalist_name)
            if journalist_image:
                all_data['journalist_image'] = journalist_image
                logger.info(f"SUCCESS: Journalist profile image found")
            
            time.sleep(0.3)
            
            # Source 2: Wikipedia (for bio and fallback image)
            wikipedia_data = self.wikipedia_api(journalist_name)
            if wikipedia_data and wikipedia_data.get('extract'):
                all_data['sections']['wikipedia'] = wikipedia_data
                all_data['metadata']['sources_used'].append('Wikipedia')
                all_data['metadata']['total_results'] += 1
                logger.info(f"SUCCESS: Wikipedia: Found ({len(wikipedia_data.get('extract', ''))} chars)")
                
                # Use Wikipedia image as fallback if Google Images failed
                if not journalist_image and wikipedia_data.get('image'):
                    all_data['journalist_image'] = wikipedia_data['image']
                    logger.info(f"SUCCESS: Using Wikipedia image as fallback")
            else:
                # Wikipedia failed - use AI knowledge immediately for bio
                logger.warning(f"WARNING: Wikipedia unavailable, using AI for biography")
                if ai_client:
                    try:
                        prompt = f"""Provide a comprehensive 200-word biography of journalist {journalist_name} including:
- Career background and current position
- Major works and investigations
- Awards and recognition
- Impact on journalism

Be factual and specific."""

                        response = ai_client.chat.completions.create(
                            model="qwen/qwen3-coder-480b-a35b-instruct",
                            messages=[
                                {"role": "system", "content": "You are a journalism research expert."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.2,
                            max_tokens=400,
                            timeout=30
                        )
                        
                        ai_bio = response.choices[0].message.content.strip()
                        all_data['sections']['wikipedia'] = {
                            'extract': ai_bio,
                            'source': 'AI Knowledge'
                        }
                        all_data['metadata']['sources_used'].append('AI Knowledge (Bio)')
                        all_data['metadata']['total_results'] += 1
                        logger.info(f"SUCCESS: Using AI biography as fallback")
                    except Exception as e:
                        logger.error(f"AI bio fallback failed: {e}")
            
            time.sleep(0.2)  # Reduced delay
            
            # Source 3: OPTIMIZED SERP searches for articles (fewer queries, less delay)
            search_queries = [
                f'"{journalist_name}" journalist biography',
                f'"{journalist_name}" major works career',
                f'"{journalist_name}" awards recognition',
            ]
            
            all_articles = []
            seen_urls = set()
            
            for query in search_queries:
                results = self.serp_google_search(query, max_results=12)  # Reduced from 15
                
                if results:
                    all_data['metadata']['sources_used'].append(f'Google ({query[:40]}...)')
                    
                    for result in results[:10]:  # Only process top 10 per query
                        if result['url'] not in seen_urls:
                            # Keep result WITHOUT scraping for speed
                            all_articles.append({
                                'url': result['url'],
                                'title': result['title'],
                                'snippet': result['snippet'],
                                'domain': urlparse(result['url']).netloc,
                                'search_query': query
                            })
                            
                            seen_urls.add(result['url'])
                
                time.sleep(0.3)  # REDUCED from 0.5s for speed
                
                if len(all_articles) >= 20:  # Reduced from 25
                    break
            
            if all_articles:
                all_data['sections']['articles'] = all_articles[:20]
                all_data['metadata']['total_results'] += len(all_articles)
                logger.info(f"SUCCESS: Collected {len(all_articles)} articles")
            
            # Source 4: YouTube Videos (OPTIONAL - skip if taking too long)
            try:
                logger.info("🎥 Searching YouTube...")
                youtube_videos = self.youtube_search(journalist_name)
                if youtube_videos:
                    all_data['sections']['youtube_videos'] = youtube_videos[:5]  # Limit to 5
                    all_data['metadata']['sources_used'].append('YouTube')
                    all_data['metadata']['total_results'] += len(youtube_videos[:5])
                    logger.info(f"SUCCESS: Found {len(youtube_videos[:5])} YouTube videos")
            except Exception as e:
                logger.warning(f"YouTube search skipped: {e}")
            
            time.sleep(0.2)  # Minimal delay
            
            logger.info(f"\nSUCCESS: === SEARCH COMPLETE ===")
            logger.info(f"STATS: Total: {all_data['metadata']['total_results']} results")
            logger.info(f"STATS: Sources: {', '.join(all_data['metadata']['sources_used'][:3])}")
            
            return all_data
            
        except Exception as e:
            logger.error(f"ERROR: Search failed: {e}")
            return None
    
    def generate_case_study(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI case study - OPTIMIZED for speed while keeping comprehensive output
        """
        if not ai_client:
            return None
        
        try:
            journalist_name = data['journalist_name']
            sections = data['sections']
            
            # ULTRA-MINIMAL for MAXIMUM SPEED
            bio = sections.get('wikipedia', {}).get('extract', '')[:600]  # Reduced from 800
            

            # Top 3 articles only
            articles = "\n".join([
                f"{i+1}. {a.get('title', 'Untitled')}"
                for i, a in enumerate(sections.get('articles', [])[:3])
            ])
            
            prompt = f"""Create comprehensive educational case study for journalist {journalist_name}.

BIO: {bio}

ARTICLES: {articles}

FORMAT (NO ** symbols):

EXECUTIVE SUMMARY
3-4 paragraphs on career and impact.

CAREER TRAJECTORY & BACKGROUND
Education, early career, rise to prominence.

MAJOR WORKS & IMPACT
• 2-3 major works with publication names and impact

JOURNALISM STYLE & METHODOLOGY
Reporting techniques and approach.

ETHICAL ANALYSIS
Ethical issues and controversies.

INFLUENCE & LEGACY
Impact on journalism field.

LEARNING OBJECTIVES
Students will:
• [7-8 objectives]

CRITICAL THINKING QUESTIONS
1-12. [12 questions]

PRACTICAL APPLICATIONS
• [5-6 exercises]

CONCLUSION
2-3 paragraphs on key lessons.

RECOMMENDED RESOURCES
• List videos and articles

Be comprehensive but concise."""

            logger.info(f"AI: Generating comprehensive case study...")
            
            # FAST RETRY LOGIC - optimized for 1-2 minute response
            max_retries = 2  # Reduced from 3
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"AI: Attempt {attempt}/{max_retries}")
                    
                    response = ai_client.chat.completions.create(
                        model="qwen/qwen3-coder-480b-a35b-instruct",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a journalism educator. Create comprehensive, well-structured case studies."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.2,
                        max_tokens=4000,
                        top_p=0.8,
                        timeout=90  # Increased timeout for larger model
                    )
                    
                    analysis = response.choices[0].message.content.strip()
                    logger.info(f"AI: SUCCESS on attempt {attempt}")
                    break
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if '504' in error_str or 'timeout' in error_str or 'gateway' in error_str:
                        if attempt < max_retries:
                            wait_time = 2  # Quick 2s retry
                            logger.warning(f"AI: Timeout on attempt {attempt}, quick retry in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"AI: All {max_retries} attempts failed with timeout")
                            raise Exception("AI service timeout after retries. Please try again in a few moments.")
                    else:
                        logger.error(f"AI: Non-timeout error: {e}")
                        raise
            
            return {
                'journalist_name': journalist_name,
                'case_study_analysis': analysis,
                'journalist_image': data.get('journalist_image', ''),
                'raw_data': data,
                'generation_timestamp': datetime.now().isoformat(),
                'data_sources_count': data['metadata']['total_results'],
                'sources_used': data['metadata']['sources_used']
            }
            
        except Exception as e:
            logger.error(f"ERROR: AI generation failed: {e}")
            return None


def generate_journalist_case_study(journalist_name: str) -> Dict[str, Any]:
    """
    Main function using SERP API + Wikipedia
    """
    try:
        logger.info(f"DATA: === CASE STUDY START ===")
        logger.info(f"INFO: Journalist: {journalist_name}")
        
        scraper = WorkingJournalistScraper()
        
        # Step 1: Search
        data = scraper.comprehensive_search(journalist_name)
        
        if not data or data['metadata']['total_results'] < 1:
            return {
                'status': 'error',
                'message': f'No information found about {journalist_name}. Check spelling or try another journalist.'
            }
        
        # Step 2: AI case study
        case_study = scraper.generate_case_study(data)
        
        if not case_study:
            return {
                'status': 'error',
                'message': 'Failed to generate case study.'
            }
        
        logger.info(f"SUCCESS: === COMPLETE ===")
        logger.info(f"STATS: Sources: {case_study['data_sources_count']}")
        
        return {
            'status': 'success',
            'case_study': case_study
        }
        
    except Exception as e:
        logger.error(f"ERROR: Failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }

