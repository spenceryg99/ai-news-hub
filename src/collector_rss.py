import feedparser
from datetime import datetime
from src.collector_base import BaseCollector
from src.config import RSS_FEEDS


class RSSCollector(BaseCollector):
    source_name = "rss_news"

    def _parse_feed(self, name: str, url: str) -> list[dict]:
        import socket
        socket.setdefaulttimeout(8)
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:5]:
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6]).isoformat()
                except Exception:
                    pass
                    items.append({
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "description": (entry.get("summary") or entry.get("description", ""))[:400],
                        "published": published,
                        "source": name,
                        "type": "news",
                    })
        return items

    def collect(self) -> list[dict]:
        items = []
        for feed_conf in RSS_FEEDS:
            name = feed_conf["name"]
            url = feed_conf["url"]
            try:
                feed_items = self._parse_feed(name, url)
                items.extend(feed_items)
                print(f"  [rss_news] {name}: {len(feed_items)} items")
            except Exception as e:
                print(f"  [rss_news] error fetching {name}: {e}")

        items.sort(key=lambda x: x.get("published", ""), reverse=True)
        return items[:10]
