import requests
from bs4 import BeautifulSoup
from src.collector_base import BaseCollector

AI_KEYWORDS = [
    "ai", "llm", "gpt", "transformer", "machine-learning", "deep-learning",
    "neural", "pytorch", "tensorflow", "rag", "agent", "embedding",
    "diffusion", "language-model", "multimodal", "nlp", "chatbot",
    "openai", "claude", "llama", "mistral", "qwen", "gemma",
]


class GitHubTrendingCollector(BaseCollector):
    source_name = "github_trending"

    def _is_ai_related(self, repo: dict) -> bool:
        text = f"{repo['name']} {repo['description']} {' '.join(repo['topics'])}".lower()
        return any(kw in text for kw in AI_KEYWORDS)

    def _parse_trending(self, language: str = "") -> list[dict]:
        url = f"https://github.com/trending/{language}?since=daily"
        if language == "":
            url = "https://github.com/trending?since=daily"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        repos = []

        for article in soup.select("article.Box-row"):
            name_el = article.select_one("h2 a")
            if not name_el:
                continue
            full_name = name_el.get("href", "").strip("/")

            desc_el = article.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""

            stars_el = article.select_one(".d-inline-block.float-sm-right")
            stars = stars_el.get_text(strip=True).split()[0] if stars_el else ""

            lang_el = article.select_one("[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else ""

            topics = [t.get_text(strip=True) for t in article.select(".topic-tag")]

            repos.append({
                "title": full_name.split("/")[-1] if "/" in full_name else full_name,
                "name": full_name,
                "url": f"https://github.com/{full_name}",
                "description": description,
                "language": lang,
                "stars": stars,
                "topics": topics,
                "type": "oss",
                "source": "GitHub Trending",
            })

        return repos

    def collect(self) -> list[dict]:
        all_repos = self._parse_trending("")
        all_repos.extend(self._parse_trending("python"))

        ai_repos = [r for r in all_repos if self._is_ai_related(r)]
        seen = set()
        unique = []
        for r in ai_repos:
            if r["name"] not in seen:
                seen.add(r["name"])
                unique.append(r)

        return unique[:15]
