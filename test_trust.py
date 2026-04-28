# test_trust.py

from scoring.trust_score import calculate_trust_score

# ── Test 1: A good PubMed article ──
pubmed_source = {
    "source_url": "https://pubmed.ncbi.nlm.nih.gov/12345678",
    "source_type": "pubmed",
    "author": "Dr. Jane Smith, Prof. John Doe",
    "published_date": "2024-06-01",
    "citation_count": 85,
    "content_chunks": ["This study examines AI in healthcare..."]
}

# ── Test 2: A sketchy health blog ──
bad_blog = {
    "source_url": "https://fakehealth.net/cure-everything",
    "source_type": "blog",
    "author": "",                  # No author!
    "published_date": "2019-01-01", # Old content
    "citation_count": 0,
    "content_chunks": ["This miracle cure will fix everything!"]
    # No medical disclaimer
}

# ── Test 3: A decent YouTube video ──
youtube_source = {
    "source_url": "https://www.youtube.com/watch?v=abc123",
    "source_type": "youtube",
    "author": "Tech With Tim",
    "published_date": "2024-11-15",
    "citation_count": 3,
    "content_chunks": ["In this video we learn about machine learning..."]
}

# Run the tests
for name, source in [("PubMed", pubmed_source), ("Bad Blog", bad_blog), ("YouTube", youtube_source)]:
    result = calculate_trust_score(source)
    print(f"\n{'='*40}")
    print(f"Source: {name}")
    print(f"Trust Score: {result['trust_score']}")
    print(f"Breakdown: {result['breakdown']}")