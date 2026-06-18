import json
import os
from datetime import datetime
from src.config import DATA_DIR, today_str


class BaseCollector:
    source_name = "base"

    def collect(self) -> list[dict]:
        raise NotImplementedError

    def _save_path(self, date: str = "") -> str:
        d = date or today_str()
        path = os.path.join(DATA_DIR, d)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, f"{self.source_name}.json")

    def save(self, data: list[dict]):
        path = self._save_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"updated_at": datetime.utcnow().isoformat(), "items": data}, f, ensure_ascii=False, indent=2)
        print(f"  [{self.source_name}] saved {len(data)} items")

    def load_cached(self, date: str = "") -> list[dict]:
        path = self._save_path(date)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("items", [])
        return []

    def run(self) -> list[dict]:
        print(f"\n[{self.source_name}] collecting...")
        try:
            data = self.collect()
            self.save(data)
            return data
        except Exception as e:
            print(f"  [{self.source_name}] error: {e}")
            cached = self.load_cached()
            if cached:
                print(f"  [{self.source_name}] using cached {len(cached)} items")
            return cached
