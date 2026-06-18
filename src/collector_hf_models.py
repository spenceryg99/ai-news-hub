import requests
from src.collector_base import BaseCollector
from src.utils import hf_url


class HFModelsCollector(BaseCollector):
    source_name = "hf_models"

    def collect(self) -> list[dict]:
        url = hf_url("/api/models")
        params = {"sort": "lastModified", "direction": -1, "limit": 30, "full": "false"}
        resp = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()

        models = resp.json()
        items = []
        for model in models:
            model_id = model.get("modelId", model.get("id", ""))
            items.append({
                "title": model_id,
                "name": model_id,
                "url": hf_url("/" + model_id),
                "description": (model.get("description") or "")[:300],
                "pipeline_tag": model.get("pipeline_tag", ""),
                "tags": model.get("tags", [])[:5],
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "source": "Hugging Face Models",
                "type": "model",
            })

        return items[:15]
