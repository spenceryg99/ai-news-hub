import json
import os
from datetime import datetime
from src.config import DATA_DIR, COLLECTORS, today_str
from src.collector_hf_papers import HFPapersCollector
from src.collector_arxiv import ArxivCollector
from src.collector_github import GitHubTrendingCollector
from src.collector_hf_models import HFModelsCollector
from src.collector_rss import RSSCollector


def get_collector(name: str):
    mapping = {
        "hf_papers": HFPapersCollector,
        "arxiv": ArxivCollector,
        "github_trending": GitHubTrendingCollector,
        "hf_models": HFModelsCollector,
        "rss_news": RSSCollector,
    }
    cls = mapping.get(name)
    if cls:
        return cls()
    return None


def list_dates() -> list[str]:
    if not os.path.exists(DATA_DIR):
        return []
    dates = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d)) and "-" in d]
    dates.sort(reverse=True)
    return dates


def run_all():
    os.makedirs(DATA_DIR, exist_ok=True)

    all_data = {}
    for name, cfg in COLLECTORS.items():
        if not cfg.get("enabled", True):
            print(f"[aggregator] Skipping {name} (disabled)")
            continue
        collector = get_collector(name)
        if collector:
            items = collector.run()
            all_data[name] = items

    manifest = {
        "updated_at": datetime.utcnow().isoformat(),
        "date": today_str(),
        "sources": list(COLLECTORS.keys()),
        "total_items": sum(len(v) for v in all_data.values()),
    }

    manifest_path = os.path.join(DATA_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n[aggregator] Done! Total items: {manifest['total_items']}")
    return all_data


def load_by_date(date: str) -> dict:
    data = {}
    base = os.path.join(DATA_DIR, date)
    if not os.path.exists(base):
        return data
    for name in COLLECTORS:
        path = os.path.join(base, f"{name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data[name] = json.load(f).get("items", [])
        else:
            data[name] = []
    return data


def load_all() -> dict:
    return load_by_date(today_str())


if __name__ == "__main__":
    run_all()
