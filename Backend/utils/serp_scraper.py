import os
import re
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin, quote_plus

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("serp_scraper")
logging.basicConfig(level=logging.INFO)

SERP_API_KEY = os.getenv("SERP_API_KEY")  
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
]
DEFAULT_HEADERS = {"User-Agent": USER_AGENTS[0]}
DEFAULT_CONCURRENCY = int(os.getenv("SCRAPER_CONCURRENCY", "8"))
DEFAULT_DELAY = float(os.getenv("SCRAPER_DELAY", "0.25"))
MAX_CONTENT_CHARS = 4000
MAX_SNIPPET = 240

# Controversy / emotional / bias keyword lists (simple heuristics)
CONTROVERSY_KEYWORDS = [
    "controversy", "allegation", "allegations", "accused", "accusation",
    "scandal", "resign", "resignation", "charged", "charged with",
    "convict", "convicted", "lawsuit", "sued", "complaint", "probe", "investigation", "FIR"
]
EMOTIONAL_KEYWORDS = [
    "shock", "outrage", "heartbreaking", "angry", "angry", "devastated",
    "emotional", "passionate", "furious"
]
LEFT_KEYWORDS = ["left", "liberal", "progressive", "socialist", "secular", "anti-establishment"]
RIGHT_KEYWORDS = ["right", "conservative", "nationalist", "pro-establishment", "pro-government"]
def _get_snippet(text: str) -> str:
    return (text or "")[:MAX_SNIPPET]

# ----------------- Helper HTTP layer -----------------
async def _fetch_text(client: httpx.AsyncClient, url: str, timeout: int = 12) -> Optional[httpx.Response]:
    """Fetch url using httpx client with rotating User-Agent"""
    headers = {"User-Agent": USER_AGENTS[hash(url) % len(USER_AGENTS)]}
    try:
        r = await client.get(url, headers=headers, timeout=timeout, follow_redirects=True)
        return r
    except Exception as e:
        logger.debug("fetch error %s -> %s", url, e)
        return None


# ----------------- SerpApi discovery -----------------
async def serpapi_search(query: str, num: int = 20) -> List[str]:
    """
    Use SerpApi if SERP_API_KEY present; otherwise return empty list.
    Returns list of raw links.
    """
    key = SERP_API_KEY
    if not key:
        logger.info("SERP_API_KEY not set; skipping SerpApi discovery.")
        return []

    endpoint = "https://serpapi.com/search.json"
    params = {"engine": "google", "q": query, "num": num, "api_key": key}
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.get(endpoint, params=params, headers=DEFAULT_HEADERS)
            r.raise_for_status()
            data = r.json()
            links: List[str] = []
            # organic_results often contains 'link'
            for item in data.get("organic_results", []):
                if isinstance(item, dict):
                    link = item.get("link") or item.get("url")
                    if link:
                        links.append(link)
            # include other likely fields
            for item in data.get("top_results", []):
                if isinstance(item, dict) and item.get("link"):
                    links.append(item.get("link"))
            return links
        except Exception as e:
            logger.warning("SerpApi lookup failed: %s", e)
            return []


# ----------------- extraction utilities -----------------
def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _name_parts(name: str) -> List[str]:
    return [p.lower() for p in _clean_text(name).split() if p]


def name_in_text(name: str, text: str) -> bool:
    if not name or not text:
        return False
    parts = _name_parts(name)
    txt = re.sub(r"\s+", " ", text.lower())
    if len(parts) >= 2:
        return parts[0] in txt and parts[-1] in txt
    return parts[0] in txt


