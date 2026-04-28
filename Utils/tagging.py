# utils/tagging.py

# Dictionary of topics and their keywords
# If content contains these words → add that topic tag

TOPIC_KEYWORDS = {
    "AI":               ["artificial intelligence", "ai", "machine learning",
                         "deep learning", "neural network", "llm", "gpt"],
    "Healthcare":       ["health", "medical", "disease", "patient", "hospital",
                         "clinical", "drug", "treatment", "medicine"],
    "Data Science":     ["data science", "data analysis", "dataset", "pandas",
                         "numpy", "statistics", "visualization"],
    "Python":           ["python", "django", "flask", "pip", "pytorch"],
    "Web Development":  ["html", "css", "javascript", "react", "frontend",
                         "backend", "api", "web development"],
    "Research":         ["study", "research", "journal", "abstract", "findings",
                         "methodology", "peer-reviewed", "pubmed"],
    "Technology":       ["technology", "software", "hardware", "computer",
                         "programming", "developer", "tech"],
    "NLP":              ["nlp", "natural language", "text processing",
                         "sentiment", "tokenization", "transformer"],
    "Cybersecurity":    ["security", "hacking", "vulnerability", "encryption",
                         "firewall", "malware", "cyber"],
    "Finance":          ["finance", "stock", "investment", "economy",
                         "banking", "cryptocurrency", "market"],
}


def generate_tags(text: str, max_tags: int = 5) -> list:
    """
    Looks through the text and returns matching topic tags.
    
    Returns a list like: ["AI", "Healthcare", "Research"]
    """

    # Edge case: empty content
    if not text or text.strip() == "":
        return ["General"]

    text_lower = text.lower()
    matched_tags = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched_tags.append(topic)
                break  # Don't add same topic twice

    # If nothing matched
    if not matched_tags:
        return ["General"]

    # Return only up to max_tags
    return matched_tags[:max_tags]