# main.py  ← Run this file to scrape everything

import json
import os

from scraper.blog_scraper    import scrape_multiple_blogs
from scraper.youtube_scraper import scrape_youtube
from scraper.pubmed_scraper  import scrape_pubmed


# ── EDIT THESE URLS ──────────────────────────────
# Put any real blog/YouTube/PubMed URLs you want to scrape

BLOG_URLS = [
    "https://www.geeksforgeeks.org/python-web-scraping-tutorial/",
    "https://realpython.com/python-web-scraping-practical-introduction/",
    "https://en.wikipedia.org/wiki/Web_scraping",   # ← new 3rd blog
]

YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=XVv6mJpFOb0",
    "https://www.youtube.com/watch?v=gRLHr664tXA",  # ← new 2nd video
]

PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov/38069840/"
# ─────────────────────────────────────────────────


def main():
    all_results = []

    # ── Scrape Blogs ──
    print("\n" + "="*50)
    print("SCRAPING BLOGS...")
    print("="*50)
    blogs = scrape_multiple_blogs(BLOG_URLS)
    all_results.extend(blogs)

    # ── Scrape YouTube ──
    print("\n" + "="*50)
    print("SCRAPING YOUTUBE...")
    print("="*50)
    for url in YOUTUBE_URLS:
        result = scrape_youtube(url)
        if result:
            all_results.append(result)

    # ── Scrape PubMed ──
    print("\n" + "="*50)
    print("SCRAPING PUBMED...")
    print("="*50)
    pubmed = scrape_pubmed(PUBMED_URL)
    if pubmed:
        all_results.append(pubmed)

    # ── Save to JSON ──
    os.makedirs("output", exist_ok=True)
    output_path = "output/scraped_data.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"✓ ALL DONE! {len(all_results)} sources saved to {output_path}")
    print("="*50)


if __name__ == "__main__":
    main()