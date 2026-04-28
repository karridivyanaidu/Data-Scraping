# scraper/pubmed_scraper.py

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chunking import chunk_text
from utils.tagging import generate_tags
from scoring.trust_score import calculate_trust_score


def scrape_pubmed(pubmed_url: str) -> dict:
    """
    Scrapes a PubMed article using the free NCBI API.
    
    You don't need an API key for basic use.
    
    Example URL: https://pubmed.ncbi.nlm.nih.gov/38069840/
    We extract the ID (38069840) and call the API.
    """

    print(f"\nScraping PubMed: {pubmed_url}")

    # ── Step 1: Extract PubMed ID from URL ──
    # URL looks like: https://pubmed.ncbi.nlm.nih.gov/38069840/
    pmid = pubmed_url.rstrip("/").split("/")[-1]
    print(f"  PubMed ID: {pmid}")

    # ── Step 2: Call the NCBI API ──
    # This is a FREE public API — no key needed
    api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db":      "pubmed",
        "id":      pmid,
        "retmode": "json",
    }

    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"  ERROR calling API: {e}")
        return None

    # ── Step 3: Extract metadata from API response ──
    article = data.get("result", {}).get(pmid, {})

    title   = article.get("title", "")
    journal = article.get("fulljournalname", "")
    pub_date = article.get("pubdate", "")[:4]  # Just the year

    # Authors: API gives a list of author objects
    authors_list = article.get("authors", [])
    if authors_list:
        author = ", ".join(a.get("name", "") for a in authors_list[:3])
        if len(authors_list) > 3:
            author += " et al."
    else:
        author = "Unknown"

    # ── Step 4: Get the Abstract (separate API call) ──
    abstract_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    abstract_params = {
        "db":      "pubmed",
        "id":      pmid,
        "retmode": "text",
        "rettype": "abstract",
    }

    abstract_text = ""
    try:
        abstract_response = requests.get(abstract_url, params=abstract_params, timeout=10)
        abstract_text = abstract_response.text
    except Exception as e:
        print(f"  WARNING: Could not fetch abstract: {e}")

    # ── Step 5: Generate Tags & Chunks ──
    full_content = f"{title}\n\n{abstract_text}"
    tags   = generate_tags(full_content)
    chunks = chunk_text(full_content)

    # ── Step 6: Build source dictionary ──
    source_data = {
        "source_url":     pubmed_url,
        "source_type":    "pubmed",
        "title":          title,
        "author":         author,
        "published_date": pub_date,
        "language":       "en",      # PubMed is always English
        "region":         "",
        "journal":        journal,
        "topic_tags":     tags,
        "citation_count": 0,         # Would need separate API for this
        "content_chunks": chunks,
        "trust_score":    0,
    }

    # ── Step 7: Calculate Trust Score ──
    trust_result = calculate_trust_score(source_data)
    source_data["trust_score"] = trust_result["trust_score"]

    print(f"  ✓ Done! Trust Score: {source_data['trust_score']}")
    return source_data