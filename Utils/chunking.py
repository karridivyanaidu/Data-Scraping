# utils/chunking.py

def chunk_text(text: str, chunk_size: int = 500) -> list:
    """
    Splits a long piece of text into smaller chunks.
    
    Why? Because downstream AI tools (like embeddings)
    work better with smaller pieces of text.
    
    chunk_size = max number of characters per chunk
    """

    # Edge case: empty text
    if not text or text.strip() == "":
        return []

    # Split by paragraphs first (double newline)
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        # Skip empty paragraphs
        if not paragraph:
            continue

        # If adding this paragraph exceeds chunk size,
        # save current chunk and start a new one
        if len(current_chunk) + len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks