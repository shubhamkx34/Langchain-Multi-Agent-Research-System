import os
from langchain.tools import tool 
import requests
from dotenv import load_dotenv
from langchain_tavily import TavilySearch 
from bs4 import BeautifulSoup
from rich import print
from readability import Document
import trafilatura
import re 

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
search_tool = TavilySearch(max_results=5)

@tool 
def web_search(query:str)->str:
     """Search the web for recent information. Returns top target URLs for deep scraping and snippets for all results."""
     results = search_tool.invoke(query)
     pages = results.get("results", [])

    # Filter out direct PDF links
     web_pages = [
        r for r in pages
        if not r["url"].lower().split("?")[0].endswith(".pdf")
    ]
     if not web_pages:
        return "No valid web results found."

     # Sort results by relevance score (highest to lowest)
     web_pages.sort(key=lambda r: r.get("score", 0), reverse=True)

    # Isolate the top 2 URLs for deep scraping
     top_targets = web_pages[:2]

     summary = [
        f"Topic: {query}",
        "--- Top Target URLs for Deep Scraping ---"
    ]

     for target in top_targets:
        summary.append(f"URL: {target['url']} (Relevance Score: {target.get('score', 0):.2f})")

        summary.append("\n--- All Search Results & Snippets (Broad Context) ---")
 
    # Keep all snippets to provide broad context to the Writer Chain
     for r in web_pages:
        score_val = r.get('score', 0)
        summary.append(
            f"Title: {r['title']}\nURL: {r['url']}\nRelevance Score: {score_val:.2f}\nSnippet: {r['content'][:300]}\n"
        )
    
     return "\n".join(summary)

# TOOL 2 - CONTENT SCRAPPER TOOL:  
@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        html = response.text

# 1.Extract using Trafilatura
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

# 2.Extract using Readability and BeautifulSoup
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:5000]


 # 3.Fallback extraction
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."

# ERROR-HANDLING:

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


