import re
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from scrapy import Spider
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.signalmanager import dispatcher
from scrapy import signals

logger = logging.getLogger("scrapy_helpers")


class JournalistSpider(Spider):
    """
    Enhanced Scrapy spider for extracting journalist profile data.
    
    Extracts:
    - Profile images (multiple strategies)
    - Social media links (Twitter, LinkedIn, Instagram, Facebook, YouTube, Medium)
    - Article links (date-based URLs, article patterns)
    - Bio/description text
    - Contact information (emails)
    """
    
    name = "journalist"
    custom_settings = {
        "LOG_LEVEL": "ERROR",
        "DOWNLOAD_DELAY": 0.25,
        "CONCURRENT_REQUESTS": 4,
        "DOWNLOAD_TIMEOUT": 15,
        "RETRY_TIMES": 2,
        "ROBOTSTXT_OBEY": False,  # For better scraping coverage
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def __init__(self, start_urls: List[str], journalist_name: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls if isinstance(start_urls, list) else [start_urls]
        self.journalist_name = journalist_name
        self.scraped_data = []

    def parse(self, response):
        """Main parsing method for extracting all data from a page."""
        base_url = response.url
        domain = urlparse(base_url).netloc.replace("www.", "")
        
        data = {
            "url": base_url,
            "domain": domain,
            "profile_image": self._extract_profile_image(response, base_url),
            "social_links": self._extract_social_links(response, base_url),
            "article_links": self._extract_article_links(response, base_url),
            "bio": self._extract_bio(response),
            "emails": self._extract_emails(response),
            "title": response.css("title::text").get(),
        }
        
        self.scraped_data.append(data)
        yield data

    def _extract_profile_image(self, response, base_url: str) -> Optional[str]:
        """
        Enhanced profile image extraction with multiple strategies.
        Priority: OpenGraph > Twitter > JSON-LD > Profile hints > First image
        """
        
        # Strategy 1: Meta tags (highest priority)
        meta_selectors = [
            'meta[property="og:image"]::attr(content)',
            'meta[name="og:image"]::attr(content)',
            'meta[property="twitter:image"]::attr(content)',
            'meta[name="twitter:image"]::attr(content)',
            'meta[name="thumbnail"]::attr(content)',
        ]
        
        for selector in meta_selectors:
            img = response.css(selector).get()
            if img:
                return urljoin(base_url, img)
        
        # Strategy 2: JSON-LD structured data
        json_ld_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_ld_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    # Check for image in Person or Article schema
                    img = data.get("image") or data.get("logo") or data.get("thumbnailUrl")
                    if img:
                        if isinstance(img, str):
                            return urljoin(base_url, img)
                        elif isinstance(img, list) and img:
                            return urljoin(base_url, img[0])
                        elif isinstance(img, dict) and img.get("url"):
                            return urljoin(base_url, img["url"])
            except json.JSONDecodeError:
                continue
        
        # Strategy 3: Images with profile-related attributes
        profile_keywords = ["profile", "avatar", "author", "bio", "headshot", "journalist", "face", "photo"]
        
        # Check img alt and class attributes
        for img_selector in ['img[alt*="profile" i]', 'img[class*="profile" i]', 'img[class*="avatar" i]', 'img[class*="author" i]']:
            img_src = response.css(f'{img_selector}::attr(src), {img_selector}::attr(data-src)').get()
            if img_src:
                return urljoin(base_url, img_src)
        
        # Strategy 4: Images in URLs containing profile keywords
        all_images = response.css('img::attr(src), img::attr(data-src), img::attr(data-original)').getall()
        scored_images = []
        
        for src in all_images:
            if not src or src.startswith('data:'):
                continue
            
            score = 0
            src_lower = src.lower()
            
            # Score based on URL path
            for keyword in profile_keywords:
                if keyword in src_lower:
                    score += 2
            
            # Check for profile-related paths
            if re.search(r"/(profile|avatar|author|bio|team|about)/", src_lower):
                score += 3
            
            # Penalty for obvious non-profile images
            if any(x in src_lower for x in ["icon", "logo", "badge", "sprite", "banner"]):
                score -= 5
            
            if score > 0:
                scored_images.append((score, urljoin(base_url, src)))
        
        if scored_images:
            scored_images.sort(reverse=True, key=lambda x: x[0])
            return scored_images[0][1]
        
        # Strategy 5: First reasonable image (last resort)
        for src in all_images[:5]:  # Only check first 5 images
            if src and not src.startswith('data:'):
                return urljoin(base_url, src)
        
        return None

    def _extract_social_links(self, response, base_url: str) -> List[Dict[str, str]]:
        """
        Extract social media links with platform identification.
        Returns list of dicts with platform, handle, and URL.
        """
        
        social_patterns = {
            "twitter": [r"twitter\.com/([^/\?&#]+)", r"x\.com/([^/\?&#]+)"],
            "linkedin": [r"linkedin\.com/in/([^/\?&#]+)", r"linkedin\.com/company/([^/\?&#]+)"],
            "instagram": [r"instagram\.com/([^/\?&#]+)"],
            "facebook": [r"facebook\.com/([^/\?&#]+)", r"fb\.com/([^/\?&#]+)"],
            "youtube": [r"youtube\.com/(?:c/|channel/|user/|@)?([^/\?&#]+)"],
            "medium": [r"medium\.com/@?([^/\?&#]+)"],
        }
        
        found_links = []
        seen_handles = set()
        
        all_links = response.css('a::attr(href)').getall()
        
        for href in all_links:
            if not href:
                continue
            
            # Convert relative to absolute
            full_url = urljoin(base_url, href)
            
            for platform, patterns in social_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, full_url, re.I)
                    if match:
                        handle = match.group(1)
                        
                        # Clean handle
                        handle = re.sub(r'[^a-zA-Z0-9_-]', '', handle)
                        
                        # Skip common non-profile patterns
                        skip_words = ["share", "intent", "home", "explore", "login", "signup", "sharer", "hashtag"]
                        if handle.lower() in skip_words or len(handle) < 2:
                            continue
                        
                        key = f"{platform}:{handle.lower()}"
                        if key not in seen_handles:
                            seen_handles.add(key)
                            found_links.append({
                                "platform": platform,
                                "handle": handle,
                                "url": full_url,
                            })
                        break
        
        return found_links

    def _extract_article_links(self, response, base_url: str) -> List[str]:
        """
        Extract article links using pattern matching.
        Looks for date-based URLs and common article path patterns.
        """
        
        article_patterns = [
            r"/\d{4}/\d{2}/",  # Date-based URLs like /2024/01/
            r"/(article|story|news|blog|post|opinion|analysis|report|investigation)/",
        ]
        
        article_links = set()
        all_links = response.css('a::attr(href)').getall()
        
        for href in all_links:
            if not href or href.startswith("#"):
                continue
            
            full_url = urljoin(base_url, href)
            
            # Check if URL matches article patterns
            if any(re.search(pattern, full_url, re.I) for pattern in article_patterns):
                article_links.add(full_url)
        
        return list(article_links)[:50]  # Limit to 50 articles

    def _extract_bio(self, response) -> Optional[str]:
        """
        Extract biography or about text from common selectors.
        """
        
        bio_selectors = [
            'div[class*="bio"]::text',
            'div[class*="about"]::text',
            'div[class*="description"]::text',
            'p[class*="bio"]::text',
            'section[class*="about"]::text',
            'div[itemprop="description"]::text',
        ]
        
        for selector in bio_selectors:
            bio_parts = response.css(selector).getall()
            if bio_parts:
                bio = " ".join(bio_parts).strip()
                if len(bio) > 100:  # Only return substantial bios
                    return bio[:1500]  # Limit length
        
        # Fallback: first few paragraphs
        paragraphs = response.css('p::text').getall()
        if paragraphs:
            bio = " ".join(paragraphs[:5]).strip()
            if len(bio) > 100:
                return bio[:1500]
        
        return None

    def _extract_emails(self, response) -> List[str]:
        """Extract email addresses from page text."""
        
        page_text = " ".join(response.css('*::text').getall())
        emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text))
        
        # Filter out common non-personal emails
        filtered = {
            e for e in emails 
            if not any(x in e.lower() for x in ["noreply", "info@", "contact@", "support@", "admin@"])
        }
        
        return list(filtered)[:5]  # Limit to 5 emails

