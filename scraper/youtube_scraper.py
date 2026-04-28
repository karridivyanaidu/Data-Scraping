# scraper/youtube_scraper.py

import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from langdetect import detect
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chunking import chunk_text
from utils.tagging import generate_tags
from scoring.trust_score import calculate_trust_score


def extract_video_id(url: str) -> str:
    """
    Pulls the video ID from a YouTube URL.
    
    https://www.youtube.com/watch?v=dQw4w9WgXcQ → dQw4w9WgXcQ
    https://youtu.be/dQw4w9WgXcQ               → dQw4w9WgXcQ
    """
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",      # Standard URL
        r"youtu\.be/([a-zA-Z0-9_-]{11})",  # Short URL
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def scrape_youtube(url: str) -> dict:
    """
    Scrapes a YouTube video for metadata and transcript.
    No API key needed for transcripts!
    """

    print(f"\nScraping YouTube: {url}")

    # ── Step 1: Get Video ID ──
    video_id = extract_video_id(url)
    if not video_id:
        print("  ERROR: Could not extract video ID")
        return None

    print(f"  Video ID: {video_id}")

    # ── Step 2: Get basic metadata via oEmbed (no API key needed) ──
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    title        = ""
    channel_name = ""

    try:
        response = requests.get(oembed_url, timeout=10)
        if response.status_code == 200:
            data         = response.json()
            title        = data.get("title", "")
            channel_name = data.get("author_name", "")
    except Exception as e:
        print(f"  WARNING: Could not get metadata: {e}")

    # ── Step 3: Get Transcript ──
    transcript_text = ""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Transcript is a list of dicts: [{"text": "...", "start": 0.0}, ...]
        transcript_text = " ".join(entry["text"] for entry in transcript)
        print(f"  ✓ Transcript fetched ({len(transcript_text)} chars)")
    except Exception as e:
        print(f"  WARNING: Transcript not available: {e}")
        transcript_text = title  # Fallback to title only

    # ── Step 4: Detect Language ──
    language = "en"
    try:
        if transcript_text:
            language = detect(transcript_text[:500])
    except:
        language = "en"

    # ── Step 5: Generate Tags & Chunks ──
    full_content = f"{title}\n\n{transcript_text}"
    tags   = generate_tags(full_content)
    chunks = chunk_text(full_content)

    # ── Step 6: Build source dictionary ──
    source_data = {
        "source_url":     url,
        "source_type":    "youtube",
        "title":          title,
        "author":         channel_name,
        "published_date": "",       # Hard to get without API key
        "language":       language,
        "region":         "",
        "topic_tags":     tags,
        "citation_count": 0,
        "content_chunks": chunks,
        "trust_score":    0,
    }

    # ── Step 7: Calculate Trust Score ──
    trust_result = calculate_trust_score(source_data)
    source_data["trust_score"] = trust_result["trust_score"]

    print(f"  ✓ Done! Trust Score: {source_data['trust_score']}")
    return source_data