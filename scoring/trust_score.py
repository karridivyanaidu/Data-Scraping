# scoring/trust_score.py

# We need 'datetime' to work with dates (for recency calculation)
from datetime import datetime, timezone


# ─────────────────────────────────────────────
# SECTION 1: WEIGHTS
# These control how much each factor matters.
# All weights must add up to 1.0 (100%)
# ─────────────────────────────────────────────

WEIGHTS = {
    "author_credibility":          0.25,   # 25%
    "citation_count":              0.20,   # 20%
    "domain_authority":            0.25,   # 25%
    "recency":                     0.20,   # 20%
    "medical_disclaimer_presence": 0.10,   # 10%
}


# ─────────────────────────────────────────────
# SECTION 2: KNOWN TRUSTED DOMAINS
# These are websites we consider high-authority
# ─────────────────────────────────────────────

TRUSTED_DOMAINS = [
    "pubmed.ncbi.nlm.nih.gov",
    "who.int",
    "cdc.gov",
    "nature.com",
    "sciencedirect.com",
    "medium.com",
    "towardsdatascience.com",
    "harvard.edu",
    "mit.edu",
    "youtube.com",       # YouTube channels can be trusted
]

# Domains that are considered spammy or low quality
PENALIZED_DOMAINS = [
    "spamsite.com",
    "fakehealth.net",
    "clickbait.info",
]

# Known credible author name keywords
TRUSTED_AUTHOR_KEYWORDS = [
    "dr.", "prof.", "phd", "md", "researcher",
    "scientist", "professor", "institute", "university"
]


# ─────────────────────────────────────────────
# SECTION 3: INDIVIDUAL SCORING FUNCTIONS
# Each function returns a score from 0.0 to 1.0
# ─────────────────────────────────────────────


def score_author_credibility(author: str) -> float:
    """
    Scores how credible the author is.

    Rules:
    - If author is missing → 0.1 (very low, penalized)
    - If author name contains trusted keywords (Dr., PhD, etc.) → 0.9
    - Otherwise → 0.5 (neutral/unknown author)

    Edge Case: Multiple authors → caller passes average score directly
    """

    # Edge case: author not available
    if not author or author.strip() == "" or author.lower() == "unknown":
        return 0.1   # Penalize missing author

    # Normalize to lowercase for comparison
    author_lower = author.lower()

    # Check if author has credibility signals
    for keyword in TRUSTED_AUTHOR_KEYWORDS:
        if keyword in author_lower:
            return 0.9   # High credibility

    # Default: unknown individual author
    return 0.5


def score_citation_count(citation_count: int, source_type: str) -> float:
    """
    Scores based on number of citations or references.

    Different thresholds for different source types:
    - PubMed articles are expected to have more citations
    - Blogs may have 0 citations and that's normal

    Edge Case: If citation_count is None → treat as 0
    """

    # Edge case: missing citation data
    if citation_count is None:
        citation_count = 0

    # For academic sources (PubMed), use higher thresholds
    if source_type == "pubmed":
        if citation_count >= 100:
            return 1.0
        elif citation_count >= 50:
            return 0.8
        elif citation_count >= 10:
            return 0.6
        elif citation_count >= 1:
            return 0.4
        else:
            return 0.2   # Published but never cited — suspicious

    # For blogs and YouTube
    else:
        if citation_count >= 10:
            return 0.9
        elif citation_count >= 5:
            return 0.7
        elif citation_count >= 1:
            return 0.5
        else:
            return 0.4   # No citations — neutral for blogs (common)


def score_domain_authority(source_url: str) -> float:
    """
    Scores the domain (website) based on its reputation.

    Rules:
    - Trusted domain list → high score
    - Penalized domain list → very low score
    - Unknown domain → neutral score

    Abuse Prevention:
    - SEO spam blogs are in the penalized list
    - We check the full URL for domain matches
    """

    # Edge case: URL is missing
    if not source_url or source_url.strip() == "":
        return 0.1

    url_lower = source_url.lower()

    # Check penalized domains first (abuse prevention)
    for domain in PENALIZED_DOMAINS:
        if domain in url_lower:
            return 0.1   # Strong penalty for spam domains

    # Check trusted domains
    for domain in TRUSTED_DOMAINS:
        if domain in url_lower:
            return 0.9

    # Unknown domain — neutral score
    return 0.5


