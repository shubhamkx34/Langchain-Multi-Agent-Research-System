from src.Tools.Tools import search_tool, scrape_url

query = "Impact of AI on the job market in 2026"

# 1. Search the web
results = search_tool.invoke(query)

# 2. Select the result with the highest relevance score
pages = results.get("results", [])

# Take every search result → check its URL → exclude PDF links → store the remaining results in web_pages
web_pages = [
    r for r in pages
    if not r["url"].lower().split("?")[0].endswith(".pdf")
]

if web_pages:
    best = max(web_pages, key=lambda r: r.get("score", 0))  # lambda r: → Looks at each search result one by one.

    print("Title:", best["title"])
    print("URL:", best["url"])

    # 3. Scrape only the best URL
    content = scrape_url.invoke({"url": best["url"]})

    print("\nExtracted Content:\n", content)
else:
    print("No search results found.")