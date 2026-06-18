import json
import os
from datetime import datetime
from src.config import DATA_DIR


class BaseCollector:
    source_name = "base"

    def collect(self) -> list[dict]:
        raise NotImplementedError

    def save(self, data: list[dict]):
        os.makedirs(DATA_DIR, exist_ok=True)
        path = os.path.join(DATA_DIR, f"{self.source_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"updated_at": datetime.utcnow().isoformat(), "items": data}, f, ensure_ascii=False, indent=2)
        print(f"  [{self.source_name}] saved {len(data)} items")

    def load_cached(self) -> list[dict]:
        path = os.path.join(DATA_DIR, f"{self.source_name}.json")
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
