import os
import re
import asyncio
import logging
import json
import random
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, urljoin, quote_plus
from datetime import datetime
from collections import defaultdict

import httpx
from bs4 import BeautifulSoup

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logger = logging.getLogger("datahalo_scraper")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================================
# CONFIGURATION
# ============================================================================
SERP_API_KEY = os.getenv("SERP_API_KEY")
DEFAULT_CONCURRENCY = int(os.getenv("SCRAPER_CONCURRENCY", "8"))
DEFAULT_DELAY = float(os.getenv("SCRAPER_DELAY", "0.3"))
MAX_CONTENT_CHARS = 5000
MAX_SNIPPET = 300
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

# ============================================================================
# ENHANCED ANALYSIS KEYWORDS WITH WEIGHTED SCORING
# ============================================================================
# Weighted keywords for more accurate bias detection
BIAS_KEYWORDS_WEIGHTED = {
    "left": {
        # Strong indicators (weight: 3)
        "strong": ["socialist", "marxist", "communist", "anti-establishment", "revolutionary",
                   "anti-BJP", "congress supporter", "left-wing activist"],
        # Medium indicators (weight: 2)
        "medium": ["liberal", "progressive", "secular", "left-leaning", "social democrat",
                   "AAP supporter", "minority rights advocate", "secularist", "pro-labor"],
        # Mild indicators (weight: 1)
        "mild": ["activist", "social justice", "equality", "welfare", "environmentalist",
                 "climate activist", "pro-palestine", "workers' rights"]
    },
    "right": {
        # Strong indicators (weight: 3)
        "strong": ["hindutva", "pro-Modi", "BJP supporter", "sangh parivar", "RSS",
                   "nationalist", "saffron", "cultural nationalist"],
        # Medium indicators (weight: 2)
        "medium": ["conservative", "right-wing", "pro-government", "traditionalist",
                   "patriotic", "pro-business", "free market advocate"],
        # Mild indicators (weight: 1)
        "mild": ["traditional values", "family values", "pro-Israel", "national security",
                 "strong on defense", "privatization"]
    },
    "centrist": {
        # Strong indicators (weight: 3)
        "strong": ["non-partisan", "impartial", "objective journalist", "balanced reporting"],
        # Medium indicators (weight: 2)
        "medium": ["centrist", "moderate", "pragmatic", "fact-based", "middle ground"],
        # Mild indicators (weight: 1)
        "mild": ["balanced", "both sides", "unbiased", "neutral observer"]
    }
}

# Contextual phrases that indicate strong bias
CONTEXTUAL_BIAS_PHRASES = {
    "left": [
        r"criticizes?\s+(?:modi|bjp|hindutva|rss|sangh)",
        r"defends?\s+(?:minorities|secularism|social\s+justice)",
        r"opposes?\s+(?:privatization|corporate|capitalist)",
        r"supports?\s+(?:congress|aap|left\s+parties|communist)",
        r"questions?\s+(?:government|establishment|authority)",
        r"highlights?\s+(?:inequality|discrimination|oppression)"
    ],
    "right": [
        r"criticizes?\s+(?:congress|gandhi|secular|liberal)",
        r"defends?\s+(?:modi|bjp|hindutva|nationalism)",
        r"supports?\s+(?:privatization|free\s+market|business)",
        r"opposes?\s+(?:reservation|minority\s+appeasement)",
        r"promotes?\s+(?:hindu|cultural\s+nationalism|tradition)",
        r"questions?\s+(?:secular|liberal|leftist)"
    ],
    "centrist": [
        r"analyzes?\s+(?:both|all)\s+sides",
        r"presents?\s+(?:facts|data|evidence)",
        r"avoids?\s+(?:bias|political|partisan)",
        r"focuses?\s+on\s+(?:facts|truth|accuracy)"
    ]
}

# Advanced sentiment keywords with intensity levels
SENTIMENT_KEYWORDS = {
    "strongly_negative": {
        "keywords": ["condemns", "slams", "blasts", "destroys", "demolishes", "eviscerates",
                    "annihilates", "devastating", "catastrophic", "horrifying", "appalling"],
        "weight": 5
    },
    "negative": {
        "keywords": ["criticizes", "opposes", "questions", "challenges", "disputes", "rejects",
                    "condemns", "denounces", "attacks", "accuses"],
        "weight": 3
    },
    "mildly_negative": {
        "keywords": ["concerned", "worried", "doubts", "skeptical", "cautious", "wary",
                    "disappointed", "frustrated"],
        "weight": 1
    },
    "neutral": {
        "keywords": ["reports", "states", "explains", "describes", "analyzes", "examines",
                    "investigates", "covers", "documents"],
        "weight": 0
    },
    "mildly_positive": {
        "keywords": ["supports", "agrees", "acknowledges", "recognizes", "appreciates",
                    "welcomes", "praises moderately"],
        "weight": 1
    },
    "positive": {
        "keywords": ["praises", "lauds", "commends", "applauds", "endorses", "champions",
                    "celebrates", "defends strongly"],
        "weight": 3
    },
    "strongly_positive": {
        "keywords": ["hails", "glorifies", "extols", "venerates", "idolizes", "exalts",
                    "lionizes", "worships"],
        "weight": 5
    }
}

# Topic-based bias indicators
TOPIC_BIAS_INDICATORS = {
    "left_topics": [
        "farmers protest", "labor rights", "income inequality", "caste discrimination",
        "minority rights", "secularism", "press freedom", "dissent", "civil liberties",
        "environmental justice", "corporate accountability", "wealth tax"
    ],
    "right_topics": [
        "national security", "terrorism", "illegal immigration", "hindu identity",
        "cultural nationalism", "economic growth", "infrastructure development",
        "strong leadership", "surgical strike", "national pride"
    ],
    "centrist_topics": [
        "economic policy", "healthcare reform", "education system", "infrastructure",
        "technology innovation", "governance", "policy analysis", "data journalism"
    ]
}

# Publication bias indicators
PUBLICATION_BIAS = {
    "left_leaning": ["thewire.in", "scroll.in", "newslaundry.com", "newsclick.in",
                     "thecitizen.in", "sabrangindia.in", "altindia.net"],
    "right_leaning": ["opindia.com", "swarajyamag.com", "organiser.org", "pgurus.com",
                      "kreately.in", "tfipost.com"],
    "centrist": ["thehindu.com", "indianexpress.com", "livemint.com", "business-standard.com",
                 "theprint.in", "reuters.com", "pti.in"]
}

