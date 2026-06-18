import arxiv
from datetime import datetime, timezone
from src.collector_base import BaseCollector


class ArxivCollector(BaseCollector):
    source_name = "arxiv"

    def collect(self) -> list[dict]:
        client = arxiv.Client(page_size=10, delay_seconds=1, num_retries=1)

        categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.MA", "cs.RO", "cs.NE"]
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

                    pdf_url = ""
                    for link in result.links:
                        if link.title == "pdf":
                            pdf_url = link.href
                            break

                    items.append({
                        "title": result.title,
                        "url": result.entry_id,
                        "pdf_url": pdf_url,
                        "abstract": result.summary,
                        "summary": result.summary[:500],
                        "authors": [a.name for a in result.authors],
                        "published": result.published.isoformat() if result.published else "",
                        "updated": result.updated.isoformat() if result.updated else "",
                        "categories": result.categories,
                        "comment": getattr(result, "comment", ""),
                        "source": f"arXiv",
                        "type": "paper",
                    })
            except Exception as e:
                print(f"  [arxiv] error fetching category {cat}: {e}")

        items.sort(key=lambda x: x.get("published", ""), reverse=True)
        return items[:20]