def score_recency(published_date: str) -> float:
    """
    Scores how recent the content is.

    Rules (age of content):
    - Less than 6 months old  → 1.0
    - 6 months to 1 year      → 0.8
    - 1 to 2 years            → 0.6
    - 2 to 4 years            → 0.4
    - Older than 4 years      → 0.2

    Edge Case:
    - Date missing or unparseable → return 0.3 (penalized but not zero)

    Abuse Prevention:
    - Outdated info gets strong penalty (medical content goes stale)
    """

    # Edge case: date not available
    if not published_date or published_date.strip() == "":
        return 0.3

    # Try to parse the date string
    # We support multiple common date formats
    date_formats = [
        "%Y-%m-%d",        # 2024-03-15
        "%d/%m/%Y",        # 15/03/2024
        "%B %d, %Y",       # March 15, 2024
        "%b %d, %Y",       # Mar 15, 2024
        "%Y",              # 2024 (year only)
    ]

    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(published_date.strip(), fmt)
            break   # Stop once we successfully parse
        except ValueError:
            continue   # Try next format

    # If no format worked
    if parsed_date is None:
        return 0.3   # Unknown date — mild penalty

    # Calculate how old the content is (in days)
    today = datetime.now()
    age_in_days = (today - parsed_date).days

    # Score based on age
    if age_in_days < 180:       # Less than 6 months
        return 1.0
    elif age_in_days < 365:     # 6 months to 1 year
        return 0.8
    elif age_in_days < 730:     # 1 to 2 years
        return 0.6
    elif age_in_days < 1460:    # 2 to 4 years
        return 0.4
    else:                        # Older than 4 years
        return 0.2


def score_medical_disclaimer(content: str, source_type: str) -> float:
    """
    Checks if medical content has a proper disclaimer.

    Rules:
    - If content contains disclaimer phrases → 1.0
    - If source is PubMed (always credible, no disclaimer needed) → 0.8
    - If no disclaimer found → 0.2 (penalized)

    Abuse Prevention:
    - Misleading health blogs that don't show disclaimers get penalized
    """

    # PubMed articles are peer-reviewed — no disclaimer needed
    if source_type == "pubmed":
        return 0.8

    # Edge case: content is empty
    if not content or content.strip() == "":
        return 0.3

    # Keywords that signal a medical disclaimer is present
    disclaimer_keywords = [
        "consult a doctor",
        "consult your physician",
        "not medical advice",
        "for informational purposes only",
        "seek professional advice",
        "talk to your healthcare provider",
        "this is not a substitute",
        "medical professional",
    ]

    content_lower = content.lower()

    for phrase in disclaimer_keywords:
        if phrase in content_lower:
            return 1.0   # Disclaimer found

    # No disclaimer — penalize (especially important for health content)
    return 0.2


# ─────────────────────────────────────────────
# SECTION 4: MAIN TRUST SCORE FUNCTION
# This is the function you call from outside
# ─────────────────────────────────────────────


def calculate_trust_score(source_data: dict) -> dict:
    """
    Main function to calculate the trust score for a source.

    Input:  source_data (dict) — the scraped JSON object
    Output: dict with individual scores + final trust_score

    How to call this:
        result = calculate_trust_score(my_source_dict)
        print(result["trust_score"])
    """

    # ── Extract fields from the source data ──
    source_url     = source_data.get("source_url", "")
    source_type    = source_data.get("source_type", "blog").lower()
    author         = source_data.get("author", "")
    published_date = source_data.get("published_date", "")
    citation_count = source_data.get("citation_count", 0)
    content        = " ".join(source_data.get("content_chunks", []))

    # ── Handle multiple authors ──
    # If author field has multiple names separated by comma
    if author and "," in author:
        authors = [a.strip() for a in author.split(",")]
        # Calculate average credibility across all authors
        author_score = sum(score_author_credibility(a) for a in authors) / len(authors)
    else:
        author_score = score_author_credibility(author)

    # ── Calculate each sub-score ──
    sub_scores = {
        "author_credibility":          round(author_score, 3),
        "citation_count":              round(score_citation_count(citation_count, source_type), 3),
        "domain_authority":            round(score_domain_authority(source_url), 3),
        "recency":                     round(score_recency(published_date), 3),
        "medical_disclaimer_presence": round(score_medical_disclaimer(content, source_type), 3),
    }

    # ── Apply weights to get final score ──
    # Formula: Trust = w1*s1 + w2*s2 + w3*s3 + w4*s4 + w5*s5
    final_score = sum(
        WEIGHTS[factor] * sub_scores[factor]
        for factor in WEIGHTS
    )

    # Round to 3 decimal places
    final_score = round(final_score, 3)

    # ── Return full breakdown ──
    return {
        "trust_score":  final_score,
        "breakdown":    sub_scores,    # Useful for debugging
        "weights_used": WEIGHTS,
    }