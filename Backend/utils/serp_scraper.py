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
            
            # Source 1: Get journalist's image
            journalist_image = self.get_journalist_image(journalist_name)
            if journalist_image:
                all_data['journalist_image'] = journalist_image
                logger.info(f"SUCCESS: Journalist image found")
            
            time.sleep(1)
            
            # Source 2: Wikipedia
            wikipedia_data = self.wikipedia_api(journalist_name)
            if wikipedia_data:
                all_data['sections']['wikipedia'] = wikipedia_data
                all_data['metadata']['sources_used'].append('Wikipedia')
                all_data['metadata']['total_results'] += 1
                logger.info(f"SUCCESS: Wikipedia: Found")
                
                # Use Wikipedia image if we don't have one yet
                if not journalist_image and wikipedia_data.get('image'):
                    all_data['journalist_image'] = wikipedia_data['image']
            
            time.sleep(1)
            
            # Source 2: SERP API Google searches
            search_queries = [
                f'"{journalist_name}" journalist biography',
                f'"{journalist_name}" news articles career',
                f'"{journalist_name}" awards journalism prize',
                f'"{journalist_name}" interview profile',
                f'{journalist_name} reporter works',
            ]
            
            all_articles = []
            seen_urls = set()
            
            for query in search_queries:
                results = self.serp_google_search(query, max_results=20)
                
                if results:
                    all_data['metadata']['sources_used'].append(f'Google ({query[:40]}...)')
                    
                    for result in results:
                        if result['url'] not in seen_urls:
                            # Try to scrape content
                            article_data = self.scrape_article(result['url'])
                            
                            if article_data:
                                article_data['snippet'] = result['snippet']
                                article_data['search_query'] = query
                                all_articles.append(article_data)
                            else:
                                # Keep result even if scraping fails
                                all_articles.append({
                                    'url': result['url'],
                                    'title': result['title'],
                                    'snippet': result['snippet'],
                                    'domain': urlparse(result['url']).netloc,
                                    'search_query': query
                                })
                            
                            seen_urls.add(result['url'])
                            time.sleep(0.3)
                
                time.sleep(1.5)
                
                if len(all_articles) >= 40:
                    break
            
            if all_articles:
                all_data['sections']['articles'] = all_articles[:40]
                all_data['metadata']['total_results'] += len(all_articles)
                logger.info(f"SUCCESS: Collected {len(all_articles)} articles")
            
            # Source 3: YouTube Videos (Educational Resources)
            logger.info("🎥 Searching YouTube for interviews and talks...")
            youtube_videos = self.youtube_search(journalist_name)
            if youtube_videos:
                all_data['sections']['youtube_videos'] = youtube_videos
                all_data['metadata']['sources_used'].append('YouTube')
                all_data['metadata']['total_results'] += len(youtube_videos)
                logger.info(f"SUCCESS: Found {len(youtube_videos)} YouTube videos")
            
            time.sleep(1)
            
            # Source 4: Awards & Recognition (dedicated search)
            logger.info("AWARD: Searching for awards and recognition...")
            awards_queries = [
                f'"{journalist_name}" awards won',
                f'"{journalist_name}" journalism prize',
            ]
            
            awards_articles = []
            for query in awards_queries:
                results = self.serp_google_search(query, max_results=10)
                if results:
                    for result in results:
                        if result['url'] not in seen_urls:
                            awards_articles.append({
                                'url': result['url'],
                                'title': result['title'],
                                'snippet': result['snippet'],
                                'domain': urlparse(result['url']).netloc,
                                'type': 'award'
                            })
                            seen_urls.add(result['url'])
                time.sleep(1)
                
            if awards_articles:
                all_data['sections']['awards'] = awards_articles
                all_data['metadata']['total_results'] += len(awards_articles)
                logger.info(f"SUCCESS: Found {len(awards_articles)} award references")
            
            time.sleep(1)
            
            # Source 4: AI Knowledge (fallback)
            if all_data['metadata']['total_results'] < 5:
                logger.info("WARNING: Limited data, using AI knowledge")
                
                if ai_client:
                    try:
                        prompt = f"""Provide comprehensive information about journalist {journalist_name}:
1. Career background and positions
2. Notable works and investigations
3. Awards and recognition
4. Writing style and methodology
5. Impact on journalism
6. Controversies or significant events

Be detailed and specific."""

                        response = ai_client.chat.completions.create(
                            model="meta/llama-3.1-70b-instruct",
                            messages=[
                                {"role": "system", "content": "You are a journalism research expert."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.3,
                            max_tokens=2000,
                        )
                        
                        ai_info = response.choices[0].message.content.strip()
                        
                        all_data['sections']['ai_knowledge'] = {
                            'content': ai_info,
                            'source': 'AI Knowledge Base'
                        }
                        all_data['metadata']['sources_used'].append('AI Knowledge')
                        all_data['metadata']['total_results'] += 1
                        
                    except Exception as e:
                        logger.error(f"AI fallback failed: {e}")
            
            logger.info(f"\nSUCCESS: === SEARCH COMPLETE ===")
            logger.info(f"STATS: Total: {all_data['metadata']['total_results']} results")
            logger.info(f"STATS: Sources: {', '.join(all_data['metadata']['sources_used'][:3])}")
            
            return all_data
            
        except Exception as e:
            logger.error(f"ERROR: Search failed: {e}")
            return None
    
    def generate_case_study(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI case study
        """
        if not ai_client:
            return None
        
        try:
            journalist_name = data['journalist_name']
            sections = data['sections']
            
            wikipedia_text = sections.get('wikipedia', {}).get('extract', '')[:2500]
            
            articles_list = "\n".join([
                f"- {a.get('title', 'Untitled')} ({a.get('domain', 'N/A')}) - {a.get('word_count', 0)} words\n  Published: {a.get('published_date', 'N/A')} | Author: {a.get('author', 'N/A')}"
                for a in sections.get('articles', [])[:15]
            ])
            
            youtube_videos = "\n".join([
                f"- {v['title']} ({v.get('channel', 'Unknown')})\n  URL: {v['url']}"
                for v in sections.get('youtube_videos', [])[:10]
            ])
            
            ai_knowledge = sections.get('ai_knowledge', {}).get('content', '')
            
            prompt = f"""You are a distinguished journalism professor creating an EDUCATIONAL CASE STUDY for students about journalist {journalist_name}.

AVAILABLE DATA:

WIKIPEDIA INFO:
{wikipedia_text}

ARTICLES & WORKS (with sources):
{articles_list}

YOUTUBE INTERVIEWS & TALKS:
{youtube_videos}

ADDITIONAL RESEARCH:
{ai_knowledge}

CREATE AN IN-DEPTH, DETAILED CASE STUDY with SPECIFIC EXAMPLES from the data above.

CRITICAL REQUIREMENTS:
- Use SPECIFIC article titles, dates, and publication names from the data above
- When mentioning major works, cite the actual article titles and sources provided
- Reference specific YouTube videos by title
- Do NOT use ** for bold text or emphasis
- Use clear section headings with ALL CAPS
- Use bullet points (•) for lists
- Make it feel real and educational, not generic AI text
- Include specific examples with source citations

Structure your response EXACTLY as follows:

EXECUTIVE SUMMARY
[Write 3-4 comprehensive paragraphs about the journalist's career, significance, and contributions. Include specific examples from the articles provided.]

CAREER TRAJECTORY & BACKGROUND
[Provide detailed information about their education, early career, and how they rose to prominence. Use specific dates and positions when available.]

MAJOR WORKS & IMPACT
[For EACH major work, include:
• The specific article/report title (use exact titles from the articles list above)
• Publication name and date
• Impact and significance
• Key findings or revelations
Format each major work as a separate subsection. Do NOT use ** for emphasis.]

JOURNALISM STYLE & METHODOLOGY
[Analyze their reporting techniques, writing style, and approach to journalism. Provide specific examples from their work.]

ETHICAL ANALYSIS
[Examine ethical considerations in their work, controversies if any, and how they navigated difficult situations.]

INFLUENCE & LEGACY
[Discuss their impact on journalism, mentorship, and lasting contributions to the field.]

LEARNING OBJECTIVES
Students will:
• [Objective 1]
• [Objective 2]
• [Continue with 7-8 total objectives]

CRITICAL THINKING QUESTIONS
1. [Question 1 - deep analytical question]
2. [Question 2 - ethical consideration]
[Continue with 10-12 thought-provoking questions]

PRACTICAL APPLICATIONS
• [Activity 1 - hands-on journalism exercise]
• [Activity 2 - analysis assignment]
[Include 5-6 practical activities]

CONCLUSION
[Synthesize the key lessons and takeaways. 2-3 paragraphs.]

RECOMMENDED RESOURCES FOR FURTHER STUDY
• [Specific YouTube video titles from the data]
• [Specific articles from the data]
• [Other relevant resources]

Remember: Use actual article titles, publication names, and dates from the provided data. Make every example specific and verifiable."""

            logger.info(f"AI: Generating case study...")
            
            response = ai_client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a distinguished journalism professor creating educational case studies for students."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=8000,
                top_p=0.9
            )
            
            analysis = response.choices[0].message.content.strip()
            
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


if __name__ == "__main__":
    test = "Barkha Dutt"
    logger.info(f"🧪 Testing: {test}")
    result = generate_journalist_case_study(test)
    
    if result['status'] == 'success':
        print(f"\nSUCCESS: SUCCESS")
        print(f"Sources: {result['case_study']['data_sources_count']}")
        print(f"Preview: {result['case_study']['case_study_analysis'][:300]}...")
    else:
        print(f"\nERROR: FAILED: {result['message']}")
