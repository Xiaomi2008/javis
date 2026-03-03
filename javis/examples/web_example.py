"""Example of web operations."""

from javis import Javis


def main():
    javis = Javis()
    
    print("🌐 Web Search (requires BRAVE_API_KEY)")
    try:
        results = javis.web_search("Python asyncio best practices", count=3)
        for r in results:
            print(f"  - {r.title}: {r.url}")
    except Exception as e:
        print(f"  Search failed: {e}")
    
    print("\n📄 Web Fetch")
    try:
        content = javis.web_fetch("https://docs.python.org/3/library/asyncio.html", max_chars=500)
        print(content[:500] + "...")
    except Exception as e:
        print(f"  Fetch failed: {e}")


if __name__ == "__main__":
    main()