# ============================================================================
# ENHANCED ANALYSIS KEYWORDS
# ============================================================================
CONTROVERSY_KEYWORDS = {
    "strong": ["scandal", "convicted", "charged", "arrested", "sued", "lawsuit", "FIR", "indicted", "impeached",
               "fired", "dismissed", "expelled", "banned", "suspended from", "investigation into", "accused of corruption"],
    "medium": ["controversy", "allegation", "accused", "complaint", "probe", "investigation", "resign", "suspended",
               "criticized for", "backlash", "under fire", "faces criticism", "questioned by", "disputed claims"],
    "mild": ["criticized", "questioned", "disputed", "debated", "controversial opinion", "mixed reactions",
             "divided opinion", "some controversy", "raised eyebrows", "sparked debate"]
}

EMOTIONAL_KEYWORDS = {
    "high": ["outrage", "furious", "devastated", "shocking", "explosive", "horrific", "slammed", "blasted",
             "ripped apart", "destroyed", "annihilated", "obliterated", "catastrophic"],
    "medium": ["angry", "emotional", "passionate", "heated", "intense", "dramatic", "harsh", "strong words",
               "fired back", "hit out", "lashed out", "condemned"],
    "mild": ["concerned", "worried", "disappointed", "frustrated", "expressed doubts", "raised concerns"]
}

# ENHANCED BIAS KEYWORDS with more nuanced detection
BIAS_KEYWORDS = {
    "left": [
        # Political orientation
        "liberal", "progressive", "secular", "left-wing", "socialist", "social democrat", "leftist",
        # Indian context
        "anti-establishment", "anti-BJP", "congress supporter", "AAP supporter", "communist", "marxist",
        # Social issues
        "activist", "social justice", "equality advocate", "minority rights", "secularist",
        # Economic
        "pro-labor", "workers' rights", "wealth redistribution", "welfare state",
        # International
        "pro-palestine", "anti-imperialism", "environmentalist", "climate activist"
    ],
    "right": [
        # Political orientation
        "conservative", "nationalist", "right-wing", "traditionalist", "right-leaning",
        # Indian context
        "pro-government", "BJP supporter", "hindutva", "patriotic", "nationalistic", "saffron",
        "pro-Modi", "sangh", "RSS", "cultural nationalist",
        # Social issues
        "traditional values", "family values", "religious conservative", "pro-majority",
        # Economic
        "pro-business", "free market", "capitalist", "privatization advocate",
        # International
        "pro-Israel", "strong on defense", "national security hawk"
    ],
    "centrist": [
        "balanced", "objective", "impartial", "non-partisan", "fact-based", "unbiased",
        "moderate", "pragmatic", "centrist", "middle ground", "both sides"
    ],
    "libertarian": [
        "libertarian", "individual freedom", "limited government", "free speech absolutist",
        "civil liberties", "anti-authoritarian", "personal liberty"
    ]
}

# POLITICAL AFFILIATION INDICATORS
POLITICAL_AFFILIATION_KEYWORDS = {
    "BJP": ["BJP", "Bharatiya Janata Party", "Modi government", "NDA", "saffron party"],
    "Congress": ["Congress", "INC", "Indian National Congress", "Gandhi family", "UPA"],
    "AAP": ["AAP", "Aam Aadmi Party", "Arvind Kejriwal", "Delhi government"],
    "Communist": ["CPI", "CPM", "Communist Party", "Left Front", "marxist", "communist"],
    "Regional": ["TMC", "DMK", "AIADMK", "Shiv Sena", "NCP", "TDP", "TRS", "BJD"],
    "Anti-establishment": ["anti-government", "opposition", "dissent", "protest", "resistance"]
}

# ENHANCED CREDIBILITY INDICATORS
CREDIBILITY_INDICATORS = {
    "positive": [
        # Awards & Recognition
        "pulitzer", "award-winning", "acclaimed", "respected", "veteran", "renowned",
        "prestigious award", "journalism award", "padma shri", "padma bhushan", "ramon magsaysay",
        # Experience
        "senior editor", "chief editor", "investigative", "fact-checker", "decades of experience",
        "foreign correspondent", "bureau chief", "columnist",
        # Verification
        "verified account", "blue tick", "authenticated", "official account",
        # Recognition
        "cited by", "referenced in", "quoted by", "featured in", "appeared on",
        "ted talk", "keynote speaker", "guest lecturer"
    ],
    "negative": [
        # Misinformation
        "fake news", "misinformation", "propaganda", "biased reporting", "discredited",
        "fact-check failed", "debunked", "false claim", "misleading",
        # Professional issues
        "fired", "retracted", "plagiarism", "fabrication", "unverified", "anonymous sources",
        "conflict of interest", "undisclosed", "paid content", "sponsored",
        # Legal issues
        "defamation", "libel", "sued for", "legal action", "court case"
    ]
}

# AWARD PATTERNS for extraction
AWARD_PATTERNS = [
    r"(?i)(pulitzer\s+prize)",
    r"(?i)(ramnath\s+goenka\s+award)",
    r"(?i)(padma\s+(?:shri|bhushan|vibhushan))",
    r"(?i)(ramon\s+magsaysay\s+award)",
    r"(?i)(international\s+press\s+freedom\s+award)",
    r"(?i)(journalist\s+of\s+the\s+year)",
    r"(?i)(lifetime\s+achievement\s+award)",
    r"(?i)(george\s+polk\s+award)",
    r"(?i)(redink\s+award)",
    r"(?i)(laadli\s+media\s+award)",
]

# Trusted domains for credibility scoring
TRUSTED_DOMAINS = {
    "wikipedia.org": 10,
    "bbc.com": 9,
    "reuters.com": 9,
    "apnews.com": 9,
    "theguardian.com": 8,
    "nytimes.com": 8,
    "washingtonpost.com": 8,
    "thehindu.com": 8,
    "indianexpress.com": 7,
    "scroll.in": 7,
    "thewire.in": 7,
    "ndtv.com": 7,
    "theprint.in": 7,
    "bbc.co.uk": 9,
    "aljazeera.com": 7,
    "economist.com": 8,
    "ft.com": 8,
    "time.com": 7,
    "newslaundry.com": 7,
}

