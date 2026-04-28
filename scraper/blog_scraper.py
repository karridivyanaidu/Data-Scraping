# scraper/blog_scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from langdetect import detect

# Import our utility functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chunking import chunk_text
from utils.tagging import generate_tags
from scoring.trust_score import calculate_trust_score


def scrape_blog(url: str) -> dict:
    """
    Scrapes a single blog post URL.
    Returns a structured dictionary.
    """

    print(f"\nScraping blog: {url}")

    # ── Step 1: Download the page ──
    try:
        headers = {
            # We pretend to be a browser so websites don't block us
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises error if page not found
    except Exception as e:
        print(f"  ERROR downloading page: {e}")
        return None

    # ── Step 2: Parse the HTML ──
    soup = BeautifulSoup(response.text, "html.parser")

    # ── Step 3: Extract Title ──
    title = ""
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.find("title"):
        title = soup.find("title").get_text(strip=True)

    # ── Step 4: Extract Author ──
    author = "Unknown"

    # Try common HTML patterns for author
    author_patterns = [
        {"name": "author"},
        {"class": "author"},
        {"class": "byline"},
        {"rel": "author"},
        {"itemprop": "author"},
    ]

    for pattern in author_patterns:
        tag = soup.find(attrs=pattern)
        if tag:
            author = tag.get_text(strip=True)
            break

    # Also check meta tags
    meta_author = soup.find("meta", {"name": "author"})
    if meta_author and author == "Unknown":
        author = meta_author.get("content", "Unknown")

    # ── Step 5: Extract Published Date ──
    published_date = ""

    # Try meta tags first
    date_meta_names = [
        "article:published_time",
        "publishedDate",
        "date",
        "DC.date",
        "og:published_time",
    ]

    for name in date_meta_names:
        meta = soup.find("meta", {"property": name}) or soup.find("meta", {"name": name})
        if meta:
            published_date = meta.get("content", "")[:10]  # Take only YYYY-MM-DD
            break

    # Try <time> tag
    if not published_date:
        time_tag = soup.find("time")
        if time_tag:
            published_date = time_tag.get("datetime", time_tag.get_text(strip=True))[:10]

    # ── Step 6: Extract Main Content ──
    # Remove unwanted elements first
    for tag in soup(["nav", "header", "footer", "script", "style", "aside", "form"]):
        tag.decompose()  # Delete these tags from the HTML

    # Try to find the main article body
    article_body = (
        soup.find("article") or
        soup.find("main") or
        soup.find(class_=["post-content", "article-body",
                          "entry-content", "content", "blog-content"])
    )

    if article_body:
        raw_text = article_body.get_text(separator="\n\n", strip=True)
    else:
        # Fallback: get all paragraph text
        paragraphs = soup.find_all("p")
        raw_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

    # ── Step 7: Detect Language ──
    language = "en"  # Default
    try:
        if raw_text:
            language = detect(raw_text[:500])  # Detect from first 500 chars
    except:
        language = "en"

    # ── Step 8: Generate Tags & Chunks ──
    tags = generate_tags(raw_text)
    chunks = chunk_text(raw_text)

    # ── Step 9: Build the source dictionary ──
    source_data = {
        "source_url":     url,
        "source_type":    "blog",
        "title":          title,
        "author":         author,
        "published_date": published_date,
        "language":       language,
        "region":         "",        # Hard to detect for blogs
        "topic_tags":     tags,
        "citation_count": 0,         # Blogs rarely have citation counts
        "content_chunks": chunks,
        "trust_score":    0,         # Will be calculated below
    }

    # ── Step 10: Calculate Trust Score ──
    trust_result = calculate_trust_score(source_data)
    source_data["trust_score"] = trust_result["trust_score"]

    print(f"  ✓ Done! Trust Score: {source_data['trust_score']}")
    return source_data


def scrape_multiple_blogs(urls: list) -> list:
    """Scrapes a list of blog URLs and returns all results."""
    results = []
    for url in urls:
        result = scrape_blog(url)
        if result:
            results.append(result)
    return results