# ============================================================================
# RUNNER FUNCTIONS
# ============================================================================

def run_scrapy_for_url(
    url: str,
    journalist_name: Optional[str] = None,
    save_local: bool = False
) -> Dict[str, Any]:
    """
    Run Scrapy spider for a single URL (blocking version).
    
    Args:
        url: URL to scrape
        journalist_name: Name of journalist (for context)
        save_local: Whether to save results to JSON file
    
    Returns:
        Dictionary with scraped data
    """
    
    scraped_result = []
    
    class TempSpider(JournalistSpider):
        def closed(self, reason):
            nonlocal scraped_result
            scraped_result = self.scraped_data
    
    try:
        process = CrawlerProcess(settings={
            "LOG_ENABLED": False,
            "TELNETCONSOLE_ENABLED": False,
        })
        process.crawl(TempSpider, start_urls=[url], journalist_name=journalist_name)
        process.start()  # Blocking call
        
        if save_local and scraped_result:
            output_file = "scrapy_journalist_data.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(scraped_result[0], f, ensure_ascii=False, indent=2)
            logger.info(f"Scraped data saved to {output_file}")
        
        return scraped_result[0] if scraped_result else {}
    
    except Exception as e:
        logger.error(f"Scrapy error for {url}: {str(e)}")
        return {}

