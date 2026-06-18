import requests
from bs4 import BeautifulSoup
from src.collector_base import BaseCollector
from src.utils import hf_url


class HFPapersCollector(BaseCollector):
    source_name = "hf_papers"

    def collect(self) -> list[dict]:
        url = hf_url("/papers")
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        items = []

        for article in soup.select("article"):
            title_el = article.select_one("h3 a, h2 a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            if link and not link.startswith("http"):
                link = hf_url(link)

            desc_el = article.select_one("p, .description, .paper-description")
            description = desc_el.get_text(strip=True)[:300] if desc_el else ""

            items.append({
                "title": title,
                "url": link,
                "description": description,
                "source": "Hugging Face Daily Papers",
            })

        return items[:15]