# Social media platform patterns (enhanced)
SOCIAL_MEDIA_PATTERNS = {
    "twitter": [
        r"(?:twitter\.com|x\.com)/([^/\?&#\s]+)",
        r"@([a-zA-Z0-9_]{1,15})\b"  # Twitter handle pattern
    ],
    "linkedin": [
        r"linkedin\.com/in/([^/\?&#\s]+)",
        r"linkedin\.com/pub/([^/\?&#\s]+)"
    ],
    "instagram": [
        r"instagram\.com/([^/\?&#\s]+)",
        r"instagr\.am/([^/\?&#\s]+)"
    ],
    "facebook": [
        r"facebook\.com/([^/\?&#\s]+)",
        r"fb\.com/([^/\?&#\s]+)",
        r"fb\.me/([^/\?&#\s]+)"
    ],
    "youtube": [
        r"youtube\.com/(?:c/|channel/|user/|@)([^/\?&#\s]+)",
        r"youtu\.be/([^/\?&#\s]+)"
    ],
    "medium": [
        r"medium\.com/@([^/\?&#\s]+)"
    ],
    "substack": [
        r"([^/\?&#\s]+)\.substack\.com"
    ],
    "telegram": [
        r"t\.me/([^/\?&#\s]+)",
        r"telegram\.me/([^/\?&#\s]+)"
    ]
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _clean_text(s: str) -> str:
    """Clean and normalize text."""
    if not s:
        return ""
    s = re.sub(r'\s+', ' ', s.strip())
    return s

def _get_snippet(text: str, max_len: int = MAX_SNIPPET) -> str:
    """Get clean snippet of text."""
    clean = _clean_text(text)
    return clean[:max_len] + ("..." if len(clean) > max_len else "")

def _name_parts(name: str) -> List[str]:
    """Split name into searchable parts."""
    return [p.lower() for p in _clean_text(name).split() if len(p) > 2]

def name_in_text(name: str, text: str) -> bool:
    """Check if journalist name appears in text with flexible matching."""
    if not name or not text:
        return False

    parts = _name_parts(name)
    if not parts:
        return False

    text_lower = text.lower()

    # Full name match
    if name.lower() in text_lower:
        return True

    # First + Last name match within reasonable distance
    if len(parts) >= 2:
        first_pos = text_lower.find(parts[0])
        last_pos = text_lower.find(parts[-1])
        if first_pos != -1 and last_pos != -1 and abs(first_pos - last_pos) < 100:
            return True

    # Single name match (for mononyms)
    if len(parts) == 1 and parts[0] in text_lower:
        return True

    return False

def _calculate_domain_trust_score(domain: str) -> int:
    """Calculate trust score for a domain (0-10)."""
    domain_clean = domain.replace("www.", "").lower()

    if domain_clean in TRUSTED_DOMAINS:
        return TRUSTED_DOMAINS[domain_clean]

    for trusted, score in TRUSTED_DOMAINS.items():
        if trusted in domain_clean or domain_clean in trusted:
            return score

    if domain_clean.endswith(('.gov', '.edu')):
        return 8
    elif domain_clean.endswith(('.org', '.in')):
        return 5
    elif domain_clean.endswith(('.com', '.net')):
        return 4

    return 3

# ============================================================================
# HTTP CLIENT
# ============================================================================

async def _fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    max_retries: int = MAX_RETRIES
) -> Optional[httpx.Response]:
    """Fetch URL with exponential backoff retry logic."""

    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            response = await client.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True
            )

            if response.status_code == 200:
                logger.debug(f"✓ Fetched: {url}")
                return response

            if response.status_code in [429, 503]:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited on {url}, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                continue

            logger.warning(f"Non-200 status {response.status_code} for {url}")
            return None

        except httpx.TimeoutException:
            logger.warning(f"Timeout on {url} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 + attempt)
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)

    logger.error(f"✗ Failed after {max_retries} attempts: {url}")
    return None

# ============================================================================
# ENHANCED SERP API INTEGRATION
# ============================================================================

async def serpapi_search(query: str, num: int = 30) -> List[str]:
    """Search using SerpApi and return URLs."""
    if not SERP_API_KEY:
        logger.info("SERP_API_KEY not set; skipping SerpApi discovery.")
        return []

    endpoint = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": query,
        "num": num,
        "api_key": SERP_API_KEY,
        "hl": "en",
        "gl": "in",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            logger.info(f"Querying SerpApi: {query}")
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            links = []

            # Knowledge graph (highest priority)
            kg = data.get("knowledge_graph", {})
            if kg and kg.get("website"):
                links.append(kg["website"])

            # Organic results
            for item in data.get("organic_results", []):
                if isinstance(item, dict):
                    url = item.get("link") or item.get("url")
                    if url:
                        links.append(url)

            logger.info(f"Found {len(links)} results from SerpApi")
            return links

        except Exception as e:
            logger.error(f"SerpApi lookup failed: {str(e)}")
            return []

async def serpapi_multi_query_search(name: str, max_per_query: int = 15) -> List[str]:
    """
    Perform multiple targeted searches to gather comprehensive data.
    """
    queries = [
        f'"{name}" journalist profile',
        f'"{name}" twitter OR instagram OR linkedin',
        f'"{name}" awards OR recognition OR achievements',
        f'"{name}" controversy OR criticism OR scandal',
        f'"{name}" political bias OR ideology OR leaning',
        f'"{name}" articles OR publications OR writings',
        f'"{name}" biography OR about OR background',
        f'"{name}" wikipedia OR wiki',
    ]

    all_urls = []
    seen = set()

    for query in queries:
        urls = await serpapi_search(query, num=max_per_query)
        for url in urls:
            if url not in seen:
                seen.add(url)
                all_urls.append(url)
        await asyncio.sleep(0.5)  # Rate limiting between queries

    logger.info(f"Multi-query search found {len(all_urls)} unique URLs")
    return all_urls

# ============================================================================
# ADVANCED EXTRACTION FUNCTIONS
# ============================================================================

