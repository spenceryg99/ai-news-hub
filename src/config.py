from datetime import datetime

DATA_DIR = "data"
OUTPUT_DIR = "output"

COLLECTORS = {
    "hf_papers": {"enabled": True, "max_items": 15},
    "arxiv": {"enabled": True, "max_items": 15},
    "github_trending": {"enabled": True, "max_items": 15},
    "hf_models": {"enabled": True, "max_items": 15},
    "rss_news": {"enabled": True, "max_items": 10},
}

RSS_FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "ArXiv Blog", "url": "https://blog.arxiv.org/feed/"},
    {"name": "Reddit r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/.rss"},
    {"name": "MIT AI News", "url": "https://news.mit.edu/topic/artificial-intelligence2/rss"},
    {"name": "Google AI Blog", "url": "https://feeds.feedburner.com/blog/research/generative-ai"},
]

SITE_CONFIG = {
    "title": "AI News Hub",
    "description": "Daily aggregation of AI news, papers, open-source models, and trending GitHub repos.",
    "language": "zh-CN",
}

def today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")