def _extract_meta(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """Extract standard meta info, json-ld, social links, images."""
    out: Dict[str, Any] = {}
    
    # Title extraction
    out["title"] = _clean_text(soup.title.string) if soup.title else None

    # Profile image extraction (prioritized)
    out["image"] = None
    # Try OpenGraph image first
    og_image = soup.find("meta", property="og:image") or soup.find("meta", property="twitter:image")
    if og_image and og_image.get("content"):
        out["image"] = urljoin(base_url, og_image["content"])
    
    if not out["image"]:
        # Try author/profile images
        profile_imgs = soup.find_all("img", class_=re.compile(r"profile|author|avatar"))
        if profile_imgs:
            for img in profile_imgs:
                src = img.get("src") or img.get("data-src")
                if src:
                    out["image"] = urljoin(base_url, src)
                    break

    # Social links extraction (improved)
    social: Set[str] = set()
    social_patterns = {
        "twitter.com": r"twitter\.com/([^/\?]+)",
        "x.com": r"x\.com/([^/\?]+)",
        "linkedin.com": r"linkedin\.com/in/([^/\?]+)",
        "instagram.com": r"instagram\.com/([^/\?]+)",
        "facebook.com": r"facebook\.com/([^/\?]+)",
    }
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue
            
        # Convert relative URLs to absolute
        if href.startswith("/"):
            href = urljoin(base_url, href)
            
        # Clean up social URLs
        for domain, pattern in social_patterns.items():
            if domain in href.lower():
                match = re.search(pattern, href, re.I)
                if match:
                    clean_url = f"https://{domain}/{match.group(1)}"
                    social.add(clean_url)
                    break
    
    out["social_links"] = list(social)

    # Article links extraction (improved)
    article_links: Set[str] = set()
    article_patterns = [
        r"/\d{4}/\d{2}/",  # Date-based URLs
        r"/article/",
        r"/news/",
        r"/story/",
        r"/author/",
        r"/byline/",
        r"/profile/",
        r"/about/"
    ]
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue
            
        full_url = urljoin(base_url, href)
        
        # Check URL patterns
        if any(re.search(p, full_url, re.I) for p in article_patterns):
            article_links.add(full_url)
            
        # Check link text for article indicators
        link_text = a.get_text(" ", strip=True).lower()
        if any(w in link_text for w in ["read more", "full article", "continue reading"]):
            article_links.add(full_url)

    out["article_links"] = list(article_links)
    
    # Log extraction results
    logger.debug(f"Extracted from {base_url}:")
    logger.debug(f"- Image: {bool(out['image'])}")
    logger.debug(f"- Social links: {len(out['social_links'])}")
    logger.debug(f"- Article links: {len(out['article_links'])}")
    
    return out
def _extract_publish_date_from_meta_or_jsonld(meta_dict: Dict[str, Any], page_text: str) -> Optional[str]:
    """
    Simple heuristics: look into json_ld, meta tags, or datePublished field patterns in page.
    Returns ISO-like string or None.
    """
    # 1) try json_ld quick regex for "datePublished"
    json_ld = meta_dict.get("json_ld")
    if json_ld:
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', json_ld)
        if m:
            return m.group(1)
        m2 = re.search(r'"dateCreated"\s*:\s*"([^"]+)"', json_ld)
        if m2:
            return m2.group(1)

    # 2) common meta tags
    for key in ("article:published_time", "publication_date", "pubdate", "date"):
        # search meta property or meta name
        m = re.search(rf'<meta[^>]+(?:property|name)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']', page_text, re.I)
        if m:
            return m.group(1)

    # 3) loose ISO date pattern in page text (first match)
    m = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', page_text)
    if m:
        return m.group(1)
    # date like YYYY-MM-DD
    m2 = re.search(r'(\d{4}-\d{2}-\d{2})', page_text)
    if m2:
        return m2.group(1)
    return None


def _analyze_tone_and_controversy(texts: List[str], name: str) -> Dict[str, Any]:
    """
    Lightweight heuristics across aggregated texts:
    - tone_score: ratio of emotional keywords to words (0..1)
    - controversy_snippets: sentences containing controversy keywords
    - bias_hint: simple heuristic counting left/right keywords
    """
    joined = " ".join([t or "" for t in texts])
    low = joined.lower()
    total_words = max(1, len(re.findall(r"\w+", low)))
    emotional_count = sum(low.count(k) for k in EMOTIONAL_KEYWORDS)
    tone_score = round(emotional_count / total_words, 5)

    # controversy detection: extract sentences with keywords
    controversy_sentences = []
    sentences = re.split(r'(?<=[.!?])\s+', joined)
    for s in sentences:
        for k in CONTROVERSY_KEYWORDS:
            if k in s.lower():
                controversy_sentences.append(_clean_text(s))
                break

    # bias hint: naive counts
    left_count = sum(low.count(k) for k in LEFT_KEYWORDS)
    right_count = sum(low.count(k) for k in RIGHT_KEYWORDS)
    if left_count > right_count and left_count >= 2:
        bias_hint = "left-leaning"
    elif right_count > left_count and right_count >= 2:
        bias_hint = "right-leaning"
    else:
        bias_hint = "unclear"

    # influence indicator: number of unique domains & social links
    domains = set(re.findall(r"https?://([^/]+)", joined))
    influence_level = "Low"
    if len(domains) >= 5:
        influence_level = "High"
    elif len(domains) >= 2:
        influence_level = "Moderate"

    return {
        "tone_score": tone_score,
        "controversy_snippets": controversy_sentences,
        "bias_hint": bias_hint,
        "left_keyword_count": left_count,
        "right_keyword_count": right_count,
        "influence_level": influence_level
    }

    # ideology / political leaning inference
    ideology_hint = None
    ideolog_phrases = {
        "left-leaning": ["leftist", "liberal", "progressive", "secular voice", "critic of government"],
        "right-leaning": ["nationalist", "pro-government", "hindutva", "right-wing", "rss supporter"],
        "centrist": ["neutral", "balanced", "non-partisan"]
    }
    lower_text = page_text.lower()
    for label, keys in ideolog_phrases.items():
        if any(k in lower_text for k in keys):
            ideology_hint = label
            break

    result["ideology_hint"] = ideology_hint

# ----------------- page processing -----------------
async def _process_page(client: httpx.AsyncClient, url: str, name: str) -> Optional[Dict[str, Any]]:
    """Fetch page, extract meta + content snippet + candidate article links + author presence."""
    resp = await _fetch_text(client, url)
    if not resp:
        logger.debug("No response for %s", url)
        return None

    status = resp.status_code
    domain = urlparse(url).netloc.replace("www.", "").lower()
    if status != 200:
        logger.debug("Non-200 %s -> %s", status, url)
        return {"source": url, "domain": domain, "error_status": status}

    page_text = resp.text or ""
    soup = BeautifulSoup(page_text, "html.parser")
    base = url
    meta = _extract_meta(soup, base)

    # content blob (first N paragraphs)
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    content = " ".join(paras[:40])
    snippet = _get_snippet(meta.get("meta_description") or content[:400])

    # author verification heuristics (more robust)
    author_verified = False
    # 1) meta author match
    if meta.get("meta_author") and name_in_text(name, meta.get("meta_author")):
        author_verified = True

    # 2) json-ld author fields
    json_ld = meta.get("json_ld") or ""
    if json_ld and name_in_text(name, json_ld):
        author_verified = True

    # 3) byline in top headings / by <name>
    if not author_verified:
        top_texts = []
        if soup.title and soup.title.string:
            top_texts.append(soup.title.string)
        for tag in soup.find_all(["h1", "h2"], limit=8):
            if tag and tag.get_text():
                top_texts.append(tag.get_text(" ", strip=True))
        top_blob = " ".join(top_texts + [snippet[:1000]])
        if re.search(r"\bby\s+" + re.escape(name.split()[0]), top_blob, re.I) and name_in_text(name, top_blob):
            author_verified = True

    # 4) full page name presence
    if not author_verified and name_in_text(name, page_text):
        author_verified = True

    publish_date = _extract_publish_date_from_meta_or_jsonld(meta, page_text)

    result = {
        "title": meta.get("title") or (snippet[:80] if snippet else "Untitled"),
        "link": url,
        "domain": domain,
        "snippet": snippet,
        "content": (content[:MAX_CONTENT_CHARS] if content else None),
        "meta_author": meta.get("meta_author"),
        "profile_image": meta.get("image"),
        "bio_section": meta.get("bio_section"),
        "social": meta.get("social_links"),
        "emails": meta.get("emails"),
        "candidate_article_links": meta.get("candidate_article_links", []),
        "author_verified": author_verified,
        "publish_date": publish_date,
        "error_status": None,
    }
    return result
async def _fetch_with_retry(client: httpx.AsyncClient, url: str, max_retries: int = 3) -> Optional[httpx.Response]:
    """Fetch URL with retries and exponential backoff."""
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": USER_AGENTS[hash(url) % len(USER_AGENTS)],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            response = await client.get(
                url, 
                headers=headers,
                timeout=15,
                follow_redirects=True
            )
            
            if response.status_code == 200:
                return response
                
            if response.status_code in [429, 503]:  # Rate limited
                wait_time = (2 ** attempt) + random.random()
                logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                continue
                
        except Exception as e:
            logger.debug(f"Fetch error {url} (attempt {attempt+1}): {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            continue
            
    return None

# ----------------- public function -----------------
async def fetch_journalist_data(name: str, extra_sites: Optional[List[str]] = None, max_results: int = 60) -> Dict[str, Any]:
    """
    Async pipeline:
    1. Discover links via SerpApi (if available) + extra_sites
    2. Fetch discovered links concurrently
    3. Extract profile info, candidate article links, content
    4. Run light analysis (tone/bias/controversy) over aggregated text
    Returns structured dict with:
      - name, query, links_scanned
      - profiles_found (rich dicts)
      - articles (list of article objects with verification flags)
      - analysis: tone_score, bias_hint, controversy_snippets
      - raw_pages: array for debugging
    """
    if not name or not name.strip():
        raise ValueError("Name required")

    normalized = name.strip()
    query = f'"{normalized}" author OR "by {normalized}" OR "{normalized} profile"'
    logger.info("Searching for: %s", query)

    # discover
    discovered = await serpapi_search(query, num=min(50, max_results))
    if extra_sites:
        for s in extra_sites:
            if s not in discovered:
                discovered.append(s)

    # fallback seeds if discovery failed or limited
    if not discovered:
        guess = normalized.replace(" ", "-").lower()
        discovered = [
            f"https://en.wikipedia.org/wiki/{guess}",
            f"https://www.imdb.com/find?q={quote_plus(normalized)}",
            f"https://www.google.com/search?q={quote_plus(normalized)}",
            f"https://starsunfolded.com/{quote_plus(normalized.replace(' ', '-'))}"
        ]

    # dedupe keep order, cap results
    seen: Set[str] = set()
    links: List[str] = []
    for l in discovered:
        if not l:
            continue
        if l in seen:
            continue
        seen.add(l)
        links.append(l)
        if len(links) >= max_results:
            break

    # concurrently fetch pages
    sem = asyncio.Semaphore(DEFAULT_CONCURRENCY)
    async with httpx.AsyncClient(timeout=25, limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)) as client:
        async def worker(u):
            async with sem:
                logger.info("Scraping %s", u)
                res = await _process_page(client, u, normalized)
                await asyncio.sleep(DEFAULT_DELAY)
                return res

        tasks = [asyncio.create_task(worker(u)) for u in links]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    pages: List[Dict[str, Any]] = []
    for res in results:
        if isinstance(res, Exception):
            logger.debug("worker exception: %s", res)
            continue
        if not res:
            continue
        pages.append(res)

    # build articles & profiles
    verified = [p for p in pages if p.get("author_verified")]
    unverified = [p for p in pages if not p.get("author_verified")]

    # profile selection (prioritize verified & profile-like domains)
    profile = None
    if verified:
        # pick the verified page with the richest bio image or social links
        verified_sorted = sorted(verified, key=lambda x: (bool(x.get("profile_image")), len(x.get("social") or []), bool(x.get("bio_section"))), reverse=True)
        profile = verified_sorted[0]
    else:
        # heuristics: wikipedia/imdb/starsunfolded first
        for p in pages:
            dom = (p.get("domain") or "").lower()
            if any(x in dom for x in ("wikipedia.org", "imdb.com", "starsunfolded", "khojstudios")):
                profile = p
                break
    profile = profile or (pages[0] if pages else None)

    # prepare article list
    def to_article_obj(p: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": p.get("title"),
            "link": p.get("link"),
            "source": p.get("domain"),
            "snippet": p.get("snippet"),
            "author_verified": bool(p.get("author_verified")),
            "publish_date": p.get("publish_date"),
            "content_preview": (p.get("content")[:MAX_CONTENT_CHARS] if p.get("content") else None),
            "social": p.get("social"),
            "emails": p.get("emails"),
        }

    articles = [to_article_obj(p) for p in verified] + [to_article_obj(p) for p in unverified]

    # attempt to expand candidate article links (follow internal candidate_article_links for author pages)
    # For performance, follow only candidate links from verified pages (bounded)
    extra_article_links: Set[str] = set()
    follow_limit_per_site = 8
    async with httpx.AsyncClient(timeout=20) as client:
        for p in (verified or pages[:3]):  # prefer verified pages; fallback to first 3
            cand = p.get("candidate_article_links") or []
            cnt = 0
            for l in cand:
                if cnt >= follow_limit_per_site:
                    break
                if l in seen:
                    continue
                seen.add(l)
                try:
                    logger.info("Following candidate article link %s", l)
                    r = await _fetch_text(client, l)
                    if r and r.status_code == 200 and r.text:
                        soup = BeautifulSoup(r.text, "html.parser")
                        meta = _extract_meta(soup, l)
                        paras = [pg.get_text(" ", strip=True) for pg in soup.find_all("p")]
                        content = " ".join(paras[:40])
                        snippet = _get_snippet(meta.get("meta_description") or content[:400])
                        publish_date = _extract_publish_date_from_meta_or_jsonld(meta, r.text)
                        article_obj = {
                            "title": meta.get("title") or snippet[:80],
                            "link": l,
                            "source": urlparse(l).netloc.replace("www.", ""),
                            "snippet": snippet,
                            "author_verified": name_in_text(name, meta.get("meta_author") or "") or name_in_text(name, r.text),
                            "publish_date": publish_date,
                            "content_preview": (content[:MAX_CONTENT_CHARS] if content else None),
                            "social": meta.get("social_links"),
                        }
                        # append if not duplicate link
                        if not any(a["link"] == l for a in articles):
                            articles.append(article_obj)
                    cnt += 1
                    await asyncio.sleep(DEFAULT_DELAY)
                except Exception as e:
                    logger.debug("follow link err %s -> %s", l, e)
                    continue

    # run light analysis across content snippets
    aggregated_texts = [a.get("content_preview") or a.get("snippet") or "" for a in articles]
    analysis = _analyze_tone_and_controversy(aggregated_texts, normalized)

    # enrich profile with merged fields
    merged_profile = {
        "source": profile.get("link") if profile else None,
        "domain": profile.get("domain") if profile else None,
        "bio": profile.get("bio_section") if profile else None,
        "profile_image": profile.get("profile_image") if profile else None,
        "social": profile.get("social") if profile else [],
        "emails": profile.get("emails") if profile else [],
    } if profile else {}

    return {
        "name": normalized,
        "query": query,
        "links_scanned": len(links),
        "profiles_found": [merged_profile] if merged_profile else [],
        "articles": articles,
        "analysis": analysis,
        "raw_pages": pages,
    }