def _extract_profile_image(soup: BeautifulSoup, base_url: str, page_text: str = "") -> Optional[str]:
    """
    Comprehensive profile image extraction.
    Priority: Meta tags > JSON-LD > Profile hints > CDN > Largest
    """

    # Strategy 1: Meta tags
    meta_props = [
        {"property": "og:image"},
        {"name": "og:image"},
        {"property": "twitter:image"},
        {"name": "twitter:image"},
        {"name": "thumbnail"},
        {"property": "og:image:secure_url"},
    ]

    for attrs in meta_props:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            img_url = urljoin(base_url, tag["content"])
            logger.debug(f"Found meta image: {img_url}")
            return img_url

    # Strategy 2: JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or script.text or "{}")

            def extract_image_recursive(obj):
                if isinstance(obj, str) and obj.startswith("http"):
                    return obj
                elif isinstance(obj, dict):
                    for key in ["image", "thumbnailUrl", "logo", "photo", "url"]:
                        if key in obj:
                            val = obj[key]
                            if isinstance(val, str) and val.startswith("http"):
                                return val
                            elif isinstance(val, dict) and "url" in val:
                                return val["url"]
                            elif isinstance(val, list) and val:
                                first = val[0]
                                if isinstance(first, str):
                                    return first
                                elif isinstance(first, dict) and "url" in first:
                                    return first["url"]
                    for val in obj.values():
                        result = extract_image_recursive(val)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = extract_image_recursive(item)
                        if result:
                            return result
                return None

            img = extract_image_recursive(data)
            if img:
                img_url = urljoin(base_url, img)
                logger.debug(f"Found JSON-LD image: {img_url}")
                return img_url

        except json.JSONDecodeError:
            continue

    # Strategy 3: Inline img tags with profile hints
    profile_keywords = ["profile", "avatar", "author", "journalist", "headshot", "bio", "photo", "face", "portrait"]
    scored_images = []

    for img in soup.find_all("img", limit=50):
        src = (
            img.get("src") or
            img.get("data-src") or
            img.get("data-lazy-src") or
            img.get("data-original") or
            img.get("data-lazy") or
            ""
        )

        # Handle srcset
        if not src and img.get("srcset"):
            srcset = img["srcset"].split(",")[0].strip().split()[0]
            src = srcset

        if not src or src.startswith("data:"):
            continue

        score = 0
        alt = (img.get("alt") or "").lower()
        cls = " ".join(img.get("class") or []).lower()

        # Score based on hints
        for keyword in profile_keywords:
            if keyword in alt:
                score += 3
            if keyword in cls:
                score += 2
            if keyword in src.lower():
                score += 2

        # Path-based scoring
        if re.search(r"/(profile|avatar|author|bio|team|about|headshot)/", src, re.I):
            score += 3

        # Size hints
        width = img.get("width")
        height = img.get("height")
        if width and height:
            try:
                w, h = int(width), int(height)
                # Profile images typically square or portrait
                if 100 <= w <= 500 and 100 <= h <= 500:
                    score += 2
            except:
                pass

        # Penalty for obvious non-profile images
        if any(x in src.lower() for x in ["icon", "logo", "badge", "sprite", "banner", "ad"]):
            score -= 5

        if score > 0:
            scored_images.append((score, urljoin(base_url, src)))

    if scored_images:
        scored_images.sort(reverse=True, key=lambda x: x[0])
        logger.debug(f"Found profile hint image (score={scored_images[0][0]}): {scored_images[0][1]}")
        return scored_images[0][1]

    # Strategy 4: Google/CDN hosted images
    if page_text:
        cdn_patterns = [
            r'https?://lh3\.googleusercontent\.com/[^\s"\'<>]+',
            r'https?://[^\s"\'<>]*gstatic\.com/[^\s"\'<>]+',
            r'https?://[^\s"\'<>]*encrypted-tbn0[^\s"\'<>]+',
            r'https?://upload\.wikimedia\.org/[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)',
        ]
        for pattern in cdn_patterns:
            match = re.search(pattern, page_text)
            if match:
                url = match.group(0).rstrip('",')
                logger.debug(f"Found CDN image: {url}")
                return url

    # Strategy 5: Largest image (last resort)
    largest = None
    max_area = 0

    for img in soup.find_all("img", limit=30):
        src = img.get("src") or img.get("data-src")
        if not src or src.startswith("data:"):
            continue

        try:
            width = int(img.get("width") or 200)
            height = int(img.get("height") or 200)
            area = width * height

            if area > max_area and area > 10000:
                max_area = area
                largest = urljoin(base_url, src)
        except (ValueError, TypeError):
            continue

    if largest:
        logger.debug(f"Found largest image: {largest}")
        return largest

    return None

def _extract_social_links(soup: BeautifulSoup, base_url: str, page_text: str = "") -> List[Dict[str, str]]:
    """
    Enhanced social media link extraction with multiple strategies.
    """
    found_links = []
    seen_handles = set()

    # Strategy 1: Extract from anchor tags
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        if href.startswith("/"):
            href = urljoin(base_url, href)

        for platform, patterns in SOCIAL_MEDIA_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, href, re.I)
                if match:
                    handle = match.group(1)
                    handle = re.sub(r'[^a-zA-Z0-9_-]', '', handle)

                    # Skip common non-profile patterns
                    skip_words = ["share", "intent", "home", "explore", "login", "signup", "sharer", "hashtag",
                                  "privacy", "terms", "help", "about", "404", "search"]
                    if handle.lower() in skip_words or len(handle) < 2:
                        continue

                    key = f"{platform}:{handle.lower()}"
                    if key not in seen_handles:
                        seen_handles.add(key)
                        found_links.append({
                            "platform": platform,
                            "handle": handle,
                            "url": href,
                        })
                    break

    # Strategy 2: Extract from page text (for @ mentions)
    if page_text:
        # Twitter handles
        twitter_mentions = re.findall(r'@([a-zA-Z0-9_]{1,15})\b', page_text)
        for handle in twitter_mentions:
            if len(handle) > 2 and handle.lower() not in ["twitter", "follow", "share"]:
                key = f"twitter:{handle.lower()}"
                if key not in seen_handles:
                    seen_handles.add(key)
                    found_links.append({
                        "platform": "twitter",
                        "handle": handle,
                        "url": f"https://twitter.com/{handle}",
                    })

    # Strategy 3: Look for social icons with aria-labels
    social_icon_patterns = {
        "twitter": ["twitter", "tweet"],
        "facebook": ["facebook", "fb"],
        "instagram": ["instagram", "insta"],
        "linkedin": ["linkedin"],
        "youtube": ["youtube", "yt"],
    }

    for icon_link in soup.find_all("a", {"aria-label": True}):
        label = icon_link.get("aria-label", "").lower()
        href = icon_link.get("href", "")

        for platform, keywords in social_icon_patterns.items():
            if any(kw in label for kw in keywords) and href:
                for pattern in SOCIAL_MEDIA_PATTERNS.get(platform, []):
                    match = re.search(pattern, href, re.I)
                    if match:
                        handle = match.group(1)
                        key = f"{platform}:{handle.lower()}"
                        if key not in seen_handles:
                            seen_handles.add(key)
                            found_links.append({
                                "platform": platform,
                                "handle": handle,
                                "url": href,
                            })
                        break

    return found_links

def _extract_contact_info(soup: BeautifulSoup) -> Dict[str, List[str]]:
    """Extract emails and phone numbers."""

    page_text = soup.get_text(" ", strip=True)

    # Email extraction
    emails = set(re.findall(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        page_text
    ))

    # Filter out common non-personal emails
    emails = {e for e in emails if not any(x in e.lower() for x in ["noreply", "info@", "contact@", "support@"])}

    # Phone extraction (international + Indian)
    phones = set(re.findall(
        r'(?:\+91|0)?[6-9]\d{9}',
        page_text
    ))

    return {
        "emails": list(emails)[:5],
        "phones": list(phones)[:3]
    }