def run_scrapy_for_urls(
    urls: List[str],
    journalist_name: Optional[str] = None,
    save_local: bool = False
) -> List[Dict[str, Any]]:
    """
    Run Scrapy spider for multiple URLs (blocking version).
    
    Args:
        urls: List of URLs to scrape
        journalist_name: Name of journalist (for context)
        save_local: Whether to save results to JSON file
    
    Returns:
        List of dictionaries with scraped data
    """
    
    scraped_results = []
    
    class TempSpider(JournalistSpider):
        def closed(self, reason):
            nonlocal scraped_results
            scraped_results = self.scraped_data
    
    try:
        process = CrawlerProcess(settings={
            "LOG_ENABLED": False,
            "TELNETCONSOLE_ENABLED": False,
        })
        process.crawl(TempSpider, start_urls=urls, journalist_name=journalist_name)
        process.start()  # Blocking call
        
        if save_local and scraped_results:
            output_file = "scrapy_journalist_data_batch.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(scraped_results, f, ensure_ascii=False, indent=2)
            logger.info(f"Scraped data saved to {output_file}")
        
        return scraped_results
    
    except Exception as e:
        logger.error(f"Scrapy batch error: {str(e)}")
        return []

# ============================================================================
# ASYNC VERSION (for integration with asyncio)
# ============================================================================

async def run_scrapy_async(
    urls: List[str],
    journalist_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Run Scrapy spider asynchronously (non-blocking).
    Compatible with asyncio event loops.
    
    Args:
        urls: List of URLs to scrape
        journalist_name: Name of journalist (for context)
    
    Returns:
        List of dictionaries with scraped data
    """
    
    scraped_results = []
    
    @defer.inlineCallbacks
    def crawl():
        runner = CrawlerRunner(settings={
            "LOG_ENABLED": False,
            "TELNETCONSOLE_ENABLED": False,
        })
        
        yield runner.crawl(JournalistSpider, start_urls=urls, journalist_name=journalist_name)
        
        # Access spider's scraped data
        for spider in runner.crawlers:
            scraped_results.extend(spider.spider.scraped_data)
    
    try:
        crawl()
        return scraped_results
    except Exception as e:
        logger.error(f"Async Scrapy error: {str(e)}")
        return []

# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scrapy_helpers.py <url> [journalist_name]")
        sys.exit(1)
    
    test_url = sys.argv[1]
    test_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\nSEARCH: Scraping: {test_url}")
    if test_name:
        print(f"👤 Journalist: {test_name}")
    
    result = run_scrapy_for_url(test_url, journalist_name=test_name, save_local=True)
    
    print("\n" + "=" * 80)
    print("STATS: SCRAPY RESULTS")
    print("=" * 80)
    
    print(json.dumps({
        "url": result.get("url"),
        "domain": result.get("domain"),
        "has_profile_image": bool(result.get("profile_image")),
        "profile_image": result.get("profile_image"),
        "social_links_count": len(result.get("social_links", [])),
        "social_links": result.get("social_links", []),
        "article_links_count": len(result.get("article_links", [])),
        "has_bio": bool(result.get("bio")),
        "bio_length": len(result.get("bio", "")),
        "emails": result.get("emails", []),
    }, indent=2))
    
    print("\nSUCCESS: Done!")