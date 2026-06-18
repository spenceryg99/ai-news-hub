import arxiv
from datetime import datetime, timezone
from src.collector_base import BaseCollector


class ArxivCollector(BaseCollector):
    source_name = "arxiv"

    def collect(self) -> list[dict]:
        client = arxiv.Client(page_size=10, delay_seconds=1, num_retries=1)

        categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]
        seen = set()
        items = []

        for cat in categories:
            try:
                search = arxiv.Search(
                    query=f"cat:{cat}",
                    max_results=8,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                )
                for result in client.results(search):
                    if result.entry_id in seen:
                        continue
                    seen.add(result.entry_id)
                    items.append({
                        "title": result.title,
                        "url": result.entry_id,
                        "description": result.summary[:400],
                        "authors": [a.name for a in result.authors[:5]],
                        "published": result.published.isoformat() if result.published else "",
                        "categories": [c for c in result.categories[:3]],
                        "source": f"arXiv ({cat})",
                    })
            except Exception as e:
                print(f"  [arxiv] error fetching category {cat}: {e}")

        items.sort(key=lambda x: x.get("published", ""), reverse=True)
        return items[:15]