def _extract_bio_and_description(soup: BeautifulSoup, name: str) -> Optional[str]:
    """Extract biography or description text."""

    # Look for common bio containers
    bio_selectors = [
        'div[class*="bio"]',
        'div[class*="about"]',
        'div[class*="description"]',
        'div[class*="author-bio"]',
        'section[class*="bio"]',
        'section[class*="about"]',
        'p[class*="bio"]',
        'div[itemprop="description"]',
    ]

    for selector in bio_selectors:
        elements = soup.select(selector)
        for elem in elements:
            text = elem.get_text(" ", strip=True)
            if name_in_text(name, text) and len(text) > 100:
                return _clean_text(text)[:1500]

    # Fallback: paragraphs mentioning the name
    paragraphs = []
    for p in soup.find_all("p", limit=20):
        text = p.get_text(" ", strip=True)
        if len(text) > 50 and name_in_text(name, text):
            paragraphs.append(text)
            if len(" ".join(paragraphs)) > 800:
                break

    if paragraphs:
        return _clean_text(" ".join(paragraphs))[:1500]

    return None

def _extract_awards(soup: BeautifulSoup, page_text: str, name: str) -> List[Dict[str, str]]:
    """
    Extract awards and recognitions from page content.
    """
    awards = []
    seen_awards = set()

    # Search for award patterns
    for pattern in AWARD_PATTERNS:
        matches = re.finditer(pattern, page_text, re.I)
        for match in matches:
            award_text = match.group(0)

            # Get context around the award mention
            start = max(0, match.start() - 200)
            end = min(len(page_text), match.end() + 200)
            context = page_text[start:end]

            # Check if the name is mentioned near the award
            if name_in_text(name, context):
                award_clean = _clean_text(award_text)
                if award_clean.lower() not in seen_awards:
                    seen_awards.add(award_clean.lower())

                    # Try to extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', context)
                    year = year_match.group(0) if year_match else None

                    awards.append({
                        "name": award_clean,
                        "year": year,
                        "context": _get_snippet(context, 150)
                    })

    # Look for general award mentions
    award_indicators = [
        r"received.*?award",
        r"won.*?(?:award|prize|honor)",
        r"honored with",
        r"recipient of",
        r"awarded.*?(?:for|by)"
    ]

    for indicator in award_indicators:
        matches = re.finditer(indicator, page_text, re.I)
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(page_text), match.end() + 150)
            context = page_text[start:end]

            if name_in_text(name, context):
                # Extract potential award name
                award_sentence = _get_snippet(context, 200)
                if award_sentence and len(awards) < 10:
                    awards.append({
                        "name": "Recognition",
                        "year": None,
                        "context": award_sentence
                    })

    return awards[:10]  # Limit to 10 awards

def _extract_political_affiliation(text: str) -> Dict[str, Any]:
    """
    Analyze text for political affiliation indicators.
    """
    text_lower = text.lower()

    affiliation_scores = defaultdict(int)

    for party, keywords in POLITICAL_AFFILIATION_KEYWORDS.items():
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            affiliation_scores[party] += count

    # Find dominant affiliation
    if affiliation_scores:
        dominant = max(affiliation_scores.items(), key=lambda x: x[1])
        if dominant[1] >= 2:  # At least 2 mentions
            return {
                "affiliation": dominant[0],
                "confidence": min(dominant[1] * 10, 100),
                "all_scores": dict(affiliation_scores)
            }

    return {
        "affiliation": "unknown",
        "confidence": 0,
        "all_scores": dict(affiliation_scores)
    }

