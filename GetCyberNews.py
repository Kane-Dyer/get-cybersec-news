import requests
import textwrap
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import os

def summarise_text(text, max_length=120):
    return textwrap.shorten(text or "No description available", width=max_length, placeholder="...")

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y at %H:%M UTC")
    except Exception:
        return "Unknown date"

class NewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cybersecurity News Fetcher")
        self.geometry("900x650")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="x")

        # API Key
        ttk.Label(frm, text="NewsAPI Key:").grid(column=0, row=0, sticky="w")
        self.api_key_var = tk.StringVar(value=os.getenv("NEWSAPI_KEY",""))
        ttk.Entry(frm, textvariable=self.api_key_var, width=60).grid(column=1, row=0, sticky="w", padx=5, pady=2, columnspan=3)

        # Keywords
        ttk.Label(frm, text="Keywords:").grid(column=0, row=1, sticky="w")
        self.keywords_var = tk.StringVar(value="cybersecurity OR data breach OR malware OR ransomware")
        ttk.Entry(frm, textvariable=self.keywords_var, width=60).grid(column=1, row=1, sticky="w", padx=5, pady=2, columnspan=3)

        # Domains
        ttk.Label(frm, text="Domains (comma separated):").grid(column=0, row=2, sticky="w")
        self.domains_var = tk.StringVar(value="thehackernews.com,bleepingcomputer.com,darkreading.com,securityweek.com,infosecurity-magazine.com,threatpost.com")
        ttk.Entry(frm, textvariable=self.domains_var, width=60).grid(column=1, row=2, sticky="w", padx=5, pady=2, columnspan=3)

        # Page size
        ttk.Label(frm, text="Page Size:").grid(column=0, row=3, sticky="w")
        self.page_size_var = tk.IntVar(value=30)
        ttk.Spinbox(frm, from_=1, to=100, textvariable=self.page_size_var, width=6).grid(column=1, row=3, sticky="w", padx=5, pady=2)

        # Fetch button
        self.fetch_btn = ttk.Button(frm, text="Fetch News", command=self.fetch_news)
        self.fetch_btn.grid(column=3, row=3, sticky="e", padx=5, pady=2)

        # Results area
        self.results = scrolledtext.ScrolledText(self, wrap="word", height=25)
        self.results.pack(fill="both", expand=True, padx=10, pady=8)
        self.results.tag_configure("title", font=("TkDefaultFont", 10, "bold"))
        self.results.tag_configure("link", foreground="blue", underline=True)
        self.results.tag_bind("link", "<Button-1>", lambda e: self.open_link(e))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=5)
        status.pack(fill="x", side="bottom")

    def fetch_news(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Missing API Key", "Please provide your NewsAPI API key in the top field (or set NEWSAPI_KEY in your environment).")
            return

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": self.keywords_var.get(),
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": self.page_size_var.get(),
            "domains": self.domains_var.get(),
            "apiKey": api_key
        }

        self.status_var.set("Fetching...")
        self.update_idletasks()

        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
        except Exception as e:
            messagebox.showerror("Request error", f"Failed to fetch news:\n{e}")
            self.status_var.set("Error")
            return

        if data.get("status") != "ok":
            messagebox.showerror("API error", f"NewsAPI returned an error:\n{data}")
            self.status_var.set("Error")
            return

        articles = data.get("articles", [])
        if not articles:
            self.results.delete("1.0", tk.END)
            self.results.insert(tk.END, "No articles found.\n")
            self.status_var.set("No articles")
            return

        self.results.delete("1.0", tk.END)
        self.status_var.set(f"Fetched {len(articles)} articles")
        for i, article in enumerate(articles, start=1):
            title = article.get("title") or "No title"
            source = article.get("source", {}).get("name", "Unknown Source")
            published_at = format_date(article.get("publishedAt"))
            desc = summarise_text(article.get("description"), max_length=160)
            url = article.get("url") or ""

            self.results.insert(tk.END, f"{i}. ", ("title",))
            start_index = self.results.index(tk.INSERT)
            self.results.insert(tk.END, f"{title}\n", ("title",))
            end_index = self.results.index(tk.INSERT)

            # Insert link
            link_text = f"Read more: {url}\n"
            link_start = self.results.index(tk.INSERT)
            self.results.insert(tk.END, link_text, ("link",))
            link_end = self.results.index(tk.INSERT)
            # Attach URL to the text via a tag named with the index
            tag_name = f"link_{i}"
            self.results.tag_add(tag_name, link_start, link_end)
            self.results.tag_bind(tag_name, "<Button-1>", lambda e, u=url: webbrowser.open(u))

            # Article meta and summary
            self.results.insert(tk.END, f"Source: {source} | Published: {published_at}\n")
            self.results.insert(tk.END, f"Summary: {desc}\n")
            self.results.insert(tk.END, "-"*80 + "\n")

    def open_link(self, event):
        # Not used; individual tags open links directly.
        pass

if __name__ == "__main__":
    app = NewsApp()
    app.mainloop()
