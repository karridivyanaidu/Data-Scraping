# Data Scraping

## Tools & Libraries used: 
- requests -  for HTTP fetching for all scrapers
- beautifulsoup4 - HTML parsing and element extraction
- lmxl - for fast HTML parsing backend
- trafilatura - cleans article body text extraction
- youtube-transcript-api — fetches auto-generated and manual youtube transcipts
- langdetect — language detection

## Scraping Approach:
Blog posts:
- The blog scrapper uses a multilayer extraction strategy to handle wide variety of blog platforms like wordpress, medium, custom CMS etc.
-  Fetches HTML with a browser User-Agent, then extracts author/date through a cascade: meta tags → JSON-LD → CSS selectors. Body text uses trafilatura first, falls back to BeautifulSoup targeting common article containers. Dates are normalised to ISO-8601.

Youtube:
- Reads Open Graph meta tags for title/description/date. Channel name comes from the ytInitialData JSON blob embedded in the page source. Transcripts are fetched via youtube-transcript-api (manual → auto-generated → any language), falling back to the video description if none are available.

PubMed:
Uses the official NCBI E-utilities API (efetch) to get clean XML with title, authors, journal, abstract, and date. Falls back to BeautifulSoup HTML scraping if the PMID can't be extracted from the URL.

## Limitations
- Some sites block author/date extraction
- YouTube transcripts unavailable for some videos
- YouTube publish dates require API key