def _extract_articles_and_bylines(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extract article links."""

    articles = set()
    article_patterns = [
        r"/\d{4}/\d{2}/",
        r"/(article|story|news|blog|post|opinion|analysis|report)/",
    ]

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue

        full_url = urljoin(base_url, href)

        if any(re.search(pattern, full_url, re.I) for pattern in article_patterns):
            articles.add(full_url)

    return list(articles)[:50]

def _extract_publish_date(soup: BeautifulSoup, page_text: str) -> Optional[str]:
    """Extract article publish date."""

    date_meta_names = [
        "article:published_time",
        "datePublished",
        "publishDate",
        "date",
        "pubdate",
        "publication_date",
        "DC.date.issued",
    ]

    for name in date_meta_names:
        for attr in ["property", "name", "itemprop"]:
            tag = soup.find("meta", {attr: name})
            if tag and tag.get("content"):
                return tag["content"]

    # JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict):
                date = data.get("datePublished") or data.get("dateCreated")
                if date:
                    return date
        except:
            pass

    # Time tag
    time_tag = soup.find("time")
    if time_tag:
        return time_tag.get("datetime") or time_tag.get_text(strip=True)

    # Pattern matching
    iso_date = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', page_text)
    if iso_date:
        return iso_date.group(0)

    simple_date = re.search(r'\d{4}-\d{2}-\d{2}', page_text)
    if simple_date:
        return simple_date.group(0)

    return None

# ============================================================================
# CONTENT ANALYSIS
# ============================================================================

def _analyze_content_quality(text: str) -> Dict[str, Any]:
    """Analyze content quality."""

    if not text:
        return {"quality_score": 0, "indicators": []}

    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words)

    if total_words == 0:
        return {"quality_score": 0, "indicators": []}

    sentences = re.split(r'[.!?]+', text)
    num_sentences = len([s for s in sentences if len(s.strip()) > 10])

    avg_word_length = sum(len(w) for w in words) / total_words
    avg_sentence_length = total_words / num_sentences if num_sentences > 0 else 0

    indicators = []
    quality_score = 5

    if total_words > 300:
        indicators.append("substantial_content")
        quality_score += 2

    if 15 < avg_sentence_length < 30:
        indicators.append("readable_sentences")
        quality_score += 1

    if avg_word_length > 4.5:
        indicators.append("sophisticated_vocabulary")
        quality_score += 1

    if re.search(r'\b(according to|sources?|reported|cited|research|study|data shows)\b', text, re.I):
        indicators.append("cited_sources")
        quality_score += 2

    return {
        "quality_score": min(quality_score, 10),
        "total_words": total_words,
        "num_sentences": num_sentences,
        "indicators": indicators,
    }

def _analyze_tone_and_bias(texts: List[str], name: str) -> Dict[str, Any]:
    """
    ENHANCED comprehensive tone and bias analysis with advanced algorithms.
    Uses weighted scoring, contextual analysis, publication bias, and topic analysis.
    """

    if not texts:
        return {
            "tone_score": 0,
            "bias_label": "unknown",
            "bias_confidence": 0,
            "controversy_score": 0,
            "credibility_score": 5,
            "political_affiliation": {"affiliation": "unknown", "confidence": 0},
            "sentiment_analysis": {},
            "topic_analysis": {}
        }

    combined = " ".join([t for t in texts if t])
    combined_lower = combined.lower()
    words = re.findall(r'\b\w+\b', combined_lower)
    total_words = max(len(words), 1)

    # =========================
    # 1. WEIGHTED BIAS SCORING
    # =========================
    weighted_bias_scores = {"left": 0, "right": 0, "centrist": 0}

    for bias_type, weight_categories in BIAS_KEYWORDS_WEIGHTED.items():
        for weight_level, keywords in weight_categories.items():
            weight = 3 if weight_level == "strong" else (2 if weight_level == "medium" else 1)
            for keyword in keywords:
                count = combined_lower.count(keyword.lower())
                weighted_bias_scores[bias_type] += count * weight
                if count > 0:
                    logger.debug(f"Found {bias_type} indicator '{keyword}' x{count} (weight: {weight})")

    # =========================
    # 2. CONTEXTUAL PHRASE ANALYSIS
    # =========================
    contextual_scores = {"left": 0, "right": 0, "centrist": 0}

    for bias_type, phrases in CONTEXTUAL_BIAS_PHRASES.items():
        for phrase_pattern in phrases:
            matches = re.findall(phrase_pattern, combined_lower, re.I)
            if matches:
                contextual_scores[bias_type] += len(matches) * 5  # High weight for contextual matches
                logger.debug(f"Contextual match for {bias_type}: {phrase_pattern} ({len(matches)} times)")

    # =========================
    # 3. PUBLICATION BIAS ANALYSIS
    # =========================
    publication_scores = {"left": 0, "right": 0, "centrist": 0}

    # Analyze which publications the journalist writes for
    for text in texts:
        text_lower = text.lower()
        for pub in PUBLICATION_BIAS["left_leaning"]:
            if pub in text_lower:
                publication_scores["left"] += 2
        for pub in PUBLICATION_BIAS["right_leaning"]:
            if pub in text_lower:
                publication_scores["right"] += 2
        for pub in PUBLICATION_BIAS["centrist"]:
            if pub in text_lower:
                publication_scores["centrist"] += 1

    # =========================
    # 4. TOPIC-BASED BIAS ANALYSIS
    # =========================
    topic_scores = {"left": 0, "right": 0, "centrist": 0}
    topics_covered = {"left": [], "right": [], "centrist": []}

    for topic in TOPIC_BIAS_INDICATORS["left_topics"]:
        if topic.lower() in combined_lower:
            topic_scores["left"] += 3
            topics_covered["left"].append(topic)

    for topic in TOPIC_BIAS_INDICATORS["right_topics"]:
        if topic.lower() in combined_lower:
            topic_scores["right"] += 3
            topics_covered["right"].append(topic)

    for topic in TOPIC_BIAS_INDICATORS["centrist_topics"]:
        if topic.lower() in combined_lower:
            topic_scores["centrist"] += 2
            topics_covered["centrist"].append(topic)

    # =========================
    # 5. AGGREGATE BIAS SCORES
    # =========================
    final_bias_scores = {}
    for bias_type in ["left", "right", "centrist"]:
        final_bias_scores[bias_type] = (
            weighted_bias_scores[bias_type] +
            contextual_scores[bias_type] * 1.5 +  # Contextual phrases weighted higher
            publication_scores[bias_type] +
            topic_scores[bias_type]
        )

    # Normalize scores
    total_score = sum(final_bias_scores.values())
    if total_score > 0:
        final_bias_scores_normalized = {
            k: round((v / total_score) * 100, 2)
            for k, v in final_bias_scores.items()
        }
    else:
        final_bias_scores_normalized = {"left": 0, "right": 0, "centrist": 0}

    # =========================
    # 6. DETERMINE BIAS LABEL
    # =========================
    sorted_biases = sorted(final_bias_scores.items(), key=lambda x: x[1], reverse=True)

    # Calculate confidence based on score distribution
    if sorted_biases[0][1] > 0:
        confidence = min(sorted_biases[0][1] / max(total_score, 1) * 100, 100)

        # Check for mixed bias
        if len(sorted_biases) > 1 and sorted_biases[1][1] >= sorted_biases[0][1] * 0.4:
            bias_label = f"{sorted_biases[0][0]}-{sorted_biases[1][0]} mixed"
            confidence = confidence * 0.7  # Lower confidence for mixed
        elif sorted_biases[0][1] >= 10:  # Threshold for clear bias
            bias_label = sorted_biases[0][0]
        else:
            bias_label = "centrist"
            confidence = 50
    else:
        bias_label = "unknown"
        confidence = 0

    logger.info(f"Bias detection: {bias_label} (confidence: {confidence:.1f}%)")
    logger.info(f"Score breakdown - Left: {final_bias_scores['left']}, Right: {final_bias_scores['right']}, Centrist: {final_bias_scores['centrist']}")

    # =========================
    # 7. SENTIMENT ANALYSIS
    # =========================
    sentiment_score = 0
    sentiment_breakdown = defaultdict(int)

    for sentiment_type, sentiment_data in SENTIMENT_KEYWORDS.items():
        keywords = sentiment_data["keywords"]
        weight = sentiment_data["weight"]

        for keyword in keywords:
            count = combined_lower.count(keyword.lower())
            if count > 0:
                sentiment_score += count * weight
                sentiment_breakdown[sentiment_type] += count

    # Normalize sentiment to -10 to +10 scale
    sentiment_normalized = max(min(sentiment_score / max(total_words / 100, 1), 10), -10)

    # =========================
    # 8. EMOTIONAL TONE
    # =========================
    emotion_score = 0
    emotion_breakdown = defaultdict(int)

    for level, keywords in EMOTIONAL_KEYWORDS.items():
        count = sum(combined_lower.count(k) for k in keywords)
        emotion_breakdown[level] = count
        if level == "high":
            emotion_score += count * 3
        elif level == "medium":
            emotion_score += count * 2
        else:
            emotion_score += count

    tone_score = min((emotion_score / total_words) * 100, 10)

    # =========================
    # 9. POLITICAL AFFILIATION
    # =========================
    political_affiliation = _extract_political_affiliation(combined)

    # =========================
    # 10. CONTROVERSY ANALYSIS
    # =========================
    controversy_score = 0
    controversy_snippets = []

    sentences = re.split(r'[.!?]+', combined)
    for sentence in sentences[:100]:
        sentence_clean = sentence.strip()
        if len(sentence_clean) < 20:
            continue

        for level, keywords in CONTROVERSY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in sentence_clean:
                    if level == "strong":
                        controversy_score += 3
                    elif level == "medium":
                        controversy_score += 2
                    else:
                        controversy_score += 1

                    if len(controversy_snippets) < 10:
                        controversy_snippets.append({
                            "text": sentence_clean[:200],
                            "keyword": keyword,
                            "severity": level
                        })
                    break

    # =========================
    # 11. CREDIBILITY SCORING
    # =========================
    credibility_score = 5
    cred_indicators = []

    for indicator_type, keywords in CREDIBILITY_INDICATORS.items():
        for keyword in keywords:
            if keyword in combined_lower:
                if indicator_type == "positive":
                    credibility_score += 1
                    cred_indicators.append(f"+{keyword}")
                else:
                    credibility_score -= 1
                    cred_indicators.append(f"-{keyword}")

    credibility_score = max(0, min(credibility_score, 10))

    # =========================
    # RETURN COMPREHENSIVE ANALYSIS
    # =========================
    return {
        "tone_score": round(tone_score, 2),
        "emotion_breakdown": dict(emotion_breakdown),
        "bias_label": bias_label,
        "bias_confidence": round(confidence, 2),
        "bias_scores": final_bias_scores_normalized,
        "bias_score_details": {
            "weighted_keywords": weighted_bias_scores,
            "contextual_phrases": contextual_scores,
            "publication_bias": publication_scores,
            "topic_bias": topic_scores
        },
        "political_affiliation": political_affiliation,
        "sentiment_score": round(sentiment_normalized, 2),
        "sentiment_breakdown": dict(sentiment_breakdown),
        "topic_analysis": {
            "left_topics": topics_covered["left"],
            "right_topics": topics_covered["right"],
            "centrist_topics": topics_covered["centrist"]
        },
        "controversy_score": min(controversy_score, 10),
        "controversy_snippets": controversy_snippets,
        "credibility_score": credibility_score,
        "credibility_indicators": cred_indicators,
    }

# ============================================================================
# PAGE PROCESSING
# ============================================================================

async def _process_page(
    client: httpx.AsyncClient,
    url: str,
    name: str,
    rank: int = 0
) -> Optional[Dict[str, Any]]:
    """Process a single page and extract all data."""

    logger.info(f"Processing: {url}")

    response = await _fetch_with_retry(client, url)
    if not response or response.status_code != 200:
        return {
            "url": url,
            "domain": urlparse(url).netloc.replace("www.", ""),
            "error": "fetch_failed",
        }

    try:
        page_text = response.text
        soup = BeautifulSoup(page_text, "html.parser")
        base_url = str(response.url)
        domain = urlparse(base_url).netloc.replace("www.", "")

        # Extract components
        title = _clean_text(soup.title.string) if soup.title else None
        profile_image = _extract_profile_image(soup, base_url, page_text)
        social_links = _extract_social_links(soup, base_url, page_text)
        article_links = _extract_articles_and_bylines(soup, base_url)
        contact = _extract_contact_info(soup)
        bio = _extract_bio_and_description(soup, name)
        publish_date = _extract_publish_date(soup, page_text)

        # Extract awards from this page
        awards = _extract_awards(soup, page_text, name)

        # Content
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p", limit=50)]
        content = " ".join(paragraphs)

        # Meta
        desc_tag = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
        meta_description = desc_tag.get("content") if desc_tag else None
        snippet = _get_snippet(meta_description or content)

        author_meta = soup.find("meta", {"name": "author"})
        meta_author = author_meta.get("content") if author_meta else None

        # Author verification
        author_verified = False
        verification_method = None

        if meta_author and name_in_text(name, meta_author):
            author_verified = True
            verification_method = "meta_tag"
        elif bio and name_in_text(name, bio):
            author_verified = True
            verification_method = "bio_section"
        elif re.search(rf'\bby\s+{re.escape(name.split()[0])}', page_text, re.I):
            if name_in_text(name, page_text):
                author_verified = True
                verification_method = "byline_pattern"
        elif name_in_text(name, page_text):
            author_verified = True
            verification_method = "content_mention"

        # Analysis
        quality = _analyze_content_quality(content)
        trust_score = _calculate_domain_trust_score(domain)

        result = {
            "url": base_url,
            "domain": domain,
            "rank": rank,
            "title": title,
            "snippet": snippet,
            "content": content[:MAX_CONTENT_CHARS] if content else None,
            "profile_image": profile_image,
            "bio": bio,
            "social_links": social_links,
            "emails": contact["emails"],
            "phones": contact["phones"],
            "article_links": article_links,
            "publish_date": publish_date,
            "awards": awards,
            "author_verified": author_verified,
            "verification_method": verification_method,
            "domain_trust_score": trust_score,
            "content_quality": quality,
            "meta_author": meta_author,
            "fetched_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"✓ Processed {domain} - Verified: {author_verified}, Trust: {trust_score}/10, Awards: {len(awards)}")
        return result

    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        return {
            "url": url,
            "domain": urlparse(url).netloc.replace("www.", ""),
            "error": str(e),
        }

# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

async def fetch_journalist_data(
    name: str,
    extra_sites: Optional[List[str]] = None,
    max_results: int = 60,
    run_ai: bool = False
) -> Dict[str, Any]:
    """
    Main function to fetch comprehensive journalist data.

    Returns complete profile with:
    - Primary profile (bio, image, social, contact)
    - Articles list
    - Tone, bias, controversy, credibility analysis
    - Raw scraped data
    """

    if not name or not name.strip():
        raise ValueError("Journalist name is required")

    start_time = datetime.utcnow()
    normalized_name = _clean_text(name)

    logger.info("=" * 80)
    logger.info(f"🔍 Fetching data for: {normalized_name}")
    logger.info("=" * 80)

    # Step 1: Discovery
    # Enhanced: multi-query discovery for political, awards, controversy, socials, biography, etc.
    discovered_urls = await serpapi_multi_query_search(normalized_name, max_per_query=min(10, max_results // 8))

    if extra_sites:
        discovered_urls.extend(extra_sites)

    if not discovered_urls:
        name_slug = normalized_name.lower().replace(" ", "-")
        discovered_urls = [
            f"https://en.wikipedia.org/wiki/{name_slug}",
            f"https://www.google.com/search?q={quote_plus(normalized_name)}+journalist",
            f"https://twitter.com/{name_slug}",
            f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(normalized_name)}",
        ]

    # Deduplicate
    seen_urls = set()
    urls_to_process = []
    for url in discovered_urls:
        if url not in seen_urls and len(urls_to_process) < max_results:
            seen_urls.add(url)
            urls_to_process.append(url)

    logger.info(f"📋 Discovered {len(urls_to_process)} URLs to process")

    # Step 2: Concurrent scraping
    semaphore = asyncio.Semaphore(DEFAULT_CONCURRENCY)

    async def worker(url, idx):
        async with semaphore:
            result = await _process_page(client, url, normalized_name, rank=idx)
            await asyncio.sleep(DEFAULT_DELAY)
            return result

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
    ) as client:
        tasks = [worker(url, i) for i, url in enumerate(urls_to_process)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Step 3: Process results
    valid_pages = []
    failed_pages = []

    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Task exception: {result}")
            failed_pages.append({"error": str(result)})
        elif result and not result.get("error"):
            valid_pages.append(result)
        else:
            failed_pages.append(result)

    logger.info(f"✅ Successfully processed: {len(valid_pages)}/{len(urls_to_process)} pages")

    # Step 4: Select best profile
    verified_pages = [p for p in valid_pages if p.get("author_verified")]

    primary_profile = None
    if verified_pages:
        primary_profile = max(
            verified_pages,
            key=lambda p: (
                p.get("domain_trust_score", 0),
                bool(p.get("bio")),
                bool(p.get("profile_image")),
                len(p.get("social_links", []))
            )
        )
    elif valid_pages:
        primary_profile = max(valid_pages, key=lambda p: p.get("domain_trust_score", 0))

    # Step 5: Aggregate articles
    articles = []
    for page in verified_pages:
        articles.append({
            "title": page.get("title"),
            "url": page.get("url"),
            "domain": page.get("domain"),
            "snippet": page.get("snippet"),
            "publish_date": page.get("publish_date"),
            "content_quality": page.get("content_quality"),
            "trust_score": page.get("domain_trust_score"),
        })

    # Step 6: Enhanced Analysis
    all_content = [p.get("content", "") for p in valid_pages if p.get("content")]
    analysis = _analyze_tone_and_bias(all_content, normalized_name)

    # Step 7: Gather awards and recognitions from all pages
    awards_found = []
    for page in valid_pages:
        text = page.get("content", "")
        page_awards = _extract_awards(None, text, normalized_name) if text else []
        awards_found.extend(page_awards)
    # Deduplicate award contexts/names
    seen_award_keys = set()
    final_awards = []
    for award in awards_found:
        key = (award['name'].lower(), award['year'])
        if key not in seen_award_keys and len(final_awards) < 10:
            seen_award_keys.add(key)
            final_awards.append(award)

    # Step 8: Compile final profile
    profile_data = {
        "name": normalized_name,
        "query_timestamp": start_time.isoformat(),
        "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),

        "urls_discovered": len(urls_to_process),
        "pages_processed": len(valid_pages),
        "pages_failed": len(failed_pages),
        "verification_rate": round(len(verified_pages) / max(len(valid_pages), 1) * 100, 2),

        "primary_profile": {
            "url": primary_profile.get("url") if primary_profile else None,
            "domain": primary_profile.get("domain") if primary_profile else None,
            "bio": primary_profile.get("bio") if primary_profile else None,
            "profile_image": primary_profile.get("profile_image") if primary_profile else None,
            "social_links": primary_profile.get("social_links", []) if primary_profile else [],
            "emails": primary_profile.get("emails", []) if primary_profile else [],
            "phones": primary_profile.get("phones", []) if primary_profile else [],
            "trust_score": primary_profile.get("domain_trust_score") if primary_profile else 0,
        } if primary_profile else None,

        "articles": articles,
        "total_articles_found": len(articles),
        "awards": final_awards,

        "analysis": {
            "tone_score": analysis.get("tone_score", 0),
            "emotion_breakdown": analysis.get("emotion_breakdown", {}),
            "bias_label": analysis.get("bias_label", "unknown"),
            "bias_scores": analysis.get("bias_scores", {}),
            "political_affiliation": analysis.get("political_affiliation", {}),
            "controversy_score": analysis.get("controversy_score", 0),
            "controversy_snippets": analysis.get("controversy_snippets", []),
            "credibility_score": analysis.get("credibility_score", 5),
            "credibility_indicators": analysis.get("credibility_indicators", []),
        },

        "raw_pages": valid_pages,
        "errors": failed_pages,
    }

    # Step 9: AI analysis (optional)
    if run_ai:
        try:
            from .ai_analysis import analyze_journalist
            ai_result = analyze_journalist(normalized_name, profile_data)
            profile_data["ai_analysis"] = ai_result
        except Exception as e:
            logger.warning(f"AI analysis failed: {str(e)}")

    logger.info("=" * 80)
    logger.info(f"✅ Completed: {normalized_name}")
    logger.info(f"📊 Articles: {len(articles)}, Verification: {profile_data['verification_rate']}%")
    logger.info("=" * 80)

    return profile_data

# ============================================================================
# SYNC WRAPPER
# ============================================================================

def fetch_journalist_data_sync(
    name: str,
    extra_sites: Optional[List[str]] = None,
    max_results: int = 60
) -> Dict[str, Any]:
    """Synchronous wrapper."""
    return asyncio.run(
        fetch_journalist_data(
            name=name,
            extra_sites=extra_sites,
            max_results=max_results
        )
    )

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python serp_scraper_complete.py 'Journalist Name'")
        sys.exit(1)

    journalist_name = sys.argv[1]
    print(f"\n🔍 Fetching data for: {journalist_name}\n")

    result = fetch_journalist_data_sync(journalist_name, max_results=30)

    print("\n" + "=" * 80)
    print("📊 RESULTS SUMMARY")
    print("=" * 80)

    summary = {
        "name": result["name"],
        "pages_processed": result["pages_processed"],
        "articles_found": result["total_articles_found"],
        "verification_rate": f"{result['verification_rate']}%",
        "profile": {
            "has_bio": bool(result["primary_profile"]["bio"]) if result["primary_profile"] else False,
            "has_image": bool(result["primary_profile"]["profile_image"]) if result["primary_profile"] else False,
            "social_links": len(result["primary_profile"]["social_links"]) if result["primary_profile"] else 0,
            "trust_score": f"{result['primary_profile']['trust_score']}/10" if result["primary_profile"] else "0/10",
        },
        "analysis": {
            "tone_score": result["analysis"]["tone_score"],
            "bias": result["analysis"]["bias_label"],
            "controversy_score": result["analysis"]["controversy_score"],
            "credibility_score": result["analysis"]["credibility_score"],
        }
    }

    print(json.dumps(summary, indent=2))

    # Save full results
    output_file = f"journalist_data_{normalized_name.replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Full results saved to: {output_file}")