def _extract_image(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract the most probable profile image using multiple strategies."""
    # 1️⃣ Meta tags (OpenGraph / Twitter)
    meta_props = [
        {"property": "og:image"},
        {"name": "og:image"},
        {"property": "twitter:image"},
        {"name": "twitter:image"},
    ]
    for attrs in meta_props:
        m = soup.find("meta", attrs=attrs)
        if m and m.get("content"):
            return urljoin(base_url, m["content"])

    # 2️⃣ Inline image tags with relevant hints
    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy")
            or img.get("data-original")
        )
        if not src:
            continue
        alt = (img.get("alt") or "").lower()
        cls = " ".join(img.get("class") or []).lower()
        if any(k in src.lower() for k in ["profile", "avatar", "author", "bio", "face"]) or \
           any(k in alt for k in ["profile", "journalist", "author", "reporter"]) or \
           any(k in cls for k in ["profile", "avatar", "author", "bio"]):
            return urljoin(base_url, src)

    # 3️⃣ noscript fallback (common in lazy-loaded images)
    for ns in soup.find_all("noscript"):
        if "img" in ns.text:
            match = re.search(r'src=["\']([^"\']+)["\']', ns.text)
            if match:
                return urljoin(base_url, match.group(1))

    # 4️⃣ JSON-LD structured data (schema.org)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.text)
            if isinstance(data, dict) and "image" in data:
                if isinstance(data["image"], str):
                    return urljoin(base_url, data["image"])
                elif isinstance(data["image"], list) and data["image"]:
                    return urljoin(base_url, data["image"][0])
        except Exception:
            continue

    # 5️⃣ Fallback: first large image on the page
    imgs = soup.find_all("img")
    if imgs:
        biggest = max(imgs, key=lambda i: int(i.get("width") or 0) * int(i.get("height") or 0))
        src = (
            biggest.get("src")
            or biggest.get("data-src")
            or biggest.get("data-original")
            or biggest.get("data-lazy")
        )
        if src:
            return urljoin(base_url, src)

    return None


# Sync wrapper for backwards compatibility
def fetch_journalist_data_sync(name: str, extra_sites: Optional[List[str]] = None, max_results: int = 60) -> Dict[str, Any]:
    import asyncio
    return asyncio.run(fetch_journalist_data(name=name, extra_sites=extra_sites, max_results=max_results))


# Quick dev run
if __name__ == "__main__":
    import asyncio, json
    out = asyncio.run(fetch_journalist_data("Barkha Dutt", max_results=20))
    print(json.dumps(out, indent=2, ensure_ascii=False)[:8000])
