import requests
import textwrap
from datetime import datetime
from dotenv import load_dotenv
import os

# Get API key
load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")

KEYWORDS = "cybersecurity OR data breach OR malware OR ransomware" # Adjust keywords however you want

# Specify specific domains to search
DOMAINS = (
    "thehackernews.com,bleepingcomputer.com,darkreading.com,securityweek.com,infosecurity-magazine.com,threatpost.com"
)

URL = "https://newsapi.org/v2/everything"

# Search parameters
params = {
    "q": KEYWORDS,
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 100, # Control how many news articles are displayed.
    "domains": DOMAINS,
    "apiKey": API_KEY
}

# Shortens description without altering meaning
def summarise_text(text, max_length=80):
    return textwrap.shorten(text or "No description available", width=max_length, placeholder="...")

# Convert ISO date string to a more readable format
def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y at %H:%M UTC")

    except Exception:
        return "Unknown date"


def main():
    response = requests.get(URL, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print("Error fetching data:", data)
        return

    articles = data.get("articles", [])

    if not articles:
        print("No cybersecurity-related news found.")
        return

    print(f"Fetched {len(articles)} cybersecurity news articles. \n")

    for article in articles:
        title = article.get("title")
        description = article.get("description")
        url = article.get("url")
        source = article.get("source", {}).get("name", "Unknown Source")
        published_at = article.get("publishedAt")
        readable_date = format_date(published_at)

        summary = summarise_text(description)

        print(f"Title: {title}")
        print(f"Source: {source}")
        print(f"Published: {readable_date}")
        print(f"Summary: {summary}")
        print(f"Read More: {url}")
        print("-" * 80)


if __name__ == "__main__":
    main()


