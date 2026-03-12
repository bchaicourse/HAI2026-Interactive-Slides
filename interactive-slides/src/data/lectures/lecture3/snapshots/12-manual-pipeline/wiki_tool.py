"""Wikipedia search tool for AutoGen agents."""

import json
import urllib.request
import urllib.parse


def search_wikipedia(query: str) -> str:
    """Search Wikipedia for a topic and return a brief summary.

    Args:
        query: The topic to search for on Wikipedia.

    Returns:
        A summary of the most relevant Wikipedia article.
    """
    try:
        headers = {"User-Agent": "DecisionSupport/1.0"}

        params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 1,
            "format": "json",
        })
        req = urllib.request.Request(
            f"https://en.wikipedia.org/w/api.php?{params}",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        results = data.get("query", {}).get("search", [])
        if not results:
            return f"No Wikipedia articles found for '{query}'."

        title = results[0]["title"]

        params2 = urllib.parse.urlencode({
            "action": "query",
            "titles": title,
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "format": "json",
        })
        req2 = urllib.request.Request(
            f"https://en.wikipedia.org/w/api.php?{params2}",
            headers=headers,
        )
        with urllib.request.urlopen(req2, timeout=10) as resp:
            data2 = json.loads(resp.read())

        pages = data2.get("query", {}).get("pages", {})
        for page in pages.values():
            extract = page.get("extract", "")
            if extract:
                if len(extract) > 1000:
                    extract = extract[:1000] + "..."
                return f"{title}: {extract}"

        return f"Found '{title}' but could not retrieve summary."
    except Exception as e:
        return f"Wikipedia search failed: {e}"
